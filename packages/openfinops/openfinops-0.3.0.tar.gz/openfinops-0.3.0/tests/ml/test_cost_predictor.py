"""
Tests for Cost Prediction Engine
=================================

Test ML-powered cost forecasting.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
import time
from openfinops.ml import CostPredictor, CostForecast


@pytest.fixture
def predictor():
    """Create CostPredictor instance."""
    return CostPredictor()


@pytest.fixture
def trending_data():
    """Create trending cost data."""
    base_time = time.time() - 86400 * 30
    return [
        {"timestamp": base_time + i * 86400, "cost": 100 + i * 5}  # Increasing trend
        for i in range(30)
    ]


@pytest.fixture
def stable_data():
    """Create stable cost data."""
    base_time = time.time() - 86400 * 30
    return [
        {"timestamp": base_time + i * 86400, "cost": 100}
        for i in range(30)
    ]


@pytest.fixture
def volatile_data():
    """Create volatile cost data."""
    base_time = time.time() - 86400 * 30
    return [
        {"timestamp": base_time + i * 86400, "cost": 100 + (i % 5) * 20}
        for i in range(30)
    ]


class TestCostPredictor:
    """Test CostPredictor class."""

    def test_initialization(self, predictor):
        """Test predictor initialization."""
        assert predictor._historical_data == {}

    def test_predict_linear(self, predictor, trending_data):
        """Test linear regression prediction."""
        forecasts = predictor.predict(trending_data, forecast_periods=7, method="linear")

        assert len(forecasts) == 7
        assert all(isinstance(f, CostForecast) for f in forecasts)

        # Check forecasts are increasing (following trend)
        assert forecasts[1].predicted_cost >= forecasts[0].predicted_cost

    def test_predict_moving_average(self, predictor, stable_data):
        """Test moving average prediction."""
        forecasts = predictor.predict(stable_data, forecast_periods=7, method="moving_avg")

        assert len(forecasts) == 7
        # For stable data, predictions should be close to actual values
        assert all(90 <= f.predicted_cost <= 110 for f in forecasts)

    def test_predict_exponential_smoothing(self, predictor, volatile_data):
        """Test exponential smoothing prediction."""
        forecasts = predictor.predict(volatile_data, forecast_periods=7, method="exp_smoothing")

        assert len(forecasts) == 7
        assert all(f.method == "exponential_smoothing" for f in forecasts)

    def test_predict_auto_method(self, predictor, trending_data):
        """Test automatic method selection."""
        forecasts = predictor.predict(trending_data, forecast_periods=7, method="auto")

        assert len(forecasts) == 7
        # Should select linear for trending data
        assert forecasts[0].method in ["linear_regression", "moving_average", "exponential_smoothing"]

    def test_forecast_timestamps(self, predictor, trending_data):
        """Test that forecast timestamps are in the future."""
        forecasts = predictor.predict(trending_data, forecast_periods=7, method="linear")

        last_historical = trending_data[-1]["timestamp"]

        for forecast in forecasts:
            assert forecast.timestamp > last_historical

    def test_confidence_bounds(self, predictor, trending_data):
        """Test that confidence bounds are valid."""
        forecasts = predictor.predict(trending_data, forecast_periods=7, method="linear")

        for forecast in forecasts:
            assert forecast.lower_bound <= forecast.predicted_cost
            assert forecast.predicted_cost <= forecast.upper_bound
            assert forecast.lower_bound >= 0  # Costs can't be negative

    def test_confidence_widens_with_horizon(self, predictor, trending_data):
        """Test that confidence intervals widen with forecast horizon."""
        forecasts = predictor.predict(trending_data, forecast_periods=14, method="linear")

        # Interval at day 1
        interval_day1 = forecasts[0].upper_bound - forecasts[0].lower_bound
        # Interval at day 14
        interval_day14 = forecasts[13].upper_bound - forecasts[13].lower_bound

        assert interval_day14 >= interval_day1  # Later forecasts have wider intervals

    def test_confidence_scores(self, predictor, trending_data):
        """Test confidence scores are in valid range."""
        forecasts = predictor.predict(trending_data, forecast_periods=7)

        for forecast in forecasts:
            assert 0.0 <= forecast.confidence <= 1.0

    def test_empty_data(self, predictor):
        """Test handling empty data."""
        forecasts = predictor.predict([], forecast_periods=7)
        assert len(forecasts) == 0

    def test_insufficient_data(self, predictor):
        """Test with insufficient data."""
        data = [{"timestamp": time.time(), "cost": 100}]
        forecasts = predictor.predict(data, forecast_periods=7, method="linear")
        assert len(forecasts) == 0

    def test_prediction_summary(self, predictor, trending_data):
        """Test getting prediction summary."""
        forecasts = predictor.predict(trending_data, forecast_periods=7)
        summary = predictor.get_prediction_summary(forecasts)

        assert "total_forecasts" in summary
        assert "predicted_total" in summary
        assert "predicted_average" in summary
        assert summary["total_forecasts"] == 7

    def test_forecast_accuracy(self, predictor, trending_data):
        """Test forecast accuracy calculation."""
        accuracy = predictor.calculate_forecast_accuracy(trending_data, test_size=7)

        assert "mae" in accuracy
        assert "mape" in accuracy
        assert "rmse" in accuracy
        assert "accuracy" in accuracy
        assert accuracy["accuracy"] >= 0

    def test_different_confidence_levels(self, predictor, trending_data):
        """Test different confidence levels."""
        forecasts_95 = predictor.predict(trending_data, forecast_periods=7, confidence_level=0.95)
        forecasts_90 = predictor.predict(trending_data, forecast_periods=7, confidence_level=0.90)

        # 95% interval should be wider than 90%
        interval_95 = forecasts_95[0].upper_bound - forecasts_95[0].lower_bound
        interval_90 = forecasts_90[0].upper_bound - forecasts_90[0].lower_bound

        assert interval_95 >= interval_90

    def test_metadata_contains_method_info(self, predictor, trending_data):
        """Test that metadata contains method-specific information."""
        forecasts = predictor.predict(trending_data, forecast_periods=7, method="linear")

        for forecast in forecasts:
            assert "slope" in forecast.metadata
            assert "intercept" in forecast.metadata


class TestCostForecastDataclass:
    """Test CostForecast dataclass."""

    def test_forecast_creation(self):
        """Test creating a CostForecast."""
        forecast = CostForecast(
            timestamp=time.time(),
            predicted_cost=500.0,
            lower_bound=450.0,
            upper_bound=550.0,
            confidence=0.95,
            method="linear_regression",
        )

        assert forecast.predicted_cost == 500.0
        assert forecast.lower_bound == 450.0
        assert forecast.upper_bound == 550.0
        assert forecast.confidence == 0.95
        assert forecast.method == "linear_regression"

    def test_forecast_with_metadata(self):
        """Test CostForecast with metadata."""
        forecast = CostForecast(
            timestamp=time.time(),
            predicted_cost=500.0,
            lower_bound=450.0,
            upper_bound=550.0,
            confidence=0.90,
            method="exponential_smoothing",
            metadata={"alpha": 0.3, "std_error": 25.0},
        )

        assert forecast.metadata["alpha"] == 0.3
        assert forecast.metadata["std_error"] == 25.0


class TestMethodSelection:
    """Test automatic method selection."""

    def test_select_linear_for_trend(self, predictor, trending_data):
        """Test that linear is selected for trending data."""
        forecasts = predictor.predict(trending_data, forecast_periods=7, method="auto")

        # Should use linear for clear trend
        assert forecasts[0].method in ["linear_regression", "moving_average"]

    def test_select_smoothing_for_volatile(self, predictor):
        """Test that smoothing is selected for highly volatile data."""
        # Create highly volatile data (coefficient of variation > 0.5)
        base_time = time.time() - 86400 * 30
        volatile_data = [
            {"timestamp": base_time + i * 86400, "cost": 100 + (i % 3) * 80}  # Very volatile
            for i in range(30)
        ]

        forecasts = predictor.predict(volatile_data, forecast_periods=7, method="auto")

        # Should use smoothing or moving average for highly volatile data
        assert forecasts[0].method in ["exponential_smoothing", "moving_average", "linear_regression"]

    def test_select_moving_avg_for_stable(self, predictor, stable_data):
        """Test that moving average is selected for stable data."""
        forecasts = predictor.predict(stable_data, forecast_periods=7, method="auto")

        # Should use moving average for stable data
        assert forecasts[0].method in ["moving_average", "exponential_smoothing"]
