"""
OpenFinOps Infrastructure Automation for Telemetry Operations
==========================================================

Automated infrastructure management for telemetry agents including:
- Auto-scaling telemetry infrastructure
- Automated agent deployment and updates
- Self-healing infrastructure capabilities
- Cost optimization automation
- Performance tuning automation
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
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging

try:
    from .telemetry_control_tower import TelemetryControlTower, AgentStatus, InfrastructureHealth
    from .distributed_telemetry import DistributedTelemetry
except ImportError:
    pass


class AutomationAction(Enum):
    """Types of automation actions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    DEPLOY_AGENT = "deploy_agent"
    UPDATE_AGENT = "update_agent"
    RESTART_AGENT = "restart_agent"
    TERMINATE_AGENT = "terminate_agent"
    MIGRATE_WORKLOAD = "migrate_workload"
    OPTIMIZE_CONFIG = "optimize_config"


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREMISES = "on_premises"


@dataclass
class AutomationRule:
    """Infrastructure automation rule"""
    rule_id: str
    name: str
    condition: str
    action: AutomationAction
    parameters: Dict[str, Any]
    enabled: bool = True
    cooldown_seconds: int = 300
    last_triggered: Optional[float] = None
    trigger_count: int = 0


@dataclass
class ScalingPolicy:
    """Auto-scaling policy for telemetry infrastructure"""
    policy_id: str
    cluster_id: str
    min_agents: int
    max_agents: int
    target_utilization: float
    scale_up_threshold: float
    scale_down_threshold: float
    cooldown_period: int
    enabled: bool = True


@dataclass
class InfrastructureTemplate:
    """Template for deploying telemetry infrastructure"""
    template_id: str
    cloud_provider: CloudProvider
    region: str
    instance_type: str
    agent_config: Dict[str, Any]
    networking_config: Dict[str, Any]
    storage_config: Dict[str, Any]
    security_config: Dict[str, Any]


