"""
AI Training Observability Dashboard System
=========================================

Enterprise-grade observability platform for AI/ML training infrastructure.
Provides comprehensive monitoring, alerting, and visualization for distributed
training systems with focus on performance, reliability, and cost optimization.

Key Features:
- Real-time system health monitoring across clusters
- Distributed training infrastructure observability
- Multi-dimensional performance metrics visualization
- Service dependency mapping and tracing
- Predictive failure detection and alerting
- Cost attribution and optimization insights
- Security and compliance monitoring
- Automated incident response workflows

Usage:
    >>> import openfinops as vc
    >>> from openfinops.observability import ObservabilityDashboard
    >>>
    >>> # Initialize observability platform
    >>> obs = ObservabilityDashboard()
    >>> obs.monitor_cluster('gpu-cluster-1', nodes=64)
    >>> obs.track_service('training-service', replicas=8)
    >>> obs.show_real_time_dashboard()
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



from .system_monitor import SystemHealthMonitor, ClusterMonitor, NodeMetrics
from .infrastructure_dashboard import InfrastructureDashboard, ResourceAnalyzer
from .distributed_telemetry import DistributedTelemetry, TraceVisualizer
from .performance_dashboard import PerformanceDashboard, BottleneckAnalyzer
from .service_mesh import ServiceMeshMonitor, DependencyMapper
from .alerting_engine import AlertingEngine, IncidentManager
from .cost_observatory import CostObservatory, ResourceOptimizer
from .security_monitor import SecurityMonitor, ComplianceTracker
from .observability_hub import ObservabilityHub, UnifiedDashboard

__all__ = [
    # Core System Monitoring
    "SystemHealthMonitor",
    "ClusterMonitor",
    "NodeMetrics",

    # Infrastructure Observability
    "InfrastructureDashboard",
    "ResourceAnalyzer",

    # Distributed System Telemetry
    "DistributedTelemetry",
    "TraceVisualizer",

    # Performance Analysis
    "PerformanceDashboard",
    "BottleneckAnalyzer",

    # Service Mesh Monitoring
    "ServiceMeshMonitor",
    "DependencyMapper",

    # Alerting & Incident Management
    "AlertingEngine",
    "IncidentManager",

    # Cost & Resource Optimization
    "CostObservatory",
    "ResourceOptimizer",

    # Security & Compliance
    "SecurityMonitor",
    "ComplianceTracker",

    # Unified Observability Platform
    "ObservabilityHub",
    "UnifiedDashboard",
]