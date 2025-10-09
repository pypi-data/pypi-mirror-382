"""
ML-Powered Anomaly Detection and Prediction
============================================

Machine learning capabilities for cost anomaly detection, prediction,
and optimization.

This module provides:
- Statistical and ML-based anomaly detection
- Cost forecasting and prediction
- Pattern recognition in resource usage
- Auto-remediation recommendations
- Integration with insight system

Example:
    >>> from openfinops.ml import AnomalyDetector
    >>> from openfinops.observability import CostObservatory
    >>>
    >>> cost_obs = CostObservatory()
    >>> detector = AnomalyDetector()
    >>>
    >>> # Detect cost anomalies
    >>> anomalies = detector.detect_anomalies(cost_obs.get_cost_history())
    >>> for anomaly in anomalies:
    ...     print(f"Anomaly detected: {anomaly.description}")
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from .anomaly_detector import (
    AnomalyDetector,
    Anomaly,
    AnomalySeverity,
    AnomalyType,
)
from .cost_predictor import CostPredictor, CostForecast
from .pattern_recognition import PatternRecognizer, UsagePattern, PatternType

__all__ = [
    # Anomaly detection
    "AnomalyDetector",
    "Anomaly",
    "AnomalySeverity",
    "AnomalyType",
    # Cost prediction
    "CostPredictor",
    "CostForecast",
    # Pattern recognition
    "PatternRecognizer",
    "UsagePattern",
    "PatternType",
]
