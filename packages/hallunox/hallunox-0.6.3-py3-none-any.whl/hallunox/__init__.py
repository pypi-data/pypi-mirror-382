"""
HalluNox: Confidence-Aware Routing for Large Language Model Reliability Enhancement

A multi-signal approach to pre-generation hallucination mitigation that combines
semantic alignment measurement, internal convergence analysis, and learned confidence
estimation to produce unified confidence scores.

Author: Nandakishor M
Company: Convai Innovations Pvt. Ltd.
Email: support@convaiinnovations.com
License: AGPL-3.0
"""

__version__ = "0.6.3"
__author__ = "Nandakishor M"
__email__ = "support@convaiinnovations.com"
__company__ = "Convai Innovations Pvt. Ltd."
__license__ = "AGPL-3.0"

from .detector import HallucinationDetector, ProjectionHead, UltraStableProjectionHead
from .training import TrainingConfig, Trainer, MultiDatasetLoader
from .utils import download_model, download_medgemma_model, setup_logging

__all__ = [
    "HallucinationDetector",
    "ProjectionHead",
    "UltraStableProjectionHead",
    "TrainingConfig",
    "Trainer",
    "MultiDatasetLoader",
    "download_model",
    "download_medgemma_model",
    "setup_logging",
]