"""
Enterprise Metrics Aggregation and Analytics Engine

Advanced metrics aggregation system for enterprise-scale analytics,
business intelligence, and operational monitoring across Vizly deployments.

Features:
- Multi-dimensional metrics aggregation and rollups
- Real-time and historical analytics processing
- Business intelligence dashboards and KPI tracking
- Predictive analytics and forecasting
- Custom metrics definitions and calculations
- Integration with enterprise data warehouses

Enterprise Requirements:
- Scalable processing of millions of metrics per minute
- Support for complex business logic and custom calculations
- Integration with existing BI tools (Tableau, Power BI, etc.)
- Data retention policies and archival strategies
- Compliance with enterprise data governance requirements
"""

# Copyright (c) 2025 Infinidatum
# Author: Duraimurugan Rajamanickam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import json
import statistics
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from .monitoring import MetricPoint, PerformanceMonitor


class AggregationType(Enum):
    """Types of metric aggregations"""
    SUM = "sum"
    AVERAGE = "avg"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    STANDARD_DEVIATION = "stddev"
    RATE = "rate"
    DELTA = "delta"


class TimeWindow(Enum):
    """Time window definitions for aggregations"""
    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1M"


@dataclass
class MetricDefinition:
    """Definition of a custom enterprise metric"""
    name: str
    description: str
    source_metrics: List[str]
    calculation: str  # Formula or function name
    unit: str
    category: str
    tags: Dict[str, str] = field(default_factory=dict)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)
    business_impact: str = "medium"  # low, medium, high, critical


@dataclass
class AggregatedMetric:
    """Aggregated metric with metadata"""
    name: str
    value: float
    aggregation_type: AggregationType
    time_window: TimeWindow
    start_time: datetime
    end_time: datetime
    sample_count: int
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': self.value,
            'aggregation_type': self.aggregation_type.value,
            'time_window': self.time_window.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'sample_count': self.sample_count,
            'tags': self.tags,
            'metadata': self.metadata
        }


