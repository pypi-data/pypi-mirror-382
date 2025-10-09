"""Real-time streaming analytics and aggregation for Vizly."""

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



from __future__ import annotations

import numpy as np
import time
import threading
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field
from collections import deque, defaultdict
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


@dataclass
class AggregationResult:
    """Result of a streaming aggregation."""
    timestamp: float
    value: Union[float, int, np.ndarray]
    count: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'value': self.value.tolist() if isinstance(self.value, np.ndarray) else self.value,
            'count': self.count,
            'metadata': self.metadata
        }


class StreamingAggregator(ABC):
    """Abstract base class for streaming aggregators."""

    def __init__(self, window_size: float = 60.0):
        self.window_size = window_size  # seconds
        self.reset()

    @abstractmethod
    def update(self, value: Union[float, int, np.ndarray], timestamp: float):
        """Update aggregator with new value."""
        pass

    @abstractmethod
    def get_result(self) -> Optional[AggregationResult]:
        """Get current aggregation result."""
        pass

    @abstractmethod
    def reset(self):
        """Reset aggregator state."""
        pass


class MeanAggregator(StreamingAggregator):
    """Streaming mean aggregator."""

    def reset(self):
        self.sum = 0.0
        self.count = 0
        self.first_timestamp = None
        self.last_timestamp = None

    def update(self, value: Union[float, int, np.ndarray], timestamp: float):
        if isinstance(value, np.ndarray):
            value = np.mean(value)  # Average multi-dimensional data

        self.sum += float(value)
        self.count += 1

        if self.first_timestamp is None:
            self.first_timestamp = timestamp
        self.last_timestamp = timestamp

    def get_result(self) -> Optional[AggregationResult]:
        if self.count == 0:
            return None

        return AggregationResult(
            timestamp=self.last_timestamp,
            value=self.sum / self.count,
            count=self.count,
            metadata={'window_duration': self.last_timestamp - self.first_timestamp}
        )


class SumAggregator(StreamingAggregator):
    """Streaming sum aggregator."""

    def reset(self):
        self.sum = 0.0
        self.count = 0
        self.last_timestamp = None

    def update(self, value: Union[float, int, np.ndarray], timestamp: float):
        if isinstance(value, np.ndarray):
            value = np.sum(value)

        self.sum += float(value)
        self.count += 1
        self.last_timestamp = timestamp

    def get_result(self) -> Optional[AggregationResult]:
        if self.count == 0:
            return None

        return AggregationResult(
            timestamp=self.last_timestamp,
            value=self.sum,
            count=self.count
        )


class CountAggregator(StreamingAggregator):
    """Streaming count aggregator."""

    def reset(self):
        self.count = 0
        self.last_timestamp = None

    def update(self, value: Union[float, int, np.ndarray], timestamp: float):
        self.count += 1
        self.last_timestamp = timestamp

    def get_result(self) -> Optional[AggregationResult]:
        if self.count == 0:
            return None

        return AggregationResult(
            timestamp=self.last_timestamp,
            value=self.count,
            count=self.count
        )


class MinMaxAggregator(StreamingAggregator):
    """Streaming min/max aggregator."""

    def reset(self):
        self.min_value = float('inf')
        self.max_value = float('-inf')
        self.count = 0
        self.last_timestamp = None

    def update(self, value: Union[float, int, np.ndarray], timestamp: float):
        if isinstance(value, np.ndarray):
            min_val, max_val = np.min(value), np.max(value)
        else:
            min_val = max_val = float(value)

        self.min_value = min(self.min_value, min_val)
        self.max_value = max(self.max_value, max_val)
        self.count += 1
        self.last_timestamp = timestamp

    def get_result(self) -> Optional[AggregationResult]:
        if self.count == 0:
            return None

        return AggregationResult(
            timestamp=self.last_timestamp,
            value={'min': self.min_value, 'max': self.max_value},
            count=self.count
        )


