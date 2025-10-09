"""
Service Mesh Monitoring and Dependency Mapping
===============================================

Advanced service mesh observability with service dependency mapping,
communication pattern analysis, and distributed system health monitoring.

Features:
- Service dependency graph construction
- Communication pattern analysis
- Service mesh health monitoring
- Circuit breaker pattern detection
- Load balancing effectiveness analysis
- Security policy compliance tracking
- Performance bottleneck identification in service interactions
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
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
import uuid


class ServiceType(Enum):
    """Service types in the mesh"""
    API_GATEWAY = "api_gateway"
    MICROSERVICE = "microservice"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    LOAD_BALANCER = "load_balancer"
    EXTERNAL_SERVICE = "external_service"


class CommunicationProtocol(Enum):
    """Communication protocols"""
    HTTP = "http"
    HTTPS = "https"
    GRPC = "grpc"
    TCP = "tcp"
    UDP = "udp"
    WEBSOCKET = "websocket"


class ServiceHealth(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Service registry information"""
    service_id: str
    service_name: str
    service_type: ServiceType
    version: str
    namespace: str = "default"
    cluster: str = "default"
    instances: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    registered_at: float = field(default_factory=time.time)


@dataclass
class ServiceCommunication:
    """Service-to-service communication record"""
    communication_id: str
    source_service: str
    destination_service: str
    protocol: CommunicationProtocol
    timestamp: float
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    latency_ms: Optional[float] = None
    status_code: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


@dataclass
class ServiceDependency:
    """Service dependency relationship"""
    dependency_id: str
    source_service: str
    destination_service: str
    dependency_type: str  # 'sync', 'async', 'data', 'config'
    criticality: str  # 'critical', 'high', 'medium', 'low'
    discovered_at: float
    last_seen: float
    communication_count: int = 0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    circuit_breaker_state: str = "closed"  # 'open', 'half_open', 'closed'


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_id: str
    timestamp: float
    request_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_rps: float = 0.0
    cpu_utilization: Optional[float] = None
    memory_utilization: Optional[float] = None
    active_connections: Optional[int] = None
    health_status: ServiceHealth = ServiceHealth.UNKNOWN


