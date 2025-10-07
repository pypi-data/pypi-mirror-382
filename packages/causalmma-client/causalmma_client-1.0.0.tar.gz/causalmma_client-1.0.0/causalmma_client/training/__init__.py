"""
Training Module for CausalMMA SDK

This module provides training capabilities for causal inference models,
including local training and federated learning support.
"""

from .local_trainer import LocalTrainer
from .federated_trainer import FederatedTrainer

__all__ = [
    'LocalTrainer',
    'FederatedTrainer'
]

__version__ = '1.0.0'
