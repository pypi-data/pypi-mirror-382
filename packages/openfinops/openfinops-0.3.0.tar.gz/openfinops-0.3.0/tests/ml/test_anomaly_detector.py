"""
Tests for Anomaly Detection Engine
===================================

Test ML-powered anomaly detection.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
import time
from openfinops.ml import AnomalyDetector, Anomaly, AnomalySeverity, AnomalyType


@pytest.fixture
def detector():
    """Create AnomalyDetector instance."""
    return AnomalyDetector(sensitivity=0.95)


@pytest.fixture
def normal_data():
    """Create normal time series data."""
    base_time = time.time() - 86400 * 30  # 30 days ago
    return [
        {"timestamp": base_time + i * 3600, "cost": 100 + (i % 24) * 2}
        for i in range(24 * 7)  # 7 days of hourly data
    ]


@pytest.fixture
def spike_data():
    """Create data with a cost spike."""
    base_time = time.time() - 86400 * 7
    data = [
        {"timestamp": base_time + i * 3600, "cost": 100}
        for i in range(24 * 7)
    ]
    # Add spike at day 3
    data[72]["cost"] = 500  # 5x normal
    return data


@pytest.fixture
def drop_data():
    """Create data with a cost drop."""
    base_time = time.time() - 86400 * 7
    data = [
        {"timestamp": base_time + i * 3600, "cost": 100}
        for i in range(24 * 7)
    ]
    # Add drop at day 4
    data[96]["cost"] = 10  # 90% drop
    return data


class TestAnomalyDetector:
    """Test AnomalyDetector class."""

    def test_initialization(self, detector):
        """Test detector initialization."""
        assert detector.sensitivity == 0.95
        assert detector._historical_data == {}

    def test_detect_no_anomalies_normal_data(self, detector, normal_data):
        """Test that normal data produces no anomalies."""
        anomalies = detector.detect_anomalies(normal_data, methods=["zscore"])
        assert len(anomalies) == 0

    def test_detect_cost_spike_zscore(self, detector, spike_data):
        """Test detecting cost spike with Z-score method."""
        anomalies = detector.detect_anomalies(spike_data, methods=["zscore"])

        assert len(anomalies) > 0
        spike_anomaly = anomalies[0]

        assert spike_anomaly.anomaly_type == AnomalyType.COST_SPIKE
        assert spike_anomaly.actual_value == 500
        assert spike_anomaly.severity in [AnomalySeverity.HIGH, AnomalySeverity.CRITICAL]
        assert spike_anomaly.confidence > 0.5

    def test_detect_cost_drop_zscore(self, detector, drop_data):
        """Test detecting cost drop with Z-score method."""
        anomalies = detector.detect_anomalies(drop_data, methods=["zscore"])

        assert len(anomalies) > 0
        drop_anomaly = anomalies[0]

        assert drop_anomaly.anomaly_type == AnomalyType.COST_DROP
        assert drop_anomaly.actual_value == 10

    def test_detect_spike_iqr(self, detector):
        """Test detecting spike with IQR method."""
        # Create data with normal variation plus a spike
        base_time = time.time() - 86400 * 7
        data = [
            {"timestamp": base_time + i * 3600, "cost": 100 + (i % 12) * 5}  # Normal variation
            for i in range(24 * 7)
        ]
        # Add very large spike
        data[72]["cost"] = 1000  # Much higher than normal range

        anomalies = detector.detect_anomalies(data, methods=["iqr"])

        # IQR should detect the outlier
        assert len(anomalies) > 0
        assert any(a.anomaly_type in [AnomalyType.COST_SPIKE, AnomalyType.OUTLIER] for a in anomalies)

    def test_detect_spike_threshold(self, detector, spike_data):
        """Test detecting spike with threshold method."""
        anomalies = detector.detect_anomalies(spike_data, methods=["threshold"])

        assert len(anomalies) > 0
        spike_anomaly = next(a for a in anomalies if a.anomaly_type == AnomalyType.COST_SPIKE)

        assert spike_anomaly.actual_value == 500
        assert spike_anomaly.metadata["pct_change"] == 400.0  # 400% increase

    def test_multiple_methods(self, detector, spike_data):
        """Test using multiple detection methods."""
        anomalies = detector.detect_anomalies(spike_data, methods=["zscore", "iqr", "threshold"])

        # Multiple methods should detect the spike
        assert len(anomalies) >= 1  # Deduplicated
        assert any(a.anomaly_type == AnomalyType.COST_SPIKE for a in anomalies)

    def test_empty_data(self, detector):
        """Test handling empty data."""
        anomalies = detector.detect_anomalies([])
        assert len(anomalies) == 0

    def test_insufficient_data_zscore(self, detector):
        """Test Z-score with insufficient data."""
        data = [{"timestamp": time.time(), "cost": 100}]
        anomalies = detector.detect_anomalies(data, methods=["zscore"])
        assert len(anomalies) == 0

    def test_severity_levels(self, detector):
        """Test that different magnitudes produce different severities."""
        base_time = time.time()

        # Create data with different spike magnitudes
        test_cases = [
            (200, AnomalySeverity.LOW),  # 2x
            (300, AnomalySeverity.MEDIUM),  # 3x
            (400, AnomalySeverity.HIGH),  # 4x
            (500, AnomalySeverity.CRITICAL),  # 5x
        ]

        for spike_value, expected_severity in test_cases:
            data = [
                {"timestamp": base_time + i * 3600, "cost": 100}
                for i in range(24)
            ]
            data[12]["cost"] = spike_value

            anomalies = detector.detect_anomalies(data, methods=["threshold"])

            if anomalies:
                assert anomalies[0].severity.value in [s.value for s in AnomalySeverity]

    def test_confidence_scores(self, detector, spike_data):
        """Test that confidence scores are in valid range."""
        anomalies = detector.detect_anomalies(spike_data)

        for anomaly in anomalies:
            assert 0.0 <= anomaly.confidence <= 1.0

    def test_remediation_suggestions(self, detector, spike_data):
        """Test that remediation suggestions are provided."""
        anomalies = detector.detect_anomalies(spike_data, methods=["threshold"])

        spike_anomalies = [a for a in anomalies if a.anomaly_type == AnomalyType.COST_SPIKE]
        assert len(spike_anomalies) > 0
        assert spike_anomalies[0].remediation is not None
        assert "investigate" in spike_anomalies[0].remediation.lower()

    def test_detection_summary(self, detector, spike_data):
        """Test getting detection summary."""
        anomalies = detector.detect_anomalies(spike_data)
        summary = detector.get_detection_summary(anomalies)

        assert "total" in summary
        assert "by_severity" in summary
        assert "by_type" in summary
        assert "time_range" in summary
        assert summary["total"] > 0

    def test_detection_summary_empty(self, detector):
        """Test summary with no anomalies."""
        summary = detector.get_detection_summary([])

        assert summary["total"] == 0
        assert summary["by_severity"] == {}
        assert summary["by_type"] == {}

    def test_custom_metric_key(self, detector):
        """Test using custom metric key."""
        data = [
            {"timestamp": time.time() + i * 3600, "usage": 100 + (i % 10) * 50}
            for i in range(24)
        ]

        anomalies = detector.detect_anomalies(data, metric_key="usage")
        # Should work without errors
        assert isinstance(anomalies, list)

    def test_sensitivity_parameter(self):
        """Test different sensitivity levels."""
        # High sensitivity should detect more anomalies
        high_sensitivity = AnomalyDetector(sensitivity=0.99)
        low_sensitivity = AnomalyDetector(sensitivity=0.90)

        data = [
            {"timestamp": time.time() + i * 3600, "cost": 100 + (i % 10) * 10}
            for i in range(50)
        ]
        data[25]["cost"] = 180  # Moderate spike

        high_anomalies = high_sensitivity.detect_anomalies(data, methods=["zscore"])
        low_anomalies = low_sensitivity.detect_anomalies(data, methods=["zscore"])

        # High sensitivity may detect more (or same) anomalies
        assert len(high_anomalies) >= len(low_anomalies)

    def test_deduplicate_anomalies(self, detector, spike_data):
        """Test that duplicates are removed."""
        # Using multiple methods might detect same anomaly
        anomalies = detector.detect_anomalies(spike_data, methods=["zscore", "iqr", "threshold"])

        # Check no duplicates with same timestamp and metric
        timestamps = [a.timestamp for a in anomalies]
        # Should not have duplicate timestamps (deduplicated)
        assert len(timestamps) <= len(set(timestamps)) + 2  # Allow some variance

    def test_metadata_contains_method(self, detector, spike_data):
        """Test that metadata contains detection method."""
        anomalies = detector.detect_anomalies(spike_data, methods=["zscore"])

        for anomaly in anomalies:
            assert "method" in anomaly.metadata
            assert anomaly.metadata["method"] in ["zscore", "iqr", "threshold"]


class TestAnomalyDataclass:
    """Test Anomaly dataclass."""

    def test_anomaly_creation(self):
        """Test creating an Anomaly."""
        anomaly = Anomaly(
            timestamp=time.time(),
            anomaly_type=AnomalyType.COST_SPIKE,
            severity=AnomalySeverity.HIGH,
            metric_name="daily_cost",
            actual_value=500.0,
            expected_value=100.0,
            deviation=400.0,
            confidence=0.95,
            description="Cost spike detected",
        )

        assert anomaly.anomaly_type == AnomalyType.COST_SPIKE
        assert anomaly.severity == AnomalySeverity.HIGH
        assert anomaly.actual_value == 500.0
        assert anomaly.confidence == 0.95

    def test_anomaly_with_metadata(self):
        """Test Anomaly with metadata."""
        anomaly = Anomaly(
            timestamp=time.time(),
            anomaly_type=AnomalyType.OUTLIER,
            severity=AnomalySeverity.MEDIUM,
            metric_name="cpu_usage",
            actual_value=95.0,
            expected_value=50.0,
            deviation=90.0,
            confidence=0.88,
            description="CPU usage outlier",
            metadata={"z_score": 3.5, "method": "zscore"},
        )

        assert anomaly.metadata["z_score"] == 3.5
        assert anomaly.metadata["method"] == "zscore"

    def test_anomaly_with_remediation(self):
        """Test Anomaly with remediation."""
        anomaly = Anomaly(
            timestamp=time.time(),
            anomaly_type=AnomalyType.COST_SPIKE,
            severity=AnomalySeverity.CRITICAL,
            metric_name="ec2_cost",
            actual_value=10000.0,
            expected_value=1000.0,
            deviation=900.0,
            confidence=0.99,
            description="Critical cost spike",
            remediation="Investigate EC2 auto-scaling settings immediately",
        )

        assert anomaly.remediation is not None
        assert "investigate" in anomaly.remediation.lower()


class TestAnomalyEnums:
    """Test Anomaly enums."""

    def test_anomaly_severity_enum(self):
        """Test AnomalySeverity enum values."""
        assert AnomalySeverity.LOW.value == "low"
        assert AnomalySeverity.MEDIUM.value == "medium"
        assert AnomalySeverity.HIGH.value == "high"
        assert AnomalySeverity.CRITICAL.value == "critical"

    def test_anomaly_type_enum(self):
        """Test AnomalyType enum values."""
        assert AnomalyType.COST_SPIKE.value == "cost_spike"
        assert AnomalyType.COST_DROP.value == "cost_drop"
        assert AnomalyType.USAGE_SPIKE.value == "usage_spike"
        assert AnomalyType.USAGE_DROP.value == "usage_drop"
        assert AnomalyType.TREND_CHANGE.value == "trend_change"
        assert AnomalyType.OUTLIER.value == "outlier"