class ServiceMeshMonitor:
    """Service mesh monitoring and analysis system"""

    def __init__(self, collection_interval: float = 10.0):
        self.collection_interval = collection_interval
        self.service_registry: Dict[str, ServiceInfo] = {}
        self.service_communications = deque(maxlen=50000)  # Communication history
        self.service_dependencies: Dict[str, ServiceDependency] = {}
        self.service_metrics = defaultdict(lambda: deque(maxlen=1000))

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.collection_lock = threading.Lock()

        # Dependency analysis
        self.dependency_graph = defaultdict(set)  # source -> destinations
        self.reverse_dependency_graph = defaultdict(set)  # destination -> sources

        # Communication patterns
        self.communication_patterns = defaultdict(list)
        self.protocol_usage = defaultdict(int)

        # Circuit breaker tracking
        self.circuit_breaker_states = defaultdict(lambda: "closed")
        self.failure_counts = defaultdict(int)

    def register_service(self, service_info: ServiceInfo):
        """Register service in mesh"""
        with self.collection_lock:
            self.service_registry[service_info.service_id] = service_info

    def unregister_service(self, service_id: str):
        """Unregister service from mesh"""
        with self.collection_lock:
            if service_id in self.service_registry:
                del self.service_registry[service_id]

    def record_communication(self, communication: ServiceCommunication):
        """Record service-to-service communication"""
        with self.collection_lock:
            self.service_communications.append(communication)

            # Update dependency graph
            self._update_dependency_graph(communication)

            # Update communication patterns
            pattern_key = f"{communication.source_service}->{communication.destination_service}"
            self.communication_patterns[pattern_key].append({
                'timestamp': communication.timestamp,
                'latency_ms': communication.latency_ms,
                'success': communication.success,
                'protocol': communication.protocol.value
            })

            # Track protocol usage
            self.protocol_usage[communication.protocol.value] += 1

            # Update circuit breaker logic
            self._update_circuit_breaker_state(communication)

    def _update_dependency_graph(self, communication: ServiceCommunication):
        """Update service dependency graph"""
        source = communication.source_service
        destination = communication.destination_service

        self.dependency_graph[source].add(destination)
        self.reverse_dependency_graph[destination].add(source)

        # Create or update dependency record
        dependency_key = f"{source}->{destination}"
        if dependency_key not in self.service_dependencies:
            self.service_dependencies[dependency_key] = ServiceDependency(
                dependency_id=dependency_key,
                source_service=source,
                destination_service=destination,
                dependency_type="sync" if communication.protocol in [CommunicationProtocol.HTTP, CommunicationProtocol.HTTPS, CommunicationProtocol.GRPC] else "async",
                criticality="medium",  # Default, could be configured
                discovered_at=communication.timestamp,
                last_seen=communication.timestamp
            )

        dependency = self.service_dependencies[dependency_key]
        dependency.last_seen = communication.timestamp
        dependency.communication_count += 1

        # Update metrics
        if communication.latency_ms:
            total_latency = dependency.avg_latency_ms * (dependency.communication_count - 1) + communication.latency_ms
            dependency.avg_latency_ms = total_latency / dependency.communication_count

        if not communication.success:
            dependency.error_rate = (dependency.error_rate * (dependency.communication_count - 1) + 1) / dependency.communication_count
        else:
            dependency.error_rate = (dependency.error_rate * (dependency.communication_count - 1)) / dependency.communication_count

    def _update_circuit_breaker_state(self, communication: ServiceCommunication):
        """Update circuit breaker state based on communication results"""
        service_pair = f"{communication.source_service}->{communication.destination_service}"

        if not communication.success:
            self.failure_counts[service_pair] += 1

            # Simplified circuit breaker logic
            if self.failure_counts[service_pair] >= 5:  # Failure threshold
                self.circuit_breaker_states[service_pair] = "open"
                if service_pair in self.service_dependencies:
                    self.service_dependencies[service_pair].circuit_breaker_state = "open"
        else:
            # Reset failure count on success
            self.failure_counts[service_pair] = 0
            if self.circuit_breaker_states[service_pair] == "open":
                self.circuit_breaker_states[service_pair] = "half_open"
                if service_pair in self.service_dependencies:
                    self.service_dependencies[service_pair].circuit_breaker_state = "half_open"

    def add_service_metrics(self, metrics: ServiceMetrics):
        """Add service performance metrics"""
        with self.collection_lock:
            self.service_metrics[metrics.service_id].append(metrics)

    def analyze_dependency_criticality(self) -> Dict[str, Any]:
        """Analyze dependency criticality and create rankings"""
        dependency_analysis = {}

        with self.collection_lock:
            for dep_key, dependency in self.service_dependencies.items():
                # Calculate criticality score based on multiple factors
                criticality_score = 0

                # Communication frequency (higher = more critical)
                freq_score = min(dependency.communication_count / 1000, 1.0) * 30

                # Error rate (lower = more critical for reliability)
                error_score = (1 - dependency.error_rate) * 25

                # Average latency (lower = more critical for performance)
                latency_score = max(0, (1000 - dependency.avg_latency_ms) / 1000) * 25

                # Downstream dependency count
                downstream_count = len(self.dependency_graph.get(dependency.destination_service, set()))
                downstream_score = min(downstream_count / 10, 1.0) * 20

                criticality_score = freq_score + error_score + latency_score + downstream_score

                # Determine criticality level
                if criticality_score >= 80:
                    criticality_level = "critical"
                elif criticality_score >= 60:
                    criticality_level = "high"
                elif criticality_score >= 40:
                    criticality_level = "medium"
                else:
                    criticality_level = "low"

                dependency_analysis[dep_key] = {
                    "dependency": asdict(dependency),
                    "criticality_score": criticality_score,
                    "criticality_level": criticality_level,
                    "downstream_services": len(self.dependency_graph.get(dependency.destination_service, set())),
                    "upstream_services": len(self.reverse_dependency_graph.get(dependency.source_service, set()))
                }

        # Sort by criticality score
        sorted_dependencies = sorted(
            dependency_analysis.items(),
            key=lambda x: x[1]["criticality_score"],
            reverse=True
        )

        return {
            "total_dependencies": len(dependency_analysis),
            "critical_dependencies": len([d for d in dependency_analysis.values() if d["criticality_level"] == "critical"]),
            "dependencies": dict(sorted_dependencies)
        }

    def detect_communication_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in service communication patterns"""
        anomalies = []
        current_time = time.time()

        with self.collection_lock:
            # Analyze recent communications (last hour)
            recent_threshold = current_time - 3600
            recent_communications = [
                comm for comm in self.service_communications
                if comm.timestamp > recent_threshold
            ]

        if not recent_communications:
            return anomalies

        # Group by service pair
        service_pair_metrics = defaultdict(list)
        for comm in recent_communications:
            pair_key = f"{comm.source_service}->{comm.destination_service}"
            service_pair_metrics[pair_key].append(comm)

        for pair_key, communications in service_pair_metrics.items():
            if len(communications) < 10:  # Need sufficient data
                continue

            # Calculate metrics
            latencies = [c.latency_ms for c in communications if c.latency_ms is not None]
            error_rate = sum(1 for c in communications if not c.success) / len(communications)

            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                max_latency = max(latencies)

                # Detect high latency anomaly
                if avg_latency > 1000:  # > 1 second
                    anomalies.append({
                        "type": "high_latency",
                        "service_pair": pair_key,
                        "avg_latency_ms": avg_latency,
                        "max_latency_ms": max_latency,
                        "severity": "high" if avg_latency > 5000 else "medium",
                        "description": f"High latency detected for {pair_key}: {avg_latency:.1f}ms average"
                    })

            # Detect high error rate anomaly
            if error_rate > 0.05:  # > 5% error rate
                anomalies.append({
                    "type": "high_error_rate",
                    "service_pair": pair_key,
                    "error_rate": error_rate * 100,
                    "total_requests": len(communications),
                    "severity": "critical" if error_rate > 0.2 else "high",
                    "description": f"High error rate for {pair_key}: {error_rate*100:.1f}%"
                })

            # Detect unusual traffic patterns
            request_timestamps = [c.timestamp for c in communications]
            if len(set(int(ts/300) for ts in request_timestamps)) < 4:  # All requests in < 4 time buckets
                anomalies.append({
                    "type": "traffic_spike",
                    "service_pair": pair_key,
                    "request_count": len(communications),
                    "time_window_minutes": (max(request_timestamps) - min(request_timestamps)) / 60,
                    "severity": "medium",
                    "description": f"Traffic spike detected for {pair_key}: {len(communications)} requests in short time window"
                })

        return sorted(anomalies, key=lambda a: {"critical": 3, "high": 2, "medium": 1, "low": 0}.get(a["severity"], 0), reverse=True)

    def get_service_health_summary(self) -> Dict[str, Any]:
        """Get overall service mesh health summary"""
        with self.collection_lock:
            total_services = len(self.service_registry)
            healthy_services = 0
            degraded_services = 0
            unhealthy_services = 0

            # Analyze service health based on recent metrics
            for service_id, metrics_deque in self.service_metrics.items():
                if not metrics_deque:
                    continue

                recent_metrics = list(metrics_deque)[-5:]  # Last 5 samples
                if recent_metrics:
                    latest_health = recent_metrics[-1].health_status
                    if latest_health == ServiceHealth.HEALTHY:
                        healthy_services += 1
                    elif latest_health == ServiceHealth.DEGRADED:
                        degraded_services += 1
                    else:
                        unhealthy_services += 1

            # Analyze circuit breaker status
            open_circuit_breakers = sum(1 for state in self.circuit_breaker_states.values() if state == "open")

            # Communication success rate
            recent_threshold = time.time() - 3600
            recent_comms = [c for c in self.service_communications if c.timestamp > recent_threshold]
            success_rate = sum(1 for c in recent_comms if c.success) / len(recent_comms) * 100 if recent_comms else 0

        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "degraded_services": degraded_services,
            "unhealthy_services": unhealthy_services,
            "open_circuit_breakers": open_circuit_breakers,
            "communication_success_rate": success_rate,
            "total_dependencies": len(self.service_dependencies),
            "total_communications_last_hour": len(recent_comms) if 'recent_comms' in locals() else 0
        }


class DependencyMapper:
    """Service dependency mapping and visualization"""

    def __init__(self, service_mesh_monitor: ServiceMeshMonitor):
        self.monitor = service_mesh_monitor

    def generate_dependency_map(self) -> Dict[str, Any]:
        """Generate comprehensive dependency map"""
        with self.monitor.collection_lock:
            services = dict(self.monitor.service_registry)
            dependencies = dict(self.monitor.service_dependencies)

        # Build nodes (services)
        nodes = []
        for service_id, service_info in services.items():
            # Calculate service metrics
            service_metrics = self.monitor.service_metrics.get(service_id, deque())
            recent_metrics = list(service_metrics)[-1] if service_metrics else None

            node = {
                "id": service_id,
                "name": service_info.service_name,
                "type": service_info.service_type.value,
                "version": service_info.version,
                "namespace": service_info.namespace,
                "cluster": service_info.cluster,
                "health": recent_metrics.health_status.value if recent_metrics else "unknown",
                "instances": len(service_info.instances),
                "tags": service_info.tags
            }

            # Add performance metrics if available
            if recent_metrics:
                node.update({
                    "throughput_rps": recent_metrics.throughput_rps,
                    "avg_latency_ms": recent_metrics.avg_latency_ms,
                    "error_rate": recent_metrics.error_count / max(recent_metrics.request_count, 1) * 100,
                    "cpu_utilization": recent_metrics.cpu_utilization,
                    "memory_utilization": recent_metrics.memory_utilization
                })

            nodes.append(node)

        # Build edges (dependencies)
        edges = []
        for dep_key, dependency in dependencies.items():
            edge = {
                "source": dependency.source_service,
                "destination": dependency.destination_service,
                "type": dependency.dependency_type,
                "criticality": dependency.criticality,
                "communication_count": dependency.communication_count,
                "avg_latency_ms": dependency.avg_latency_ms,
                "error_rate": dependency.error_rate * 100,
                "circuit_breaker_state": dependency.circuit_breaker_state,
                "last_communication": dependency.last_seen
            }
            edges.append(edge)

        return {
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "total_services": len(nodes),
                "total_dependencies": len(edges),
                "generated_at": time.time()
            }
        }

    def find_critical_paths(self) -> List[List[str]]:
        """Find critical service dependency paths"""
        critical_paths = []

        # Find services that are entry points (API gateways, load balancers)
        entry_services = []
        for service_id, service_info in self.monitor.service_registry.items():
            if service_info.service_type in [ServiceType.API_GATEWAY, ServiceType.LOAD_BALANCER]:
                entry_services.append(service_id)

        # Traverse from each entry point to find critical paths
        for entry_service in entry_services:
            paths = self._find_paths_from_service(entry_service, max_depth=5)
            # Filter for critical dependencies
            critical_service_paths = [
                path for path in paths
                if self._is_critical_path(path)
            ]
            critical_paths.extend(critical_service_paths)

        return critical_paths

    def _find_paths_from_service(self, service_id: str, max_depth: int, current_path: List[str] = None) -> List[List[str]]:
        """Recursively find all paths from a service"""
        if current_path is None:
            current_path = [service_id]

        if len(current_path) >= max_depth:
            return [current_path]

        paths = [current_path]  # Include current path
        downstream_services = self.monitor.dependency_graph.get(service_id, set())

        for downstream_service in downstream_services:
            if downstream_service not in current_path:  # Avoid cycles
                sub_paths = self._find_paths_from_service(
                    downstream_service,
                    max_depth,
                    current_path + [downstream_service]
                )
                paths.extend(sub_paths)

        return paths

    def _is_critical_path(self, path: List[str]) -> bool:
        """Determine if a service path is critical"""
        if len(path) < 2:
            return False

        # Check if any dependency in the path is critical
        for i in range(len(path) - 1):
            dep_key = f"{path[i]}->{path[i+1]}"
            dependency = self.monitor.service_dependencies.get(dep_key)
            if dependency and dependency.criticality in ["critical", "high"]:
                return True

        return False

    def generate_service_map_html(self, output_file: str = "service_dependency_map.html"):
        """Generate interactive service dependency map visualization"""
        dependency_map = self.generate_dependency_map()
        health_summary = self.monitor.get_service_health_summary()
        anomalies = self.monitor.detect_communication_anomalies()

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Service Mesh Dependency Map</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); color: white; }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .dashboard-grid {{ display: grid; grid-template-columns: 1fr 300px; gap: 20px; }}
        .main-content {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; }}
        .sidebar {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; }}
        .metric-card {{ margin: 15px 0; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px; }}
        .service-node {{ margin: 10px 0; padding: 12px; background: rgba(255,255,255,0.15); border-radius: 8px; }}
        .service-node.healthy {{ border-left: 4px solid #4CAF50; }}
        .service-node.degraded {{ border-left: 4px solid #FF9800; }}
        .service-node.unhealthy {{ border-left: 4px solid #f44336; }}
        .anomaly-item {{ margin: 8px 0; padding: 10px; background: rgba(244,67,54,0.2); border-radius: 6px; }}
        .dependency-list {{ max-height: 400px; overflow-y: auto; }}
        .dependency-item {{ margin: 5px 0; padding: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🕸️  Service Mesh Dependency Map</h1>
            <p>Real-time service communication and dependency analysis</p>
        </div>

        <div class="dashboard-grid">
            <div class="main-content">
                <h2>📊 Service Health Overview</h2>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0;">
                    <div class="metric-card" style="text-align: center; background: rgba(76,175,80,0.3);">
                        <h3>{health_summary['healthy_services']}</h3>
                        <p>Healthy Services</p>
                    </div>
                    <div class="metric-card" style="text-align: center; background: rgba(255,152,0,0.3);">
                        <h3>{health_summary['degraded_services']}</h3>
                        <p>Degraded Services</p>
                    </div>
                    <div class="metric-card" style="text-align: center; background: rgba(244,67,54,0.3);">
                        <h3>{health_summary['unhealthy_services']}</h3>
                        <p>Unhealthy Services</p>
                    </div>
                    <div class="metric-card" style="text-align: center;">
                        <h3>{health_summary['communication_success_rate']:.1f}%</h3>
                        <p>Success Rate</p>
                    </div>
                </div>

                <h3>🔗 Service Dependencies</h3>
                <div class="dependency-list">
"""

        for edge in dependency_map['edges'][:15]:  # Show top 15 dependencies
            criticality_color = {
                'critical': '#f44336',
                'high': '#ff9800',
                'medium': '#2196f3',
                'low': '#4caf50'
            }.get(edge['criticality'], '#666')

            html_content += f"""
                    <div class="dependency-item" style="border-left: 3px solid {criticality_color};">
                        <strong>{edge['source']} → {edge['destination']}</strong><br>
                        <small>
                            Latency: {edge['avg_latency_ms']:.1f}ms |
                            Error Rate: {edge['error_rate']:.1f}% |
                            Calls: {edge['communication_count']} |
                            Circuit Breaker: {edge['circuit_breaker_state']}
                        </small>
                    </div>
"""

        html_content += """
                </div>
            </div>

            <div class="sidebar">
                <h3>📈 Metrics Summary</h3>
                <div class="metric-card">
                    <strong>Total Services:</strong> """ + str(health_summary['total_services']) + """<br>
                    <strong>Total Dependencies:</strong> """ + str(health_summary['total_dependencies']) + """<br>
                    <strong>Open Circuit Breakers:</strong> """ + str(health_summary['open_circuit_breakers']) + """<br>
                    <strong>Comms Last Hour:</strong> """ + str(health_summary['total_communications_last_hour']) + """
                </div>

                <h3>⚠️ Communication Anomalies</h3>
"""

        if anomalies:
            for anomaly in anomalies[:5]:  # Show top 5 anomalies
                html_content += f"""
                <div class="anomaly-item">
                    <strong>{anomaly['type'].replace('_', ' ').title()}</strong><br>
                    <small>{anomaly['description']}</small><br>
                    <small style="color: #ffcdd2;">Severity: {anomaly['severity']}</small>
                </div>
"""
        else:
            html_content += "<p>No anomalies detected</p>"

        html_content += f"""

                <h3>🏥 Service Status</h3>
"""

        for node in dependency_map['nodes'][:8]:  # Show top 8 services
            health_class = node.get('health', 'unknown')
            html_content += f"""
                <div class="service-node {health_class}">
                    <strong>{node['name']}</strong><br>
                    <small>Type: {node['type']}</small><br>
                    <small>Health: {health_class.title()}</small><br>
                    <small>Instances: {node['instances']}</small>
                </div>
"""

        html_content += """
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file