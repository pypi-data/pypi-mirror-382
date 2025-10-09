"""
Real-time Performance Metrics Dashboard
=======================================

Advanced performance monitoring and analysis system for AI training infrastructure
with real-time dashboards, bottleneck detection, and optimization recommendations.

Features:
- Real-time performance metric collection
- Multi-dimensional performance analysis
- Interactive dashboard generation
- Bottleneck identification and analysis
- Resource optimization recommendations
- Historical performance trending
- Predictive performance modeling
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



import json
import time
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import threading
import math


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    timestamp: float
    node_id: str

    # CPU Metrics
    cpu_utilization: float
    cpu_frequency: float
    memory_used_gb: float
    memory_total_gb: float
    memory_utilization: float
    cpu_temperature: Optional[float] = None

    # Memory Metrics
    memory_bandwidth_gbps: Optional[float] = None

    # GPU Metrics
    gpu_utilization: Optional[float] = None
    gpu_memory_used_gb: Optional[float] = None
    gpu_memory_total_gb: Optional[float] = None
    gpu_temperature: Optional[float] = None
    gpu_power_watts: Optional[float] = None
    gpu_compute_capability: Optional[str] = None

    # Network Metrics
    network_rx_mbps: float = 0.0
    network_tx_mbps: float = 0.0
    network_latency_ms: Optional[float] = None
    network_packet_loss: Optional[float] = None

    # Storage Metrics
    disk_read_mbps: float = 0.0
    disk_write_mbps: float = 0.0
    disk_utilization: float = 0.0
    disk_queue_depth: Optional[float] = None

    # Application Metrics
    throughput_ops_per_sec: Optional[float] = None
    response_time_ms: Optional[float] = None
    error_rate_percent: Optional[float] = None
    queue_depth: Optional[int] = None


@dataclass
class BottleneckAnalysis:
    """Performance bottleneck analysis result"""
    bottleneck_type: str  # 'cpu', 'memory', 'gpu', 'network', 'storage', 'application'
    severity: str  # 'critical', 'high', 'medium', 'low'
    impact_score: float  # 0-100, higher is more impactful
    affected_components: List[str]
    current_utilization: float
    recommended_threshold: float
    optimization_suggestions: List[str]
    estimated_improvement: float  # Percentage improvement estimate


class PerformanceDashboard:
    """Real-time performance monitoring dashboard"""

    def __init__(self, collection_interval: float = 5.0):
        self.collection_interval = collection_interval
        self.metrics_buffer = deque(maxlen=2000)  # ~2.7 hours at 5s intervals
        self.node_metrics = defaultdict(lambda: deque(maxlen=1000))
        self.is_collecting = False
        self.collection_thread = None
        self.collection_lock = threading.Lock()

        # Performance baselines for anomaly detection
        self.performance_baselines = {}
        self.baseline_window = 100  # Number of samples for baseline

        # Bottleneck detection configuration
        self.bottleneck_thresholds = {
            'cpu_critical': 95.0,
            'cpu_high': 85.0,
            'memory_critical': 95.0,
            'memory_high': 85.0,
            'gpu_critical': 98.0,
            'gpu_high': 90.0,
            'storage_critical': 95.0,
            'storage_high': 80.0,
            'network_high_latency': 100.0,  # ms
            'network_packet_loss': 0.1  # %
        }

    def collect_metrics(self, node_id: str = None) -> PerformanceMetrics:
        """Collect current performance metrics from system"""
        import psutil

        node_id = node_id or f"node_{int(time.time()) % 1000}"
        timestamp = time.time()

        # CPU metrics
        cpu_utilization = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        cpu_frequency = cpu_freq.current if cpu_freq else 0.0
        cpu_temp = self._get_cpu_temperature()

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_used_gb = (memory.total - memory.available) / (1024**3)
        memory_total_gb = memory.total / (1024**3)

        # Network metrics
        network_io = psutil.net_io_counters()
        prev_network = getattr(self, '_prev_network_io', network_io)
        time_diff = time.time() - getattr(self, '_prev_network_time', timestamp - 1)

        network_rx_mbps = ((network_io.bytes_recv - prev_network.bytes_recv) * 8) / (time_diff * 1024 * 1024)
        network_tx_mbps = ((network_io.bytes_sent - prev_network.bytes_sent) * 8) / (time_diff * 1024 * 1024)

        self._prev_network_io = network_io
        self._prev_network_time = timestamp

        # Storage metrics
        disk_io = psutil.disk_io_counters()
        if disk_io:
            prev_disk = getattr(self, '_prev_disk_io', disk_io)
            disk_read_mbps = ((disk_io.read_bytes - prev_disk.read_bytes)) / (time_diff * 1024 * 1024)
            disk_write_mbps = ((disk_io.write_bytes - prev_disk.write_bytes)) / (time_diff * 1024 * 1024)
            self._prev_disk_io = disk_io
        else:
            disk_read_mbps = disk_write_mbps = 0.0

        disk_usage = psutil.disk_usage('/')

        # GPU metrics
        gpu_metrics = self._get_gpu_metrics()

        return PerformanceMetrics(
            timestamp=timestamp,
            node_id=node_id,
            cpu_utilization=cpu_utilization,
            cpu_frequency=cpu_frequency,
            cpu_temperature=cpu_temp,
            memory_used_gb=memory_used_gb,
            memory_total_gb=memory_total_gb,
            memory_utilization=memory.percent,
            network_rx_mbps=max(0, network_rx_mbps),
            network_tx_mbps=max(0, network_tx_mbps),
            disk_read_mbps=max(0, disk_read_mbps),
            disk_write_mbps=max(0, disk_write_mbps),
            disk_utilization=disk_usage.percent,
            **gpu_metrics
        )

    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature if available"""
        try:
            import psutil
            sensors = psutil.sensors_temperatures()
            if 'coretemp' in sensors:
                return sensors['coretemp'][0].current
            elif 'cpu_thermal' in sensors:
                return sensors['cpu_thermal'][0].current
        except (ImportError, AttributeError, IndexError):
            pass
        return None

    def _get_gpu_metrics(self) -> Dict[str, Optional[float]]:
        """Get GPU metrics if available"""
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Primary GPU
                return {
                    'gpu_utilization': gpu.load * 100,
                    'gpu_memory_used_gb': gpu.memoryUsed / 1024,
                    'gpu_memory_total_gb': gpu.memoryTotal / 1024,
                    'gpu_temperature': gpu.temperature,
                    'gpu_power_watts': getattr(gpu, 'power', None),
                    'gpu_compute_capability': getattr(gpu, 'name', 'Unknown')
                }
        except ImportError:
            pass

        return {
            'gpu_utilization': None,
            'gpu_memory_used_gb': None,
            'gpu_memory_total_gb': None,
            'gpu_temperature': None,
            'gpu_power_watts': None,
            'gpu_compute_capability': None
        }

    def add_metrics(self, metrics: PerformanceMetrics):
        """Add performance metrics to buffer"""
        with self.collection_lock:
            self.metrics_buffer.append(metrics)
            self.node_metrics[metrics.node_id].append(metrics)

            # Update baselines
            self._update_baselines(metrics)

    def _update_baselines(self, metrics: PerformanceMetrics):
        """Update performance baselines for anomaly detection"""
        node_id = metrics.node_id
        if node_id not in self.performance_baselines:
            self.performance_baselines[node_id] = {
                'cpu_baseline': deque(maxlen=self.baseline_window),
                'memory_baseline': deque(maxlen=self.baseline_window),
                'gpu_baseline': deque(maxlen=self.baseline_window)
            }

        baselines = self.performance_baselines[node_id]
        baselines['cpu_baseline'].append(metrics.cpu_utilization)
        baselines['memory_baseline'].append(metrics.memory_utilization)

        if metrics.gpu_utilization is not None:
            baselines['gpu_baseline'].append(metrics.gpu_utilization)

    def start_collection(self, node_id: str = None):
        """Start automatic metrics collection"""
        if self.is_collecting:
            return

        self.is_collecting = True
        self.collection_thread = threading.Thread(
            target=self._collection_loop,
            args=(node_id,)
        )
        self.collection_thread.daemon = True
        self.collection_thread.start()

    def stop_collection(self):
        """Stop automatic metrics collection"""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join()

    def _collection_loop(self, node_id: str):
        """Background metrics collection loop"""
        while self.is_collecting:
            try:
                metrics = self.collect_metrics(node_id)
                self.add_metrics(metrics)
                time.sleep(self.collection_interval)
            except Exception as e:
                print(f"Metrics collection error: {e}")
                time.sleep(self.collection_interval)


