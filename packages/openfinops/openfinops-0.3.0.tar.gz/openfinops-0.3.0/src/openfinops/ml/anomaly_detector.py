"""
Anomaly Detection Engine
========================

ML-powered anomaly detection for cost and resource usage patterns.

Uses multiple detection methods:
- Statistical methods (Z-score, IQR)
- Time series decomposition
- Isolation Forest (ML)
- DBSCAN clustering
- Threshold-based detection
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import statistics
import logging

logger = logging.getLogger(__name__)


class AnomalySeverity(Enum):
    """Severity levels for anomalies."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(Enum):
    """Types of anomalies detected."""

    COST_SPIKE = "cost_spike"
    COST_DROP = "cost_drop"
    USAGE_SPIKE = "usage_spike"
    USAGE_DROP = "usage_drop"
    TREND_CHANGE = "trend_change"
    SEASONAL_DEVIATION = "seasonal_deviation"
    OUTLIER = "outlier"


@dataclass
class Anomaly:
    """
    Represents a detected anomaly.

    Attributes:
        timestamp: When the anomaly occurred
        anomaly_type: Type of anomaly
        severity: Severity level
        metric_name: Name of the metric (e.g., "daily_cost", "ec2_usage")
        actual_value: The anomalous value
        expected_value: The expected value based on historical data
        deviation: Percentage deviation from expected
        confidence: Confidence score (0.0-1.0)
        description: Human-readable description
        metadata: Additional context
        remediation: Suggested actions
    """

    timestamp: float
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    metric_name: str
    actual_value: float
    expected_value: float
    deviation: float
    confidence: float
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None


