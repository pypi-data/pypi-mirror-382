"""
Propensity Score Model

Model for estimating treatment propensity scores.
Used in propensity score matching and doubly robust estimation.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier

from .base_model import CausalModel


class PropensityScoreModel(CausalModel):
    """
    Propensity score model for treatment assignment probability

    Estimates P(Treatment = 1 | Covariates)

    Example:
        >>> model = PropensityScoreModel(method='logistic')
        >>> model.fit(X_covariates, treatment)
        >>> propensity_scores = model.predict_proba(X_test)[:, 1]
    """

    def __init__(
        self,
        method: str = 'logistic',
        name: str = 'propensity_score',
        **kwargs
    ):
        """
        Initialize propensity score model

        Args:
            method: 'logistic' or 'gradient_boosting'
            name: Model name
            **kwargs: Additional parameters for base model
        """
        super().__init__(name=name, method=method, **kwargs)

        self.method = method
        self.model = None

        # Initialize sklearn model
        if method == 'logistic':
            self.model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                **kwargs
            )
        elif method == 'gradient_boosting':
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=3,
                random_state=42,
                **kwargs
            )
        else:
            raise ValueError(f"Unknown method: {method}. Use 'logistic' or 'gradient_boosting'")

    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> 'PropensityScoreModel':
        """
        Train propensity score model

        Args:
            X: Covariates (features)
            y: Treatment indicator (0 or 1)
            **kwargs: Additional training parameters

        Returns:
            self: Fitted model
        """
        # Validate treatment is binary
        unique_treatments = y.unique()
        if len(unique_treatments) != 2:
            raise ValueError(f"Treatment must be binary. Found {len(unique_treatments)} unique values")

        if not set(unique_treatments).issubset({0, 1}):
            raise ValueError("Treatment must be encoded as 0 and 1")

        # Store feature names
        self.metadata['feature_names'] = list(X.columns)
        self.metadata['num_samples'] = len(X)
        self.metadata['trained_at'] = datetime.utcnow().isoformat()

        # Fit model
        self.model.fit(X, y)
        self.is_fitted = True

        print(f"✓ Propensity score model trained on {len(X)} samples")

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict treatment class (0 or 1)

        Args:
            X: Covariates

        Returns:
            Predicted treatment class
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict propensity scores (probability of treatment)

        Args:
            X: Covariates

        Returns:
            Array of shape (n_samples, 2) with [P(T=0), P(T=1)]
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        return self.model.predict_proba(X)

    def get_propensity_scores(self, X: pd.DataFrame) -> np.ndarray:
        """
        Get propensity scores (P(Treatment = 1))

        Args:
            X: Covariates

        Returns:
            Propensity scores (probabilities)
        """
        return self.predict_proba(X)[:, 1]

    def get_weights(self) -> Dict[str, Any]:
        """
        Get model weights for federated learning

        Returns:
            Dictionary of model weights
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        weights = {}

        if self.method == 'logistic':
            weights['coef'] = self.model.coef_.tolist()
            weights['intercept'] = self.model.intercept_.tolist()
        elif self.method == 'gradient_boosting':
            # For tree-based models, we'd need custom serialization
            # For now, return feature importances
            weights['feature_importances'] = self.model.feature_importances_.tolist()

        weights['metadata'] = self.metadata

        return weights

    def set_weights(self, weights: Dict[str, Any]):
        """
        Set model weights (from federated learning)

        Args:
            weights: Dictionary of model weights
        """
        if self.method == 'logistic':
            if 'coef' in weights and 'intercept' in weights:
                self.model.coef_ = np.array(weights['coef'])
                self.model.intercept_ = np.array(weights['intercept'])
                self.is_fitted = True
        elif self.method == 'gradient_boosting':
            # Tree-based models are harder to aggregate
            # Would need custom implementation
            pass

        if 'metadata' in weights:
            self.metadata.update(weights['metadata'])

    def check_overlap(
        self,
        X: pd.DataFrame,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Check propensity score overlap (common support)

        Args:
            X: Covariates
            threshold: Minimum acceptable propensity score

        Returns:
            Dictionary with overlap statistics
        """
        propensity_scores = self.get_propensity_scores(X)

        overlap_stats = {
            'min_score': float(propensity_scores.min()),
            'max_score': float(propensity_scores.max()),
            'mean_score': float(propensity_scores.mean()),
            'num_below_threshold': int((propensity_scores < threshold).sum()),
            'num_above_threshold': int((propensity_scores > (1 - threshold)).sum()),
            'pct_in_common_support': float(
                ((propensity_scores >= threshold) &
                 (propensity_scores <= (1 - threshold))).mean() * 100
            )
        }

        return overlap_stats

    def trim_by_propensity(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        treatment: pd.Series,
        lower: float = 0.1,
        upper: float = 0.9
    ) -> tuple:
        """
        Trim samples outside propensity score range

        Args:
            X: Covariates
            y: Outcome
            treatment: Treatment indicator
            lower: Lower threshold
            upper: Upper threshold

        Returns:
            Tuple of (X_trimmed, y_trimmed, treatment_trimmed)
        """
        propensity_scores = self.get_propensity_scores(X)

        # Find samples in common support
        in_support = (propensity_scores >= lower) & (propensity_scores <= upper)

        X_trimmed = X[in_support]
        y_trimmed = y[in_support]
        treatment_trimmed = treatment[in_support]

        dropped_pct = (1 - in_support.mean()) * 100
        print(f"✓ Trimmed {dropped_pct:.1f}% of samples outside [{lower}, {upper}]")

        return X_trimmed, y_trimmed, treatment_trimmed
