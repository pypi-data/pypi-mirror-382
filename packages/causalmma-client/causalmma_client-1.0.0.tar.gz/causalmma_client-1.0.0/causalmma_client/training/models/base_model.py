"""
Base Model Class for Causal Inference

All causal models inherit from this base class to ensure consistent interface.
"""

from abc import ABC, abstractmethod
import pickle
import json
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from pathlib import Path


class CausalModel(ABC):
    """
    Abstract base class for causal inference models

    All causal models must implement:
    - fit(): Train the model
    - predict(): Make predictions
    - save(): Save model to disk
    - load(): Load model from disk
    - get_weights(): Get model weights for federated learning
    """

    def __init__(self, name: str = "causal_model", **kwargs):
        self.name = name
        self.is_fitted = False
        self.metadata = {
            "model_type": self.__class__.__name__,
            "version": "1.0.0",
            "created_at": None,
            "trained_at": None,
            "num_samples": 0,
            "feature_names": [],
            "hyperparameters": kwargs
        }

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> 'CausalModel':
        """
        Train the model on data

        Args:
            X: Features (covariates)
            y: Target (treatment or outcome)
            **kwargs: Additional training parameters

        Returns:
            self: Fitted model
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions

        Args:
            X: Features

        Returns:
            Predictions
        """
        pass

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict probabilities (for classification models)

        Args:
            X: Features

        Returns:
            Predicted probabilities
        """
        pass

    @abstractmethod
    def get_weights(self) -> Dict[str, Any]:
        """
        Get model weights for federated learning

        Returns:
            Dictionary of model weights
        """
        pass

    @abstractmethod
    def set_weights(self, weights: Dict[str, Any]):
        """
        Set model weights (from federated learning)

        Args:
            weights: Dictionary of model weights
        """
        pass

    def save(self, path: str):
        """
        Save model to disk

        Args:
            path: File path to save model
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save model
        with open(path, 'wb') as f:
            pickle.dump(self, f)

        # Save metadata as JSON
        metadata_path = path.with_suffix('.json')
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)

        print(f"✓ Model saved to {path}")

    @classmethod
    def load(cls, path: str) -> 'CausalModel':
        """
        Load model from disk

        Args:
            path: File path to load model

        Returns:
            Loaded model
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        with open(path, 'rb') as f:
            model = pickle.load(f)

        print(f"✓ Model loaded from {path}")
        return model

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Evaluate model performance

        Args:
            X: Features
            y: True labels

        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import accuracy_score, roc_auc_score, mean_squared_error

        predictions = self.predict(X)

        metrics = {}

        # Classification metrics
        if len(np.unique(y)) <= 10:  # Classification
            metrics['accuracy'] = accuracy_score(y, predictions)

            if hasattr(self, 'predict_proba'):
                proba = self.predict_proba(X)
                if proba.shape[1] == 2:  # Binary classification
                    metrics['auc'] = roc_auc_score(y, proba[:, 1])

        # Regression metrics
        else:
            metrics['mse'] = mean_squared_error(y, predictions)
            metrics['rmse'] = np.sqrt(metrics['mse'])

        return metrics

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', fitted={self.is_fitted})"
