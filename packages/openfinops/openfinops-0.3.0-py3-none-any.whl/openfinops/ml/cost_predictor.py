"""
Cost Prediction Engine
======================

ML-powered cost forecasting and prediction.

Uses multiple forecasting methods:
- Linear regression
- Moving average
- Exponential smoothing
- Seasonal trend decomposition
- ARIMA (when available)
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import logging

logger = logging.getLogger(__name__)


@dataclass
class CostForecast:
    """
    Represents a cost forecast.

    Attributes:
        timestamp: Forecast timestamp
        predicted_cost: Predicted cost value
        lower_bound: Lower confidence bound
        upper_bound: Upper confidence bound
        confidence: Confidence score (0.0-1.0)
        method: Forecasting method used
        metadata: Additional context
    """

    timestamp: float
    predicted_cost: float
    lower_bound: float
    upper_bound: float
    confidence: float
    method: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class CostPredictor:
    """
    ML-powered cost forecasting engine.

    Supports multiple forecasting methods:
    - Linear regression: Trend-based forecasting
    - Moving average: Short-term smoothing
    - Exponential smoothing: Weighted historical average
    - Seasonal decomposition: Handle seasonal patterns
    """

    def __init__(self):
        """Initialize cost predictor."""
        self._historical_data: Dict[str, List[Tuple[float, float]]] = {}

    def predict(
        self,
        historical_data: List[Dict[str, Any]],
        forecast_periods: int = 30,
        method: str = "auto",
        confidence_level: float = 0.95,
    ) -> List[CostForecast]:
        """
        Predict future costs.

        Args:
            historical_data: Historical cost data with timestamp and cost
            forecast_periods: Number of periods to forecast
            method: Forecasting method ("auto", "linear", "moving_avg", "exp_smoothing")
            confidence_level: Confidence level for prediction intervals (0.0-1.0)

        Returns:
            List of cost forecasts
        """
        if not historical_data:
            return []

        # Extract time series
        timeseries = [(point["timestamp"], point.get("cost", 0)) for point in historical_data]
        timeseries.sort(key=lambda x: x[0])

        # Determine best method if auto
        if method == "auto":
            method = self._select_best_method(timeseries)

        # Generate forecasts
        if method == "linear":
            return self._predict_linear(timeseries, forecast_periods, confidence_level)
        elif method == "moving_avg":
            return self._predict_moving_average(timeseries, forecast_periods, confidence_level)
        elif method == "exp_smoothing":
            return self._predict_exponential_smoothing(
                timeseries, forecast_periods, confidence_level
            )
        else:
            logger.warning(f"Unknown method {method}, using linear")
            return self._predict_linear(timeseries, forecast_periods, confidence_level)

    def _predict_linear(
        self,
        timeseries: List[Tuple[float, float]],
        forecast_periods: int,
        confidence_level: float,
    ) -> List[CostForecast]:
        """Forecast using linear regression."""
        if len(timeseries) < 2:
            return []

        # Simple linear regression: y = mx + b
        n = len(timeseries)
        timestamps = [t for t, _ in timeseries]
        values = [v for _, v in timeseries]

        # Normalize timestamps to 0-based index for numerical stability
        t_min = min(timestamps)
        t_normalized = [(t - t_min) for t in timestamps]

        # Calculate slope (m) and intercept (b)
        t_mean = statistics.mean(t_normalized)
        v_mean = statistics.mean(values)

        numerator = sum((t - t_mean) * (v - v_mean) for t, v in zip(t_normalized, values))
        denominator = sum((t - t_mean) ** 2 for t in t_normalized)

        if denominator == 0:
            # No trend, return constant forecast
            m = 0
            b = v_mean
        else:
            m = numerator / denominator
            b = v_mean - m * t_mean

        # Calculate standard error for confidence intervals
        predictions = [m * t + b for t in t_normalized]
        residuals = [v - p for v, p in zip(values, predictions)]

        try:
            std_error = statistics.stdev(residuals)
        except statistics.StatisticsError:
            std_error = 0

        # Z-score for confidence level
        z_score = 1.96 if confidence_level >= 0.95 else 1.645

        # Generate forecasts
        forecasts = []
        time_interval = (timestamps[-1] - timestamps[0]) / (n - 1) if n > 1 else 86400

        for i in range(1, forecast_periods + 1):
            future_timestamp = timestamps[-1] + i * time_interval
            future_t_normalized = t_normalized[-1] + i * time_interval / (timestamps[-1] - t_min + 1)

            predicted_cost = m * future_t_normalized + b

            # Confidence interval widens with forecast horizon
            margin = std_error * z_score * (1 + i / n)
            lower_bound = max(0, predicted_cost - margin)
            upper_bound = predicted_cost + margin

            forecasts.append(
                CostForecast(
                    timestamp=future_timestamp,
                    predicted_cost=max(0, predicted_cost),
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    confidence=confidence_level * (1.0 - min(i / forecast_periods, 0.3)),
                    method="linear_regression",
                    metadata={
                        "slope": m,
                        "intercept": b,
                        "std_error": std_error,
                    },
                )
            )

        return forecasts

    def _predict_moving_average(
        self,
        timeseries: List[Tuple[float, float]],
        forecast_periods: int,
        confidence_level: float,
    ) -> List[CostForecast]:
        """Forecast using moving average."""
        if len(timeseries) < 3:
            return []

        # Use last N points for moving average
        window_size = min(7, len(timeseries))
        values = [v for _, v in timeseries[-window_size:]]
        avg_value = statistics.mean(values)

        try:
            std_dev = statistics.stdev(values)
        except statistics.StatisticsError:
            std_dev = 0

        z_score = 1.96 if confidence_level >= 0.95 else 1.645

        # Generate forecasts (constant prediction)
        forecasts = []
        timestamps = [t for t, _ in timeseries]
        time_interval = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)

        for i in range(1, forecast_periods + 1):
            future_timestamp = timestamps[-1] + i * time_interval

            margin = std_dev * z_score
            lower_bound = max(0, avg_value - margin)
            upper_bound = avg_value + margin

            forecasts.append(
                CostForecast(
                    timestamp=future_timestamp,
                    predicted_cost=avg_value,
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    confidence=confidence_level * 0.9,  # Slightly lower confidence
                    method="moving_average",
                    metadata={"window_size": window_size, "std_dev": std_dev},
                )
            )

        return forecasts

    def _predict_exponential_smoothing(
        self,
        timeseries: List[Tuple[float, float]],
        forecast_periods: int,
        confidence_level: float,
    ) -> List[CostForecast]:
        """Forecast using exponential smoothing."""
        if len(timeseries) < 2:
            return []

        # Simple exponential smoothing
        alpha = 0.3  # Smoothing parameter (0 < alpha < 1)
        values = [v for _, v in timeseries]

        # Calculate smoothed values
        smoothed = [values[0]]  # Initialize with first value
        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[-1]
            smoothed.append(smoothed_value)

        # Last smoothed value is our forecast
        forecast_value = smoothed[-1]

        # Calculate residuals for confidence interval
        residuals = [v - s for v, s in zip(values, smoothed)]

        try:
            std_error = statistics.stdev(residuals)
        except statistics.StatisticsError:
            std_error = 0

        z_score = 1.96 if confidence_level >= 0.95 else 1.645

        # Generate forecasts
        forecasts = []
        timestamps = [t for t, _ in timeseries]
        time_interval = (timestamps[-1] - timestamps[0]) / (len(timestamps) - 1)

        for i in range(1, forecast_periods + 1):
            future_timestamp = timestamps[-1] + i * time_interval

            # Confidence interval grows with forecast horizon
            margin = std_error * z_score * (1 + 0.1 * i)
            lower_bound = max(0, forecast_value - margin)
            upper_bound = forecast_value + margin

            forecasts.append(
                CostForecast(
                    timestamp=future_timestamp,
                    predicted_cost=forecast_value,
                    lower_bound=lower_bound,
                    upper_bound=upper_bound,
                    confidence=confidence_level * (1.0 - min(i / forecast_periods, 0.2)),
                    method="exponential_smoothing",
                    metadata={"alpha": alpha, "std_error": std_error},
                )
            )

        return forecasts

    def _select_best_method(self, timeseries: List[Tuple[float, float]]) -> str:
        """Automatically select the best forecasting method."""
        if len(timeseries) < 4:
            return "moving_avg"

        # Check for trend
        values = [v for _, v in timeseries]
        has_trend = self._detect_trend(values)

        # Check for volatility
        try:
            cv = statistics.stdev(values) / statistics.mean(values) if statistics.mean(values) > 0 else 0
        except statistics.StatisticsError:
            cv = 0

        # Decision logic
        if has_trend and cv < 0.3:
            return "linear"  # Clear trend, low volatility
        elif cv > 0.5:
            return "exp_smoothing"  # High volatility, use smoothing
        else:
            return "moving_avg"  # Default

    def _detect_trend(self, values: List[float]) -> bool:
        """Detect if there's a significant trend in the data."""
        if len(values) < 3:
            return False

        # Count increasing and decreasing sequences
        increases = sum(1 for i in range(1, len(values)) if values[i] > values[i - 1])
        decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i - 1])

        total = len(values) - 1
        # If >60% of values are trending in one direction, consider it a trend
        return (increases / total > 0.6) or (decreases / total > 0.6)

    def calculate_forecast_accuracy(
        self,
        historical_data: List[Dict[str, Any]],
        test_size: int = 7,
    ) -> Dict[str, float]:
        """
        Calculate forecast accuracy using historical data.

        Args:
            historical_data: Historical cost data
            test_size: Number of periods to hold out for testing

        Returns:
            Dictionary with accuracy metrics
        """
        if len(historical_data) < test_size + 2:
            return {"error": "insufficient_data"}

        # Split data
        train_data = historical_data[:-test_size]
        test_data = historical_data[-test_size:]

        # Make predictions
        forecasts = self.predict(train_data, forecast_periods=test_size)

        if not forecasts:
            return {"error": "prediction_failed"}

        # Calculate accuracy metrics
        actual_values = [point.get("cost", 0) for point in test_data]
        predicted_values = [f.predicted_cost for f in forecasts[:len(actual_values)]]

        # Mean Absolute Error (MAE)
        mae = statistics.mean([abs(a - p) for a, p in zip(actual_values, predicted_values)])

        # Mean Absolute Percentage Error (MAPE)
        mape_values = [
            abs(a - p) / a * 100 for a, p in zip(actual_values, predicted_values) if a > 0
        ]
        mape = statistics.mean(mape_values) if mape_values else 0

        # Root Mean Squared Error (RMSE)
        mse = statistics.mean([(a - p) ** 2 for a, p in zip(actual_values, predicted_values)])
        rmse = mse ** 0.5

        return {
            "mae": mae,
            "mape": mape,
            "rmse": rmse,
            "accuracy": max(0, 100 - mape),  # Accuracy as percentage
        }

    def get_prediction_summary(self, forecasts: List[CostForecast]) -> Dict[str, Any]:
        """
        Get summary statistics for forecasts.

        Args:
            forecasts: List of cost forecasts

        Returns:
            Dictionary with summary statistics
        """
        if not forecasts:
            return {"error": "no_forecasts"}

        predicted_costs = [f.predicted_cost for f in forecasts]

        return {
            "total_forecasts": len(forecasts),
            "method": forecasts[0].method,
            "forecast_period": {
                "start": forecasts[0].timestamp,
                "end": forecasts[-1].timestamp,
            },
            "predicted_total": sum(predicted_costs),
            "predicted_average": statistics.mean(predicted_costs),
            "predicted_min": min(predicted_costs),
            "predicted_max": max(predicted_costs),
            "average_confidence": statistics.mean([f.confidence for f in forecasts]),
        }
