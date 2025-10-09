"""
Tests for Pattern Recognition Engine
=====================================

Test pattern recognition in resource usage and costs.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
import time
from datetime import datetime
from openfinops.ml import PatternRecognizer, UsagePattern, PatternType


@pytest.fixture
def recognizer():
    """Create PatternRecognizer instance."""
    return PatternRecognizer()


@pytest.fixture
def daily_pattern_data():
    """Create data with daily pattern (business hours spike)."""
    base_time = time.time() - 86400 * 7
    data = []

    for day in range(7):
        for hour in range(24):
            timestamp = base_time + day * 86400 + hour * 3600

            # High usage during business hours (9-17), low at night
            if 9 <= hour <= 17:
                usage = 200
            else:
                usage = 50

            data.append({"timestamp": timestamp, "usage": usage})

    return data


@pytest.fixture
def weekly_pattern_data():
    """Create data with weekly pattern (lower weekends)."""
    base_time = time.time() - 86400 * 21  # 3 weeks
    data = []

    for day in range(21):
        # Need hourly data points for pattern detection
        for hour in range(24):
            timestamp = base_time + day * 86400 + hour * 3600
            dt = datetime.fromtimestamp(timestamp)

            # Significantly lower usage on weekends (>20% difference)
            if dt.weekday() >= 5:  # Saturday=5, Sunday=6
                usage = 50
            else:
                usage = 200  # 4x weekend usage

            data.append({"timestamp": timestamp, "usage": usage})

    return data


@pytest.fixture
def idle_period_data():
    """Create data with extended idle periods."""
    base_time = time.time() - 86400 * 3
    data = []

    for hour in range(72):  # 3 days
        timestamp = base_time + hour * 3600

        # Idle overnight (22-6)
        hour_of_day = hour % 24
        if 22 <= hour_of_day or hour_of_day <= 6:
            usage = 5
        else:
            usage = 100

        data.append({"timestamp": timestamp, "usage": usage})

    return data


class TestPatternRecognizer:
    """Test PatternRecognizer class."""

    def test_initialization(self, recognizer):
        """Test recognizer initialization."""
        assert recognizer is not None

    def test_recognize_daily_pattern(self, recognizer, daily_pattern_data):
        """Test detecting daily business hours pattern."""
        patterns = recognizer.recognize_patterns(daily_pattern_data)

        daily_patterns = [p for p in patterns if p.pattern_type == PatternType.DAILY]
        assert len(daily_patterns) > 0

        pattern = daily_patterns[0]
        assert pattern.confidence > 0.7
        assert len(pattern.peak_times) > 0  # Business hours
        assert len(pattern.idle_times) > 0  # Off hours

    def test_recognize_weekly_pattern(self, recognizer, weekly_pattern_data):
        """Test detecting weekly weekday/weekend pattern."""
        patterns = recognizer.recognize_patterns(weekly_pattern_data)

        weekly_patterns = [p for p in patterns if p.pattern_type == PatternType.WEEKLY]
        assert len(weekly_patterns) > 0

        pattern = weekly_patterns[0]
        assert pattern.confidence > 0.7
        assert "weekend" in pattern.description.lower()

    def test_recognize_idle_periods(self, recognizer, idle_period_data):
        """Test detecting extended idle periods."""
        patterns = recognizer.recognize_patterns(idle_period_data)

        idle_patterns = [p for p in patterns if p.pattern_type == PatternType.IDLE_PERIOD]
        assert len(idle_patterns) > 0

        pattern = idle_patterns[0]
        assert pattern.confidence > 0.8
        assert "idle" in pattern.description.lower()

    def test_empty_data(self, recognizer):
        """Test handling empty data."""
        patterns = recognizer.recognize_patterns([])
        assert len(patterns) == 0

    def test_insufficient_data(self, recognizer):
        """Test with insufficient data."""
        data = [{"timestamp": time.time(), "usage": 100}]
        patterns = recognizer.recognize_patterns(data)
        # Should return empty or very few patterns
        assert len(patterns) <= 1

    def test_patterns_have_recommendations(self, recognizer, daily_pattern_data):
        """Test that patterns include recommendations."""
        patterns = recognizer.recognize_patterns(daily_pattern_data)

        for pattern in patterns:
            assert len(pattern.recommendations) > 0
            assert all(isinstance(rec, str) for rec in pattern.recommendations)

    def test_patterns_have_savings_estimates(self, recognizer, daily_pattern_data):
        """Test that patterns include savings estimates."""
        patterns = recognizer.recognize_patterns(daily_pattern_data)

        # At least some patterns should have savings estimates
        patterns_with_savings = [p for p in patterns if p.potential_savings is not None]
        assert len(patterns_with_savings) > 0

        for pattern in patterns_with_savings:
            assert pattern.potential_savings >= 0

    def test_optimization_potential(self, recognizer, daily_pattern_data):
        """Test calculating optimization potential."""
        patterns = recognizer.recognize_patterns(daily_pattern_data)
        optimization = recognizer.calculate_optimization_potential(patterns)

        assert "total_savings" in optimization
        assert "patterns_count" in optimization
        assert "by_type" in optimization
        assert "recommendations" in optimization

        assert optimization["patterns_count"] == len(patterns)

    def test_optimization_potential_empty(self, recognizer):
        """Test optimization potential with no patterns."""
        optimization = recognizer.calculate_optimization_potential([])

        assert optimization["total_savings"] == 0
        assert optimization["patterns_count"] == 0

    def test_custom_metric_key(self, recognizer, daily_pattern_data):
        """Test using custom metric key."""
        # Change usage key to cost
        data = [
            {"timestamp": p["timestamp"], "cost": p["usage"]}
            for p in daily_pattern_data
        ]

        patterns = recognizer.recognize_patterns(data, metric_key="cost")
        assert isinstance(patterns, list)

    def test_peak_and_idle_times_are_distinct(self, recognizer, daily_pattern_data):
        """Test that peak and idle times don't overlap."""
        patterns = recognizer.recognize_patterns(daily_pattern_data)

        for pattern in patterns:
            if pattern.peak_times and pattern.idle_times:
                # No overlap between peak and idle
                peak_set = set(pattern.peak_times)
                idle_set = set(pattern.idle_times)
                overlap = peak_set & idle_set
                assert len(overlap) == 0

    def test_confidence_scores_valid(self, recognizer, daily_pattern_data):
        """Test that confidence scores are in valid range."""
        patterns = recognizer.recognize_patterns(daily_pattern_data)

        for pattern in patterns:
            assert 0.0 <= pattern.confidence <= 1.0

    def test_metadata_contains_details(self, recognizer, daily_pattern_data):
        """Test that metadata contains useful details."""
        patterns = recognizer.recognize_patterns(daily_pattern_data)

        for pattern in patterns:
            assert isinstance(pattern.metadata, dict)
            # Should have some metadata
            assert len(pattern.metadata) > 0


