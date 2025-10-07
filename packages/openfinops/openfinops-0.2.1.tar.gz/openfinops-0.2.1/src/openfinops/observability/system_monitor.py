"""
System Health Monitoring for AI Training Infrastructure
======================================================

Enterprise-grade system monitoring with real-time health metrics,
performance tracking, and predictive analysis for AI training clusters.

Features:
- Real-time CPU, memory, GPU utilization monitoring
- Network bandwidth and I/O performance tracking
- Temperature and power consumption analysis
- Cluster-wide resource coordination
- Predictive failure detection
- Performance bottleneck identification
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
import psutil
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta


@dataclass
class NodeMetrics:
    """System metrics for a single node/server"""
    node_id: str
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    gpu_utilization: Optional[float] = None
    gpu_memory_percent: Optional[float] = None
    gpu_temperature: Optional[float] = None
    gpu_power_watts: Optional[float] = None
    load_average: Optional[Tuple[float, float, float]] = None
    process_count: Optional[int] = None


@dataclass
class ClusterHealthStatus:
    """Overall cluster health assessment"""
    status: str  # "healthy", "warning", "critical"
    total_nodes: int
    healthy_nodes: int
    warning_nodes: int
    critical_nodes: int
    avg_cpu_utilization: float
    avg_memory_utilization: float
    avg_gpu_utilization: float
    network_throughput_gbps: float
    alerts: List[str]
    recommendations: List[str]


class SystemHealthMonitor:
    """Real-time system health monitoring with predictive analytics"""

    def __init__(self, node_id: str = None, collection_interval: float = 5.0):
        self.node_id = node_id or f"node_{int(time.time())}"
        self.collection_interval = collection_interval
        self.metrics_history = deque(maxlen=2000)  # ~2.7 hours at 5s intervals
        self.is_monitoring = False
        self.monitoring_thread = None
        self.gpu_available = self._check_gpu_availability()
        self.baseline_metrics = None
        self.anomaly_threshold = 2.0  # Standard deviations for anomaly detection

    def _check_gpu_availability(self) -> bool:
        """Check if GPU monitoring is available"""
        try:
            import GPUtil
            return len(GPUtil.getGPUs()) > 0
        except ImportError:
            return False

    def _collect_gpu_metrics(self) -> Dict[str, Optional[float]]:
        """Collect GPU utilization metrics"""
        if not self.gpu_available:
            return {
                'gpu_utilization': None,
                'gpu_memory_percent': None,
                'gpu_temperature': None,
                'gpu_power_watts': None
            }

        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Primary GPU
                return {
                    'gpu_utilization': gpu.load * 100,
                    'gpu_memory_percent': gpu.memoryUtil * 100,
                    'gpu_temperature': gpu.temperature,
                    'gpu_power_watts': getattr(gpu, 'power', None)
                }
        except Exception:
            pass

        return {
            'gpu_utilization': None,
            'gpu_memory_percent': None,
            'gpu_temperature': None,
            'gpu_power_watts': None
        }

    def collect_metrics(self) -> NodeMetrics:
        """Collect current system metrics"""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        # Network I/O
        network = psutil.net_io_counters()

        # System load and processes
        load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        process_count = len(psutil.pids())

        # GPU metrics
        gpu_metrics = self._collect_gpu_metrics()

        return NodeMetrics(
            node_id=self.node_id,
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available_gb=memory.available / (1024**3),
            disk_usage_percent=disk.percent,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            load_average=load_avg,
            process_count=process_count,
            **gpu_metrics
        )

    def start_monitoring(self):
        """Start continuous monitoring in background thread"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)

                # Establish baseline after collecting enough data
                if len(self.metrics_history) >= 20 and self.baseline_metrics is None:
                    self._establish_baseline()

                time.sleep(self.collection_interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(self.collection_interval)

    def _establish_baseline(self):
        """Establish baseline metrics for anomaly detection"""
        if len(self.metrics_history) < 20:
            return

        recent_metrics = list(self.metrics_history)[-20:]

        self.baseline_metrics = {
            'cpu_mean': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'cpu_std': self._calculate_std([m.cpu_percent for m in recent_metrics]),
            'memory_mean': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            'memory_std': self._calculate_std([m.memory_percent for m in recent_metrics]),
        }

        if recent_metrics[0].gpu_utilization is not None:
            gpu_utils = [m.gpu_utilization for m in recent_metrics if m.gpu_utilization is not None]
            if gpu_utils:
                self.baseline_metrics.update({
                    'gpu_mean': sum(gpu_utils) / len(gpu_utils),
                    'gpu_std': self._calculate_std(gpu_utils)
                })

    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

    def detect_anomalies(self) -> List[str]:
        """Detect system anomalies based on baseline"""
        if not self.metrics_history or not self.baseline_metrics:
            return []

        current = self.metrics_history[-1]
        anomalies = []

        # CPU anomaly
        cpu_z_score = abs(current.cpu_percent - self.baseline_metrics['cpu_mean']) / max(self.baseline_metrics['cpu_std'], 1.0)
        if cpu_z_score > self.anomaly_threshold:
            anomalies.append(f"CPU anomaly: {current.cpu_percent:.1f}% (baseline: {self.baseline_metrics['cpu_mean']:.1f}%)")

        # Memory anomaly
        mem_z_score = abs(current.memory_percent - self.baseline_metrics['memory_mean']) / max(self.baseline_metrics['memory_std'], 1.0)
        if mem_z_score > self.anomaly_threshold:
            anomalies.append(f"Memory anomaly: {current.memory_percent:.1f}% (baseline: {self.baseline_metrics['memory_mean']:.1f}%)")

        # GPU anomaly
        if current.gpu_utilization is not None and 'gpu_mean' in self.baseline_metrics:
            gpu_z_score = abs(current.gpu_utilization - self.baseline_metrics['gpu_mean']) / max(self.baseline_metrics['gpu_std'], 1.0)
            if gpu_z_score > self.anomaly_threshold:
                anomalies.append(f"GPU anomaly: {current.gpu_utilization:.1f}% (baseline: {self.baseline_metrics['gpu_mean']:.1f}%)")

        return anomalies

    def get_health_status(self) -> str:
        """Get current node health status"""
        if not self.metrics_history:
            return "unknown"

        current = self.metrics_history[-1]

        # Critical conditions
        if (current.cpu_percent > 95 or
            current.memory_percent > 95 or
            current.disk_usage_percent > 95 or
            (current.gpu_temperature is not None and current.gpu_temperature > 85)):
            return "critical"

        # Warning conditions
        if (current.cpu_percent > 80 or
            current.memory_percent > 80 or
            current.disk_usage_percent > 85 or
            (current.gpu_temperature is not None and current.gpu_temperature > 75)):
            return "warning"

        return "healthy"

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive system health report"""
        if not self.metrics_history:
            return {"error": "No metrics available"}

        current = self.metrics_history[-1]
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 readings

        return {
            "node_id": self.node_id,
            "timestamp": current.timestamp,
            "health_status": self.get_health_status(),
            "current_metrics": asdict(current),
            "averages_last_10": {
                "cpu_percent": sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
                "memory_percent": sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
                "gpu_utilization": (sum(m.gpu_utilization for m in recent_metrics if m.gpu_utilization is not None) /
                                  len([m for m in recent_metrics if m.gpu_utilization is not None])) if any(m.gpu_utilization is not None for m in recent_metrics) else None
            },
            "anomalies": self.detect_anomalies(),
            "total_samples": len(self.metrics_history)
        }


class ClusterMonitor:
    """Multi-node cluster monitoring and coordination"""

    def __init__(self):
        self.nodes: Dict[str, SystemHealthMonitor] = {}
        self.cluster_metrics = deque(maxlen=1000)
        self.alert_thresholds = {
            'cpu_critical': 90.0,
            'memory_critical': 90.0,
            'gpu_critical': 95.0,
            'temperature_critical': 85.0,
            'unhealthy_nodes_threshold': 0.2  # 20% of nodes
        }

    def add_node(self, node_id: str, monitor: SystemHealthMonitor):
        """Add node to cluster monitoring"""
        self.nodes[node_id] = monitor

    def remove_node(self, node_id: str):
        """Remove node from monitoring"""
        if node_id in self.nodes:
            self.nodes[node_id].stop_monitoring()
            del self.nodes[node_id]

    def get_cluster_health(self) -> ClusterHealthStatus:
        """Get overall cluster health status"""
        if not self.nodes:
            return ClusterHealthStatus(
                status="unknown",
                total_nodes=0,
                healthy_nodes=0,
                warning_nodes=0,
                critical_nodes=0,
                avg_cpu_utilization=0.0,
                avg_memory_utilization=0.0,
                avg_gpu_utilization=0.0,
                network_throughput_gbps=0.0,
                alerts=[],
                recommendations=[]
            )

        node_statuses = {}
        cpu_utils = []
        memory_utils = []
        gpu_utils = []
        alerts = []

        for node_id, monitor in self.nodes.items():
            status = monitor.get_health_status()
            node_statuses[node_id] = status

            if monitor.metrics_history:
                current = monitor.metrics_history[-1]
                cpu_utils.append(current.cpu_percent)
                memory_utils.append(current.memory_percent)

                if current.gpu_utilization is not None:
                    gpu_utils.append(current.gpu_utilization)

                # Check for critical conditions
                if current.cpu_percent > self.alert_thresholds['cpu_critical']:
                    alerts.append(f"Node {node_id}: Critical CPU usage ({current.cpu_percent:.1f}%)")

                if current.memory_percent > self.alert_thresholds['memory_critical']:
                    alerts.append(f"Node {node_id}: Critical memory usage ({current.memory_percent:.1f}%)")

                if (current.gpu_utilization is not None and
                    current.gpu_utilization > self.alert_thresholds['gpu_critical']):
                    alerts.append(f"Node {node_id}: Critical GPU usage ({current.gpu_utilization:.1f}%)")

                if (current.gpu_temperature is not None and
                    current.gpu_temperature > self.alert_thresholds['temperature_critical']):
                    alerts.append(f"Node {node_id}: Critical GPU temperature ({current.gpu_temperature:.1f}°C)")

        # Count node statuses
        status_counts = {"healthy": 0, "warning": 0, "critical": 0}
        for status in node_statuses.values():
            status_counts[status] = status_counts.get(status, 0) + 1

        # Determine overall cluster status
        total_nodes = len(self.nodes)
        unhealthy_ratio = (status_counts["warning"] + status_counts["critical"]) / total_nodes

        if status_counts["critical"] > 0 or unhealthy_ratio > self.alert_thresholds['unhealthy_nodes_threshold']:
            cluster_status = "critical"
        elif status_counts["warning"] > 0:
            cluster_status = "warning"
        else:
            cluster_status = "healthy"

        # Generate recommendations
        recommendations = []
        if unhealthy_ratio > 0.1:  # More than 10% nodes unhealthy
            recommendations.append("Consider redistributing workload across healthier nodes")
        if cpu_utils and sum(cpu_utils) / len(cpu_utils) > 85:
            recommendations.append("High cluster CPU utilization - consider scaling out")
        if memory_utils and sum(memory_utils) / len(memory_utils) > 85:
            recommendations.append("High memory pressure detected - monitor for OOM conditions")

        return ClusterHealthStatus(
            status=cluster_status,
            total_nodes=total_nodes,
            healthy_nodes=status_counts["healthy"],
            warning_nodes=status_counts["warning"],
            critical_nodes=status_counts["critical"],
            avg_cpu_utilization=sum(cpu_utils) / len(cpu_utils) if cpu_utils else 0.0,
            avg_memory_utilization=sum(memory_utils) / len(memory_utils) if memory_utils else 0.0,
            avg_gpu_utilization=sum(gpu_utils) / len(gpu_utils) if gpu_utils else 0.0,
            network_throughput_gbps=0.0,  # Would need network monitoring
            alerts=alerts,
            recommendations=recommendations
        )

    def start_cluster_monitoring(self):
        """Start monitoring all nodes in cluster"""
        for monitor in self.nodes.values():
            monitor.start_monitoring()

    def stop_cluster_monitoring(self):
        """Stop monitoring all nodes"""
        for monitor in self.nodes.values():
            monitor.stop_monitoring()

    def export_cluster_metrics(self) -> Dict[str, Any]:
        """Export comprehensive cluster metrics"""
        cluster_health = self.get_cluster_health()

        node_reports = {}
        for node_id, monitor in self.nodes.items():
            node_reports[node_id] = monitor.generate_report()

        return {
            "cluster_overview": asdict(cluster_health),
            "node_details": node_reports,
            "collection_timestamp": time.time(),
            "monitoring_duration": "Real-time continuous monitoring"
        }