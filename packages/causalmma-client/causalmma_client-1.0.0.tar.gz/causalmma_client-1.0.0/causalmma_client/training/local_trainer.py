"""
Local Trainer

Trains causal inference models locally (client-side only).
Data never leaves the client machine.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Literal
from pathlib import Path
from datetime import datetime

from .models import PropensityScoreModel, OutcomeModel, CausalModel


class LocalTrainer:
    """
    Local trainer for causal inference models

    Trains models entirely on local data without any network communication.
    Maximum privacy - nothing is shared.

    Example:
        >>> trainer = LocalTrainer()
        >>> ps_model = trainer.train_propensity_score(
        ...     data=df,
        ...     treatment_col='treatment',
        ...     covariate_cols=['age', 'gender', 'income']
        ... )
        >>> trainer.save_model(ps_model, 'models/propensity_score.pkl')
    """

    def __init__(self, cache_dir: str = './models'):
        """
        Initialize local trainer

        Args:
            cache_dir: Directory to save trained models
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.models = {}  # Store trained models
        self.training_history = []  # Track training runs

    def train_propensity_score(
        self,
        data: pd.DataFrame,
        treatment_col: str,
        covariate_cols: list,
        method: Literal['logistic', 'gradient_boosting'] = 'logistic',
        test_size: float = 0.2,
        **kwargs
    ) -> PropensityScoreModel:
        """
        Train propensity score model locally

        Args:
            data: Training data (stays local!)
            treatment_col: Name of treatment column
            covariate_cols: List of covariate column names
            method: 'logistic' or 'gradient_boosting'
            test_size: Proportion of data for testing
            **kwargs: Additional model parameters

        Returns:
            Trained propensity score model
        """
        print(f"\n{'='*60}")
        print(f"  Training Propensity Score Model (LOCAL ONLY)")
        print(f"{'='*60}")
        print(f"Method: {method}")
        print(f"Training samples: {len(data)}")
        print(f"Covariates: {len(covariate_cols)}")
        print(f"Data location: CLIENT (never uploaded)")
        print(f"{'='*60}\n")

        # Prepare data
        X = data[covariate_cols].copy()
        y = data[treatment_col].copy()

        # Train-test split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Initialize and train model
        model = PropensityScoreModel(method=method, **kwargs)
        model.fit(X_train, y_train)

        # Evaluate
        metrics = model.evaluate(X_test, y_test)
        print(f"\n✓ Model Performance:")
        for metric_name, value in metrics.items():
            print(f"  {metric_name}: {value:.4f}")

        # Check overlap
        overlap_stats = model.check_overlap(X_test)
        print(f"\n✓ Propensity Score Overlap:")
        print(f"  Min score: {overlap_stats['min_score']:.4f}")
        print(f"  Max score: {overlap_stats['max_score']:.4f}")
        print(f"  Mean score: {overlap_stats['mean_score']:.4f}")
        print(f"  In common support: {overlap_stats['pct_in_common_support']:.1f}%")

        # Store model
        self.models['propensity_score'] = model

        # Record training
        self.training_history.append({
            'model_type': 'propensity_score',
            'timestamp': datetime.utcnow().isoformat(),
            'num_samples': len(data),
            'metrics': metrics,
            'overlap_stats': overlap_stats
        })

        print(f"\n{'='*60}")
        print(f"✓ Propensity Score Model Trained Successfully")
        print(f"{'='*60}\n")

        return model

    def train_outcome_model(
        self,
        data: pd.DataFrame,
        outcome_col: str,
        treatment_col: str,
        covariate_cols: list,
        method: Literal['linear', 'ridge', 'random_forest', 'gradient_boosting'] = 'linear',
        test_size: float = 0.2,
        **kwargs
    ) -> OutcomeModel:
        """
        Train outcome model locally

        Args:
            data: Training data (stays local!)
            outcome_col: Name of outcome column
            treatment_col: Name of treatment column
            covariate_cols: List of covariate column names
            method: Model type
            test_size: Proportion of data for testing
            **kwargs: Additional model parameters

        Returns:
            Trained outcome model
        """
        print(f"\n{'='*60}")
        print(f"  Training Outcome Model (LOCAL ONLY)")
        print(f"{'='*60}")
        print(f"Method: {method}")
        print(f"Training samples: {len(data)}")
        print(f"Covariates: {len(covariate_cols)} + treatment")
        print(f"Data location: CLIENT (never uploaded)")
        print(f"{'='*60}\n")

        # Prepare data
        X = data[covariate_cols].copy()
        y = data[outcome_col].copy()
        treatment = data[treatment_col].copy()

        # Train-test split
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test, t_train, t_test = train_test_split(
            X, y, treatment, test_size=test_size, random_state=42
        )

        # Initialize and train model
        model = OutcomeModel(method=method, **kwargs)
        model.fit(X_train, y_train, treatment=t_train)

        # Evaluate
        metrics = model.evaluate(
            pd.concat([X_test, t_test.rename('treatment')], axis=1),
            y_test
        )
        print(f"\n✓ Model Performance:")
        for metric_name, value in metrics.items():
            print(f"  {metric_name}: {value:.4f}")

        # Estimate CATE if possible
        try:
            cate = model.estimate_cate(X_test)
            print(f"\n✓ CATE Statistics:")
            print(f"  Mean CATE: {cate.mean():.4f}")
            print(f"  Std CATE: {cate.std():.4f}")
            print(f"  Min CATE: {cate.min():.4f}")
            print(f"  Max CATE: {cate.max():.4f}")
        except:
            pass

        # Store model
        self.models['outcome'] = model

        # Record training
        self.training_history.append({
            'model_type': 'outcome',
            'timestamp': datetime.utcnow().isoformat(),
            'num_samples': len(data),
            'metrics': metrics
        })

        print(f"\n{'='*60}")
        print(f"✓ Outcome Model Trained Successfully")
        print(f"{'='*60}\n")

        return model

    def train_doubly_robust(
        self,
        data: pd.DataFrame,
        outcome_col: str,
        treatment_col: str,
        covariate_cols: list,
        ps_method: str = 'logistic',
        outcome_method: str = 'linear',
        test_size: float = 0.2
    ) -> Dict[str, CausalModel]:
        """
        Train both propensity score and outcome models for doubly robust estimation

        Args:
            data: Training data (stays local!)
            outcome_col: Name of outcome column
            treatment_col: Name of treatment column
            covariate_cols: List of covariate column names
            ps_method: Propensity score model method
            outcome_method: Outcome model method
            test_size: Proportion of data for testing

        Returns:
            Dictionary with 'propensity_score' and 'outcome' models
        """
        print(f"\n{'='*70}")
        print(f"  Training Doubly Robust Models (LOCAL ONLY)")
        print(f"{'='*70}\n")

        # Train propensity score model
        ps_model = self.train_propensity_score(
            data=data,
            treatment_col=treatment_col,
            covariate_cols=covariate_cols,
            method=ps_method,
            test_size=test_size
        )

        # Train outcome model
        outcome_model = self.train_outcome_model(
            data=data,
            outcome_col=outcome_col,
            treatment_col=treatment_col,
            covariate_cols=covariate_cols,
            method=outcome_method,
            test_size=test_size
        )

        models = {
            'propensity_score': ps_model,
            'outcome': outcome_model
        }

        print(f"\n{'='*70}")
        print(f"✓ Doubly Robust Models Trained Successfully")
        print(f"{'='*70}\n")

        return models

    def save_model(self, model: CausalModel, name: str = None):
        """
        Save model to local cache

        Args:
            model: Trained model
            name: File name (without extension)
        """
        if name is None:
            name = f"{model.name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        path = self.cache_dir / f"{name}.pkl"
        model.save(str(path))

        print(f"✓ Model saved to {path}")

    def load_model(self, name: str) -> CausalModel:
        """
        Load model from local cache

        Args:
            name: File name (with or without .pkl extension)

        Returns:
            Loaded model
        """
        if not name.endswith('.pkl'):
            name = f"{name}.pkl"

        path = self.cache_dir / name

        from .models.base_model import CausalModel
        model = CausalModel.load(str(path))

        print(f"✓ Model loaded from {path}")

        return model

    def list_models(self) -> list:
        """
        List all saved models in cache

        Returns:
            List of model file names
        """
        models = list(self.cache_dir.glob('*.pkl'))
        return [m.stem for m in models]

    def get_training_history(self) -> pd.DataFrame:
        """
        Get training history as DataFrame

        Returns:
            DataFrame with training history
        """
        if not self.training_history:
            return pd.DataFrame()

        return pd.DataFrame(self.training_history)

    def estimate_ate(
        self,
        data: pd.DataFrame,
        outcome_col: str,
        treatment_col: str,
        covariate_cols: list,
        method: Literal['outcome_regression', 'ipw', 'doubly_robust'] = 'doubly_robust'
    ) -> Dict[str, float]:
        """
        Estimate Average Treatment Effect (ATE) using trained models

        Args:
            data: Data for estimation
            outcome_col: Outcome column name
            treatment_col: Treatment column name
            covariate_cols: Covariate column names
            method: Estimation method

        Returns:
            Dictionary with ATE estimate and confidence interval
        """
        print(f"\n{'='*60}")
        print(f"  Estimating ATE (Method: {method})")
        print(f"{'='*60}\n")

        X = data[covariate_cols]
        y = data[outcome_col]
        treatment = data[treatment_col]

        if method == 'outcome_regression':
            # Use outcome model only
            if 'outcome' not in self.models:
                raise ValueError("Outcome model not trained. Train it first.")

            outcome_model = self.models['outcome']
            counterfactuals = outcome_model.predict_counterfactuals(X)

            ate = (counterfactuals['Y1'] - counterfactuals['Y0']).mean()

        elif method == 'ipw':
            # Inverse propensity weighting
            if 'propensity_score' not in self.models:
                raise ValueError("Propensity score model not trained. Train it first.")

            ps_model = self.models['propensity_score']
            ps = ps_model.get_propensity_scores(X)

            # IPW estimator
            ipw_treated = (treatment * y) / ps
            ipw_control = ((1 - treatment) * y) / (1 - ps)

            ate = ipw_treated.mean() - ipw_control.mean()

        elif method == 'doubly_robust':
            # Doubly robust estimator
            if 'propensity_score' not in self.models or 'outcome' not in self.models:
                raise ValueError("Both models not trained. Train doubly robust models first.")

            ps_model = self.models['propensity_score']
            outcome_model = self.models['outcome']

            ps = ps_model.get_propensity_scores(X)
            counterfactuals = outcome_model.predict_counterfactuals(X)

            # Doubly robust formula
            dr_treated = (treatment * y) / ps - ((treatment - ps) / ps) * counterfactuals['Y1']
            dr_control = ((1 - treatment) * y) / (1 - ps) - ((treatment - ps) / (1 - ps)) * counterfactuals['Y0']

            ate = dr_treated.mean() - dr_control.mean()

        else:
            raise ValueError(f"Unknown method: {method}")

        # Bootstrap confidence interval
        from sklearn.utils import resample

        ate_bootstrap = []
        for _ in range(100):
            # Resample data
            indices = resample(range(len(data)), random_state=None)
            data_boot = data.iloc[indices]

            X_boot = data_boot[covariate_cols]
            y_boot = data_boot[outcome_col]
            t_boot = data_boot[treatment_col]

            # Recompute ATE
            if method == 'outcome_regression':
                cf_boot = outcome_model.predict_counterfactuals(X_boot)
                ate_boot = (cf_boot['Y1'] - cf_boot['Y0']).mean()
            elif method == 'ipw':
                ps_boot = ps_model.get_propensity_scores(X_boot)
                ipw_t = (t_boot * y_boot) / ps_boot
                ipw_c = ((1 - t_boot) * y_boot) / (1 - ps_boot)
                ate_boot = ipw_t.mean() - ipw_c.mean()
            elif method == 'doubly_robust':
                ps_boot = ps_model.get_propensity_scores(X_boot)
                cf_boot = outcome_model.predict_counterfactuals(X_boot)
                dr_t = (t_boot * y_boot) / ps_boot - ((t_boot - ps_boot) / ps_boot) * cf_boot['Y1']
                dr_c = ((1 - t_boot) * y_boot) / (1 - ps_boot) - ((t_boot - ps_boot) / (1 - ps_boot)) * cf_boot['Y0']
                ate_boot = dr_t.mean() - dr_c.mean()

            ate_bootstrap.append(ate_boot)

        # Confidence interval
        ci_lower = np.percentile(ate_bootstrap, 2.5)
        ci_upper = np.percentile(ate_bootstrap, 97.5)

        results = {
            'ate': float(ate),
            'ci_lower': float(ci_lower),
            'ci_upper': float(ci_upper),
            'method': method
        }

        print(f"✓ ATE Estimate:")
        print(f"  ATE: {ate:.4f}")
        print(f"  95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
        print(f"  Method: {method}")
        print(f"\n{'='*60}\n")

        return results