class StandardDeviationAggregator(StreamingAggregator):
    """Streaming standard deviation aggregator (Welford's algorithm)."""

    def reset(self):
        self.count = 0
        self.mean = 0.0
        self.m2 = 0.0
        self.last_timestamp = None

    def update(self, value: Union[float, int, np.ndarray], timestamp: float):
        if isinstance(value, np.ndarray):
            value = np.mean(value)

        value = float(value)
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean
        self.m2 += delta * delta2
        self.last_timestamp = timestamp

    def get_result(self) -> Optional[AggregationResult]:
        if self.count < 2:
            return None

        variance = self.m2 / (self.count - 1)
        std_dev = np.sqrt(variance)

        return AggregationResult(
            timestamp=self.last_timestamp,
            value={'mean': self.mean, 'std': std_dev, 'variance': variance},
            count=self.count
        )


class PercentileAggregator(StreamingAggregator):
    """Streaming percentile aggregator."""

    def __init__(self, percentiles: List[float] = [25, 50, 75, 95], window_size: float = 60.0):
        self.percentiles = percentiles
        super().__init__(window_size)

    def reset(self):
        self.values = deque()
        self.timestamps = deque()

    def update(self, value: Union[float, int, np.ndarray], timestamp: float):
        if isinstance(value, np.ndarray):
            value = np.mean(value)

        self.values.append(float(value))
        self.timestamps.append(timestamp)

        # Remove old values outside window
        current_time = timestamp
        while (self.timestamps and
               current_time - self.timestamps[0] > self.window_size):
            self.values.popleft()
            self.timestamps.popleft()

    def get_result(self) -> Optional[AggregationResult]:
        if not self.values:
            return None

        values_array = np.array(list(self.values))
        percentile_values = {}

        for p in self.percentiles:
            percentile_values[f'p{p}'] = np.percentile(values_array, p)

        return AggregationResult(
            timestamp=self.timestamps[-1],
            value=percentile_values,
            count=len(self.values)
        )


class LiveAggregator:
    """Manages multiple streaming aggregators for live data."""

    def __init__(self):
        self.aggregators: Dict[str, Dict[str, StreamingAggregator]] = defaultdict(dict)
        self.last_results: Dict[str, Dict[str, AggregationResult]] = defaultdict(dict)
        self.update_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        self._lock = threading.RLock()

    def add_aggregator(self, stream_id: str, aggregator_name: str,
                      aggregator: StreamingAggregator):
        """Add an aggregator for a stream."""
        with self._lock:
            self.aggregators[stream_id][aggregator_name] = aggregator

    def remove_aggregator(self, stream_id: str, aggregator_name: str):
        """Remove an aggregator."""
        with self._lock:
            if stream_id in self.aggregators:
                self.aggregators[stream_id].pop(aggregator_name, None)
                if stream_id in self.last_results:
                    self.last_results[stream_id].pop(aggregator_name, None)

    def update_stream(self, stream_id: str, value: Union[float, int, np.ndarray],
                     timestamp: Optional[float] = None):
        """Update all aggregators for a stream."""
        if timestamp is None:
            timestamp = time.time()

        with self._lock:
            for aggregator_name, aggregator in self.aggregators[stream_id].items():
                aggregator.update(value, timestamp)

                # Get updated result
                result = aggregator.get_result()
                if result:
                    self.last_results[stream_id][aggregator_name] = result

                    # Notify callbacks
                    for callback in self.update_callbacks[stream_id]:
                        try:
                            callback(stream_id, aggregator_name, result)
                        except Exception as e:
                            logger.error(f"Error in aggregation callback: {e}")

    def get_results(self, stream_id: str) -> Dict[str, AggregationResult]:
        """Get latest results for a stream."""
        with self._lock:
            return dict(self.last_results[stream_id])

    def get_all_results(self) -> Dict[str, Dict[str, AggregationResult]]:
        """Get all latest results."""
        with self._lock:
            return {
                stream_id: dict(results)
                for stream_id, results in self.last_results.items()
            }

    def add_callback(self, stream_id: str, callback: Callable[[str, str, AggregationResult], None]):
        """Add callback for aggregation updates."""
        self.update_callbacks[stream_id].append(callback)

    def reset_stream(self, stream_id: str):
        """Reset all aggregators for a stream."""
        with self._lock:
            for aggregator in self.aggregators[stream_id].values():
                aggregator.reset()
            self.last_results[stream_id].clear()


