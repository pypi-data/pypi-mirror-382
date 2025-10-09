"""
Pattern Recognition Engine
==========================

Identify and analyze patterns in resource usage and costs.

Detects:
- Daily/weekly/monthly patterns
- Peak usage times
- Idle periods
- Seasonal trends
- Workload cycles
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


class PatternType(Enum):
    """Types of patterns detected."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    PEAK_HOURS = "peak_hours"
    IDLE_PERIOD = "idle_period"
    WORKLOAD_CYCLE = "workload_cycle"
    SEASONAL = "seasonal"


@dataclass
class UsagePattern:
    """
    Represents a detected usage pattern.

    Attributes:
        pattern_type: Type of pattern
        description: Human-readable description
        confidence: Confidence score (0.0-1.0)
        peak_times: Peak usage times (hour of day, day of week, etc.)
        idle_times: Idle/low usage times
        average_peak_value: Average value during peak times
        average_idle_value: Average value during idle times
        potential_savings: Estimated cost savings from optimizing pattern
        recommendations: List of actionable recommendations
        metadata: Additional context
    """

    pattern_type: PatternType
    description: str
    confidence: float
    peak_times: List[int] = field(default_factory=list)
    idle_times: List[int] = field(default_factory=list)
    average_peak_value: Optional[float] = None
    average_idle_value: Optional[float] = None
    potential_savings: Optional[float] = None
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PatternRecognizer:
    """
    Pattern recognition engine for resource usage and costs.

    Identifies recurring patterns to enable:
    - Auto-scaling optimization
    - Resource scheduling
    - Cost savings through pattern-aware provisioning
    """

    def __init__(self):
        """Initialize pattern recognizer."""
        pass

    def recognize_patterns(
        self,
        data: List[Dict[str, Any]],
        metric_key: str = "usage",
        timestamp_key: str = "timestamp",
    ) -> List[UsagePattern]:
        """
        Recognize patterns in time series data.

        Args:
            data: List of data points with timestamp and metric
            metric_key: Key for the metric value
            timestamp_key: Key for the timestamp

        Returns:
            List of detected patterns
        """
        if not data:
            return []

        patterns = []

        # Detect different pattern types
        patterns.extend(self._detect_daily_pattern(data, metric_key, timestamp_key))
        patterns.extend(self._detect_weekly_pattern(data, metric_key, timestamp_key))
        patterns.extend(self._detect_idle_periods(data, metric_key, timestamp_key))

        return patterns

    def _detect_daily_pattern(
        self,
        data: List[Dict[str, Any]],
        metric_key: str,
        timestamp_key: str,
    ) -> List[UsagePattern]:
        """Detect daily usage patterns (business hours vs off-hours)."""
        if len(data) < 24:  # Need at least 24 hours of data
            return []

        # Group by hour of day
        hourly_values: Dict[int, List[float]] = {hour: [] for hour in range(24)}

        for point in data:
            timestamp = point[timestamp_key]
            value = point[metric_key]

            # Convert timestamp to hour of day
            dt = datetime.fromtimestamp(timestamp)
            hour = dt.hour

            hourly_values[hour].append(value)

        # Calculate average for each hour
        hourly_averages = {
            hour: statistics.mean(values) if values else 0
            for hour, values in hourly_values.items()
        }

        if not hourly_averages or all(v == 0 for v in hourly_averages.values()):
            return []

        # Identify peak and idle hours
        overall_avg = statistics.mean([v for v in hourly_averages.values() if v > 0])

        peak_hours = [hour for hour, avg in hourly_averages.items() if avg > overall_avg * 1.5]
        idle_hours = [hour for hour, avg in hourly_averages.items() if avg < overall_avg * 0.5]

        if not peak_hours and not idle_hours:
            return []

        # Calculate potential savings
        peak_values = [hourly_averages[h] for h in peak_hours] if peak_hours else [0]
        idle_values = [hourly_averages[h] for h in idle_hours] if idle_hours else [0]

        avg_peak = statistics.mean(peak_values)
        avg_idle = statistics.mean(idle_values)

        # Estimate savings: if resources are scaled down during idle hours
        savings_per_hour = (avg_idle * 0.7) if avg_idle > 0 else 0  # 70% reduction possible
        daily_savings = savings_per_hour * len(idle_hours)

        # Generate recommendations
        recommendations = []
        if peak_hours:
            recommendations.append(
                f"Scale up resources during peak hours ({min(peak_hours)}:00 - {max(peak_hours)}:00)"
            )
        if idle_hours:
            recommendations.append(
                f"Scale down resources during idle hours ({min(idle_hours)}:00 - {max(idle_hours)}:00) "
                f"for estimated ${daily_savings:.2f}/day savings"
            )

        return [
            UsagePattern(
                pattern_type=PatternType.DAILY,
                description=f"Daily usage pattern detected with peaks at {peak_hours} and idle at {idle_hours}",
                confidence=0.85,
                peak_times=peak_hours,
                idle_times=idle_hours,
                average_peak_value=avg_peak,
                average_idle_value=avg_idle,
                potential_savings=daily_savings * 30,  # Monthly estimate
                recommendations=recommendations,
                metadata={
                    "hourly_averages": hourly_averages,
                    "overall_average": overall_avg,
                },
            )
        ]

    def _detect_weekly_pattern(
        self,
        data: List[Dict[str, Any]],
        metric_key: str,
        timestamp_key: str,
    ) -> List[UsagePattern]:
        """Detect weekly usage patterns (weekday vs weekend)."""
        if len(data) < 7 * 24:  # Need at least a week of hourly data
            return []

        # Group by day of week (0=Monday, 6=Sunday)
        weekly_values: Dict[int, List[float]] = {day: [] for day in range(7)}

        for point in data:
            timestamp = point[timestamp_key]
            value = point[metric_key]

            dt = datetime.fromtimestamp(timestamp)
            day_of_week = dt.weekday()

            weekly_values[day_of_week].append(value)

        # Calculate average for each day
        daily_averages = {
            day: statistics.mean(values) if values else 0
            for day, values in weekly_values.items()
        }

        if not daily_averages or all(v == 0 for v in daily_averages.values()):
            return []

        # Compare weekday vs weekend
        weekday_avg = statistics.mean([daily_averages[d] for d in range(5)])  # Mon-Fri
        weekend_avg = statistics.mean([daily_averages[d] for d in range(5, 7)])  # Sat-Sun

        # Detect significant difference
        if weekday_avg == 0 or abs(weekday_avg - weekend_avg) / weekday_avg < 0.2:
            return []  # No significant weekly pattern

        is_weekend_lower = weekend_avg < weekday_avg
        pct_difference = abs(weekday_avg - weekend_avg) / weekday_avg * 100

        # Estimate savings
        if is_weekend_lower:
            # Can scale down on weekends
            savings_per_weekend_day = (weekday_avg - weekend_avg) * 0.5  # 50% of difference
            monthly_savings = savings_per_weekend_day * 8  # ~8 weekend days per month
        else:
            monthly_savings = 0

        recommendations = []
        if is_weekend_lower:
            recommendations.append(
                f"Reduce resource allocation on weekends ({pct_difference:.0f}% lower usage) "
                f"for estimated ${monthly_savings:.2f}/month savings"
            )
        else:
            recommendations.append(
                f"Weekend usage is {pct_difference:.0f}% higher than weekdays - "
                "investigate unusual weekend workloads"
            )

        return [
            UsagePattern(
                pattern_type=PatternType.WEEKLY,
                description=f"Weekly pattern: {'Lower' if is_weekend_lower else 'Higher'} weekend usage ({pct_difference:.0f}%)",
                confidence=0.80,
                peak_times=[d for d in range(7) if daily_averages[d] > weekday_avg],
                idle_times=[d for d in range(7) if daily_averages[d] < weekday_avg * 0.7],
                average_peak_value=max(weekday_avg, weekend_avg),
                average_idle_value=min(weekday_avg, weekend_avg),
                potential_savings=monthly_savings,
                recommendations=recommendations,
                metadata={
                    "daily_averages": daily_averages,
                    "weekday_avg": weekday_avg,
                    "weekend_avg": weekend_avg,
                },
            )
        ]

    def _detect_idle_periods(
        self,
        data: List[Dict[str, Any]],
        metric_key: str,
        timestamp_key: str,
    ) -> List[UsagePattern]:
        """Detect extended idle periods."""
        if len(data) < 24:
            return []

        # Find consecutive periods with very low usage
        threshold = statistics.mean([point[metric_key] for point in data]) * 0.1

        idle_periods = []
        current_idle_start = None
        current_idle_duration = 0

        for i, point in enumerate(data):
            value = point[metric_key]

            if value < threshold:
                if current_idle_start is None:
                    current_idle_start = point[timestamp_key]
                current_idle_duration += 1
            else:
                if current_idle_duration > 3:  # At least 3 consecutive idle points
                    idle_periods.append(
                        {
                            "start": current_idle_start,
                            "duration": current_idle_duration,
                            "avg_value": threshold,
                        }
                    )
                current_idle_start = None
                current_idle_duration = 0

        # Check last period
        if current_idle_duration > 3:
            idle_periods.append(
                {
                    "start": current_idle_start,
                    "duration": current_idle_duration,
                    "avg_value": threshold,
                }
            )

        if not idle_periods:
            return []

        # Calculate potential savings
        total_idle_duration = sum(p["duration"] for p in idle_periods)
        avg_cost_per_period = statistics.mean([point[metric_key] for point in data])
        potential_savings = avg_cost_per_period * total_idle_duration * 0.8  # 80% reduction

        recommendations = [
            "Implement auto-shutdown during extended idle periods",
            f"Detected {len(idle_periods)} idle periods - configure scheduled scaling",
        ]

        return [
            UsagePattern(
                pattern_type=PatternType.IDLE_PERIOD,
                description=f"Detected {len(idle_periods)} extended idle periods",
                confidence=0.90,
                peak_times=[],
                idle_times=list(range(len(idle_periods))),
                average_idle_value=threshold,
                potential_savings=potential_savings,
                recommendations=recommendations,
                metadata={
                    "idle_periods": idle_periods,
                    "total_idle_duration": total_idle_duration,
                    "threshold": threshold,
                },
            )
        ]

    def calculate_optimization_potential(
        self, patterns: List[UsagePattern]
    ) -> Dict[str, Any]:
        """
        Calculate total optimization potential from detected patterns.

        Args:
            patterns: List of detected usage patterns

        Returns:
            Dictionary with optimization metrics
        """
        if not patterns:
            return {"total_savings": 0, "patterns_count": 0}

        total_savings = sum(
            p.potential_savings for p in patterns if p.potential_savings is not None
        )

        by_type = {}
        for pattern in patterns:
            type_key = pattern.pattern_type.value
            if type_key not in by_type:
                by_type[type_key] = {
                    "count": 0,
                    "savings": 0,
                    "confidence": [],
                }

            by_type[type_key]["count"] += 1
            by_type[type_key]["savings"] += pattern.potential_savings or 0
            by_type[type_key]["confidence"].append(pattern.confidence)

        # Calculate average confidence per type
        for type_data in by_type.values():
            type_data["avg_confidence"] = statistics.mean(type_data["confidence"])
            del type_data["confidence"]

        return {
            "total_savings": total_savings,
            "patterns_count": len(patterns),
            "by_type": by_type,
            "recommendations": [
                rec for pattern in patterns for rec in pattern.recommendations
            ],
        }