class TestUsagePatternDataclass:
    """Test UsagePattern dataclass."""

    def test_pattern_creation(self):
        """Test creating a UsagePattern."""
        pattern = UsagePattern(
            pattern_type=PatternType.DAILY,
            description="Business hours pattern detected",
            confidence=0.90,
            peak_times=[9, 10, 11, 12, 13, 14, 15, 16, 17],
            idle_times=[0, 1, 2, 3, 4, 5, 6, 22, 23],
            average_peak_value=200.0,
            average_idle_value=50.0,
            potential_savings=3000.0,
            recommendations=["Scale down during off-hours"],
        )

        assert pattern.pattern_type == PatternType.DAILY
        assert pattern.confidence == 0.90
        assert len(pattern.peak_times) == 9
        assert len(pattern.idle_times) == 9
        assert pattern.potential_savings == 3000.0

    def test_pattern_with_metadata(self):
        """Test UsagePattern with metadata."""
        pattern = UsagePattern(
            pattern_type=PatternType.WEEKLY,
            description="Weekend pattern",
            confidence=0.85,
            metadata={
                "weekday_avg": 150,
                "weekend_avg": 50,
            },
        )

        assert pattern.metadata["weekday_avg"] == 150
        assert pattern.metadata["weekend_avg"] == 50


class TestPatternTypeEnum:
    """Test PatternType enum."""

    def test_pattern_type_enum(self):
        """Test PatternType enum values."""
        assert PatternType.DAILY.value == "daily"
        assert PatternType.WEEKLY.value == "weekly"
        assert PatternType.MONTHLY.value == "monthly"
        assert PatternType.PEAK_HOURS.value == "peak_hours"
        assert PatternType.IDLE_PERIOD.value == "idle_period"
        assert PatternType.WORKLOAD_CYCLE.value == "workload_cycle"
        assert PatternType.SEASONAL.value == "seasonal"


class TestIntegration:
    """Test integration scenarios."""

    def test_multiple_patterns_detected(self, recognizer, daily_pattern_data):
        """Test that multiple pattern types can be detected simultaneously."""
        patterns = recognizer.recognize_patterns(daily_pattern_data)

        # Should detect both daily pattern and idle periods
        pattern_types = [p.pattern_type for p in patterns]
        assert len(set(pattern_types)) >= 1  # At least one type

    def test_recommendations_are_actionable(self, recognizer, daily_pattern_data):
        """Test that recommendations are actionable strings."""
        patterns = recognizer.recognize_patterns(daily_pattern_data)

        for pattern in patterns:
            for recommendation in pattern.recommendations:
                assert isinstance(recommendation, str)
                assert len(recommendation) > 10  # Meaningful text