class StreamingAnalytics:
    """Comprehensive real-time analytics system."""

    def __init__(self):
        self.live_aggregator = LiveAggregator()
        self.anomaly_detectors: Dict[str, 'AnomalyDetector'] = {}
        self.alert_rules: Dict[str, List['AlertRule']] = defaultdict(list)
        self.alert_callbacks: List[Callable] = []

        # Performance tracking
        self.processed_points = 0
        self.processing_time = 0.0
        self.start_time = time.time()

    def add_stream_analytics(self, stream_id: str, analytics_config: Dict[str, Any]):
        """Add analytics configuration for a stream."""
        # Add standard aggregators
        aggregators = analytics_config.get('aggregators', ['mean', 'count'])
        window_size = analytics_config.get('window_size', 60.0)

        for agg_name in aggregators:
            if agg_name == 'mean':
                aggregator = MeanAggregator(window_size)
            elif agg_name == 'sum':
                aggregator = SumAggregator(window_size)
            elif agg_name == 'count':
                aggregator = CountAggregator(window_size)
            elif agg_name == 'minmax':
                aggregator = MinMaxAggregator(window_size)
            elif agg_name == 'std':
                aggregator = StandardDeviationAggregator(window_size)
            elif agg_name == 'percentiles':
                percentiles = analytics_config.get('percentiles', [25, 50, 75, 95])
                aggregator = PercentileAggregator(percentiles, window_size)
            else:
                logger.warning(f"Unknown aggregator type: {agg_name}")
                continue

            self.live_aggregator.add_aggregator(stream_id, agg_name, aggregator)

        # Add anomaly detection
        if analytics_config.get('anomaly_detection', False):
            threshold = analytics_config.get('anomaly_threshold', 3.0)
            self.anomaly_detectors[stream_id] = ZScoreAnomalyDetector(threshold)

        # Add alert rules
        alert_rules = analytics_config.get('alert_rules', [])
        for rule_config in alert_rules:
            rule = AlertRule.from_config(rule_config)
            self.alert_rules[stream_id].append(rule)

    def process_data_point(self, stream_id: str, value: Union[float, int, np.ndarray],
                          timestamp: Optional[float] = None):
        """Process a single data point through analytics pipeline."""
        start_time = time.time()

        if timestamp is None:
            timestamp = time.time()

        # Update aggregators
        self.live_aggregator.update_stream(stream_id, value, timestamp)

        # Anomaly detection
        if stream_id in self.anomaly_detectors:
            is_anomaly = self.anomaly_detectors[stream_id].check(value, timestamp)
            if is_anomaly:
                self._trigger_alert(stream_id, 'anomaly', {
                    'value': value,
                    'timestamp': timestamp,
                    'type': 'anomaly_detected'
                })

        # Check alert rules
        results = self.live_aggregator.get_results(stream_id)
        for rule in self.alert_rules[stream_id]:
            if rule.check(results):
                self._trigger_alert(stream_id, 'rule_triggered', {
                    'rule_name': rule.name,
                    'condition': rule.condition,
                    'results': {k: v.to_dict() for k, v in results.items()}
                })

        # Update performance metrics
        self.processed_points += 1
        self.processing_time += time.time() - start_time

    def get_analytics_summary(self, stream_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics summary for a stream."""
        results = self.live_aggregator.get_results(stream_id)

        summary = {
            'aggregations': {k: v.to_dict() for k, v in results.items()},
            'anomaly_detection': {},
            'alerts': []
        }

        # Anomaly detection status
        if stream_id in self.anomaly_detectors:
            detector = self.anomaly_detectors[stream_id]
            summary['anomaly_detection'] = {
                'enabled': True,
                'threshold': detector.threshold,
                'recent_anomalies': detector.recent_anomalies
            }

        return summary

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get analytics performance statistics."""
        uptime = time.time() - self.start_time
        avg_processing_time = (self.processing_time / self.processed_points
                             if self.processed_points > 0 else 0)

        return {
            'uptime': uptime,
            'processed_points': self.processed_points,
            'points_per_second': self.processed_points / max(uptime, 1),
            'avg_processing_time': avg_processing_time,
            'total_processing_time': self.processing_time,
            'streams': len(self.live_aggregator.aggregators),
            'anomaly_detectors': len(self.anomaly_detectors),
            'alert_rules': sum(len(rules) for rules in self.alert_rules.values())
        }

    def add_alert_callback(self, callback: Callable[[str, str, Dict], None]):
        """Add callback for alert notifications."""
        self.alert_callbacks.append(callback)

    def _trigger_alert(self, stream_id: str, alert_type: str, alert_data: Dict):
        """Trigger an alert."""
        alert = {
            'stream_id': stream_id,
            'type': alert_type,
            'timestamp': time.time(),
            'data': alert_data
        }

        for callback in self.alert_callbacks:
            try:
                callback(stream_id, alert_type, alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")


class ZScoreAnomalyDetector:
    """Z-score based anomaly detector."""

    def __init__(self, threshold: float = 3.0, window_size: int = 100):
        self.threshold = threshold
        self.window_size = window_size
        self.values = deque(maxlen=window_size)
        self.recent_anomalies: List[Dict] = []

    def check(self, value: Union[float, int, np.ndarray], timestamp: float) -> bool:
        """Check if value is an anomaly."""
        if isinstance(value, np.ndarray):
            value = np.mean(value)

        value = float(value)
        self.values.append(value)

        if len(self.values) < 3:  # Need minimum samples
            return False

        # Calculate z-score
        mean_val = np.mean(self.values)
        std_val = np.std(self.values)

        if std_val == 0:
            return False

        z_score = abs((value - mean_val) / std_val)
        is_anomaly = z_score > self.threshold

        if is_anomaly:
            anomaly_record = {
                'timestamp': timestamp,
                'value': value,
                'z_score': z_score,
                'mean': mean_val,
                'std': std_val
            }
            self.recent_anomalies.append(anomaly_record)

            # Keep only recent anomalies
            if len(self.recent_anomalies) > 50:
                self.recent_anomalies = self.recent_anomalies[-50:]

        return is_anomaly


class AlertRule:
    """Configurable alert rule for streaming analytics."""

    def __init__(self, name: str, condition: str, aggregator: str,
                 threshold: float, comparison: str = 'gt'):
        self.name = name
        self.condition = condition
        self.aggregator = aggregator
        self.threshold = threshold
        self.comparison = comparison  # 'gt', 'lt', 'eq', 'gte', 'lte'

        self.triggered_count = 0
        self.last_triggered = None

    def check(self, results: Dict[str, AggregationResult]) -> bool:
        """Check if rule condition is met."""
        if self.aggregator not in results:
            return False

        result = results[self.aggregator]
        value = result.value

        # Handle different value types
        if isinstance(value, dict):
            # For complex aggregations, use the first numeric value
            for key, val in value.items():
                if isinstance(val, (int, float)):
                    value = val
                    break
            else:
                return False

        if not isinstance(value, (int, float)):
            return False

        # Apply comparison
        triggered = False
        if self.comparison == 'gt':
            triggered = value > self.threshold
        elif self.comparison == 'lt':
            triggered = value < self.threshold
        elif self.comparison == 'gte':
            triggered = value >= self.threshold
        elif self.comparison == 'lte':
            triggered = value <= self.threshold
        elif self.comparison == 'eq':
            triggered = abs(value - self.threshold) < 1e-6

        if triggered:
            self.triggered_count += 1
            self.last_triggered = time.time()

        return triggered

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'AlertRule':
        """Create alert rule from configuration."""
        return cls(
            name=config['name'],
            condition=config['condition'],
            aggregator=config['aggregator'],
            threshold=config['threshold'],
            comparison=config.get('comparison', 'gt')
        )