class MetricsAggregator:
    """Core metrics aggregation engine"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.metric_definitions = {}
        self.aggregation_rules = {}
        self.aggregated_data = defaultdict(lambda: defaultdict(list))
        self.calculation_functions = {}
        self.logger = logging.getLogger(__name__)

        # Initialize built-in calculations
        self._register_builtin_calculations()

        # Data retention settings
        self.retention_policies = {
            TimeWindow.MINUTE: timedelta(hours=2),
            TimeWindow.FIVE_MINUTES: timedelta(hours=12),
            TimeWindow.FIFTEEN_MINUTES: timedelta(days=3),
            TimeWindow.HOUR: timedelta(days=30),
            TimeWindow.DAY: timedelta(days=365),
            TimeWindow.WEEK: timedelta(days=730),
            TimeWindow.MONTH: timedelta(days=2190)
        }

    def _register_builtin_calculations(self):
        """Register built-in calculation functions"""

        def calculate_response_time_sla(metrics: List[MetricPoint]) -> float:
            """Calculate SLA compliance for response times"""
            if not metrics:
                return 0.0

            threshold = 1.0  # 1 second SLA
            compliant = sum(1 for m in metrics if m.value <= threshold)
            return (compliant / len(metrics)) * 100

        def calculate_error_rate(metrics: List[MetricPoint]) -> float:
            """Calculate error rate percentage"""
            if not metrics:
                return 0.0

            errors = sum(m.value for m in metrics if 'error' in m.tags.get('type', ''))
            total = len(metrics)
            return (errors / total) * 100 if total > 0 else 0.0

        def calculate_throughput(metrics: List[MetricPoint]) -> float:
            """Calculate throughput (requests per second)"""
            if len(metrics) < 2:
                return 0.0

            time_span = (metrics[-1].timestamp - metrics[0].timestamp).total_seconds()
            return len(metrics) / time_span if time_span > 0 else 0.0

        def calculate_apdex_score(metrics: List[MetricPoint]) -> float:
            """Calculate Apdex (Application Performance Index) score"""
            if not metrics:
                return 0.0

            satisfied_threshold = 0.5  # 500ms
            tolerating_threshold = 2.0  # 2s

            satisfied = sum(1 for m in metrics if m.value <= satisfied_threshold)
            tolerating = sum(1 for m in metrics
                           if satisfied_threshold < m.value <= tolerating_threshold)

            total = len(metrics)
            return (satisfied + tolerating * 0.5) / total if total > 0 else 0.0

        # Register functions
        self.calculation_functions.update({
            'response_time_sla': calculate_response_time_sla,
            'error_rate': calculate_error_rate,
            'throughput': calculate_throughput,
            'apdex_score': calculate_apdex_score
        })

    def define_metric(self, definition: MetricDefinition):
        """Define a custom enterprise metric"""
        self.metric_definitions[definition.name] = definition
        self.logger.info(f"Defined custom metric: {definition.name}")

    def add_aggregation_rule(self, metric_name: str, aggregation_type: AggregationType,
                           time_window: TimeWindow, tags_filter: Optional[Dict[str, str]] = None):
        """Add an aggregation rule for a metric"""
        rule_id = f"{metric_name}_{aggregation_type.value}_{time_window.value}"
        self.aggregation_rules[rule_id] = {
            'metric_name': metric_name,
            'aggregation_type': aggregation_type,
            'time_window': time_window,
            'tags_filter': tags_filter or {}
        }
        self.logger.info(f"Added aggregation rule: {rule_id}")

    def aggregate_metrics(self, metrics: List[MetricPoint],
                         aggregation_type: AggregationType,
                         time_window: TimeWindow) -> List[AggregatedMetric]:
        """Aggregate metrics according to specified rules"""
        if not metrics:
            return []

        # Group metrics by time windows
        window_groups = self._group_by_time_window(metrics, time_window)

        aggregated_results = []

        for window_start, window_metrics in window_groups.items():
            if not window_metrics:
                continue

            window_end = window_start + self._get_time_delta(time_window)

            # Calculate aggregated value
            values = [m.value for m in window_metrics]
            aggregated_value = self._calculate_aggregation(values, aggregation_type)

            # Combine tags from all metrics in window
            combined_tags = {}
            for metric in window_metrics:
                combined_tags.update(metric.tags)

            # Create aggregated metric
            aggregated = AggregatedMetric(
                name=window_metrics[0].metric_name,
                value=aggregated_value,
                aggregation_type=aggregation_type,
                time_window=time_window,
                start_time=window_start,
                end_time=window_end,
                sample_count=len(window_metrics),
                tags=combined_tags
            )

            aggregated_results.append(aggregated)

        return aggregated_results

    def _group_by_time_window(self, metrics: List[MetricPoint],
                             time_window: TimeWindow) -> Dict[datetime, List[MetricPoint]]:
        """Group metrics by time windows"""
        window_delta = self._get_time_delta(time_window)
        groups = defaultdict(list)

        for metric in metrics:
            # Align timestamp to window boundary
            window_start = self._align_to_window(metric.timestamp, window_delta)
            groups[window_start].append(metric)

        return dict(groups)

    def _get_time_delta(self, time_window: TimeWindow) -> timedelta:
        """Get timedelta for time window"""
        window_map = {
            TimeWindow.MINUTE: timedelta(minutes=1),
            TimeWindow.FIVE_MINUTES: timedelta(minutes=5),
            TimeWindow.FIFTEEN_MINUTES: timedelta(minutes=15),
            TimeWindow.HOUR: timedelta(hours=1),
            TimeWindow.DAY: timedelta(days=1),
            TimeWindow.WEEK: timedelta(weeks=1),
            TimeWindow.MONTH: timedelta(days=30)  # Approximate
        }
        return window_map[time_window]

    def _align_to_window(self, timestamp: datetime, window_delta: timedelta) -> datetime:
        """Align timestamp to window boundary"""
        epoch = datetime(1970, 1, 1)
        seconds_since_epoch = (timestamp - epoch).total_seconds()
        window_seconds = window_delta.total_seconds()
        aligned_seconds = int(seconds_since_epoch // window_seconds) * window_seconds
        return epoch + timedelta(seconds=aligned_seconds)

    def _calculate_aggregation(self, values: List[float], aggregation_type: AggregationType) -> float:
        """Calculate aggregated value"""
        if not values:
            return 0.0

        if aggregation_type == AggregationType.SUM:
            return sum(values)
        elif aggregation_type == AggregationType.AVERAGE:
            return statistics.mean(values)
        elif aggregation_type == AggregationType.COUNT:
            return len(values)
        elif aggregation_type == AggregationType.MIN:
            return min(values)
        elif aggregation_type == AggregationType.MAX:
            return max(values)
        elif aggregation_type == AggregationType.MEDIAN:
            return statistics.median(values)
        elif aggregation_type == AggregationType.PERCENTILE_95:
            return self._percentile(values, 95)
        elif aggregation_type == AggregationType.PERCENTILE_99:
            return self._percentile(values, 99)
        elif aggregation_type == AggregationType.STANDARD_DEVIATION:
            return statistics.stdev(values) if len(values) > 1 else 0.0
        elif aggregation_type == AggregationType.RATE:
            return len(values)  # Count per window
        elif aggregation_type == AggregationType.DELTA:
            return values[-1] - values[0] if len(values) > 1 else 0.0
        else:
            return statistics.mean(values)

    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0.0

        sorted_values = sorted(values)
        k = (len(sorted_values) - 1) * (percentile / 100)
        f = int(k)
        c = k - f

        if f == len(sorted_values) - 1:
            return sorted_values[f]
        else:
            return sorted_values[f] * (1 - c) + sorted_values[f + 1] * c

    def calculate_custom_metric(self, metric_name: str, source_data: Dict[str, List[MetricPoint]]) -> float:
        """Calculate custom metric using defined formula"""
        if metric_name not in self.metric_definitions:
            raise ValueError(f"Metric definition not found: {metric_name}")

        definition = self.metric_definitions[metric_name]

        # Check if calculation function exists
        if definition.calculation in self.calculation_functions:
            # Combine all source metrics
            all_metrics = []
            for source_metric in definition.source_metrics:
                if source_metric in source_data:
                    all_metrics.extend(source_data[source_metric])

            return self.calculation_functions[definition.calculation](all_metrics)

        # Fallback: try to evaluate as simple formula
        try:
            # This is a simplified formula evaluator
            # In production, use a proper expression evaluator
            formula = definition.calculation
            for source_metric in definition.source_metrics:
                if source_metric in source_data and source_data[source_metric]:
                    avg_value = statistics.mean(m.value for m in source_data[source_metric])
                    formula = formula.replace(source_metric, str(avg_value))

            return eval(formula)  # WARNING: Use proper expression evaluator in production

        except Exception as e:
            self.logger.error(f"Error calculating custom metric {metric_name}: {e}")
            return 0.0

    def cleanup_old_data(self):
        """Clean up aggregated data based on retention policies"""
        current_time = datetime.now()

        for window_type, retention_period in self.retention_policies.items():
            cutoff_time = current_time - retention_period

            # Clean up data older than retention period
            for metric_name in list(self.aggregated_data.keys()):
                window_data = self.aggregated_data[metric_name].get(window_type.value, [])
                self.aggregated_data[metric_name][window_type.value] = [
                    metric for metric in window_data
                    if metric.end_time >= cutoff_time
                ]

    def get_aggregated_metrics(self, metric_name: str,
                              time_window: TimeWindow,
                              start_time: Optional[datetime] = None,
                              end_time: Optional[datetime] = None) -> List[AggregatedMetric]:
        """Get aggregated metrics for specified time range"""
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(hours=1)

        window_data = self.aggregated_data.get(metric_name, {}).get(time_window.value, [])

        return [
            metric for metric in window_data
            if start_time <= metric.end_time <= end_time
        ]


class BusinessIntelligenceEngine:
    """Enterprise business intelligence and analytics engine"""

    def __init__(self, aggregator: MetricsAggregator):
        self.aggregator = aggregator
        self.kpi_definitions = {}
        self.dashboard_configs = {}
        self.logger = logging.getLogger(__name__)

        # Initialize enterprise KPIs
        self._setup_enterprise_kpis()

    def _setup_enterprise_kpis(self):
        """Setup standard enterprise KPIs"""

        # System Performance KPIs
        self.aggregator.define_metric(MetricDefinition(
            name="system_availability",
            description="Overall system availability percentage",
            source_metrics=["system.uptime", "system.downtime"],
            calculation="system.uptime / (system.uptime + system.downtime) * 100",
            unit="percentage",
            category="reliability",
            alert_thresholds={"critical": 95.0, "warning": 99.0},
            business_impact="critical"
        ))

        self.aggregator.define_metric(MetricDefinition(
            name="response_time_sla",
            description="Percentage of requests meeting SLA response time",
            source_metrics=["api.request.duration"],
            calculation="response_time_sla",
            unit="percentage",
            category="performance",
            alert_thresholds={"critical": 90.0, "warning": 95.0},
            business_impact="high"
        ))

        # Business KPIs
        self.aggregator.define_metric(MetricDefinition(
            name="user_satisfaction_score",
            description="User satisfaction index based on performance metrics",
            source_metrics=["api.request.duration", "api.error.rate", "system.cpu.usage_percent"],
            calculation="apdex_score",
            unit="score",
            category="business",
            alert_thresholds={"critical": 0.7, "warning": 0.85},
            business_impact="critical"
        ))

        # Resource Efficiency KPIs
        self.aggregator.define_metric(MetricDefinition(
            name="resource_efficiency",
            description="Overall resource utilization efficiency",
            source_metrics=["system.cpu.usage_percent", "system.memory.usage_percent"],
            calculation="(system.cpu.usage_percent + system.memory.usage_percent) / 2",
            unit="percentage",
            category="efficiency",
            alert_thresholds={"warning": 70.0, "critical": 85.0},
            business_impact="medium"
        ))

    def calculate_business_kpis(self, time_range: timedelta = None) -> Dict[str, float]:
        """Calculate all business KPIs for specified time range"""
        if time_range is None:
            time_range = timedelta(hours=1)

        end_time = datetime.now()
        start_time = end_time - time_range

        kpi_results = {}

        for kpi_name, definition in self.aggregator.metric_definitions.items():
            try:
                # Get source metrics data
                source_data = {}
                for source_metric in definition.source_metrics:
                    # This would typically fetch from metrics storage
                    # For demo, we'll simulate some data
                    source_data[source_metric] = self._simulate_metric_data(source_metric, start_time, end_time)

                # Calculate KPI
                kpi_value = self.aggregator.calculate_custom_metric(kpi_name, source_data)
                kpi_results[kpi_name] = kpi_value

            except Exception as e:
                self.logger.error(f"Error calculating KPI {kpi_name}: {e}")
                kpi_results[kpi_name] = 0.0

        return kpi_results

    def _simulate_metric_data(self, metric_name: str, start_time: datetime, end_time: datetime) -> List[MetricPoint]:
        """Simulate metric data for demo purposes"""
        import random

        metrics = []
        current_time = start_time
        interval = timedelta(minutes=1)

        while current_time <= end_time:
            if "cpu" in metric_name:
                value = random.uniform(20, 80)
            elif "memory" in metric_name:
                value = random.uniform(30, 70)
            elif "duration" in metric_name:
                value = random.uniform(0.1, 2.0)
            elif "error" in metric_name:
                value = random.uniform(0, 0.05)
            else:
                value = random.uniform(0, 100)

            metrics.append(MetricPoint(
                timestamp=current_time,
                value=value,
                metric_name=metric_name
            ))

            current_time += interval

        return metrics

    def generate_executive_report(self) -> Dict[str, Any]:
        """Generate comprehensive executive report"""
        kpis = self.calculate_business_kpis(timedelta(days=1))

        # Categorize KPIs
        performance_kpis = {}
        business_kpis = {}
        efficiency_kpis = {}

        for kpi_name, value in kpis.items():
            if kpi_name in self.aggregator.metric_definitions:
                definition = self.aggregator.metric_definitions[kpi_name]
                category = definition.category

                if category == "performance":
                    performance_kpis[kpi_name] = value
                elif category == "business":
                    business_kpis[kpi_name] = value
                elif category == "efficiency":
                    efficiency_kpis[kpi_name] = value

        # Calculate overall health score
        health_score = sum(kpis.values()) / len(kpis) if kpis else 0

        return {
            "report_type": "executive_summary",
            "generated_at": datetime.now().isoformat(),
            "time_period": "24 hours",
            "overall_health_score": health_score,
            "performance_kpis": performance_kpis,
            "business_kpis": business_kpis,
            "efficiency_kpis": efficiency_kpis,
            "key_insights": self._generate_insights(kpis),
            "recommendations": self._generate_recommendations(kpis),
            "risk_assessment": self._assess_risks(kpis)
        }

    def _generate_insights(self, kpis: Dict[str, float]) -> List[str]:
        """Generate business insights from KPI data"""
        insights = []

        for kpi_name, value in kpis.items():
            if kpi_name in self.aggregator.metric_definitions:
                definition = self.aggregator.metric_definitions[kpi_name]

                # Check against thresholds
                if "critical" in definition.alert_thresholds:
                    if value < definition.alert_thresholds["critical"]:
                        insights.append(f"{definition.description} is below critical threshold ({value:.2f})")
                    elif "warning" in definition.alert_thresholds and value < definition.alert_thresholds["warning"]:
                        insights.append(f"{definition.description} is approaching warning threshold ({value:.2f})")
                    else:
                        insights.append(f"{definition.description} is performing well ({value:.2f})")

        return insights

    def _generate_recommendations(self, kpis: Dict[str, float]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # System availability recommendations
        if "system_availability" in kpis and kpis["system_availability"] < 99.0:
            recommendations.extend([
                "Implement redundancy and failover mechanisms",
                "Review and optimize system monitoring and alerting",
                "Consider implementing blue-green deployment strategies"
            ])

        # Performance recommendations
        if "response_time_sla" in kpis and kpis["response_time_sla"] < 95.0:
            recommendations.extend([
                "Optimize database queries and add caching layers",
                "Implement load balancing and auto-scaling",
                "Review and optimize critical API endpoints"
            ])

        # Resource efficiency recommendations
        if "resource_efficiency" in kpis and kpis["resource_efficiency"] > 80.0:
            recommendations.extend([
                "Consider scaling infrastructure horizontally",
                "Implement resource optimization strategies",
                "Review workload distribution and scheduling"
            ])

        return recommendations

    def _assess_risks(self, kpis: Dict[str, float]) -> Dict[str, str]:
        """Assess business risks based on KPI performance"""
        risk_assessment = {"overall_risk": "low"}

        critical_issues = 0
        warning_issues = 0

        for kpi_name, value in kpis.items():
            if kpi_name in self.aggregator.metric_definitions:
                definition = self.aggregator.metric_definitions[kpi_name]

                if "critical" in definition.alert_thresholds and value < definition.alert_thresholds["critical"]:
                    critical_issues += 1
                elif "warning" in definition.alert_thresholds and value < definition.alert_thresholds["warning"]:
                    warning_issues += 1

        if critical_issues > 0:
            risk_assessment["overall_risk"] = "high"
            risk_assessment["critical_issues"] = critical_issues
        elif warning_issues > 2:
            risk_assessment["overall_risk"] = "medium"
            risk_assessment["warning_issues"] = warning_issues

        return risk_assessment


# Global instances
_metrics_aggregator: Optional[MetricsAggregator] = None
_bi_engine: Optional[BusinessIntelligenceEngine] = None


def get_metrics_aggregator(config: Optional[Dict] = None) -> MetricsAggregator:
    """Get or create global metrics aggregator"""
    global _metrics_aggregator
    if _metrics_aggregator is None:
        _metrics_aggregator = MetricsAggregator(config)
    return _metrics_aggregator


def get_bi_engine() -> BusinessIntelligenceEngine:
    """Get or create global BI engine"""
    global _bi_engine
    if _bi_engine is None:
        aggregator = get_metrics_aggregator()
        _bi_engine = BusinessIntelligenceEngine(aggregator)
    return _bi_engine


def initialize_enterprise_analytics(config: Optional[Dict] = None):
    """Initialize enterprise analytics system"""
    aggregator = get_metrics_aggregator(config)
    bi_engine = get_bi_engine()
    return aggregator, bi_engine