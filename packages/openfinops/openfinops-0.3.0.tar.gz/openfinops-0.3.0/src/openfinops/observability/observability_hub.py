"""
Unified Observability Hub for AI Training Infrastructure
======================================================

Central observability platform that provides comprehensive monitoring,
alerting, and visualization for distributed AI training environments.
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



import time
import json
import threading
import random
from typing import Dict, List, Optional, Any, Tuple, Union
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

# Import persistence layer
try:
    from .persistence import (
        BasePersistenceBackend,
        PersistenceConfig,
        StorageBackend,
        create_persistence_backend
    )
    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False

# Import OpenFinOps integration for professional visualizations
try:
    from .vizly_chart_integration import OpenFinOpsObservabilityRenderer, ObservabilityVisualization
    VIZLYCHART_INTEGRATION_AVAILABLE = True
except ImportError:
    VIZLYCHART_INTEGRATION_AVAILABLE = False

# Import LLM observability components
try:
    from .llm_observability import LLMObservabilityHub
    from .llm_dashboards import LLMDashboardCreator
    LLM_OBSERVABILITY_AVAILABLE = True
except ImportError:
    LLM_OBSERVABILITY_AVAILABLE = False


class SystemHealth(Enum):
    """System health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class SystemMetrics:
    """Comprehensive system metrics for observability."""
    timestamp: float
    cpu_usage: float  # Percentage
    memory_usage: float  # Percentage
    disk_usage: float  # Percentage

    # Optional identifier fields
    cluster_id: str = "default"
    node_id: str = "default"

    # Resource Utilization (optional)
    gpu_usage: float = 0.0  # Percentage
    network_io: Any = None  # MB/s or dict
    active_connections: int = 0  # For test compatibility
    error_count: int = 0  # For test compatibility
    warning_count: int = 0  # For test compatibility

    # Performance Metrics (optional)
    throughput: float = 0.0  # Operations/second
    latency_p50: float = 0.0  # Milliseconds
    latency_p95: float = 0.0  # Milliseconds
    latency_p99: float = 0.0  # Milliseconds
    error_rate: float = 0.0  # Percentage

    # Training Specific (optional)
    training_active: bool = False
    model_loading: bool = False
    data_loading: bool = False
    gradient_sync: bool = False
    checkpoint_saving: bool = False

    # Health Indicators (optional)
    temperature: float = 0.0  # Celsius
    power_consumption: float = 0.0  # Watts
    fan_speed: float = 0.0  # RPM
    health_status: SystemHealth = SystemHealth.HEALTHY

    # Cost Metrics (optional)
    cost_per_hour: float = 0.0
    estimated_daily_cost: float = 0.0


@dataclass
class ServiceMetrics:
    """Service-level observability metrics."""
    service_name: str
    timestamp: float

    # Service Health
    status: str
    uptime: float  # Seconds
    restart_count: int

    # Performance
    request_rate: float  # Requests/second
    response_time: float  # Milliseconds
    success_rate: float  # Percentage

    # Resources
    cpu_limit: float
    memory_limit: float
    cpu_request: float
    memory_request: float

    # Dependencies
    dependency_health: Dict[str, str]

    # Training Specific
    training_jobs_active: int
    training_jobs_queued: int
    training_jobs_failed: int


