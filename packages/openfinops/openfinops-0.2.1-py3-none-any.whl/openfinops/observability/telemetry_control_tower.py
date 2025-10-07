"""
OpenFinOps Telemetry Control Tower & Health Monitor
===============================================

Centralized control tower for telemetry infrastructure operations with comprehensive
health monitoring, agent management, and automated remediation capabilities.

Features:
- Centralized telemetry agent health monitoring
- Real-time infrastructure operations dashboard
- Automated agent deployment and scaling
- Cross-cloud telemetry coordination
- Incident response automation
- Cost optimization and resource management
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
import uuid
import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import hashlib

# Import OpenFinOps visualization components
try:
    from ..vizlychart.core.renderer import VizlyChart
    VIZLYCHART_AVAILABLE = True
except ImportError:
    VIZLYCHART_AVAILABLE = False


class AgentStatus(Enum):
    """Telemetry agent status states"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class InfrastructureHealth(Enum):
    """Infrastructure health levels"""
    OPTIMAL = "optimal"
    STABLE = "stable"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OUTAGE = "outage"


class IncidentSeverity(Enum):
    """Incident severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DeploymentStrategy(Enum):
    """Agent deployment strategies"""
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    IMMEDIATE = "immediate"


@dataclass
class TelemetryAgent:
    """Telemetry agent metadata and status"""
    agent_id: str
    hostname: str
    cloud_provider: str
    region: str
    instance_type: str
    agent_version: str
    status: AgentStatus
    last_heartbeat: float
    uptime_seconds: float

    # Resource metrics
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float

    # Telemetry metrics
    events_per_second: float
    data_ingestion_rate: float  # MB/s
    buffer_utilization: float
    error_rate: float

    # Health indicators
    connectivity_status: bool
    data_quality_score: float
    latency_ms: float

    # Configuration
    config_version: str
    features_enabled: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class InfrastructureCluster:
    """Infrastructure cluster information"""
    cluster_id: str
    cluster_name: str
    cloud_provider: str
    region: str
    environment: str
    agent_count: int
    healthy_agents: int
    total_capacity: float
    utilization: float
    health_status: InfrastructureHealth
    cost_per_hour: float


@dataclass
class TelemetryIncident:
    """Telemetry infrastructure incident"""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: str
    created_at: float
    updated_at: float
    affected_agents: List[str]
    affected_clusters: List[str]
    root_cause: Optional[str] = None
    resolution_steps: List[str] = field(default_factory=list)
    estimated_resolution: Optional[float] = None


@dataclass
class DeploymentTask:
    """Agent deployment task"""
    task_id: str
    target_agents: List[str]
    deployment_type: str  # 'update', 'config_change', 'restart'
    strategy: DeploymentStrategy
    config_payload: Dict[str, Any]
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    progress: float = 0.0
    errors: List[str] = field(default_factory=list)


class TelemetryControlTower:
    """Central control tower for telemetry infrastructure operations"""

    def __init__(self, control_tower_id: str = None):
        self.control_tower_id = control_tower_id or f"control-tower-{int(time.time())}"
        self.logger = logging.getLogger(__name__)

        # Agent registry and monitoring
        self.agents: Dict[str, TelemetryAgent] = {}
        self.clusters: Dict[str, InfrastructureCluster] = {}
        self.agent_groups: Dict[str, Set[str]] = defaultdict(set)

        # Health monitoring
        self.health_history = deque(maxlen=10000)
        self.alert_history = deque(maxlen=5000)
        self.incident_registry: Dict[str, TelemetryIncident] = {}

        # Operations management
        self.deployment_queue: List[DeploymentTask] = []
        self.active_deployments: Dict[str, DeploymentTask] = {}
        self.maintenance_windows: List[Dict[str, Any]] = []

        # Control tower state
        self.is_running = False
        self.monitoring_threads: List[threading.Thread] = []
        self.operation_lock = threading.Lock()

        # Configuration
        self.config = self._load_default_config()

        # Performance metrics
        self.metrics = {
            'total_agents': 0,
            'healthy_agents': 0,
            'data_ingestion_rate': 0.0,
            'average_latency': 0.0,
            'total_incidents': 0,
            'active_incidents': 0
        }

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default control tower configuration"""
        return {
            'monitoring': {
                'heartbeat_timeout': 300,  # 5 minutes
                'health_check_interval': 30,  # 30 seconds
                'metrics_retention_hours': 72,
                'alert_cooldown_minutes': 15
            },
            'deployment': {
                'default_strategy': DeploymentStrategy.ROLLING,
                'batch_size': 10,
                'rollback_on_failure': True,
                'health_check_grace_period': 60
            },
            'alerting': {
                'cpu_threshold': 85.0,
                'memory_threshold': 90.0,
                'error_rate_threshold': 5.0,
                'latency_threshold': 1000.0
            },
            'auto_remediation': {
                'enabled': True,
                'max_restart_attempts': 3,
                'escalation_threshold': 5
            }
        }

    def start_control_tower(self):
        """Start the telemetry control tower"""
        self.logger.info(f"Starting Telemetry Control Tower: {self.control_tower_id}")

        self.is_running = True

        # Start monitoring threads
        self.monitoring_threads = [
            threading.Thread(target=self._agent_health_monitor, daemon=True),
            threading.Thread(target=self._infrastructure_monitor, daemon=True),
            threading.Thread(target=self._deployment_processor, daemon=True),
            threading.Thread(target=self._incident_processor, daemon=True),
            threading.Thread(target=self._auto_remediation_engine, daemon=True)
        ]

        for thread in self.monitoring_threads:
            thread.start()

        self.logger.info("✅ Telemetry Control Tower started successfully")

    def stop_control_tower(self):
        """Stop the telemetry control tower"""
        self.logger.info("Stopping Telemetry Control Tower...")
        self.is_running = False

        # Wait for threads to complete
        for thread in self.monitoring_threads:
            thread.join(timeout=10)

        self.logger.info("✅ Telemetry Control Tower stopped")

    def register_agent(self, agent: TelemetryAgent):
        """Register a new telemetry agent"""
        with self.operation_lock:
            self.agents[agent.agent_id] = agent

            # Add to cluster group
            cluster_key = f"{agent.cloud_provider}-{agent.region}"
            self.agent_groups[cluster_key].add(agent.agent_id)

            # Update cluster information
            self._update_cluster_info(cluster_key)

        self.logger.info(f"Registered agent {agent.agent_id} on {agent.hostname}")

    def unregister_agent(self, agent_id: str):
        """Unregister a telemetry agent"""
        with self.operation_lock:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                cluster_key = f"{agent.cloud_provider}-{agent.region}"

                # Remove from groups
                self.agent_groups[cluster_key].discard(agent_id)

                # Remove agent
                del self.agents[agent_id]

                # Update cluster information
                self._update_cluster_info(cluster_key)

        self.logger.info(f"Unregistered agent {agent_id}")

    def update_agent_status(self, agent_id: str, status_update: Dict[str, Any]):
        """Update agent status and metrics"""
        with self.operation_lock:
            if agent_id in self.agents:
                agent = self.agents[agent_id]

                # Update fields from status_update
                for field, value in status_update.items():
                    if hasattr(agent, field):
                        setattr(agent, field, value)

                agent.last_heartbeat = time.time()

                # Determine health status
                agent.status = self._calculate_agent_health(agent)

    def _calculate_agent_health(self, agent: TelemetryAgent) -> AgentStatus:
        """Calculate agent health status based on metrics"""
        current_time = time.time()

        # Check connectivity
        if current_time - agent.last_heartbeat > self.config['monitoring']['heartbeat_timeout']:
            return AgentStatus.OFFLINE

        # Check resource utilization
        if (agent.cpu_usage > self.config['alerting']['cpu_threshold'] or
            agent.memory_usage > self.config['alerting']['memory_threshold']):
            return AgentStatus.CRITICAL

        # Check error rate
        if agent.error_rate > self.config['alerting']['error_rate_threshold']:
            return AgentStatus.WARNING

        # Check latency
        if agent.latency_ms > self.config['alerting']['latency_threshold']:
            return AgentStatus.WARNING

        # Check data quality
        if agent.data_quality_score < 0.8:
            return AgentStatus.DEGRADED

        return AgentStatus.HEALTHY

    def _update_cluster_info(self, cluster_key: str):
        """Update cluster information"""
        if cluster_key not in self.agent_groups:
            return

        agent_ids = self.agent_groups[cluster_key]
        if not agent_ids:
            return

        # Get agents in this cluster
        cluster_agents = [self.agents[aid] for aid in agent_ids if aid in self.agents]
        if not cluster_agents:
            return

        # Calculate cluster metrics
        total_agents = len(cluster_agents)
        healthy_agents = len([a for a in cluster_agents if a.status == AgentStatus.HEALTHY])

        avg_utilization = sum(a.cpu_usage for a in cluster_agents) / total_agents
        total_cost = sum(a.cost_per_hour for a in cluster_agents if hasattr(a, 'cost_per_hour'))

        # Determine cluster health
        health_ratio = healthy_agents / total_agents
        if health_ratio >= 0.95:
            cluster_health = InfrastructureHealth.OPTIMAL
        elif health_ratio >= 0.8:
            cluster_health = InfrastructureHealth.STABLE
        elif health_ratio >= 0.6:
            cluster_health = InfrastructureHealth.DEGRADED
        elif health_ratio >= 0.3:
            cluster_health = InfrastructureHealth.CRITICAL
        else:
            cluster_health = InfrastructureHealth.OUTAGE

        # Update or create cluster
        sample_agent = cluster_agents[0]
        self.clusters[cluster_key] = InfrastructureCluster(
            cluster_id=cluster_key,
            cluster_name=f"{sample_agent.cloud_provider.title()} {sample_agent.region}",
            cloud_provider=sample_agent.cloud_provider,
            region=sample_agent.region,
            environment="production",  # Could be derived from tags
            agent_count=total_agents,
            healthy_agents=healthy_agents,
            total_capacity=total_agents,
            utilization=avg_utilization,
            health_status=cluster_health,
            cost_per_hour=total_cost
        )

    def _agent_health_monitor(self):
        """Monitor agent health continuously"""
        while self.is_running:
            try:
                current_time = time.time()

                # Check each agent
                for agent_id, agent in list(self.agents.items()):
                    # Check for stale heartbeats
                    if current_time - agent.last_heartbeat > self.config['monitoring']['heartbeat_timeout']:
                        if agent.status != AgentStatus.OFFLINE:
                            self._create_incident(
                                title=f"Agent {agent_id} is offline",
                                description=f"Agent {agent_id} on {agent.hostname} has not sent heartbeat for {current_time - agent.last_heartbeat:.0f} seconds",
                                severity=IncidentSeverity.HIGH,
                                affected_agents=[agent_id]
                            )
                            agent.status = AgentStatus.OFFLINE

                    # Check for performance issues
                    if agent.status == AgentStatus.HEALTHY:
                        new_status = self._calculate_agent_health(agent)
                        if new_status != AgentStatus.HEALTHY:
                            agent.status = new_status
                            self._create_alert(
                                f"Agent {agent_id} health degraded to {new_status.value}",
                                agent_id
                            )

                # Update global metrics
                self._update_global_metrics()

                time.sleep(self.config['monitoring']['health_check_interval'])

            except Exception as e:
                self.logger.error(f"Error in agent health monitor: {e}")
                time.sleep(10)

    def _infrastructure_monitor(self):
        """Monitor overall infrastructure health"""
        while self.is_running:
            try:
                # Update cluster health
                for cluster_key in list(self.clusters.keys()):
                    self._update_cluster_info(cluster_key)

                # Check for infrastructure-wide issues
                total_clusters = len(self.clusters)
                if total_clusters > 0:
                    critical_clusters = len([c for c in self.clusters.values()
                                           if c.health_status in [InfrastructureHealth.CRITICAL, InfrastructureHealth.OUTAGE]])

                    if critical_clusters / total_clusters > 0.5:
                        self._create_incident(
                            title="Infrastructure-wide degradation detected",
                            description=f"{critical_clusters}/{total_clusters} clusters are in critical state",
                            severity=IncidentSeverity.CRITICAL,
                            affected_clusters=list(self.clusters.keys())
                        )

                time.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in infrastructure monitor: {e}")
                time.sleep(30)

    def _deployment_processor(self):
        """Process deployment tasks"""
        while self.is_running:
            try:
                with self.operation_lock:
                    # Process pending deployments
                    for task in list(self.deployment_queue):
                        if task.status == 'pending':
                            self._execute_deployment_task(task)
                            self.deployment_queue.remove(task)
                            self.active_deployments[task.task_id] = task

                # Check active deployments
                for task_id, task in list(self.active_deployments.items()):
                    if task.status in ['completed', 'failed']:
                        self._finalize_deployment(task)
                        del self.active_deployments[task_id]

                time.sleep(30)

            except Exception as e:
                self.logger.error(f"Error in deployment processor: {e}")
                time.sleep(10)

    def _incident_processor(self):
        """Process and manage incidents"""
        while self.is_running:
            try:
                current_time = time.time()

                # Auto-resolve incidents if conditions are met
                for incident_id, incident in list(self.incident_registry.items()):
                    if incident.status == 'open':
                        # Check if affected agents are now healthy
                        if all(self.agents.get(aid, type('obj', (object,), {'status': AgentStatus.OFFLINE})).status == AgentStatus.HEALTHY
                               for aid in incident.affected_agents):
                            incident.status = 'resolved'
                            incident.updated_at = current_time
                            self.logger.info(f"Auto-resolved incident {incident_id}: {incident.title}")

                time.sleep(120)  # Check every 2 minutes

            except Exception as e:
                self.logger.error(f"Error in incident processor: {e}")
                time.sleep(30)

    def _auto_remediation_engine(self):
        """Automated remediation for common issues"""
        while self.is_running:
            try:
                if not self.config['auto_remediation']['enabled']:
                    time.sleep(60)
                    continue

                # Check for agents that need remediation
                for agent_id, agent in list(self.agents.items()):
                    if agent.status in [AgentStatus.CRITICAL, AgentStatus.DEGRADED]:
                        self._attempt_auto_remediation(agent)

                time.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Error in auto-remediation engine: {e}")
                time.sleep(60)

    def _attempt_auto_remediation(self, agent: TelemetryAgent):
        """Attempt automated remediation for an agent"""
        remediation_history = getattr(agent, '_remediation_attempts', 0)
        max_attempts = self.config['auto_remediation']['max_restart_attempts']

        if remediation_history >= max_attempts:
            self.logger.warning(f"Max remediation attempts reached for agent {agent.agent_id}")
            return

        self.logger.info(f"Attempting auto-remediation for agent {agent.agent_id}")

        # Implement remediation strategies
        if agent.memory_usage > 90:
            self._restart_agent(agent.agent_id, "High memory usage")
        elif agent.error_rate > 10:
            self._restart_agent(agent.agent_id, "High error rate")
        elif agent.data_quality_score < 0.5:
            self._reconfigure_agent(agent.agent_id, {"data_validation": "strict"})

        # Track remediation attempts
        setattr(agent, '_remediation_attempts', remediation_history + 1)

    def _create_incident(self, title: str, description: str, severity: IncidentSeverity,
                        affected_agents: List[str] = None, affected_clusters: List[str] = None):
        """Create a new incident"""
        incident_id = f"INC-{int(time.time())}-{hashlib.md5(title.encode()).hexdigest()[:8]}"

        incident = TelemetryIncident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status='open',
            created_at=time.time(),
            updated_at=time.time(),
            affected_agents=affected_agents or [],
            affected_clusters=affected_clusters or []
        )

        self.incident_registry[incident_id] = incident
        self.logger.warning(f"Created incident {incident_id}: {title}")

        return incident_id

    def _create_alert(self, message: str, agent_id: str):
        """Create an alert"""
        alert = {
            'timestamp': time.time(),
            'message': message,
            'agent_id': agent_id,
            'severity': 'warning'
        }
        self.alert_history.append(alert)
        self.logger.warning(f"Alert: {message}")

    def _update_global_metrics(self):
        """Update global control tower metrics"""
        total_agents = len(self.agents)
        healthy_agents = len([a for a in self.agents.values() if a.status == AgentStatus.HEALTHY])

        total_ingestion = sum(a.data_ingestion_rate for a in self.agents.values())
        avg_latency = sum(a.latency_ms for a in self.agents.values()) / max(total_agents, 1)

        active_incidents = len([i for i in self.incident_registry.values() if i.status == 'open'])

        self.metrics.update({
            'total_agents': total_agents,
            'healthy_agents': healthy_agents,
            'data_ingestion_rate': total_ingestion,
            'average_latency': avg_latency,
            'total_incidents': len(self.incident_registry),
            'active_incidents': active_incidents
        })

    # Deployment Management Methods
    def deploy_agent_update(self, target_agents: List[str], new_version: str,
                           strategy: DeploymentStrategy = DeploymentStrategy.ROLLING) -> str:
        """Deploy agent updates"""
        task_id = f"deploy-{int(time.time())}"

        task = DeploymentTask(
            task_id=task_id,
            target_agents=target_agents,
            deployment_type='update',
            strategy=strategy,
            config_payload={'version': new_version},
            status='pending',
            created_at=time.time()
        )

        self.deployment_queue.append(task)
        self.logger.info(f"Queued deployment task {task_id} for {len(target_agents)} agents")

        return task_id

    def deploy_configuration_change(self, target_agents: List[str], config_changes: Dict[str, Any],
                                  strategy: DeploymentStrategy = DeploymentStrategy.ROLLING) -> str:
        """Deploy configuration changes"""
        task_id = f"config-{int(time.time())}"

        task = DeploymentTask(
            task_id=task_id,
            target_agents=target_agents,
            deployment_type='config_change',
            strategy=strategy,
            config_payload=config_changes,
            status='pending',
            created_at=time.time()
        )

        self.deployment_queue.append(task)
        self.logger.info(f"Queued configuration deployment {task_id} for {len(target_agents)} agents")

        return task_id

    def _execute_deployment_task(self, task: DeploymentTask):
        """Execute a deployment task"""
        task.status = 'in_progress'
        task.started_at = time.time()

        self.logger.info(f"Starting deployment task {task.task_id}")

        # Implement deployment strategy
        if task.strategy == DeploymentStrategy.ROLLING:
            self._execute_rolling_deployment(task)
        elif task.strategy == DeploymentStrategy.BLUE_GREEN:
            self._execute_blue_green_deployment(task)
        elif task.strategy == DeploymentStrategy.CANARY:
            self._execute_canary_deployment(task)
        else:
            self._execute_immediate_deployment(task)

    def _execute_rolling_deployment(self, task: DeploymentTask):
        """Execute rolling deployment"""
        batch_size = self.config['deployment']['batch_size']
        target_agents = task.target_agents

        for i in range(0, len(target_agents), batch_size):
            batch = target_agents[i:i + batch_size]

            # Deploy to batch
            for agent_id in batch:
                if agent_id in self.agents:
                    success = self._deploy_to_agent(agent_id, task.config_payload)
                    if not success:
                        task.errors.append(f"Failed to deploy to agent {agent_id}")

            # Update progress
            task.progress = min(100.0, (i + batch_size) / len(target_agents) * 100)

            # Health check grace period
            time.sleep(self.config['deployment']['health_check_grace_period'])

        task.status = 'completed' if not task.errors else 'failed'
        task.completed_at = time.time()

    def _deploy_to_agent(self, agent_id: str, config_payload: Dict[str, Any]) -> bool:
        """Deploy configuration to a specific agent"""
        # This would be implemented to actually communicate with the agent
        # For now, we simulate the deployment
        self.logger.info(f"Deploying to agent {agent_id}: {config_payload}")

        # Simulate deployment time
        time.sleep(1)

        # Simulate success/failure (90% success rate)
        import random
        return random.random() > 0.1

    def _restart_agent(self, agent_id: str, reason: str):
        """Restart a telemetry agent"""
        self.logger.info(f"Restarting agent {agent_id}: {reason}")
        # Implementation would send restart command to agent

    def _reconfigure_agent(self, agent_id: str, config_changes: Dict[str, Any]):
        """Reconfigure a telemetry agent"""
        self.logger.info(f"Reconfiguring agent {agent_id}: {config_changes}")
        # Implementation would send configuration changes to agent

    # Query and Reporting Methods
    def get_infrastructure_overview(self) -> Dict[str, Any]:
        """Get comprehensive infrastructure overview"""
        return {
            'control_tower_id': self.control_tower_id,
            'timestamp': time.time(),
            'global_metrics': self.metrics,
            'clusters': {k: asdict(v) for k, v in self.clusters.items()},
            'agent_summary': {
                'total': len(self.agents),
                'by_status': {
                    status.value: len([a for a in self.agents.values() if a.status == status])
                    for status in AgentStatus
                },
                'by_cloud': {
                    cloud: len([a for a in self.agents.values() if a.cloud_provider == cloud])
                    for cloud in set(a.cloud_provider for a in self.agents.values())
                }
            },
            'incidents': {
                'total': len(self.incident_registry),
                'active': len([i for i in self.incident_registry.values() if i.status == 'open']),
                'by_severity': {
                    sev.value: len([i for i in self.incident_registry.values()
                                  if i.severity == sev and i.status == 'open'])
                    for sev in IncidentSeverity
                }
            }
        }

    def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed agent information"""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        return {
            'agent': asdict(agent),
            'cluster': next((asdict(c) for c in self.clusters.values()
                           if agent_id in self.agent_groups.get(f"{agent.cloud_provider}-{agent.region}", set())), None),
            'recent_alerts': [alert for alert in list(self.alert_history)[-50:]
                            if alert.get('agent_id') == agent_id],
            'incidents': [asdict(i) for i in self.incident_registry.values()
                         if agent_id in i.affected_agents]
        }

    def generate_health_dashboard_data(self) -> Dict[str, Any]:
        """Generate data for health monitoring dashboard"""
        if not VIZLYCHART_AVAILABLE:
            return self._generate_basic_dashboard_data()

        # Generate professional dashboard with VizlyChart
        return self._generate_vizly_dashboard_data()

    def _generate_basic_dashboard_data(self) -> Dict[str, Any]:
        """Generate basic dashboard data without VizlyChart"""
        current_time = time.time()

        # Agent status distribution
        status_counts = defaultdict(int)
        for agent in self.agents.values():
            status_counts[agent.status.value] += 1

        # Cloud provider distribution
        cloud_counts = defaultdict(int)
        for agent in self.agents.values():
            cloud_counts[agent.cloud_provider] += 1

        # Recent metrics history (simulate time series)
        time_series = []
        for i in range(24):  # Last 24 hours
            timestamp = current_time - (23 - i) * 3600
            time_series.append({
                'timestamp': timestamp,
                'healthy_agents': len([a for a in self.agents.values() if a.status == AgentStatus.HEALTHY]),
                'total_agents': len(self.agents),
                'avg_latency': sum(a.latency_ms for a in self.agents.values()) / max(len(self.agents), 1),
                'data_ingestion': sum(a.data_ingestion_rate for a in self.agents.values())
            })

        return {
            'overview': self.get_infrastructure_overview(),
            'status_distribution': dict(status_counts),
            'cloud_distribution': dict(cloud_counts),
            'time_series': time_series,
            'top_alerts': list(self.alert_history)[-10:],
            'active_deployments': {k: asdict(v) for k, v in self.active_deployments.items()}
        }

    def export_telemetry_health_report(self, output_file: str = None) -> str:
        """Export comprehensive telemetry health report"""
        if output_file is None:
            output_file = f"telemetry_health_report_{int(time.time())}.json"

        report_data = {
            'report_metadata': {
                'generated_at': time.time(),
                'control_tower_id': self.control_tower_id,
                'report_version': '1.0'
            },
            'infrastructure_overview': self.get_infrastructure_overview(),
            'agent_details': {aid: asdict(agent) for aid, agent in self.agents.items()},
            'cluster_details': {cid: asdict(cluster) for cid, cluster in self.clusters.items()},
            'incident_history': {iid: asdict(incident) for iid, incident in self.incident_registry.items()},
            'deployment_history': [asdict(task) for task in self.deployment_queue + list(self.active_deployments.values())],
            'configuration': self.config
        }

        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        self.logger.info(f"Exported telemetry health report to {output_file}")
        return output_file


# Health Monitoring Dashboard Generator
class TelemetryHealthDashboard:
    """Generate visual health monitoring dashboards"""

    def __init__(self, control_tower: TelemetryControlTower):
        self.control_tower = control_tower

    def generate_operations_dashboard_html(self, output_file: str = "telemetry_operations_dashboard.html"):
        """Generate comprehensive operations dashboard"""
        dashboard_data = self.control_tower.generate_health_dashboard_data()
        overview = dashboard_data['overview']

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenFinOps Telemetry Control Tower</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }}

        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}

        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 1.1em; }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: rgba(255,255,255,0.15);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .metric-card:hover {{ transform: translateY(-5px); }}

        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .metric-label {{
            font-size: 1.1em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-left: 8px;
        }}

        .status-healthy {{ background: #4CAF50; }}
        .status-warning {{ background: #FF9800; }}
        .status-critical {{ background: #F44336; }}
        .status-offline {{ background: #757575; }}

        .clusters-section {{
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
        }}

        .cluster-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .cluster-card {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #4CAF50;
        }}

        .cluster-card.degraded {{ border-left-color: #FF9800; }}
        .cluster-card.critical {{ border-left-color: #F44336; }}

        .incidents-section {{
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 15px;
        }}

        .incident-item {{
            background: rgba(255,255,255,0.1);
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid #F44336;
        }}

        .refresh-indicator {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(76, 175, 80, 0.9);
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.9em;
        }}

        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
            100% {{ opacity: 1; }}
        }}

        .pulse {{ animation: pulse 2s infinite; }}
    </style>
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);

        // Update timestamp
        setInterval(() => {{
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        }}, 1000);
    </script>
</head>
<body>
    <div class="refresh-indicator">
        🔄 Auto-refresh: <span id="last-update">{datetime.now().strftime('%H:%M:%S')}</span>
    </div>

    <div class="container">
        <div class="header">
            <h1>🏗️ OpenFinOps Telemetry Control Tower</h1>
            <p>Real-time Infrastructure Operations & Health Monitoring</p>
            <p><strong>Control Tower ID:</strong> {overview['control_tower_id']}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{overview['global_metrics']['total_agents']}</div>
                <div class="metric-label">Total Agents</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview['global_metrics']['healthy_agents']}</div>
                <div class="metric-label">Healthy Agents</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview['global_metrics']['data_ingestion_rate']:.1f}</div>
                <div class="metric-label">Data Ingestion (MB/s)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview['global_metrics']['average_latency']:.0f}</div>
                <div class="metric-label">Avg Latency (ms)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{overview['global_metrics']['active_incidents']}</div>
                <div class="metric-label">Active Incidents</div>
            </div>
        </div>

        <div class="clusters-section">
            <h2>🌐 Infrastructure Clusters</h2>
            <div class="cluster-grid">
"""

        # Add cluster information
        for cluster_id, cluster in overview['clusters'].items():
            health_class = cluster['health_status'].lower()
            health_indicator = f"<span class='status-indicator status-{health_class}'></span>"

            html_content += f"""
                <div class="cluster-card {health_class}">
                    <h3>{cluster['cluster_name']} {health_indicator}</h3>
                    <p><strong>Provider:</strong> {cluster['cloud_provider'].title()}</p>
                    <p><strong>Region:</strong> {cluster['region']}</p>
                    <p><strong>Agents:</strong> {cluster['healthy_agents']}/{cluster['agent_count']}</p>
                    <p><strong>Utilization:</strong> {cluster['utilization']:.1f}%</p>
                    <p><strong>Cost/Hour:</strong> ${cluster['cost_per_hour']:.2f}</p>
                </div>
"""

        html_content += """
            </div>
        </div>

        <div class="incidents-section">
            <h2>🚨 Recent Incidents & Alerts</h2>
"""

        # Add recent incidents
        recent_incidents = sorted(
            overview.get('incidents', {}).items(),
            key=lambda x: x[1].get('created_at', 0) if isinstance(x[1], dict) else 0,
            reverse=True
        )[:5]

        if recent_incidents:
            for incident_id, incident in recent_incidents:
                if isinstance(incident, dict):
                    html_content += f"""
                <div class="incident-item">
                    <strong>{incident.get('title', 'Unknown Incident')}</strong>
                    <p>{incident.get('description', 'No description available')}</p>
                    <small>Severity: {incident.get('severity', 'unknown').title()} |
                    Status: {incident.get('status', 'unknown').title()}</small>
                </div>
"""
        else:
            html_content += "<p>✅ No recent incidents - system running smoothly!</p>"

        html_content += """
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file


# Example usage and testing
if __name__ == "__main__":
    # Create control tower
    control_tower = TelemetryControlTower("prod-control-tower-01")

    # Register some sample agents
    sample_agents = [
        TelemetryAgent(
            agent_id=f"agent-aws-{i}",
            hostname=f"ip-10-0-{i}-100",
            cloud_provider="aws",
            region="us-east-1",
            instance_type="t3.medium",
            agent_version="1.0.0",
            status=AgentStatus.HEALTHY,
            last_heartbeat=time.time(),
            uptime_seconds=3600 * 24,
            cpu_usage=30.0 + i * 5,
            memory_usage=40.0 + i * 3,
            disk_usage=20.0,
            network_io=15.5,
            events_per_second=1000.0,
            data_ingestion_rate=25.0,
            buffer_utilization=45.0,
            error_rate=0.1,
            connectivity_status=True,
            data_quality_score=0.95,
            latency_ms=150.0,
            config_version="v1.0",
            features_enabled=["metrics", "tracing", "logging"]
        ) for i in range(5)
    ]

    # Register agents
    for agent in sample_agents:
        control_tower.register_agent(agent)

    # Start control tower
    control_tower.start_control_tower()

    # Generate dashboard
    dashboard = TelemetryHealthDashboard(control_tower)
    dashboard_file = dashboard.generate_operations_dashboard_html()

    print(f"✅ Generated telemetry operations dashboard: {dashboard_file}")
    print(f"📊 Infrastructure overview: {json.dumps(control_tower.get_infrastructure_overview(), indent=2, default=str)}")

    # Let it run for a few seconds to see monitoring in action
    time.sleep(10)

    # Stop control tower
    control_tower.stop_control_tower()