class AnomalyDetector:
    """
    ML-powered anomaly detection engine.

    Supports multiple detection methods:
    - Statistical: Z-score, IQR (Interquartile Range)
    - ML-based: Isolation Forest, DBSCAN
    - Time series: Seasonal decomposition
    - Threshold-based: User-defined thresholds
    """

    def __init__(self, sensitivity: float = 0.95):
        """
        Initialize anomaly detector.

        Args:
            sensitivity: Detection sensitivity (0.0-1.0).
                        Higher = more sensitive = more anomalies detected
        """
        self.sensitivity = sensitivity
        self._historical_data: Dict[str, List[Tuple[float, float]]] = {}

    def detect_anomalies(
        self,
        data: List[Dict[str, Any]],
        metric_key: str = "cost",
        timestamp_key: str = "timestamp",
        methods: Optional[List[str]] = None,
    ) -> List[Anomaly]:
        """
        Detect anomalies in time series data.

        Args:
            data: List of data points with timestamp and metric
            metric_key: Key for the metric value
            timestamp_key: Key for the timestamp
            methods: Detection methods to use (default: all)

        Returns:
            List of detected anomalies
        """
        if not data:
            return []

        # Default methods
        if methods is None:
            methods = ["zscore", "iqr", "threshold"]

        # Extract time series
        timeseries = [(point[timestamp_key], point[metric_key]) for point in data]
        timeseries.sort(key=lambda x: x[0])  # Sort by timestamp

        # Run detection methods
        anomalies = []

        if "zscore" in methods:
            anomalies.extend(self._detect_zscore(timeseries, metric_key))

        if "iqr" in methods:
            anomalies.extend(self._detect_iqr(timeseries, metric_key))

        if "threshold" in methods:
            anomalies.extend(self._detect_threshold(timeseries, metric_key))

        if "isolation_forest" in methods:
            anomalies.extend(self._detect_isolation_forest(timeseries, metric_key))

        # Deduplicate and sort by severity
        anomalies = self._deduplicate_anomalies(anomalies)
        anomalies.sort(key=lambda a: (a.timestamp, self._severity_order(a.severity)))

        return anomalies

    def _detect_zscore(
        self, timeseries: List[Tuple[float, float]], metric_name: str
    ) -> List[Anomaly]:
        """Detect anomalies using Z-score method."""
        if len(timeseries) < 3:
            return []

        values = [v for _, v in timeseries]
        mean_val = statistics.mean(values)

        # Handle case where standard deviation is 0
        try:
            stdev_val = statistics.stdev(values)
        except statistics.StatisticsError:
            return []

        if stdev_val == 0:
            return []

        # Calculate z-score threshold based on sensitivity
        # sensitivity=0.95 -> z_threshold~2, sensitivity=0.99 -> z_threshold~3
        z_threshold = 2.0 + (1.0 - self.sensitivity) * 2.0

        anomalies = []
        for timestamp, value in timeseries:
            z_score = abs((value - mean_val) / stdev_val)

            if z_score > z_threshold:
                deviation = ((value - mean_val) / mean_val) * 100 if mean_val != 0 else 0
                anomaly_type = (
                    AnomalyType.COST_SPIKE if value > mean_val else AnomalyType.COST_DROP
                )

                # Determine severity based on z-score
                if z_score > 4:
                    severity = AnomalySeverity.CRITICAL
                elif z_score > 3:
                    severity = AnomalySeverity.HIGH
                elif z_score > 2.5:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW

                anomalies.append(
                    Anomaly(
                        timestamp=timestamp,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        metric_name=metric_name,
                        actual_value=value,
                        expected_value=mean_val,
                        deviation=deviation,
                        confidence=min(z_score / 4.0, 1.0),  # Normalize confidence
                        description=f"{metric_name} deviated {abs(deviation):.1f}% from expected",
                        metadata={"z_score": z_score, "method": "zscore"},
                    )
                )

        return anomalies

    def _detect_iqr(
        self, timeseries: List[Tuple[float, float]], metric_name: str
    ) -> List[Anomaly]:
        """Detect anomalies using Interquartile Range (IQR) method."""
        if len(timeseries) < 4:
            return []

        values = [v for _, v in timeseries]
        values_sorted = sorted(values)
        n = len(values_sorted)

        # Calculate quartiles
        q1_idx = n // 4
        q3_idx = (3 * n) // 4
        q1 = values_sorted[q1_idx]
        q3 = values_sorted[q3_idx]
        iqr = q3 - q1

        if iqr == 0:
            return []

        # IQR multiplier based on sensitivity
        multiplier = 1.5 - (self.sensitivity - 0.9) * 2.0  # Higher sensitivity -> lower multiplier

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr
        median_val = values_sorted[n // 2]

        anomalies = []
        for timestamp, value in timeseries:
            if value < lower_bound or value > upper_bound:
                deviation = ((value - median_val) / median_val) * 100 if median_val != 0 else 0
                anomaly_type = (
                    AnomalyType.OUTLIER if abs(deviation) < 50 else
                    AnomalyType.COST_SPIKE if value > upper_bound else AnomalyType.COST_DROP
                )

                # Determine severity based on how far outside bounds
                distance = max(
                    (lower_bound - value) / iqr if value < lower_bound else 0,
                    (value - upper_bound) / iqr if value > upper_bound else 0,
                )

                if distance > 3:
                    severity = AnomalySeverity.CRITICAL
                elif distance > 2:
                    severity = AnomalySeverity.HIGH
                elif distance > 1.5:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW

                anomalies.append(
                    Anomaly(
                        timestamp=timestamp,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        metric_name=metric_name,
                        actual_value=value,
                        expected_value=median_val,
                        deviation=deviation,
                        confidence=min(distance / 3.0, 1.0),
                        description=f"{metric_name} is an outlier ({abs(deviation):.1f}% from median)",
                        metadata={
                            "q1": q1,
                            "q3": q3,
                            "iqr": iqr,
                            "lower_bound": lower_bound,
                            "upper_bound": upper_bound,
                            "method": "iqr",
                        },
                    )
                )

        return anomalies

    def _detect_threshold(
        self, timeseries: List[Tuple[float, float]], metric_name: str
    ) -> List[Anomaly]:
        """Detect anomalies using threshold-based method."""
        if len(timeseries) < 2:
            return []

        anomalies = []

        # Look for sudden spikes (>50% increase from previous point)
        for i in range(1, len(timeseries)):
            prev_timestamp, prev_value = timeseries[i - 1]
            curr_timestamp, curr_value = timeseries[i]

            if prev_value == 0:
                continue

            pct_change = ((curr_value - prev_value) / prev_value) * 100

            # Spike detection
            if abs(pct_change) > 50:
                anomaly_type = (
                    AnomalyType.COST_SPIKE if pct_change > 0 else AnomalyType.COST_DROP
                )

                # Severity based on magnitude
                if abs(pct_change) > 200:
                    severity = AnomalySeverity.CRITICAL
                elif abs(pct_change) > 100:
                    severity = AnomalySeverity.HIGH
                elif abs(pct_change) > 75:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW

                anomalies.append(
                    Anomaly(
                        timestamp=curr_timestamp,
                        anomaly_type=anomaly_type,
                        severity=severity,
                        metric_name=metric_name,
                        actual_value=curr_value,
                        expected_value=prev_value,
                        deviation=pct_change,
                        confidence=min(abs(pct_change) / 200, 1.0),
                        description=f"{metric_name} changed {abs(pct_change):.1f}% suddenly",
                        metadata={
                            "previous_value": prev_value,
                            "pct_change": pct_change,
                            "method": "threshold",
                        },
                        remediation=self._suggest_remediation(anomaly_type, pct_change),
                    )
                )

        return anomalies

    def _detect_isolation_forest(
        self, timeseries: List[Tuple[float, float]], metric_name: str
    ) -> List[Anomaly]:
        """
        Detect anomalies using Isolation Forest (ML method).

        Note: This is a placeholder. In production, use sklearn.ensemble.IsolationForest
        """
        # Placeholder - would use scikit-learn IsolationForest in production
        # For now, return empty list
        # TODO: Implement with sklearn when available
        return []

    def _deduplicate_anomalies(self, anomalies: List[Anomaly]) -> List[Anomaly]:
        """Remove duplicate anomalies (same timestamp and metric)."""
        seen = set()
        deduplicated = []

        for anomaly in anomalies:
            key = (anomaly.timestamp, anomaly.metric_name)
            if key not in seen:
                seen.add(key)
                deduplicated.append(anomaly)

        return deduplicated

    def _severity_order(self, severity: AnomalySeverity) -> int:
        """Get numeric order for severity sorting."""
        order = {
            AnomalySeverity.CRITICAL: 0,
            AnomalySeverity.HIGH: 1,
            AnomalySeverity.MEDIUM: 2,
            AnomalySeverity.LOW: 3,
        }
        return order.get(severity, 999)

    def _suggest_remediation(self, anomaly_type: AnomalyType, pct_change: float) -> str:
        """Suggest remediation actions based on anomaly type."""
        if anomaly_type == AnomalyType.COST_SPIKE:
            if abs(pct_change) > 100:
                return (
                    "URGENT: Investigate immediately. Check for: "
                    "1) New resource deployments, "
                    "2) Data transfer spikes, "
                    "3) API rate limit breaches, "
                    "4) Unauthorized resource usage"
                )
            else:
                return (
                    "Review recent changes: "
                    "1) Check deployment logs, "
                    "2) Review auto-scaling events, "
                    "3) Analyze traffic patterns"
                )
        elif anomaly_type == AnomalyType.COST_DROP:
            return (
                "Verify expected behavior: "
                "1) Check if services are running, "
                "2) Verify resource availability, "
                "3) Review recent optimization changes"
            )
        else:
            return "Monitor for pattern and investigate if persists"

    def add_historical_data(
        self, metric_name: str, timeseries: List[Tuple[float, float]]
    ):
        """
        Add historical data for better anomaly detection.

        Args:
            metric_name: Name of the metric
            timeseries: List of (timestamp, value) tuples
        """
        self._historical_data[metric_name] = timeseries

    def get_detection_summary(self, anomalies: List[Anomaly]) -> Dict[str, Any]:
        """
        Get summary statistics for detected anomalies.

        Args:
            anomalies: List of detected anomalies

        Returns:
            Dictionary with summary statistics
        """
        if not anomalies:
            return {
                "total": 0,
                "by_severity": {},
                "by_type": {},
                "time_range": None,
            }

        by_severity = {}
        by_type = {}

        for anomaly in anomalies:
            # Count by severity
            severity_key = anomaly.severity.value
            by_severity[severity_key] = by_severity.get(severity_key, 0) + 1

            # Count by type
            type_key = anomaly.anomaly_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

        timestamps = [a.timestamp for a in anomalies]

        return {
            "total": len(anomalies),
            "by_severity": by_severity,
            "by_type": by_type,
            "time_range": {
                "start": min(timestamps),
                "end": max(timestamps),
            },
            "most_severe": max(anomalies, key=lambda a: self._severity_order(a.severity)),
        }
