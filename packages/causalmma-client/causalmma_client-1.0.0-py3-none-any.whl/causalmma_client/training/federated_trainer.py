"""
Federated Trainer

Trains causal inference models with federated learning support.
Trains locally, shares only weights (not data) with federation.
"""

import pandas as pd
import numpy as np
import requests
from typing import Dict, Any, Optional, Literal
from pathlib import Path
from datetime import datetime
import pickle
import base64

from .local_trainer import LocalTrainer
from .models import PropensityScoreModel, OutcomeModel


class FederatedTrainer(LocalTrainer):
    """
    Federated learning trainer for causal inference models

    Extends LocalTrainer with federated learning capabilities:
    - Downloads global model from control plane
    - Trains locally (data stays local!)
    - Uploads only weights (not data!) to federation

    Privacy guarantee: Only model weights are shared, never raw data.

    Example:
        >>> from causalmma_client import LocalEngine
        >>> engine = LocalEngine(api_key="ca_live_pro_xxx")
        >>>
        >>> trainer = FederatedTrainer(engine)
        >>> result = trainer.train_and_contribute(
        ...     data=df,  # Stays local!
        ...     model_type="propensity_score",
        ...     treatment_col="treatment",
        ...     covariate_cols=["age", "gender"],
        ...     participate_in_federation=True  # Share weights, not data
        ... )
    """

    def __init__(self, engine, cache_dir: str = './models'):
        """
        Initialize federated trainer

        Args:
            engine: LocalEngine instance (for API access)
            cache_dir: Directory to save trained models
        """
        super().__init__(cache_dir=cache_dir)

        self.engine = engine
        self.control_plane_url = engine.control_plane_url
        self.api_key = engine.api_key
        self.client_id = engine.client_id

        # Check if federated learning is enabled
        if not hasattr(engine, 'features') or engine.features is None:
            print("⚠ Warning: Cannot verify federated learning access")
        elif 'federated_training' not in engine.features:
            print("⚠ Warning: Federated training not in your tier. Upgrade to Pro/Enterprise.")

    def train_and_contribute(
        self,
        data: pd.DataFrame,
        model_type: Literal['propensity_score', 'outcome', 'doubly_robust'],
        outcome_col: Optional[str] = None,
        treatment_col: str = 'treatment',
        covariate_cols: Optional[list] = None,
        method: str = 'logistic',
        epochs: int = 1,
        participate_in_federation: bool = True,
        download_global_model: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Train model locally and optionally contribute to federation

        Args:
            data: Training data (NEVER sent to server!)
            model_type: Type of model ('propensity_score', 'outcome', 'doubly_robust')
            outcome_col: Outcome column name (required for outcome models)
            treatment_col: Treatment column name
            covariate_cols: List of covariate columns (if None, infer from data)
            method: Model method
            epochs: Number of training iterations (currently only 1 supported)
            participate_in_federation: Share weights (not data!) with federation
            download_global_model: Download and initialize from global model
            **kwargs: Additional model parameters

        Returns:
            Dictionary with trained model and metadata
        """
        print(f"\n{'='*70}")
        print(f"  FEDERATED LEARNING TRAINING")
        print(f"{'='*70}")
        print(f"Model type: {model_type}")
        print(f"Training samples: {len(data)}")
        print(f"Participation: {'YES (weights only)' if participate_in_federation else 'NO (local only)'}")
        print(f"Data location: CLIENT (never uploaded)")
        print(f"{'='*70}\n")

        # Infer covariates if not provided
        if covariate_cols is None:
            all_cols = set(data.columns)
            exclude_cols = {treatment_col}
            if outcome_col:
                exclude_cols.add(outcome_col)
            covariate_cols = list(all_cols - exclude_cols)
            print(f"ℹ Inferred {len(covariate_cols)} covariate columns")

        # Step 1: Download global model (if participating and available)
        global_model = None
        if participate_in_federation and download_global_model:
            try:
                global_model = self._download_global_model(model_type)
                print(f"✓ Downloaded global model version {global_model['version']}")
            except Exception as e:
                print(f"ℹ No global model available yet (first contributor?): {e}")

        # Step 2: Train locally
        print(f"\n{'─'*70}")
        print(f"  TRAINING LOCALLY (Data stays on your machine)")
        print(f"{'─'*70}\n")

        if model_type == 'propensity_score':
            model = self.train_propensity_score(
                data=data,
                treatment_col=treatment_col,
                covariate_cols=covariate_cols,
                method=method,
                **kwargs
            )
            # Initialize from global if available
            if global_model and 'weights' in global_model:
                try:
                    model.set_weights(global_model['weights'])
                    # Re-train for a few iterations
                    X = data[covariate_cols]
                    y = data[treatment_col]
                    model.fit(X, y)
                    print("✓ Fine-tuned from global model")
                except Exception as e:
                    print(f"⚠ Could not initialize from global model: {e}")

        elif model_type == 'outcome':
            if outcome_col is None:
                raise ValueError("outcome_col required for outcome models")

            model = self.train_outcome_model(
                data=data,
                outcome_col=outcome_col,
                treatment_col=treatment_col,
                covariate_cols=covariate_cols,
                method=method,
                **kwargs
            )

        elif model_type == 'doubly_robust':
            if outcome_col is None:
                raise ValueError("outcome_col required for doubly robust models")

            models = self.train_doubly_robust(
                data=data,
                outcome_col=outcome_col,
                treatment_col=treatment_col,
                covariate_cols=covariate_cols,
                ps_method=method if model_type == 'propensity_score' else 'logistic',
                outcome_method=method if model_type == 'outcome' else 'linear'
            )
            model = models  # Both models

        else:
            raise ValueError(f"Unknown model_type: {model_type}")

        # Step 3: Optionally contribute to federation
        if participate_in_federation:
            print(f"\n{'─'*70}")
            print(f"  CONTRIBUTING TO FEDERATION")
            print(f"{'─'*70}\n")

            if model_type == 'doubly_robust':
                # Upload both models
                self._submit_to_federation(
                    model=models['propensity_score'],
                    model_type='propensity_score',
                    num_samples=len(data)
                )
                self._submit_to_federation(
                    model=models['outcome'],
                    model_type='outcome',
                    num_samples=len(data)
                )
            else:
                self._submit_to_federation(
                    model=model,
                    model_type=model_type,
                    num_samples=len(data)
                )

            print(f"\n✓ Contributed to federation (weights only, no data shared)")
        else:
            print(f"\nℹ Local training only (not participating in federation)")

        # Step 4: Save model locally
        if model_type != 'doubly_robust':
            self.save_model(model)
        else:
            self.save_model(models['propensity_score'], name='propensity_score')
            self.save_model(models['outcome'], name='outcome')

        print(f"\n{'='*70}")
        print(f"✓ TRAINING COMPLETE")
        print(f"{'='*70}\n")

        return {
            "model": model,
            "model_type": model_type,
            "num_samples": len(data),
            "participated_in_federation": participate_in_federation,
            "metadata": model.metadata if hasattr(model, 'metadata') else {}
        }

    def _download_global_model(self, model_type: str) -> Dict[str, Any]:
        """
        Download current global model from control plane

        Args:
            model_type: Type of model to download

        Returns:
            Dictionary with model version, weights, and metadata
        """
        if self.engine.offline_mode:
            raise ValueError("Cannot download global model in offline mode")

        response = requests.get(
            f"{self.control_plane_url}/control/v1/training/global_model",
            headers={"X-API-Key": self.api_key},
            params={"model_type": model_type},
            timeout=10
        )

        if response.status_code == 404:
            raise ValueError("No global model available yet")

        if response.status_code != 200:
            raise ValueError(f"Failed to download global model: {response.status_code} - {response.text}")

        data = response.json()

        # Download weights
        if 'weights' in data:
            # Weights might be base64 encoded
            if isinstance(data['weights'], str):
                weights_bytes = base64.b64decode(data['weights'])
                weights = pickle.loads(weights_bytes)
                data['weights'] = weights

        return data

    def _submit_to_federation(
        self,
        model,
        model_type: str,
        num_samples: int
    ):
        """
        Submit model update to federation (weights only, no data!)

        Args:
            model: Trained model
            model_type: Type of model
            num_samples: Number of training samples (count only)
        """
        if self.engine.offline_mode:
            print("⚠ Offline mode: Skipping federation submission")
            return

        # Get model weights
        weights = model.get_weights()

        # Serialize weights
        weights_serialized = self._serialize_weights(weights)

        # Create update payload
        update = {
            "client_id": self.client_id,
            "model_type": model_type,
            "model_weights": weights_serialized,
            "num_samples": num_samples,  # Just the count!
            "metrics": {
                # Only summary stats, no raw data
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        # Submit to control plane
        try:
            response = requests.post(
                f"{self.control_plane_url}/control/v1/training/submit_update",
                json=update,
                headers={"X-API-Key": self.api_key},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✓ Update submitted successfully")
                print(f"  Round number: {data.get('round_number', 'N/A')}")
                print(f"  Aggregation status: {data.get('status', 'pending')}")
            else:
                print(f"⚠ Failed to submit update: {response.status_code}")
                print(f"  Response: {response.text}")

        except Exception as e:
            print(f"⚠ Error submitting to federation: {e}")

    def _serialize_weights(self, weights: Dict[str, Any]) -> Dict[str, str]:
        """
        Serialize model weights for transmission

        Args:
            weights: Model weights dictionary

        Returns:
            Serialized weights (base64 encoded)
        """
        # Serialize to bytes
        weights_bytes = pickle.dumps(weights)

        # Encode as base64 for JSON transmission
        weights_b64 = base64.b64encode(weights_bytes).decode('utf-8')

        return {"data": weights_b64}

    def _deserialize_weights(self, weights_serialized: Dict[str, str]) -> Dict[str, Any]:
        """
        Deserialize model weights from transmission format

        Args:
            weights_serialized: Serialized weights

        Returns:
            Deserialized weights dictionary
        """
        weights_b64 = weights_serialized["data"]
        weights_bytes = base64.b64decode(weights_b64)
        weights = pickle.loads(weights_bytes)

        return weights

    def get_federation_status(self) -> Dict[str, Any]:
        """
        Get federated learning status from control plane

        Returns:
            Dictionary with federation status
        """
        if self.engine.offline_mode:
            return {"status": "offline", "message": "Offline mode enabled"}

        try:
            response = requests.get(
                f"{self.control_plane_url}/control/v1/training/status",
                headers={"X-API-Key": self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_available_models(self) -> Dict[str, Any]:
        """
        List available global models from control plane

        Returns:
            Dictionary with available models
        """
        if self.engine.offline_mode:
            return {"models": [], "message": "Offline mode enabled"}

        try:
            response = requests.get(
                f"{self.control_plane_url}/control/v1/training/models",
                headers={"X-API-Key": self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "models": [],
                    "message": f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {"models": [], "message": str(e)}
