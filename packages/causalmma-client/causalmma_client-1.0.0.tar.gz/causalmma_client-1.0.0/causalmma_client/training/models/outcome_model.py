"""
Outcome Model

Model for predicting outcomes conditional on treatment and covariates.
Used in doubly robust estimation and other causal inference methods.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Literal
from datetime import datetime
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

from .base_model import CausalModel


class OutcomeModel(CausalModel):
    """
    Outcome model for causal inference

    Estimates E[Y | Treatment, Covariates]

    Used in:
    - Doubly robust estimation
    - S-learner, T-learner approaches
    - Conditional average treatment effect (CATE) estimation

    Example:
        >>> model = OutcomeModel(method='linear')
        >>> model.fit(X_with_treatment, outcomes)
        >>> predicted_outcomes = model.predict(X_test)
    """

    def __init__(
        self,
        method: Literal['linear', 'ridge', 'random_forest', 'gradient_boosting'] = 'linear',
        name: str = 'outcome_model',
        **kwargs
    ):
        """
        Initialize outcome model

        Args:
            method: Model type ('linear', 'ridge', 'random_forest', 'gradient_boosting')
            name: Model name
            **kwargs: Additional parameters for base model
        """
        super().__init__(name=name, method=method, **kwargs)

        self.method = method
        self.model = None

        # Initialize sklearn model
        if method == 'linear':
            self.model = LinearRegression(**kwargs)
        elif method == 'ridge':
            self.model = Ridge(alpha=1.0, random_state=42, **kwargs)
        elif method == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                **kwargs
            )
        elif method == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=3,
                random_state=42,
                **kwargs
            )
        else:
            raise ValueError(
                f"Unknown method: {method}. "
                f"Use 'linear', 'ridge', 'random_forest', or 'gradient_boosting'"
            )

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        treatment: Optional[pd.Series] = None,
        **kwargs
    ) -> 'OutcomeModel':
        """
        Train outcome model

        Args:
            X: Covariates (features)
            y: Outcome variable
            treatment: Treatment indicator (optional, will be added to X if provided)
            **kwargs: Additional training parameters

        Returns:
            self: Fitted model
        """
        # If treatment provided, add to features
        if treatment is not None:
            X = X.copy()
            X['treatment'] = treatment

        # Store feature names
        self.metadata['feature_names'] = list(X.columns)
        self.metadata['num_samples'] = len(X)
        self.metadata['trained_at'] = datetime.utcnow().isoformat()

        # Fit model
        self.model.fit(X, y)
        self.is_fitted = True

        print(f"✓ Outcome model trained on {len(X)} samples")

        return self

    def predict(self, X: pd.DataFrame, treatment: Optional[pd.Series] = None) -> np.ndarray:
        """
        Predict outcomes

        Args:
            X: Covariates
            treatment: Treatment indicator (optional, will be added to X if provided)

        Returns:
            Predicted outcomes
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        # If treatment provided, add to features
        if treatment is not None:
            X = X.copy()
            X['treatment'] = treatment

        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Not applicable for regression models

        Raises:
            NotImplementedError
        """
        raise NotImplementedError("Outcome models are regression models and don't have predict_proba")

    def predict_counterfactuals(
        self,
        X: pd.DataFrame
    ) -> Dict[str, np.ndarray]:
        """
        Predict outcomes under different treatment assignments

        Args:
            X: Covariates (without treatment)

        Returns:
            Dictionary with 'Y0' (control) and 'Y1' (treatment) predictions
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        # Predict under control (T=0)
        X_control = X.copy()
        X_control['treatment'] = 0
        Y0 = self.model.predict(X_control)

        # Predict under treatment (T=1)
        X_treatment = X.copy()
        X_treatment['treatment'] = 1
        Y1 = self.model.predict(X_treatment)

        return {'Y0': Y0, 'Y1': Y1}

    def estimate_cate(self, X: pd.DataFrame) -> np.ndarray:
        """
        Estimate Conditional Average Treatment Effect (CATE)

        CATE(x) = E[Y | T=1, X=x] - E[Y | T=0, X=x]

        Args:
            X: Covariates (without treatment)

        Returns:
            CATE estimates for each sample
        """
        counterfactuals = self.predict_counterfactuals(X)
        cate = counterfactuals['Y1'] - counterfactuals['Y0']

        return cate

    def get_weights(self) -> Dict[str, Any]:
        """
        Get model weights for federated learning

        Returns:
            Dictionary of model weights
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        weights = {}

        if self.method in ['linear', 'ridge']:
            weights['coef'] = self.model.coef_.tolist()
            weights['intercept'] = float(self.model.intercept_)
        elif self.method in ['random_forest', 'gradient_boosting']:
            # For tree-based models, return feature importances
            weights['feature_importances'] = self.model.feature_importances_.tolist()

        weights['metadata'] = self.metadata

        return weights

    def set_weights(self, weights: Dict[str, Any]):
        """
        Set model weights (from federated learning)

        Args:
            weights: Dictionary of model weights
        """
        if self.method in ['linear', 'ridge']:
            if 'coef' in weights and 'intercept' in weights:
                self.model.coef_ = np.array(weights['coef'])
                self.model.intercept_ = float(weights['intercept'])
                self.is_fitted = True

        if 'metadata' in weights:
            self.metadata.update(weights['metadata'])

    def get_feature_importances(self) -> pd.DataFrame:
        """
        Get feature importances (for tree-based models)

        Returns:
            DataFrame with feature names and importances
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        if self.method not in ['random_forest', 'gradient_boosting']:
            raise ValueError(f"Feature importances not available for {self.method}")

        importances = pd.DataFrame({
            'feature': self.metadata['feature_names'],
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        return importances

    def get_coefficients(self) -> pd.DataFrame:
        """
        Get model coefficients (for linear models)

        Returns:
            DataFrame with feature names and coefficients
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        if self.method not in ['linear', 'ridge']:
            raise ValueError(f"Coefficients not available for {self.method}")

        coefs = pd.DataFrame({
            'feature': self.metadata['feature_names'],
            'coefficient': self.model.coef_
        }).sort_values('coefficient', ascending=False, key=abs)

        return coefs