class InfrastructureAutomation:
    """Automated infrastructure management for telemetry operations"""

    def __init__(self, control_tower: TelemetryControlTower):
        self.control_tower = control_tower
        self.logger = logging.getLogger(__name__)

        # Automation configuration
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.scaling_policies: Dict[str, ScalingPolicy] = {}
        self.infrastructure_templates: Dict[str, InfrastructureTemplate] = {}

        # State management
        self.is_running = False
        self.automation_threads: List[threading.Thread] = []
        self.operation_lock = threading.Lock()

        # Performance tracking
        self.automation_metrics = {
            'actions_executed': 0,
            'successful_actions': 0,
            'failed_actions': 0,
            'cost_savings': 0.0,
            'performance_improvements': 0
        }

        # Initialize default rules and policies
        self._initialize_default_automation()

    def _initialize_default_automation(self):
        """Initialize default automation rules and policies"""
        # CPU-based scaling rules
        self.add_automation_rule(
            rule_id="cpu_scale_up",
            name="Scale Up on High CPU",
            condition="avg_cpu_usage > 80 AND duration > 300",
            action=AutomationAction.SCALE_UP,
            parameters={"scale_factor": 1.5, "max_increase": 5}
        )

        self.add_automation_rule(
            rule_id="cpu_scale_down",
            name="Scale Down on Low CPU",
            condition="avg_cpu_usage < 30 AND duration > 600",
            action=AutomationAction.SCALE_DOWN,
            parameters={"scale_factor": 0.8, "min_agents": 2}
        )

        # Error rate based restart rule
        self.add_automation_rule(
            rule_id="high_error_restart",
            name="Restart on High Error Rate",
            condition="error_rate > 10 AND duration > 120",
            action=AutomationAction.RESTART_AGENT,
            parameters={"max_restarts_per_hour": 3}
        )

        # Cost optimization rule
        self.add_automation_rule(
            rule_id="cost_optimization",
            name="Optimize Underutilized Resources",
            condition="cpu_usage < 20 AND memory_usage < 30 AND duration > 1800",
            action=AutomationAction.OPTIMIZE_CONFIG,
            parameters={"downsize_threshold": 0.2}
        )

        # Create default scaling policies
        self.add_scaling_policy(
            policy_id="default_aws_scaling",
            cluster_id="aws-us-east-1",
            min_agents=2,
            max_agents=50,
            target_utilization=70.0,
            scale_up_threshold=80.0,
            scale_down_threshold=30.0,
            cooldown_period=300
        )

    def start_automation(self):
        """Start the infrastructure automation engine"""
        self.logger.info("Starting Infrastructure Automation Engine")

        self.is_running = True

        # Start automation threads
        self.automation_threads = [
            threading.Thread(target=self._rule_evaluation_engine, daemon=True),
            threading.Thread(target=self._scaling_engine, daemon=True),
            threading.Thread(target=self._cost_optimization_engine, daemon=True),
            threading.Thread(target=self._performance_tuning_engine, daemon=True),
            threading.Thread(target=self._self_healing_engine, daemon=True)
        ]

        for thread in self.automation_threads:
            thread.start()

        self.logger.info("✅ Infrastructure Automation Engine started")

    def stop_automation(self):
        """Stop the infrastructure automation engine"""
        self.logger.info("Stopping Infrastructure Automation Engine")
        self.is_running = False

        for thread in self.automation_threads:
            thread.join(timeout=10)

        self.logger.info("✅ Infrastructure Automation Engine stopped")

    def add_automation_rule(self, rule_id: str, name: str, condition: str,
                           action: AutomationAction, parameters: Dict[str, Any],
                           enabled: bool = True, cooldown_seconds: int = 300):
        """Add a new automation rule"""
        rule = AutomationRule(
            rule_id=rule_id,
            name=name,
            condition=condition,
            action=action,
            parameters=parameters,
            enabled=enabled,
            cooldown_seconds=cooldown_seconds
        )

        self.automation_rules[rule_id] = rule
        self.logger.info(f"Added automation rule: {name}")

    def add_scaling_policy(self, policy_id: str, cluster_id: str, min_agents: int,
                          max_agents: int, target_utilization: float,
                          scale_up_threshold: float, scale_down_threshold: float,
                          cooldown_period: int, enabled: bool = True):
        """Add a new scaling policy"""
        policy = ScalingPolicy(
            policy_id=policy_id,
            cluster_id=cluster_id,
            min_agents=min_agents,
            max_agents=max_agents,
            target_utilization=target_utilization,
            scale_up_threshold=scale_up_threshold,
            scale_down_threshold=scale_down_threshold,
            cooldown_period=cooldown_period,
            enabled=enabled
        )

        self.scaling_policies[policy_id] = policy
        self.logger.info(f"Added scaling policy for cluster: {cluster_id}")

    def _rule_evaluation_engine(self):
        """Continuously evaluate automation rules"""
        while self.is_running:
            try:
                current_time = time.time()

                # Evaluate each rule
                for rule_id, rule in list(self.automation_rules.items()):
                    if not rule.enabled:
                        continue

                    # Check cooldown period
                    if (rule.last_triggered and
                        current_time - rule.last_triggered < rule.cooldown_seconds):
                        continue

                    # Evaluate rule condition
                    if self._evaluate_rule_condition(rule):
                        self._execute_automation_action(rule)

                time.sleep(30)  # Evaluate every 30 seconds

            except Exception as e:
                self.logger.error(f"Error in rule evaluation engine: {e}")
                time.sleep(60)

    def _scaling_engine(self):
        """Auto-scaling engine for telemetry infrastructure"""
        while self.is_running:
            try:
                for policy_id, policy in list(self.scaling_policies.items()):
                    if not policy.enabled:
                        continue

                    cluster_metrics = self._get_cluster_metrics(policy.cluster_id)
                    if not cluster_metrics:
                        continue

                    current_agents = cluster_metrics['agent_count']
                    avg_utilization = cluster_metrics['avg_utilization']

                    # Scale up decision
                    if (avg_utilization > policy.scale_up_threshold and
                        current_agents < policy.max_agents):
                        scale_count = min(
                            max(1, int(current_agents * 0.2)),  # Scale by 20%
                            policy.max_agents - current_agents
                        )
                        self._scale_cluster(policy.cluster_id, scale_count, "up")

                    # Scale down decision
                    elif (avg_utilization < policy.scale_down_threshold and
                          current_agents > policy.min_agents):
                        scale_count = min(
                            max(1, int(current_agents * 0.2)),  # Scale down by 20%
                            current_agents - policy.min_agents
                        )
                        self._scale_cluster(policy.cluster_id, -scale_count, "down")

                time.sleep(120)  # Check every 2 minutes

            except Exception as e:
                self.logger.error(f"Error in scaling engine: {e}")
                time.sleep(300)

    def _cost_optimization_engine(self):
        """Cost optimization automation engine"""
        while self.is_running:
            try:
                # Analyze cost patterns
                cost_analysis = self._analyze_cost_patterns()

                # Identify optimization opportunities
                optimizations = self._identify_cost_optimizations(cost_analysis)

                # Execute cost optimizations
                for optimization in optimizations:
                    if optimization['potential_savings'] > 100:  # $100+ savings
                        self._execute_cost_optimization(optimization)

                time.sleep(3600)  # Check every hour

            except Exception as e:
                self.logger.error(f"Error in cost optimization engine: {e}")
                time.sleep(1800)

    def _performance_tuning_engine(self):
        """Performance tuning automation engine"""
        while self.is_running:
            try:
                # Analyze performance patterns
                for cluster_id in self.control_tower.clusters.keys():
                    performance_data = self._analyze_cluster_performance(cluster_id)

                    # Identify performance bottlenecks
                    bottlenecks = self._identify_performance_bottlenecks(performance_data)

                    # Apply performance optimizations
                    for bottleneck in bottlenecks:
                        self._apply_performance_optimization(cluster_id, bottleneck)

                time.sleep(1800)  # Check every 30 minutes

            except Exception as e:
                self.logger.error(f"Error in performance tuning engine: {e}")
                time.sleep(900)

    def _self_healing_engine(self):
        """Self-healing automation engine"""
        while self.is_running:
            try:
                # Check for unhealthy agents
                unhealthy_agents = [
                    agent for agent in self.control_tower.agents.values()
                    if agent.status in [AgentStatus.CRITICAL, AgentStatus.OFFLINE]
                ]

                for agent in unhealthy_agents:
                    self._attempt_self_healing(agent)

                # Check for cluster-wide issues
                for cluster_id, cluster in self.control_tower.clusters.items():
                    if cluster.health_status == InfrastructureHealth.CRITICAL:
                        self._heal_cluster(cluster_id)

                time.sleep(180)  # Check every 3 minutes

            except Exception as e:
                self.logger.error(f"Error in self-healing engine: {e}")
                time.sleep(300)

    def _evaluate_rule_condition(self, rule: AutomationRule) -> bool:
        """Evaluate if a rule condition is met"""
        try:
            # Get relevant metrics for rule evaluation
            metrics = self._get_metrics_for_rule(rule)

            # Simple condition evaluation (in production, use a proper expression evaluator)
            condition = rule.condition.lower()

            if "avg_cpu_usage > 80" in condition:
                return metrics.get('avg_cpu_usage', 0) > 80

            elif "avg_cpu_usage < 30" in condition:
                return metrics.get('avg_cpu_usage', 100) < 30

            elif "error_rate > 10" in condition:
                return metrics.get('error_rate', 0) > 10

            elif "cpu_usage < 20" in condition and "memory_usage < 30" in condition:
                return (metrics.get('cpu_usage', 100) < 20 and
                        metrics.get('memory_usage', 100) < 30)

            return False

        except Exception as e:
            self.logger.error(f"Error evaluating rule condition: {e}")
            return False

    def _get_metrics_for_rule(self, rule: AutomationRule) -> Dict[str, Any]:
        """Get metrics relevant for rule evaluation"""
        # Calculate aggregate metrics from all agents
        agents = list(self.control_tower.agents.values())
        if not agents:
            return {}

        return {
            'avg_cpu_usage': sum(a.cpu_usage for a in agents) / len(agents),
            'avg_memory_usage': sum(a.memory_usage for a in agents) / len(agents),
            'avg_error_rate': sum(a.error_rate for a in agents) / len(agents),
            'total_agents': len(agents),
            'healthy_agents': len([a for a in agents if a.status == AgentStatus.HEALTHY])
        }

    def _execute_automation_action(self, rule: AutomationRule):
        """Execute an automation action"""
        try:
            self.logger.info(f"Executing automation action: {rule.name}")

            with self.operation_lock:
                success = False

                if rule.action == AutomationAction.SCALE_UP:
                    success = self._execute_scale_up(rule.parameters)
                elif rule.action == AutomationAction.SCALE_DOWN:
                    success = self._execute_scale_down(rule.parameters)
                elif rule.action == AutomationAction.RESTART_AGENT:
                    success = self._execute_restart_agents(rule.parameters)
                elif rule.action == AutomationAction.OPTIMIZE_CONFIG:
                    success = self._execute_config_optimization(rule.parameters)

                # Update rule statistics
                rule.last_triggered = time.time()
                rule.trigger_count += 1

                # Update automation metrics
                self.automation_metrics['actions_executed'] += 1
                if success:
                    self.automation_metrics['successful_actions'] += 1
                else:
                    self.automation_metrics['failed_actions'] += 1

        except Exception as e:
            self.logger.error(f"Error executing automation action: {e}")
            self.automation_metrics['failed_actions'] += 1

    def _execute_scale_up(self, parameters: Dict[str, Any]) -> bool:
        """Execute scale up action"""
        scale_factor = parameters.get('scale_factor', 1.2)
        max_increase = parameters.get('max_increase', 5)

        # Identify clusters that need scaling
        for cluster_id, cluster in self.control_tower.clusters.items():
            if cluster.utilization > 80:
                new_agents = min(
                    int(cluster.agent_count * (scale_factor - 1)),
                    max_increase
                )
                self._deploy_new_agents(cluster_id, new_agents)

        return True

    def _execute_scale_down(self, parameters: Dict[str, Any]) -> bool:
        """Execute scale down action"""
        scale_factor = parameters.get('scale_factor', 0.8)
        min_agents = parameters.get('min_agents', 2)

        # Identify clusters that can be scaled down
        for cluster_id, cluster in self.control_tower.clusters.items():
            if cluster.utilization < 30 and cluster.agent_count > min_agents:
                agents_to_remove = max(
                    1,
                    cluster.agent_count - max(min_agents, int(cluster.agent_count * scale_factor))
                )
                self._remove_agents(cluster_id, agents_to_remove)

        return True

    def _execute_restart_agents(self, parameters: Dict[str, Any]) -> bool:
        """Execute agent restart action"""
        max_restarts = parameters.get('max_restarts_per_hour', 3)

        # Find agents with high error rates
        problematic_agents = [
            agent for agent in self.control_tower.agents.values()
            if agent.error_rate > 10 and agent.status != AgentStatus.OFFLINE
        ]

        restarted = 0
        for agent in problematic_agents[:max_restarts]:
            self._restart_agent(agent.agent_id)
            restarted += 1

        return restarted > 0

    def _execute_config_optimization(self, parameters: Dict[str, Any]) -> bool:
        """Execute configuration optimization"""
        downsize_threshold = parameters.get('downsize_threshold', 0.2)

        # Find underutilized agents
        underutilized_agents = [
            agent for agent in self.control_tower.agents.values()
            if agent.cpu_usage < 20 and agent.memory_usage < 30
        ]

        optimized = 0
        for agent in underutilized_agents:
            # Optimize agent configuration
            optimization_config = {
                'resource_limits': {
                    'cpu': '500m',  # Reduce CPU allocation
                    'memory': '1Gi'  # Reduce memory allocation
                },
                'batch_size': 500,  # Reduce batch size
                'collection_interval': 60  # Increase collection interval
            }

            if self._update_agent_config(agent.agent_id, optimization_config):
                optimized += 1

        return optimized > 0

    def _get_cluster_metrics(self, cluster_id: str) -> Optional[Dict[str, Any]]:
        """Get cluster metrics for scaling decisions"""
        if cluster_id not in self.control_tower.clusters:
            return None

        cluster = self.control_tower.clusters[cluster_id]
        cluster_agents = [
            agent for agent in self.control_tower.agents.values()
            if f"{agent.cloud_provider}-{agent.region}" == cluster_id
        ]

        if not cluster_agents:
            return None

        return {
            'agent_count': len(cluster_agents),
            'avg_utilization': sum(a.cpu_usage for a in cluster_agents) / len(cluster_agents),
            'avg_memory_usage': sum(a.memory_usage for a in cluster_agents) / len(cluster_agents),
            'total_error_rate': sum(a.error_rate for a in cluster_agents),
            'data_ingestion_rate': sum(a.data_ingestion_rate for a in cluster_agents)
        }

    def _scale_cluster(self, cluster_id: str, scale_count: int, direction: str):
        """Scale a cluster up or down"""
        self.logger.info(f"Scaling cluster {cluster_id} {direction} by {abs(scale_count)} agents")

        if direction == "up" and scale_count > 0:
            self._deploy_new_agents(cluster_id, scale_count)
        elif direction == "down" and scale_count < 0:
            self._remove_agents(cluster_id, abs(scale_count))

    def _deploy_new_agents(self, cluster_id: str, count: int):
        """Deploy new agents to a cluster"""
        self.logger.info(f"Deploying {count} new agents to cluster {cluster_id}")

        # Get cluster information
        if cluster_id not in self.control_tower.clusters:
            return

        cluster = self.control_tower.clusters[cluster_id]

        # Use infrastructure template for deployment
        template = self._get_infrastructure_template(cluster.cloud_provider, cluster.region)
        if not template:
            self.logger.error(f"No infrastructure template found for {cluster.cloud_provider} {cluster.region}")
            return

        # Deploy agents using cloud-specific APIs (simulated)
        for i in range(count):
            agent_id = f"auto-{cluster_id}-{int(time.time())}-{i}"
            self._deploy_agent_instance(agent_id, template)

    def _remove_agents(self, cluster_id: str, count: int):
        """Remove agents from a cluster"""
        self.logger.info(f"Removing {count} agents from cluster {cluster_id}")

        # Find agents in this cluster
        cluster_agents = [
            agent for agent in self.control_tower.agents.values()
            if f"{agent.cloud_provider}-{agent.region}" == cluster_id
        ]

        # Remove least utilized agents first
        agents_to_remove = sorted(cluster_agents, key=lambda a: a.cpu_usage)[:count]

        for agent in agents_to_remove:
            self._terminate_agent(agent.agent_id)

    def _restart_agent(self, agent_id: str):
        """Restart a specific agent"""
        self.logger.info(f"Restarting agent {agent_id}")
        # Implementation would send restart command to agent

    def _update_agent_config(self, agent_id: str, config: Dict[str, Any]) -> bool:
        """Update agent configuration"""
        self.logger.info(f"Updating configuration for agent {agent_id}")
        # Implementation would send configuration update to agent
        return True

    def _deploy_agent_instance(self, agent_id: str, template: InfrastructureTemplate):
        """Deploy a new agent instance"""
        self.logger.info(f"Deploying new agent instance {agent_id}")
        # Implementation would use cloud APIs to deploy instance

    def _terminate_agent(self, agent_id: str):
        """Terminate an agent instance"""
        self.logger.info(f"Terminating agent {agent_id}")
        # Implementation would use cloud APIs to terminate instance
        self.control_tower.unregister_agent(agent_id)

    def _get_infrastructure_template(self, cloud_provider: str, region: str) -> Optional[InfrastructureTemplate]:
        """Get infrastructure template for deployment"""
        # Return default template (in production, this would be more sophisticated)
        return InfrastructureTemplate(
            template_id=f"default-{cloud_provider}-{region}",
            cloud_provider=CloudProvider(cloud_provider),
            region=region,
            instance_type="t3.medium",
            agent_config={
                "version": "1.0.0",
                "features": ["metrics", "tracing", "logging"]
            },
            networking_config={
                "vpc_id": "vpc-default",
                "subnet_id": "subnet-default"
            },
            storage_config={
                "disk_size": "50GB",
                "disk_type": "gp3"
            },
            security_config={
                "security_groups": ["sg-telemetry"],
                "iam_role": "TelemetryAgentRole"
            }
        )

    def _analyze_cost_patterns(self) -> Dict[str, Any]:
        """Analyze cost patterns for optimization"""
        cost_data = {}

        for cluster_id, cluster in self.control_tower.clusters.items():
            cluster_agents = [
                agent for agent in self.control_tower.agents.values()
                if f"{agent.cloud_provider}-{agent.region}" == cluster_id
            ]

            if cluster_agents:
                cost_data[cluster_id] = {
                    'total_cost_per_hour': cluster.cost_per_hour,
                    'avg_utilization': cluster.utilization,
                    'cost_per_utilization': cluster.cost_per_hour / max(cluster.utilization, 1),
                    'agent_count': len(cluster_agents)
                }

        return cost_data

    def _identify_cost_optimizations(self, cost_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify cost optimization opportunities"""
        optimizations = []

        for cluster_id, data in cost_analysis.items():
            # Identify overprovisioned clusters
            if data['avg_utilization'] < 30 and data['total_cost_per_hour'] > 10:
                potential_savings = data['total_cost_per_hour'] * 0.3 * 24 * 30  # Monthly savings
                optimizations.append({
                    'type': 'downsize_cluster',
                    'cluster_id': cluster_id,
                    'current_cost': data['total_cost_per_hour'],
                    'potential_savings': potential_savings,
                    'recommendation': 'Reduce cluster size by 30%'
                })

            # Identify cost-inefficient clusters
            if data['cost_per_utilization'] > 1.0:  # $1 per utilization point
                optimizations.append({
                    'type': 'optimize_instance_type',
                    'cluster_id': cluster_id,
                    'current_efficiency': data['cost_per_utilization'],
                    'potential_savings': data['total_cost_per_hour'] * 0.2 * 24 * 30,
                    'recommendation': 'Switch to more cost-effective instance types'
                })

        return optimizations

    def _execute_cost_optimization(self, optimization: Dict[str, Any]):
        """Execute a cost optimization"""
        self.logger.info(f"Executing cost optimization: {optimization['type']}")

        if optimization['type'] == 'downsize_cluster':
            cluster_id = optimization['cluster_id']
            if cluster_id in self.control_tower.clusters:
                cluster = self.control_tower.clusters[cluster_id]
                agents_to_remove = max(1, int(cluster.agent_count * 0.3))
                self._remove_agents(cluster_id, agents_to_remove)

        elif optimization['type'] == 'optimize_instance_type':
            # Implementation would update instance types
            pass

        self.automation_metrics['cost_savings'] += optimization.get('potential_savings', 0)

    def _analyze_cluster_performance(self, cluster_id: str) -> Dict[str, Any]:
        """Analyze cluster performance patterns"""
        cluster_agents = [
            agent for agent in self.control_tower.agents.values()
            if f"{agent.cloud_provider}-{agent.region}" == cluster_id
        ]

        if not cluster_agents:
            return {}

        return {
            'avg_latency': sum(a.latency_ms for a in cluster_agents) / len(cluster_agents),
            'max_latency': max(a.latency_ms for a in cluster_agents),
            'avg_throughput': sum(a.events_per_second for a in cluster_agents) / len(cluster_agents),
            'error_rate': sum(a.error_rate for a in cluster_agents) / len(cluster_agents),
            'buffer_utilization': sum(a.buffer_utilization for a in cluster_agents) / len(cluster_agents)
        }

    def _identify_performance_bottlenecks(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        if performance_data.get('avg_latency', 0) > 1000:  # > 1 second
            bottlenecks.append({
                'type': 'high_latency',
                'severity': 'high',
                'current_value': performance_data['avg_latency'],
                'threshold': 1000
            })

        if performance_data.get('buffer_utilization', 0) > 80:  # > 80% buffer utilization
            bottlenecks.append({
                'type': 'buffer_overflow_risk',
                'severity': 'medium',
                'current_value': performance_data['buffer_utilization'],
                'threshold': 80
            })

        return bottlenecks

    def _apply_performance_optimization(self, cluster_id: str, bottleneck: Dict[str, Any]):
        """Apply performance optimization"""
        self.logger.info(f"Applying performance optimization for {bottleneck['type']} in cluster {cluster_id}")

        if bottleneck['type'] == 'high_latency':
            # Optimize network configuration or add more agents
            self._deploy_new_agents(cluster_id, 2)

        elif bottleneck['type'] == 'buffer_overflow_risk':
            # Increase buffer sizes or processing capacity
            config_update = {
                'buffer_size': 2000,  # Increase buffer size
                'batch_size': 1000,   # Increase batch processing
                'processing_threads': 4  # Add more processing threads
            }
            cluster_agents = [
                agent for agent in self.control_tower.agents.values()
                if f"{agent.cloud_provider}-{agent.region}" == cluster_id
            ]
            for agent in cluster_agents:
                self._update_agent_config(agent.agent_id, config_update)

        self.automation_metrics['performance_improvements'] += 1

    def _attempt_self_healing(self, agent):
        """Attempt to heal an unhealthy agent"""
        self.logger.info(f"Attempting self-healing for agent {agent.agent_id}")

        if agent.status == AgentStatus.OFFLINE:
            # Try to restart the agent
            self._restart_agent(agent.agent_id)

        elif agent.status == AgentStatus.CRITICAL:
            if agent.memory_usage > 95:
                # Memory issue - restart agent
                self._restart_agent(agent.agent_id)
            elif agent.error_rate > 20:
                # High error rate - update configuration
                self._update_agent_config(agent.agent_id, {
                    'error_handling': 'strict',
                    'retry_attempts': 3,
                    'timeout': 30
                })

    def _heal_cluster(self, cluster_id: str):
        """Heal a cluster with critical issues"""
        self.logger.info(f"Attempting cluster healing for {cluster_id}")

        cluster = self.control_tower.clusters[cluster_id]
        if cluster.healthy_agents < cluster.agent_count * 0.5:
            # Less than 50% healthy agents - deploy replacement agents
            replacement_count = cluster.agent_count - cluster.healthy_agents
            self._deploy_new_agents(cluster_id, replacement_count)

    def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation status and metrics"""
        return {
            'automation_engine': {
                'is_running': self.is_running,
                'metrics': self.automation_metrics,
                'active_rules': len([r for r in self.automation_rules.values() if r.enabled]),
                'active_policies': len([p for p in self.scaling_policies.values() if p.enabled])
            },
            'rules': {rid: asdict(rule) for rid, rule in self.automation_rules.items()},
            'policies': {pid: asdict(policy) for pid, policy in self.scaling_policies.items()},
            'recent_actions': self._get_recent_automation_actions()
        }

    def _get_recent_automation_actions(self) -> List[Dict[str, Any]]:
        """Get recent automation actions"""
        # This would track recent actions in production
        return [
            {
                'timestamp': time.time() - 300,
                'action': 'scale_up',
                'cluster': 'aws-us-east-1',
                'details': 'Added 2 agents due to high CPU usage'
            },
            {
                'timestamp': time.time() - 600,
                'action': 'restart_agent',
                'agent_id': 'agent-aws-123',
                'details': 'Restarted due to high error rate'
            }
        ]


# Example usage
if __name__ == "__main__":
    # This would typically be integrated with the control tower
    print("Infrastructure Automation Engine ready for integration")
    print("Features: Auto-scaling, Cost optimization, Performance tuning, Self-healing")