class ObservabilityHub:
    """
    Central hub for AI training infrastructure observability.
    Provides unified monitoring, alerting, and visualization.

    Args:
        persistence_config: Optional persistence configuration for historical data storage
    """

    def __init__(self, persistence_config: Optional['PersistenceConfig'] = None):
        # In-memory storage (for fast recent access)
        self.system_metrics = deque(maxlen=10000)
        self.service_metrics = defaultdict(lambda: deque(maxlen=5000))
        self.alerts = deque(maxlen=1000)
        self.incidents = []

        self.clusters = {}
        self.services = {}
        self.dependencies = {}

        # Real-time monitoring
        self.monitoring_active = False
        self.monitor_thread = None

        # Thresholds and rules
        self.alert_rules = self._initialize_alert_rules()
        self.cost_budgets = {}

        # Persistence layer for historical data
        self.persistence_backend: Optional[BasePersistenceBackend] = None
        if PERSISTENCE_AVAILABLE and persistence_config:
            self.persistence_backend = create_persistence_backend(persistence_config)
            self.persistence_backend.start_auto_flush()

    def register_cluster(self, cluster_id: str, nodes: List[str], region: str = "us-east-1"):
        """Register a training cluster for monitoring."""
        self.clusters[cluster_id] = {
            'nodes': nodes,
            'region': region,
            'registered_at': time.time(),
            'status': SystemHealth.HEALTHY,
            'total_nodes': len(nodes),
            'active_nodes': 0
        }

    def register_service(self, service_name: str, cluster_id: str, dependencies: List[str] = None):
        """Register a service for monitoring."""
        self.services[service_name] = {
            'cluster_id': cluster_id,
            'dependencies': dependencies or [],
            'registered_at': time.time(),
            'status': 'unknown'
        }

        # Track dependencies
        for dep in (dependencies or []):
            if dep not in self.dependencies:
                self.dependencies[dep] = set()
            self.dependencies[dep].add(service_name)

    def collect_system_metrics(self, metrics: SystemMetrics):
        """Collect system-level metrics from nodes."""
        # Store in memory for fast access
        self.system_metrics.append(metrics)

        # Store in persistent backend for historical analysis
        if self.persistence_backend:
            metrics_dict = asdict(metrics)
            # Convert enum to string
            if 'health_status' in metrics_dict and hasattr(metrics_dict['health_status'], 'value'):
                metrics_dict['health_status'] = metrics_dict['health_status'].value
            self.persistence_backend.store_system_metric(metrics_dict)

        # Update cluster status
        if metrics.cluster_id in self.clusters:
            cluster = self.clusters[metrics.cluster_id]
            if metrics.health_status != SystemHealth.DOWN:
                cluster['active_nodes'] = cluster.get('active_nodes', 0) + 1

        # Check alert conditions
        self._check_system_alerts(metrics)

    def collect_service_metrics(self, metrics: ServiceMetrics):
        """Collect service-level metrics."""
        # Store in memory for fast access
        self.service_metrics[metrics.service_name].append(metrics)

        # Store in persistent backend for historical analysis
        if self.persistence_backend:
            metrics_dict = asdict(metrics)
            self.persistence_backend.store_service_metric(metrics_dict)

        # Update service status
        if metrics.service_name in self.services:
            self.services[metrics.service_name]['status'] = metrics.status

        # Check service alerts
        self._check_service_alerts(metrics)

    def _initialize_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize default alerting rules."""
        return {
            'high_cpu_usage': {
                'threshold': 90.0,
                'duration': 300,  # 5 minutes
                'severity': AlertSeverity.WARNING,
                'description': 'High CPU usage detected'
            },
            'high_memory_usage': {
                'threshold': 85.0,
                'duration': 180,  # 3 minutes
                'severity': AlertSeverity.CRITICAL,
                'description': 'High memory usage detected'
            },
            'gpu_overheating': {
                'threshold': 85.0,  # Celsius
                'duration': 60,
                'severity': AlertSeverity.CRITICAL,
                'description': 'GPU overheating detected'
            },
            'high_error_rate': {
                'threshold': 5.0,  # Percentage
                'duration': 120,
                'severity': AlertSeverity.CRITICAL,
                'description': 'High error rate detected'
            },
            'service_down': {
                'threshold': 0,
                'duration': 30,
                'severity': AlertSeverity.EMERGENCY,
                'description': 'Service is down'
            },
            'training_stall': {
                'threshold': 300,  # 5 minutes without progress
                'duration': 300,
                'severity': AlertSeverity.WARNING,
                'description': 'Training appears to be stalled'
            },
            'cost_budget_exceeded': {
                'threshold': 100.0,  # Percentage of budget
                'duration': 0,
                'severity': AlertSeverity.WARNING,
                'description': 'Cost budget threshold exceeded'
            }
        }

    def _check_system_alerts(self, metrics: SystemMetrics):
        """Check system metrics against alert rules."""
        alerts_triggered = []

        # CPU usage alert
        if metrics.cpu_usage > self.alert_rules['high_cpu_usage']['threshold']:
            alerts_triggered.append(('high_cpu_usage', metrics.cpu_usage))

        # Memory usage alert
        if metrics.memory_usage > self.alert_rules['high_memory_usage']['threshold']:
            alerts_triggered.append(('high_memory_usage', metrics.memory_usage))

        # GPU temperature alert
        if metrics.temperature > self.alert_rules['gpu_overheating']['threshold']:
            alerts_triggered.append(('gpu_overheating', metrics.temperature))

        # Error rate alert
        if metrics.error_rate > self.alert_rules['high_error_rate']['threshold']:
            alerts_triggered.append(('high_error_rate', metrics.error_rate))

        # Process alerts
        for alert_type, value in alerts_triggered:
            self._trigger_alert(alert_type, metrics.cluster_id, metrics.node_id, value)

    def _check_service_alerts(self, metrics: ServiceMetrics):
        """Check service metrics against alert rules."""
        # Service down alert
        if metrics.status == 'down':
            self._trigger_alert('service_down', '', metrics.service_name, 0)

        # High error rate for services
        error_rate = 100.0 - metrics.success_rate
        if error_rate > self.alert_rules['high_error_rate']['threshold']:
            self._trigger_alert('high_error_rate', '', metrics.service_name, error_rate)

    def _trigger_alert(self, alert_type: str, cluster_id: str, resource_id: str, value: float):
        """Trigger an alert with proper context."""
        rule = self.alert_rules.get(alert_type, {})

        alert = {
            'timestamp': time.time(),
            'type': alert_type,
            'severity': rule.get('severity', AlertSeverity.WARNING).value,
            'cluster_id': cluster_id,
            'resource_id': resource_id,
            'value': value,
            'threshold': rule.get('threshold', 0),
            'description': rule.get('description', 'Alert triggered'),
            'acknowledged': False,
            'resolved': False
        }

        self.alerts.append(alert)

    def get_cluster_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive cluster health summary."""
        if not self.system_metrics:
            return {'status': 'no_data'}

        # Aggregate metrics by cluster
        cluster_stats = defaultdict(list)
        for metrics in list(self.system_metrics)[-1000:]:  # Last 1000 metrics
            cluster_stats[metrics.cluster_id].append(metrics)

        cluster_health = {}
        for cluster_id, metrics_list in cluster_stats.items():
            if not metrics_list:
                continue

            recent_metrics = metrics_list[-10:]  # Last 10 metrics per cluster

            cluster_health[cluster_id] = {
                'status': self._calculate_cluster_health(recent_metrics),
                'nodes_total': len(set(m.node_id for m in metrics_list)),
                'nodes_healthy': len([m for m in recent_metrics if m.health_status == SystemHealth.HEALTHY]),
                'avg_cpu_usage': np.mean([m.cpu_usage for m in recent_metrics]),
                'avg_memory_usage': np.mean([m.memory_usage for m in recent_metrics]),
                'avg_gpu_usage': np.mean([m.gpu_usage for m in recent_metrics]),
                'total_throughput': sum(m.throughput for m in recent_metrics),
                'avg_latency_p95': np.mean([m.latency_p95 for m in recent_metrics]),
                'total_power': sum(m.power_consumption for m in recent_metrics),
                'estimated_hourly_cost': sum(m.cost_per_hour for m in recent_metrics),
                'active_training_jobs': len([m for m in recent_metrics if m.training_active])
            }

        return {
            'clusters': cluster_health,
            'total_alerts': len([a for a in self.alerts if not a['resolved']]),
            'critical_alerts': len([a for a in self.alerts if a['severity'] == 'critical' and not a['resolved']]),
            'summary_timestamp': time.time()
        }

    def _calculate_cluster_health(self, metrics_list: List[SystemMetrics]) -> str:
        """Calculate overall cluster health status."""
        if not metrics_list:
            return SystemHealth.DOWN.value

        health_scores = []
        for metrics in metrics_list:
            score = 100

            # Penalize high resource usage
            if metrics.cpu_usage > 90:
                score -= 30
            elif metrics.cpu_usage > 80:
                score -= 15

            if metrics.memory_usage > 90:
                score -= 30
            elif metrics.memory_usage > 80:
                score -= 15

            # Penalize high error rates
            if metrics.error_rate > 5:
                score -= 40
            elif metrics.error_rate > 1:
                score -= 20

            # Penalize high temperatures
            if metrics.temperature > 85:
                score -= 25
            elif metrics.temperature > 80:
                score -= 10

            # Factor in system health status
            if metrics.health_status == SystemHealth.DOWN:
                score = 0
            elif metrics.health_status == SystemHealth.CRITICAL:
                score = min(score, 40)
            elif metrics.health_status == SystemHealth.WARNING:
                score = min(score, 70)

            health_scores.append(max(0, score))

        avg_score = np.mean(health_scores)

        if avg_score >= 80:
            return SystemHealth.HEALTHY.value
        elif avg_score >= 60:
            return SystemHealth.WARNING.value
        elif avg_score >= 20:
            return SystemHealth.CRITICAL.value
        else:
            return SystemHealth.DOWN.value

    def get_service_dependency_map(self) -> Dict[str, Any]:
        """Generate service dependency visualization data."""
        nodes = []
        edges = []

        # Create nodes for each service
        for service_name, service_info in self.services.items():
            # Get latest metrics
            service_metrics_list = list(self.service_metrics.get(service_name, []))
            latest_metrics = service_metrics_list[-1] if service_metrics_list else None

            status = latest_metrics.status if latest_metrics else 'unknown'

            nodes.append({
                'id': service_name,
                'label': service_name,
                'status': status,
                'cluster': service_info.get('cluster_id', 'unknown'),
                'type': 'service'
            })

        # Create edges for dependencies
        edge_id = 0
        for service_name, service_info in self.services.items():
            for dependency in service_info.get('dependencies', []):
                edges.append({
                    'id': edge_id,
                    'source': dependency,
                    'target': service_name,
                    'type': 'dependency'
                })
                edge_id += 1

        return {
            'nodes': nodes,
            'edges': edges,
            'timestamp': time.time()
        }

    def query_historical_metrics(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        cluster_id: Optional[str] = None,
        node_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query historical system metrics from persistence layer.

        Args:
            start_time: Start timestamp (unix time)
            end_time: End timestamp (unix time)
            cluster_id: Filter by cluster ID
            node_id: Filter by node ID
            limit: Maximum number of results

        Returns:
            List of historical metrics
        """
        if not self.persistence_backend:
            # Fallback to in-memory data if persistence not available
            results = []
            for metric in list(self.system_metrics):
                metric_dict = asdict(metric) if hasattr(metric, '__dataclass_fields__') else metric
                if start_time and metric_dict.get('timestamp', 0) < start_time:
                    continue
                if end_time and metric_dict.get('timestamp', 0) > end_time:
                    continue
                if cluster_id and metric_dict.get('cluster_id') != cluster_id:
                    continue
                if node_id and metric_dict.get('node_id') != node_id:
                    continue
                results.append(metric_dict)
            return results[-limit:]

        return self.persistence_backend.query_system_metrics(
            start_time=start_time,
            end_time=end_time,
            cluster_id=cluster_id,
            node_id=node_id,
            limit=limit
        )

    def cleanup_old_data(self):
        """Remove old data based on retention policy."""
        if self.persistence_backend:
            self.persistence_backend.cleanup_old_data()

    def close(self):
        """Cleanup and close connections."""
        if self.persistence_backend:
            self.persistence_backend.stop_auto_flush()
            self.persistence_backend.close()


class UnifiedDashboard:
    """
    Unified observability dashboard with comprehensive system visualization.
    """

    def __init__(self, observability_hub: ObservabilityHub):
        self.hub = observability_hub
        # Initialize OpenFinOps renderer if available
        if VIZLYCHART_INTEGRATION_AVAILABLE:
            self.viz_renderer = OpenFinOpsObservabilityRenderer(theme="professional")
            self.viz = ObservabilityVisualization(theme="professional")
        else:
            self.viz_renderer = None
            self.viz = None

        # Initialize LLM observability components
        if LLM_OBSERVABILITY_AVAILABLE:
            self.llm_hub = LLMObservabilityHub()
            self.llm_dashboard_creator = LLMDashboardCreator(self.llm_hub)
        else:
            self.llm_hub = None
            self.llm_dashboard_creator = None

    def create_observability_dashboard(self) -> str:
        """Create comprehensive observability dashboard with OpenFinOps visualizations."""
        # If OpenFinOps integration is available, use professional rendering
        if self.viz_renderer:
            return self._create_openfinops_dashboard()
        else:
            return self._create_fallback_dashboard()

    def _create_openfinops_dashboard(self) -> str:
        """Create dashboard using OpenFinOps professional rendering."""
        # Prepare data for OpenFinOps visualization
        observability_data = {
            'system_metrics': self._prepare_system_metrics_data(),
            'performance_metrics': self._prepare_performance_data(),
            'cost_data': self._prepare_cost_data(),
            'services': self._prepare_services_data(),
            'dependencies': self._prepare_dependencies_data(),
            'alerts': self._prepare_alerts_data(),
            'training_metrics': self._prepare_training_metrics_data()
        }

        # Generate professional charts using OpenFinOps
        charts = {}

        # System Health Chart
        if observability_data['system_metrics']:
            charts["System Health Monitoring"] = self.viz.create_system_health_chart(
                observability_data['system_metrics'],
                width=800, height=400
            )

        # Performance Metrics Chart
        if observability_data['performance_metrics']:
            charts["Performance Analytics"] = self.viz.create_performance_metrics_chart(
                observability_data['performance_metrics'],
                width=800, height=400
            )

        # Cost Analysis Chart
        if observability_data['cost_data']:
            charts["Cost Optimization"] = self.viz.create_cost_analysis_chart(
                observability_data['cost_data'],
                width=800, height=400
            )

        # Service Dependencies
        if observability_data['services']:
            charts["Service Dependencies"] = self.viz.create_service_dependency_chart(
                observability_data['services'],
                observability_data['dependencies'],
                width=800, height=600
            )

        # Alert Timeline
        if observability_data['alerts']:
            charts["Alert Timeline"] = self.viz.create_alert_timeline_chart(
                observability_data['alerts'],
                width=800, height=300
            )

        # Training Metrics
        if observability_data['training_metrics']:
            charts["AI Training Metrics"] = self.viz.create_training_metrics_chart(
                observability_data['training_metrics'],
                width=800, height=400
            )

        # Generate the complete dashboard HTML with OpenFinOps visualizations
        return self.viz.create_interactive_dashboard_html(
            charts,
            title="OpenFinOps Enterprise Observability Platform"
        )

    def _prepare_system_metrics_data(self) -> List[Dict[str, Any]]:
        """Prepare system metrics data for OpenFinOps visualization."""
        metrics_data = []

        # Get recent system metrics
        recent_metrics = list(self.hub.system_metrics)[-100:]  # Last 100 data points

        for metric in recent_metrics:
            metrics_data.append({
                'timestamp': metric.timestamp,
                'node_id': metric.node_id,
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'gpu_usage': getattr(metric, 'gpu_usage', None),
                'disk_usage': getattr(metric, 'disk_usage', 0),
                'network_io': getattr(metric, 'network_io', 0)
            })

        return metrics_data

    def _prepare_performance_data(self) -> List[Dict[str, Any]]:
        """Prepare performance metrics data for OpenFinOps."""
        performance_data = []

        # Extract performance data from system metrics
        recent_metrics = list(self.hub.system_metrics)[-50:]

        for metric in recent_metrics:
            performance_data.append({
                'timestamp': metric.timestamp,
                'throughput': getattr(metric, 'throughput', random.uniform(1000, 3000)),
                'response_time': getattr(metric, 'latency_p50', random.uniform(10, 50)),
                'error_rate': getattr(metric, 'error_rate', random.uniform(0.1, 2.0))
            })

        return performance_data

    def _prepare_cost_data(self) -> Dict[str, float]:
        """Prepare cost analysis data for OpenFinOps."""
        return {
            'Compute': 15000,
            'Storage': 3500,
            'Network': 1200,
            'GPU': 25000,
            'Support': 2000
        }

    def _prepare_services_data(self) -> List[Dict[str, Any]]:
        """Prepare services data for dependency visualization."""
        services = []
        for cluster_id in self.hub.clusters.keys():
            services.append({
                'id': f"cluster-{cluster_id}",
                'name': f"Cluster {cluster_id}",
                'health': 'healthy',
                'type': 'compute'
            })

        # Add some example services
        example_services = [
            {'id': 'api-gateway', 'name': 'API Gateway', 'health': 'healthy', 'type': 'gateway'},
            {'id': 'training-service', 'name': 'Training Service', 'health': 'warning', 'type': 'compute'},
            {'id': 'data-pipeline', 'name': 'Data Pipeline', 'health': 'healthy', 'type': 'data'},
            {'id': 'monitoring', 'name': 'Monitoring', 'health': 'healthy', 'type': 'monitoring'}
        ]
        services.extend(example_services)

        return services

    def _prepare_dependencies_data(self) -> List[Dict[str, Any]]:
        """Prepare service dependencies data."""
        return [
            {'source': 'api-gateway', 'target': 'training-service', 'strength': 0.8},
            {'source': 'training-service', 'target': 'data-pipeline', 'strength': 0.9},
            {'source': 'monitoring', 'target': 'training-service', 'strength': 0.6}
        ]

    def _prepare_alerts_data(self) -> List[Dict[str, Any]]:
        """Prepare alerts data for timeline visualization."""
        alerts_data = []
        current_time = time.time()

        # Sample alerts from recent activity
        for i, alert in enumerate(list(self.hub.alerts)[-20:]):
            # Handle both dictionary and object formats
            if isinstance(alert, dict):
                severity = alert.get('severity', 'unknown')
                if hasattr(severity, 'value'):
                    severity = severity.value
                else:
                    severity = str(severity)
                message = alert.get('message', 'No message')
                cluster_id = alert.get('cluster_id', 'unknown')
                timestamp = alert.get('timestamp', current_time - (i * 300))
            else:
                severity = getattr(alert, 'severity', 'unknown')
                if hasattr(severity, 'value'):
                    severity = severity.value
                else:
                    severity = str(severity)
                message = getattr(alert, 'message', 'No message')
                cluster_id = getattr(alert, 'cluster_id', 'unknown')
                timestamp = getattr(alert, 'timestamp', current_time - (i * 300))

            alerts_data.append({
                'timestamp': timestamp,
                'severity': severity,
                'message': message,
                'cluster_id': cluster_id
            })

        return alerts_data

    def _prepare_training_metrics_data(self) -> List[Dict[str, Any]]:
        """Prepare AI training metrics data."""
        training_data = []

        # Generate sample training progression
        for step in range(0, 1000, 50):
            loss = 2.5 * (0.95 ** (step / 100))  # Decreasing loss
            accuracy = min(0.95, 0.3 + (step / 1000) * 0.65)  # Increasing accuracy

            training_data.append({
                'step': step,
                'loss': loss,
                'accuracy': accuracy,
                'learning_rate': 0.001 * (0.9 ** (step / 200))
            })

        return training_data

    def _create_fallback_dashboard(self) -> str:
        """Create fallback dashboard when OpenFinOps is not available."""
        cluster_health = self.hub.get_cluster_health_summary()
        dependency_map = self.hub.get_service_dependency_map()
        recent_alerts = list(self.hub.alerts)[-20:]  # Last 20 alerts

        dashboard_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 AI Training Observability Dashboard - OpenFinOps</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0c1015 0%, #1a1f2e 50%, #2d1b2e 100%);
            color: #ffffff;
            min-height: 100vh;
            overflow-x: auto;
        }}

        .dashboard-container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(15px);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00d4aa, #00a8ff, #0078ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .status-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0, 212, 170, 0.1);
            padding: 20px;
            border-radius: 15px;
            border-left: 4px solid #00d4aa;
            margin-bottom: 30px;
        }}

        .status-indicator {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .pulse-dot {{
            width: 14px;
            height: 14px;
            background: #00d4aa;
            border-radius: 50%;
            animation: pulse 2s infinite;
            box-shadow: 0 0 20px rgba(0, 212, 170, 0.5);
        }}

        @keyframes pulse {{
            0% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.2); opacity: 0.7; }}
            100% {{ transform: scale(1); opacity: 1; }}
        }}

        .overview-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}

        .overview-card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 30px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }}

        .overview-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #00d4aa, #00a8ff);
            opacity: 0.8;
        }}

        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}

        .card-icon {{
            font-size: 2em;
            margin-right: 15px;
        }}

        .card-title {{
            font-size: 1.3em;
            font-weight: 600;
            color: #e1f5fe;
        }}

        .card-value {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .card-subtitle {{
            font-size: 0.95em;
            color: #b0bec5;
            opacity: 0.8;
        }}

        .clusters-section {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .section-title {{
            font-size: 1.5em;
            font-weight: 600;
            margin-bottom: 25px;
            color: #e1f5fe;
            display: flex;
            align-items: center;
            gap: 15px;
        }}

        .clusters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
        }}

        .cluster-card {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: all 0.3s ease;
        }}

        .cluster-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
        }}

        .cluster-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}

        .cluster-name {{
            font-size: 1.2em;
            font-weight: 600;
        }}

        .cluster-status {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .status-healthy {{
            background: rgba(76, 175, 80, 0.2);
            color: #4caf50;
            border: 1px solid #4caf50;
        }}

        .status-warning {{
            background: rgba(255, 152, 0, 0.2);
            color: #ff9800;
            border: 1px solid #ff9800;
        }}

        .status-critical {{
            background: rgba(244, 67, 54, 0.2);
            color: #f44336;
            border: 1px solid #f44336;
        }}

        .cluster-metrics {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}

        .metric-item {{
            text-align: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 10px;
        }}

        .metric-value {{
            font-size: 1.4em;
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .metric-label {{
            font-size: 0.8em;
            color: #b0bec5;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .alerts-section {{
            background: rgba(255, 152, 0, 0.05);
            border-radius: 20px;
            padding: 30px;
            border-left: 4px solid #ff9800;
            margin-bottom: 30px;
        }}

        .alerts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .alert-card {{
            background: rgba(0, 0, 0, 0.2);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ff9800;
        }}

        .alert-critical {{
            border-left-color: #f44336;
            background: rgba(244, 67, 54, 0.05);
        }}

        .alert-warning {{
            border-left-color: #ff9800;
            background: rgba(255, 152, 0, 0.05);
        }}

        .alert-info {{
            border-left-color: #2196f3;
            background: rgba(33, 150, 243, 0.05);
        }}

        .alert-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .alert-severity {{
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .service-map-section {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
        }}

        .service-graph {{
            min-height: 400px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 15px;
            padding: 20px;
            position: relative;
        }}

        .performance-charts {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        .chart-panel {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 20px;
            padding: 25px;
        }}

        .chart-container {{
            background: rgba(0, 0, 0, 0.2);
            border-radius: 15px;
            padding: 20px;
            min-height: 300px;
        }}

        .live-metrics {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.8);
            padding: 15px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            z-index: 1000;
        }}

        .refresh-indicator {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.8em;
            color: #b0bec5;
        }}

        @media (max-width: 768px) {{
            .clusters-grid, .overview-grid, .performance-charts {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>🔍 AI Training Observability Dashboard</h1>
            <p>Enterprise Infrastructure Monitoring & Analytics</p>
        </div>

        <div class="live-metrics">
            <div class="refresh-indicator">
                <div class="pulse-dot" style="width: 8px; height: 8px;"></div>
                <span>Live Monitoring Active</span>
            </div>
            <div style="font-size: 0.75em; margin-top: 5px;">
                Last Update: <span id="lastUpdate">{time.strftime('%H:%M:%S')}</span>
            </div>
        </div>

        <div class="status-bar">
            <div class="status-indicator">
                <div class="pulse-dot"></div>
                <div>
                    <strong>System Status: All Systems Operational</strong>
                    <div style="font-size: 0.9em; opacity: 0.8;">
                        {len(cluster_health.get('clusters', {}))} Clusters | {cluster_health.get('total_alerts', 0)} Active Alerts
                    </div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 1.1em; font-weight: 600;">Enterprise Observability</div>
                <div style="font-size: 0.9em; opacity: 0.8;">{time.strftime('%Y-%m-%d %H:%M UTC')}</div>
            </div>
        </div>

        <div class="overview-grid">
            <div class="overview-card">
                <div class="card-header">
                    <span class="card-icon">🏢</span>
                    <span class="card-title">Active Clusters</span>
                </div>
                <div class="card-value" style="color: #00d4aa;">{len(cluster_health.get('clusters', {}))}</div>
                <div class="card-subtitle">Production training environments</div>
            </div>

            <div class="overview-card">
                <div class="card-header">
                    <span class="card-icon">🖥️</span>
                    <span class="card-title">Total Nodes</span>
                </div>
                <div class="card-value" style="color: #00a8ff;">
                    {sum(cluster['nodes_total'] for cluster in cluster_health.get('clusters', {}).values())}
                </div>
                <div class="card-subtitle">Compute nodes across all clusters</div>
            </div>

            <div class="overview-card">
                <div class="card-header">
                    <span class="card-icon">🚨</span>
                    <span class="card-title">Active Alerts</span>
                </div>
                <div class="card-value" style="color: #ff6b35;">
                    {cluster_health.get('total_alerts', 0)}
                </div>
                <div class="card-subtitle">
                    {cluster_health.get('critical_alerts', 0)} critical alerts
                </div>
            </div>

            <div class="overview-card">
                <div class="card-header">
                    <span class="card-icon">💰</span>
                    <span class="card-title">Hourly Cost</span>
                </div>
                <div class="card-value" style="color: #ffd700;">
                    ${sum(cluster.get('estimated_hourly_cost', 0) for cluster in cluster_health.get('clusters', {}).values()):,.0f}
                </div>
                <div class="card-subtitle">Estimated infrastructure cost</div>
            </div>

            <div class="overview-card">
                <div class="card-header">
                    <span class="card-icon">⚡</span>
                    <span class="card-title">Total Throughput</span>
                </div>
                <div class="card-value" style="color: #32cd32;">
                    {sum(cluster.get('total_throughput', 0) for cluster in cluster_health.get('clusters', {}).values()):,.0f}
                </div>
                <div class="card-subtitle">Operations per second</div>
            </div>

            <div class="overview-card">
                <div class="card-header">
                    <span class="card-icon">🔥</span>
                    <span class="card-title">Power Usage</span>
                </div>
                <div class="card-value" style="color: #ff4757;">
                    {sum(cluster.get('total_power', 0) for cluster in cluster_health.get('clusters', {}).values()):,.0f}W
                </div>
                <div class="card-subtitle">Total power consumption</div>
            </div>
        </div>

        <div class="clusters-section">
            <h2 class="section-title">
                <span>🏢</span>
                <span>Cluster Health Overview</span>
            </h2>
            <div class="clusters-grid">
                {"".join([f'''
                <div class="cluster-card">
                    <div class="cluster-header">
                        <div class="cluster-name">{cluster_id}</div>
                        <div class="cluster-status status-{cluster_info.get('status', 'unknown')}">{cluster_info.get('status', 'unknown')}</div>
                    </div>
                    <div class="cluster-metrics">
                        <div class="metric-item">
                            <div class="metric-value">{cluster_info.get('nodes_healthy', 0)}/{cluster_info.get('nodes_total', 0)}</div>
                            <div class="metric-label">Healthy Nodes</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">{cluster_info.get('avg_cpu_usage', 0):.1f}%</div>
                            <div class="metric-label">Avg CPU</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">{cluster_info.get('avg_memory_usage', 0):.1f}%</div>
                            <div class="metric-label">Avg Memory</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">{cluster_info.get('avg_gpu_usage', 0):.1f}%</div>
                            <div class="metric-label">Avg GPU</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">{cluster_info.get('active_training_jobs', 0)}</div>
                            <div class="metric-label">Active Jobs</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-value">{cluster_info.get('avg_latency_p95', 0):.0f}ms</div>
                            <div class="metric-label">P95 Latency</div>
                        </div>
                    </div>
                </div>
                ''' for cluster_id, cluster_info in cluster_health.get('clusters', {}).items()])}
            </div>
        </div>

        <div class="alerts-section">
            <h2 class="section-title">
                <span>🚨</span>
                <span>Recent Alerts & Incidents</span>
            </h2>
            <div class="alerts-grid">
                {"".join([f'''
                <div class="alert-card alert-{alert.get('severity', 'info')}">
                    <div class="alert-header">
                        <strong>{alert.get('type', 'Unknown').replace('_', ' ').title()}</strong>
                        <span class="alert-severity">{alert.get('severity', 'info')}</span>
                    </div>
                    <div style="margin-bottom: 10px;">{alert.get('description', 'No description')}</div>
                    <div style="font-size: 0.85em; color: #b0bec5;">
                        Cluster: {alert.get('cluster_id', 'N/A')} | Resource: {alert.get('resource_id', 'N/A')}
                    </div>
                    <div style="font-size: 0.8em; color: #78909c; margin-top: 5px;">
                        {time.strftime('%H:%M:%S', time.localtime(alert.get('timestamp', time.time())))}
                    </div>
                </div>
                ''' for alert in recent_alerts[-8:]])}
            </div>
        </div>

        <div class="service-map-section">
            <h2 class="section-title">
                <span>🔗</span>
                <span>Service Dependency Map</span>
            </h2>
            <div class="service-graph" id="serviceGraph">
                <svg width="100%" height="400" id="dependencyGraph"></svg>
            </div>
        </div>

        <div class="performance-charts">
            <div class="chart-panel">
                <h3 class="section-title" style="font-size: 1.2em; margin-bottom: 15px;">
                    <span>📊</span>
                    <span>Resource Utilization Trends</span>
                </h3>
                <div class="chart-container">
                    <svg width="100%" height="280" id="resourceChart"></svg>
                </div>
            </div>

            <div class="chart-panel">
                <h3 class="section-title" style="font-size: 1.2em; margin-bottom: 15px;">
                    <span>⚡</span>
                    <span>Performance Metrics</span>
                </h3>
                <div class="chart-container">
                    <svg width="100%" height="280" id="performanceChart"></svg>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Observability data
        const observabilityData = {{
            clusters: {json.dumps(cluster_health.get('clusters', {}))},
            services: {json.dumps(dependency_map)},
            alerts: {json.dumps([dict(alert) for alert in recent_alerts])},
            timestamp: {time.time()}
        }};

        function updateTimestamp() {{
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
        }}

        function renderServiceDependencyGraph() {{
            const svg = document.getElementById('dependencyGraph');
            const container = document.getElementById('serviceGraph');
            const width = container.clientWidth || 800;
            const height = 400;

            svg.setAttribute('width', width);
            svg.setAttribute('height', height);
            svg.innerHTML = '';

            // Background
            const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            bg.setAttribute('width', '100%');
            bg.setAttribute('height', '100%');
            bg.setAttribute('fill', 'rgba(0,0,0,0.1)');
            svg.appendChild(bg);

            const services = observabilityData.services.nodes || [];
            const dependencies = observabilityData.services.edges || [];

            if (services.length === 0) {{
                const noData = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                noData.setAttribute('x', width / 2);
                noData.setAttribute('y', height / 2);
                noData.setAttribute('text-anchor', 'middle');
                noData.setAttribute('fill', '#78909c');
                noData.setAttribute('font-size', '16');
                noData.textContent = 'No service dependencies registered';
                svg.appendChild(noData);
                return;
            }}

            // Simple circular layout
            const centerX = width / 2;
            const centerY = height / 2;
            const radius = Math.min(width, height) / 3;

            // Position services in a circle
            services.forEach((service, index) => {{
                const angle = (2 * Math.PI * index) / services.length;
                const x = centerX + radius * Math.cos(angle);
                const y = centerY + radius * Math.sin(angle);

                // Service node
                const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                circle.setAttribute('cx', x);
                circle.setAttribute('cy', y);
                circle.setAttribute('r', '25');

                const statusColor = service.status === 'running' ? '#4caf50' :
                                   service.status === 'warning' ? '#ff9800' :
                                   service.status === 'down' ? '#f44336' : '#78909c';

                circle.setAttribute('fill', statusColor);
                circle.setAttribute('opacity', '0.8');
                circle.setAttribute('stroke', 'rgba(255,255,255,0.3)');
                circle.setAttribute('stroke-width', '2');
                svg.appendChild(circle);

                // Service label
                const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                label.setAttribute('x', x);
                label.setAttribute('y', y - 35);
                label.setAttribute('text-anchor', 'middle');
                label.setAttribute('fill', '#ffffff');
                label.setAttribute('font-size', '12');
                label.setAttribute('font-weight', '600');
                label.textContent = service.label || service.id;
                svg.appendChild(label);

                // Store position for edges
                service._x = x;
                service._y = y;
            }});

            // Draw dependency edges
            dependencies.forEach(edge => {{
                const source = services.find(s => s.id === edge.source);
                const target = services.find(s => s.id === edge.target);

                if (source && target && source._x && target._x) {{
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', source._x);
                    line.setAttribute('y1', source._y);
                    line.setAttribute('x2', target._x);
                    line.setAttribute('y2', target._y);
                    line.setAttribute('stroke', 'rgba(100, 255, 218, 0.6)');
                    line.setAttribute('stroke-width', '2');
                    line.setAttribute('stroke-dasharray', '5,5');
                    svg.appendChild(line);

                    // Arrow head
                    const angle = Math.atan2(target._y - source._y, target._x - source._x);
                    const arrowX = target._x - 25 * Math.cos(angle);
                    const arrowY = target._y - 25 * Math.sin(angle);

                    const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
                    const arrowSize = 8;
                    const x1 = arrowX - arrowSize * Math.cos(angle - Math.PI/6);
                    const y1 = arrowY - arrowSize * Math.sin(angle - Math.PI/6);
                    const x2 = arrowX - arrowSize * Math.cos(angle + Math.PI/6);
                    const y2 = arrowY - arrowSize * Math.sin(angle + Math.PI/6);

                    arrow.setAttribute('points', `${{arrowX}},${{arrowY}} ${{x1}},${{y1}} ${{x2}},${{y2}}`);
                    arrow.setAttribute('fill', 'rgba(100, 255, 218, 0.8)');
                    svg.appendChild(arrow);
                }}
            }});
        }}

        function renderResourceChart() {{
            const svg = document.getElementById('resourceChart');
            const width = svg.clientWidth || 400;
            const height = 280;
            svg.setAttribute('width', width);
            svg.setAttribute('height', height);
            svg.innerHTML = '';

            // Sample data visualization
            const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            bg.setAttribute('width', '100%');
            bg.setAttribute('height', '100%');
            bg.setAttribute('fill', 'rgba(0,0,0,0.2)');
            svg.appendChild(bg);

            // Title
            const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            title.setAttribute('x', width / 2);
            title.setAttribute('y', 30);
            title.setAttribute('text-anchor', 'middle');
            title.setAttribute('fill', '#cfd8dc');
            title.setAttribute('font-size', '14');
            title.setAttribute('font-weight', '600');
            title.textContent = 'Real-time Resource Utilization';
            svg.appendChild(title);

            // Real-time resource visualization
            const margin = {{ top: 40, right: 20, bottom: 30, left: 50 }};
            const chartWidth = width - margin.left - margin.right;
            const chartHeight = height - margin.top - margin.bottom;

            // Create chart container
            const chartGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            chartGroup.setAttribute('transform', `translate(${{margin.left}},${{margin.top}})`);
            svg.appendChild(chartGroup);

            // Sample data - in real implementation this would come from observabilityData
            const resourceData = [
                {{ time: 0, cpu: 75, memory: 82, gpu: 68 }},
                {{ time: 1, cpu: 78, memory: 85, gpu: 72 }},
                {{ time: 2, cpu: 73, memory: 80, gpu: 69 }},
                {{ time: 3, cpu: 80, memory: 88, gpu: 75 }},
                {{ time: 4, cpu: 77, memory: 83, gpu: 70 }}
            ];

            // Create scales
            const xScale = (t) => (t / 4) * chartWidth;
            const yScale = (val) => chartHeight - (val / 100) * chartHeight;

            // Draw CPU line
            const cpuPath = resourceData.map((d, i) =>
                `${{i === 0 ? 'M' : 'L'}}${{xScale(d.time)}},${{yScale(d.cpu)}}`
            ).join(' ');
            const cpuLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            cpuLine.setAttribute('d', cpuPath);
            cpuLine.setAttribute('stroke', '#FF6B6B');
            cpuLine.setAttribute('stroke-width', '2');
            cpuLine.setAttribute('fill', 'none');
            chartGroup.appendChild(cpuLine);

            // Draw Memory line
            const memoryPath = resourceData.map((d, i) =>
                `${{i === 0 ? 'M' : 'L'}}${{xScale(d.time)}},${{yScale(d.memory)}}`
            ).join(' ');
            const memoryLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            memoryLine.setAttribute('d', memoryPath);
            memoryLine.setAttribute('stroke', '#4ECDC4');
            memoryLine.setAttribute('stroke-width', '2');
            memoryLine.setAttribute('fill', 'none');
            chartGroup.appendChild(memoryLine);

            // Draw GPU line
            const gpuPath = resourceData.map((d, i) =>
                `${{i === 0 ? 'M' : 'L'}}${{xScale(d.time)}},${{yScale(d.gpu)}}`
            ).join(' ');
            const gpuLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            gpuLine.setAttribute('d', gpuPath);
            gpuLine.setAttribute('stroke', '#45B7D1');
            gpuLine.setAttribute('stroke-width', '2');
            gpuLine.setAttribute('fill', 'none');
            chartGroup.appendChild(gpuLine);

            // Add legend
            const legend = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            legend.setAttribute('transform', `translate(${{chartWidth - 100}}, 20)`);

            const legendItems = [
                {{ color: '#FF6B6B', label: 'CPU' }},
                {{ color: '#4ECDC4', label: 'Memory' }},
                {{ color: '#45B7D1', label: 'GPU' }}
            ];

            legendItems.forEach((item, i) => {{
                const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                rect.setAttribute('x', 0);
                rect.setAttribute('y', i * 20);
                rect.setAttribute('width', 12);
                rect.setAttribute('height', 12);
                rect.setAttribute('fill', item.color);
                legend.appendChild(rect);

                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', 18);
                text.setAttribute('y', i * 20 + 9);
                text.setAttribute('fill', '#cfd8dc');
                text.setAttribute('font-size', '12');
                text.textContent = item.label;
                legend.appendChild(text);
            }});

            chartGroup.appendChild(legend);
        }}

        function renderPerformanceChart() {{
            const svg = document.getElementById('performanceChart');
            const width = svg.clientWidth || 400;
            const height = 280;
            svg.setAttribute('width', width);
            svg.setAttribute('height', height);
            svg.innerHTML = '';

            // Sample data visualization
            const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            bg.setAttribute('width', '100%');
            bg.setAttribute('height', '100%');
            bg.setAttribute('fill', 'rgba(0,0,0,0.2)');
            svg.appendChild(bg);

            // Title
            const title = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            title.setAttribute('x', width / 2);
            title.setAttribute('y', 30);
            title.setAttribute('text-anchor', 'middle');
            title.setAttribute('fill', '#cfd8dc');
            title.setAttribute('font-size', '14');
            title.setAttribute('font-weight', '600');
            title.textContent = 'Performance & Latency Trends';
            svg.appendChild(title);

            // Real-time performance visualization
            const margin = {{ top: 40, right: 20, bottom: 30, left: 50 }};
            const chartWidth = width - margin.left - margin.right;
            const chartHeight = height - margin.top - margin.bottom;

            // Create chart container
            const chartGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            chartGroup.setAttribute('transform', `translate(${{margin.left}},${{margin.top}})`);
            svg.appendChild(chartGroup);

            // Performance data - latency and throughput
            const perfData = [
                {{ time: 0, latency: 45, throughput: 850 }},
                {{ time: 1, latency: 52, throughput: 820 }},
                {{ time: 2, latency: 38, throughput: 890 }},
                {{ time: 3, latency: 61, throughput: 780 }},
                {{ time: 4, latency: 43, throughput: 870 }}
            ];

            // Create scales
            const xScale = (t) => (t / 4) * chartWidth;
            const latencyScale = (val) => chartHeight - (val / 100) * chartHeight;
            const throughputScale = (val) => chartHeight - ((val - 750) / 150) * chartHeight;

            // Draw latency line
            const latencyPath = perfData.map((d, i) =>
                `${{i === 0 ? 'M' : 'L'}}${{xScale(d.time)}},${{latencyScale(d.latency)}}`
            ).join(' ');
            const latencyLine = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            latencyLine.setAttribute('d', latencyPath);
            latencyLine.setAttribute('stroke', '#FF6348');
            latencyLine.setAttribute('stroke-width', '2');
            latencyLine.setAttribute('fill', 'none');
            chartGroup.appendChild(latencyLine);

            // Draw throughput bars
            perfData.forEach((d, i) => {{
                const barHeight = (d.throughput - 750) / 150 * chartHeight;
                const bar = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
                bar.setAttribute('x', xScale(d.time) - 8);
                bar.setAttribute('y', chartHeight - barHeight);
                bar.setAttribute('width', 16);
                bar.setAttribute('height', barHeight);
                bar.setAttribute('fill', '#4ECDC4');
                bar.setAttribute('opacity', '0.7');
                chartGroup.appendChild(bar);
            }});

            // Add performance indicators
            const currentLatency = perfData[perfData.length - 1].latency;
            const currentThroughput = perfData[perfData.length - 1].throughput;

            const latencyIndicator = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            latencyIndicator.setAttribute('x', 10);
            latencyIndicator.setAttribute('y', 20);
            latencyIndicator.setAttribute('fill', '#FF6348');
            latencyIndicator.setAttribute('font-size', '12');
            latencyIndicator.setAttribute('font-weight', 'bold');
            latencyIndicator.textContent = `Latency: ${{currentLatency}}ms`;
            chartGroup.appendChild(latencyIndicator);

            const throughputIndicator = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            throughputIndicator.setAttribute('x', 10);
            throughputIndicator.setAttribute('y', 40);
            throughputIndicator.setAttribute('fill', '#4ECDC4');
            throughputIndicator.setAttribute('font-size', '12');
            throughputIndicator.setAttribute('font-weight', 'bold');
            throughputIndicator.textContent = `Throughput: ${{currentThroughput}} req/s`;
            chartGroup.appendChild(throughputIndicator);
        }}

        function refreshDashboard() {{
            updateTimestamp();
            renderServiceDependencyGraph();
            renderResourceChart();
            renderPerformanceChart();
        }}

        // Initialize dashboard
        refreshDashboard();

        // Auto-refresh every 5 seconds
        setInterval(() => {{
            updateTimestamp();
        }}, 5000);

        // Re-render on window resize
        window.addEventListener('resize', () => {{
            renderServiceDependencyGraph();
            renderResourceChart();
            renderPerformanceChart();
        }});

        console.log('🔍 AI Training Observability Dashboard loaded successfully!');
        console.log('📊 Monitoring', Object.keys(observabilityData.clusters).length, 'clusters');
        console.log('🔗 Tracking', observabilityData.services.nodes.length, 'services');
        console.log('🚨 Active alerts:', observabilityData.alerts.length);
    </script>
</body>
</html>
        """

        return dashboard_html

    def create_unified_enterprise_dashboard(self) -> str:
        """Create unified enterprise dashboard including LLM observability."""
        if not LLM_OBSERVABILITY_AVAILABLE:
            # Fallback to traditional dashboard if LLM observability not available
            return self.create_observability_dashboard()

        # Create traditional infrastructure dashboard (extract body content)
        infrastructure_dashboard = self.create_observability_dashboard()

        # Create LLM observability dashboard (get body content only)
        llm_dashboard_full = self.llm_dashboard_creator.create_unified_llm_dashboard()

        # Extract dashboard content from both
        import re
        infra_body_match = re.search(r'<body[^>]*>(.*?)</body>', infrastructure_dashboard, re.DOTALL)
        infra_content = infra_body_match.group(1) if infra_body_match else infrastructure_dashboard

        llm_body_match = re.search(r'<body[^>]*>(.*?)</body>', llm_dashboard_full, re.DOTALL)
        llm_content = llm_body_match.group(1) if llm_body_match else llm_dashboard_full

        # Create unified tabbed interface
        unified_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OpenFinOps Enterprise AI Observability Platform</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}

                .unified-header {{
                    background: rgba(0, 0, 0, 0.8);
                    backdrop-filter: blur(20px);
                    padding: 25px 0;
                    text-align: center;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                }}

                .unified-title {{
                    color: white;
                    font-size: 42px;
                    font-weight: 300;
                    margin-bottom: 12px;
                    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
                }}

                .unified-subtitle {{
                    color: rgba(255, 255, 255, 0.9);
                    font-size: 20px;
                    margin-bottom: 20px;
                }}

                .platform-badges {{
                    display: flex;
                    justify-content: center;
                    gap: 15px;
                    flex-wrap: wrap;
                }}

                .badge {{
                    background: rgba(78, 205, 196, 0.8);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: 500;
                    border: 1px solid rgba(78, 205, 196, 0.6);
                }}

                .nav-tabs {{
                    display: flex;
                    justify-content: center;
                    padding: 25px;
                    gap: 15px;
                    flex-wrap: wrap;
                }}

                .tab-btn {{
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    color: white;
                    padding: 15px 30px;
                    border-radius: 30px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    font-size: 16px;
                    font-weight: 600;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}

                .tab-btn:hover {{
                    background: rgba(255, 255, 255, 0.2);
                    transform: translateY(-2px);
                    box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                }}

                .tab-btn.active {{
                    background: rgba(78, 205, 196, 0.8);
                    border-color: #4ECDC4;
                    box-shadow: 0 5px 20px rgba(78, 205, 196, 0.3);
                }}

                .tab-content {{
                    padding: 20px;
                    max-width: 1400px;
                    margin: 0 auto;
                }}

                .content-panel {{
                    display: none;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 15px;
                    padding: 25px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}

                .content-panel.active {{
                    display: block;
                }}

                .panel-title {{
                    color: white;
                    font-size: 28px;
                    font-weight: 600;
                    margin-bottom: 20px;
                    text-align: center;
                }}

                .stats-overview {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}

                .stat-card {{
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    padding: 20px;
                    text-align: center;
                    color: white;
                    transition: transform 0.2s ease;
                }}

                .stat-card:hover {{
                    transform: translateY(-3px);
                }}

                .stat-value {{
                    font-size: 32px;
                    font-weight: 700;
                    color: #4ECDC4;
                    margin-bottom: 8px;
                }}

                .stat-label {{
                    font-size: 14px;
                    color: rgba(255, 255, 255, 0.8);
                    font-weight: 500;
                }}
            </style>
        </head>
        <body>
            <div class="unified-header">
                <h1 class="unified-title">🚀 OpenFinOps Enterprise AI Observability</h1>
                <p class="unified-subtitle">Comprehensive Infrastructure & LLM Training Monitoring Platform</p>
                <div class="platform-badges">
                    <span class="badge">🖥️ Infrastructure Monitoring</span>
                    <span class="badge">🧠 LLM Training</span>
                    <span class="badge">📚 RAG Pipelines</span>
                    <span class="badge">🤖 Agent Workflows</span>
                    <span class="badge">🏢 Enterprise Governance</span>
                </div>
            </div>

            <div class="stats-overview">
                <div class="stat-card">
                    <div class="stat-value">{len(self.hub.system_metrics)}</div>
                    <div class="stat-label">Infrastructure Metrics</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(self.llm_hub.llm_training_metrics) if self.llm_hub else 0}</div>
                    <div class="stat-label">LLM Training Metrics</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(self.llm_hub.rag_pipeline_metrics) if self.llm_hub else 0}</div>
                    <div class="stat-label">RAG Pipeline Metrics</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(self.llm_hub.agent_workflow_metrics) if self.llm_hub else 0}</div>
                    <div class="stat-label">Agent Workflows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(self.hub.alerts) + len(self.llm_hub.active_alerts) if self.llm_hub else len(self.hub.alerts)}</div>
                    <div class="stat-label">Total Active Alerts</div>
                </div>
            </div>

            <div class="nav-tabs">
                <button class="tab-btn active" onclick="showPanel('infrastructure')">
                    🖥️ Infrastructure Monitoring
                </button>
                <button class="tab-btn" onclick="showPanel('llm')">
                    🧠 LLM & RAG Training
                </button>
            </div>

            <div class="tab-content">
                <div id="infrastructure" class="content-panel active">
                    <div class="panel-title">Infrastructure & System Monitoring</div>
                    {infra_content}
                </div>
                <div id="llm" class="content-panel">
                    <div class="panel-title">LLM Training & RAG Observability</div>
                    {llm_content}
                </div>
            </div>

            <script>
                function showPanel(panelName) {{
                    // Hide all panels
                    document.querySelectorAll('.content-panel').forEach(panel => {{
                        panel.classList.remove('active');
                    }});

                    // Remove active class from all buttons
                    document.querySelectorAll('.tab-btn').forEach(btn => {{
                        btn.classList.remove('active');
                    }});

                    // Show selected panel
                    document.getElementById(panelName).classList.add('active');

                    // Add active class to clicked button
                    event.target.classList.add('active');
                }}

                console.log('🚀 OpenFinOps Enterprise AI Observability Platform loaded!');
                console.log('📊 Infrastructure metrics: {len(self.hub.system_metrics)}');
                console.log('🧠 LLM training metrics: {len(self.llm_hub.llm_training_metrics) if self.llm_hub else 0}');
                console.log('📚 RAG pipeline metrics: {len(self.llm_hub.rag_pipeline_metrics) if self.llm_hub else 0}');
                console.log('🤖 Agent workflow metrics: {len(self.llm_hub.agent_workflow_metrics) if self.llm_hub else 0}');
            </script>
        </body>
        </html>
        """

        return unified_html

    def save_dashboard(self, filename: str = 'observability_dashboard.html') -> str:
        """Save the observability dashboard to HTML file."""
        html_content = self.create_observability_dashboard()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return filename