class BottleneckAnalyzer:
    """Advanced bottleneck detection and analysis"""

    def __init__(self, dashboard: PerformanceDashboard):
        self.dashboard = dashboard
        self.analysis_history = deque(maxlen=500)

    def analyze_bottlenecks(self, node_id: str = None) -> List[BottleneckAnalysis]:
        """Comprehensive bottleneck analysis"""
        with self.dashboard.collection_lock:
            if node_id:
                recent_metrics = list(self.dashboard.node_metrics[node_id])[-10:]  # Last 10 samples
            else:
                recent_metrics = list(self.dashboard.metrics_buffer)[-10:]

        if not recent_metrics:
            return []

        bottlenecks = []

        # CPU bottleneck analysis
        cpu_bottleneck = self._analyze_cpu_bottleneck(recent_metrics)
        if cpu_bottleneck:
            bottlenecks.append(cpu_bottleneck)

        # Memory bottleneck analysis
        memory_bottleneck = self._analyze_memory_bottleneck(recent_metrics)
        if memory_bottleneck:
            bottlenecks.append(memory_bottleneck)

        # GPU bottleneck analysis
        gpu_bottleneck = self._analyze_gpu_bottleneck(recent_metrics)
        if gpu_bottleneck:
            bottlenecks.append(gpu_bottleneck)

        # Storage bottleneck analysis
        storage_bottleneck = self._analyze_storage_bottleneck(recent_metrics)
        if storage_bottleneck:
            bottlenecks.append(storage_bottleneck)

        # Network bottleneck analysis
        network_bottleneck = self._analyze_network_bottleneck(recent_metrics)
        if network_bottleneck:
            bottlenecks.append(network_bottleneck)

        # Sort by impact score
        bottlenecks.sort(key=lambda b: b.impact_score, reverse=True)
        return bottlenecks

    def _analyze_cpu_bottleneck(self, metrics: List[PerformanceMetrics]) -> Optional[BottleneckAnalysis]:
        """Analyze CPU performance bottlenecks"""
        if not metrics:
            return None

        avg_cpu = sum(m.cpu_utilization for m in metrics) / len(metrics)
        max_cpu = max(m.cpu_utilization for m in metrics)

        thresholds = self.dashboard.bottleneck_thresholds

        if avg_cpu > thresholds['cpu_critical']:
            severity = 'critical'
            impact_score = min(100, (avg_cpu - thresholds['cpu_critical']) * 5 + 80)
        elif avg_cpu > thresholds['cpu_high']:
            severity = 'high'
            impact_score = min(80, (avg_cpu - thresholds['cpu_high']) * 3 + 60)
        elif avg_cpu > 70:
            severity = 'medium'
            impact_score = min(60, (avg_cpu - 70) * 2 + 40)
        else:
            return None

        optimization_suggestions = []
        if avg_cpu > 90:
            optimization_suggestions.extend([
                "Scale out to additional nodes to distribute load",
                "Optimize CPU-intensive algorithms",
                "Enable CPU governor for performance mode",
                "Consider CPU upgrade if sustained high usage"
            ])
        elif avg_cpu > 80:
            optimization_suggestions.extend([
                "Profile application for CPU hotspots",
                "Implement CPU-efficient algorithms",
                "Consider parallel processing optimizations"
            ])

        return BottleneckAnalysis(
            bottleneck_type='cpu',
            severity=severity,
            impact_score=impact_score,
            affected_components=['CPU', 'System Performance'],
            current_utilization=avg_cpu,
            recommended_threshold=75.0,
            optimization_suggestions=optimization_suggestions,
            estimated_improvement=min(30, (avg_cpu - 75) * 0.5)
        )

    def _analyze_memory_bottleneck(self, metrics: List[PerformanceMetrics]) -> Optional[BottleneckAnalysis]:
        """Analyze memory performance bottlenecks"""
        if not metrics:
            return None

        avg_memory = sum(m.memory_utilization for m in metrics) / len(metrics)
        max_memory = max(m.memory_utilization for m in metrics)

        thresholds = self.dashboard.bottleneck_thresholds

        if avg_memory > thresholds['memory_critical']:
            severity = 'critical'
            impact_score = min(100, (avg_memory - thresholds['memory_critical']) * 10 + 85)
        elif avg_memory > thresholds['memory_high']:
            severity = 'high'
            impact_score = min(85, (avg_memory - thresholds['memory_high']) * 5 + 65)
        elif avg_memory > 75:
            severity = 'medium'
            impact_score = min(65, (avg_memory - 75) * 2 + 45)
        else:
            return None

        optimization_suggestions = []
        if avg_memory > 90:
            optimization_suggestions.extend([
                "Immediate memory optimization required",
                "Review memory allocation patterns",
                "Implement memory pooling strategies",
                "Consider memory upgrade"
            ])
        elif avg_memory > 80:
            optimization_suggestions.extend([
                "Monitor for memory leaks",
                "Optimize data structures",
                "Implement garbage collection tuning"
            ])

        return BottleneckAnalysis(
            bottleneck_type='memory',
            severity=severity,
            impact_score=impact_score,
            affected_components=['RAM', 'System Stability'],
            current_utilization=avg_memory,
            recommended_threshold=80.0,
            optimization_suggestions=optimization_suggestions,
            estimated_improvement=min(25, (avg_memory - 80) * 0.4)
        )

    def _analyze_gpu_bottleneck(self, metrics: List[PerformanceMetrics]) -> Optional[BottleneckAnalysis]:
        """Analyze GPU performance bottlenecks"""
        gpu_metrics = [m for m in metrics if m.gpu_utilization is not None]
        if not gpu_metrics:
            return None

        avg_gpu = sum(m.gpu_utilization for m in gpu_metrics) / len(gpu_metrics)
        avg_gpu_temp = sum(m.gpu_temperature for m in gpu_metrics if m.gpu_temperature) / len([m for m in gpu_metrics if m.gpu_temperature]) if any(m.gpu_temperature for m in gpu_metrics) else 0

        thresholds = self.dashboard.bottleneck_thresholds

        if avg_gpu > thresholds['gpu_critical'] or avg_gpu_temp > 85:
            severity = 'critical'
            impact_score = min(100, max((avg_gpu - thresholds['gpu_critical']) * 5 + 85, (avg_gpu_temp - 85) * 2 + 85))
        elif avg_gpu > thresholds['gpu_high'] or avg_gpu_temp > 80:
            severity = 'high'
            impact_score = min(85, max((avg_gpu - thresholds['gpu_high']) * 3 + 65, (avg_gpu_temp - 80) * 2 + 65))
        elif avg_gpu > 75:
            severity = 'medium'
            impact_score = min(65, (avg_gpu - 75) * 2 + 45)
        else:
            return None

        optimization_suggestions = []
        if avg_gpu > 95:
            optimization_suggestions.extend([
                "GPU at maximum capacity - consider GPU scaling",
                "Optimize GPU kernel efficiency",
                "Review batch sizes for optimal GPU utilization",
                "Consider mixed-precision training"
            ])
        elif avg_gpu_temp > 80:
            optimization_suggestions.extend([
                "GPU thermal throttling risk",
                "Improve GPU cooling",
                "Reduce GPU workload intensity"
            ])

        return BottleneckAnalysis(
            bottleneck_type='gpu',
            severity=severity,
            impact_score=impact_score,
            affected_components=['GPU', 'Training Performance'],
            current_utilization=avg_gpu,
            recommended_threshold=85.0,
            optimization_suggestions=optimization_suggestions,
            estimated_improvement=min(35, (avg_gpu - 85) * 0.6)
        )

    def _analyze_storage_bottleneck(self, metrics: List[PerformanceMetrics]) -> Optional[BottleneckAnalysis]:
        """Analyze storage performance bottlenecks"""
        if not metrics:
            return None

        avg_disk_util = sum(m.disk_utilization for m in metrics) / len(metrics)
        avg_read_mbps = sum(m.disk_read_mbps for m in metrics) / len(metrics)
        avg_write_mbps = sum(m.disk_write_mbps for m in metrics) / len(metrics)

        thresholds = self.dashboard.bottleneck_thresholds

        if avg_disk_util > thresholds['storage_critical']:
            severity = 'critical'
            impact_score = min(100, (avg_disk_util - thresholds['storage_critical']) * 8 + 80)
        elif avg_disk_util > thresholds['storage_high']:
            severity = 'high'
            impact_score = min(80, (avg_disk_util - thresholds['storage_high']) * 4 + 60)
        elif avg_disk_util > 70 or (avg_read_mbps + avg_write_mbps) > 500:
            severity = 'medium'
            impact_score = min(60, (avg_disk_util - 70) * 2 + 40)
        else:
            return None

        optimization_suggestions = []
        if avg_disk_util > 90:
            optimization_suggestions.extend([
                "Critical storage I/O bottleneck",
                "Consider SSD upgrade for better performance",
                "Implement data preprocessing pipelines",
                "Use faster storage tiers for active data"
            ])

        return BottleneckAnalysis(
            bottleneck_type='storage',
            severity=severity,
            impact_score=impact_score,
            affected_components=['Storage', 'Data Pipeline'],
            current_utilization=avg_disk_util,
            recommended_threshold=75.0,
            optimization_suggestions=optimization_suggestions,
            estimated_improvement=min(20, (avg_disk_util - 75) * 0.3)
        )

    def _analyze_network_bottleneck(self, metrics: List[PerformanceMetrics]) -> Optional[BottleneckAnalysis]:
        """Analyze network performance bottlenecks"""
        if not metrics:
            return None

        avg_network_mbps = sum((m.network_rx_mbps + m.network_tx_mbps) for m in metrics) / len(metrics)
        avg_latency = sum(m.network_latency_ms for m in metrics if m.network_latency_ms) / len([m for m in metrics if m.network_latency_ms]) if any(m.network_latency_ms for m in metrics) else 0

        # Network bottleneck detection based on throughput and latency
        if avg_network_mbps > 800:  # Near gigabit saturation
            severity = 'high'
            impact_score = min(80, (avg_network_mbps - 800) * 0.1 + 70)
        elif avg_latency > 100:  # High latency
            severity = 'medium'
            impact_score = min(60, (avg_latency - 100) * 0.5 + 40)
        elif avg_network_mbps > 600:
            severity = 'medium'
            impact_score = min(60, (avg_network_mbps - 600) * 0.05 + 50)
        else:
            return None

        optimization_suggestions = [
            "Monitor network bandwidth utilization",
            "Consider network interface bonding",
            "Optimize data transfer patterns",
            "Implement data compression for network transfers"
        ]

        return BottleneckAnalysis(
            bottleneck_type='network',
            severity=severity,
            impact_score=impact_score,
            affected_components=['Network', 'Distributed Training'],
            current_utilization=avg_network_mbps,
            recommended_threshold=700.0,
            optimization_suggestions=optimization_suggestions,
            estimated_improvement=min(15, (avg_network_mbps - 700) * 0.02)
        )

    def generate_performance_report(self, node_id: str = None) -> Dict[str, Any]:
        """Generate comprehensive performance analysis report"""
        bottlenecks = self.analyze_bottlenecks(node_id)

        with self.dashboard.collection_lock:
            if node_id:
                recent_metrics = list(self.dashboard.node_metrics[node_id])[-20:]
            else:
                recent_metrics = list(self.dashboard.metrics_buffer)[-20:]

        if not recent_metrics:
            return {"error": "No performance data available"}

        # Calculate performance statistics
        current = recent_metrics[-1]
        avg_metrics = self._calculate_average_metrics(recent_metrics)

        return {
            "timestamp": current.timestamp,
            "node_id": current.node_id,
            "current_performance": asdict(current),
            "average_performance": avg_metrics,
            "bottleneck_analysis": [asdict(b) for b in bottlenecks],
            "performance_score": self._calculate_performance_score(recent_metrics),
            "optimization_priority": bottlenecks[0].bottleneck_type if bottlenecks else "none",
            "total_samples": len(recent_metrics)
        }

    def _calculate_average_metrics(self, metrics: List[PerformanceMetrics]) -> Dict[str, float]:
        """Calculate average performance metrics"""
        if not metrics:
            return {}

        return {
            "cpu_utilization": sum(m.cpu_utilization for m in metrics) / len(metrics),
            "memory_utilization": sum(m.memory_utilization for m in metrics) / len(metrics),
            "gpu_utilization": sum(m.gpu_utilization for m in metrics if m.gpu_utilization is not None) / len([m for m in metrics if m.gpu_utilization is not None]) if any(m.gpu_utilization is not None for m in metrics) else 0,
            "disk_utilization": sum(m.disk_utilization for m in metrics) / len(metrics),
            "network_throughput": sum((m.network_rx_mbps + m.network_tx_mbps) for m in metrics) / len(metrics),
        }

    def _calculate_performance_score(self, metrics: List[PerformanceMetrics]) -> float:
        """Calculate overall performance score (0-100)"""
        if not metrics:
            return 0.0

        avg_metrics = self._calculate_average_metrics(metrics)

        # Performance score based on utilization efficiency
        cpu_score = max(0, 100 - max(0, avg_metrics['cpu_utilization'] - 80) * 2)
        memory_score = max(0, 100 - max(0, avg_metrics['memory_utilization'] - 85) * 3)
        gpu_score = max(0, 100 - max(0, avg_metrics['gpu_utilization'] - 90) * 1) if avg_metrics['gpu_utilization'] > 0 else 100
        disk_score = max(0, 100 - max(0, avg_metrics['disk_utilization'] - 75) * 2)

        # Weighted average (GPU gets higher weight if present)
        if avg_metrics['gpu_utilization'] > 0:
            return (cpu_score * 0.2 + memory_score * 0.25 + gpu_score * 0.4 + disk_score * 0.15)
        else:
            return (cpu_score * 0.35 + memory_score * 0.4 + disk_score * 0.25)