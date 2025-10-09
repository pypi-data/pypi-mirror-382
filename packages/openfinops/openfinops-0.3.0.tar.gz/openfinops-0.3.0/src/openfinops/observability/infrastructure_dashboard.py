"""
Infrastructure Monitoring and Resource Analysis Dashboard
=========================================================

Comprehensive infrastructure observability system for AI training environments
with resource analysis, capacity planning, and optimization recommendations.

Features:
- Multi-tier infrastructure monitoring
- Resource utilization analysis
- Capacity planning and forecasting
- Cost optimization recommendations
- Infrastructure health scoring
- Automated scaling recommendations
- Multi-cloud resource management
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
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import statistics


class InfrastructureType(Enum):
    """Infrastructure component types"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    MEMORY = "memory"
    DATABASE = "database"
    CACHE = "cache"
    LOAD_BALANCER = "load_balancer"


class ResourceStatus(Enum):
    """Resource health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


@dataclass
class ResourceMetrics:
    """Infrastructure resource metrics"""
    resource_id: str
    resource_type: InfrastructureType
    timestamp: float
    status: ResourceStatus

    # Utilization metrics
    cpu_utilization: Optional[float] = None
    memory_utilization: Optional[float] = None
    storage_utilization: Optional[float] = None
    network_utilization: Optional[float] = None

    # Capacity metrics
    total_capacity: Optional[float] = None
    available_capacity: Optional[float] = None
    reserved_capacity: Optional[float] = None

    # Performance metrics
    throughput: Optional[float] = None
    latency_ms: Optional[float] = None
    error_rate: Optional[float] = None
    queue_depth: Optional[int] = None

    # Cost metrics
    hourly_cost: Optional[float] = None
    monthly_cost_projection: Optional[float] = None

    # Metadata
    region: Optional[str] = None
    availability_zone: Optional[str] = None
    instance_type: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class CapacityForecast:
    """Infrastructure capacity planning forecast"""
    resource_type: InfrastructureType
    current_utilization: float
    projected_utilization_30d: float
    projected_utilization_90d: float
    capacity_exhaustion_date: Optional[datetime] = None
    recommended_scaling_action: str = "none"
    confidence_level: float = 0.0
    cost_impact: Optional[float] = None


@dataclass
class OptimizationRecommendation:
    """Resource optimization recommendation"""
    recommendation_id: str
    resource_id: str
    optimization_type: str  # 'rightsizing', 'scheduling', 'migration', 'termination'
    current_state: str
    recommended_state: str
    estimated_savings: float  # Monthly savings in dollars
    implementation_effort: str  # 'low', 'medium', 'high'
    risk_level: str  # 'low', 'medium', 'high'
    description: str
    implementation_steps: List[str]


class InfrastructureDashboard:
    """Infrastructure monitoring and analysis dashboard"""

    def __init__(self, collection_interval: float = 30.0):
        self.collection_interval = collection_interval
        self.resource_metrics = defaultdict(lambda: deque(maxlen=2880))  # 24 hours at 30s intervals
        self.infrastructure_inventory = {}
        self.is_monitoring = False
        self.monitoring_thread = None
        self.collection_lock = threading.Lock()

        # Cost tracking
        self.cost_history = deque(maxlen=8640)  # 72 hours of cost data
        self.cost_budgets = {}
        self.cost_alerts = []

        # Capacity planning
        self.capacity_models = {}
        self.scaling_recommendations = []

    def register_resource(self, resource_id: str, resource_type: InfrastructureType,
                         instance_type: str = None, region: str = None,
                         availability_zone: str = None, tags: Dict[str, str] = None):
        """Register infrastructure resource for monitoring"""
        self.infrastructure_inventory[resource_id] = {
            'resource_type': resource_type,
            'instance_type': instance_type,
            'region': region,
            'availability_zone': availability_zone,
            'tags': tags or {},
            'registration_time': time.time()
        }

    def add_metrics(self, metrics: ResourceMetrics):
        """Add resource metrics to monitoring system"""
        with self.collection_lock:
            self.resource_metrics[metrics.resource_id].append(metrics)

            # Update cost tracking
            if metrics.hourly_cost:
                self.cost_history.append({
                    'timestamp': metrics.timestamp,
                    'resource_id': metrics.resource_id,
                    'cost': metrics.hourly_cost,
                    'resource_type': metrics.resource_type.value
                })

    def get_resource_health(self, resource_id: str) -> Dict[str, Any]:
        """Get comprehensive resource health analysis"""
        with self.collection_lock:
            metrics_history = list(self.resource_metrics[resource_id])

        if not metrics_history:
            return {"status": "unknown", "message": "No metrics available"}

        recent_metrics = metrics_history[-10:]  # Last 10 samples
        current = recent_metrics[-1]

        # Calculate health score
        health_score = self._calculate_health_score(recent_metrics)

        # Determine status
        if health_score >= 80:
            status = ResourceStatus.HEALTHY
        elif health_score >= 60:
            status = ResourceStatus.WARNING
        else:
            status = ResourceStatus.CRITICAL

        # Generate health insights
        insights = self._generate_health_insights(recent_metrics)

        return {
            "resource_id": resource_id,
            "status": status.value,
            "health_score": health_score,
            "current_metrics": asdict(current),
            "insights": insights,
            "last_updated": current.timestamp
        }

    def _calculate_health_score(self, metrics: List[ResourceMetrics]) -> float:
        """Calculate resource health score (0-100)"""
        if not metrics:
            return 0.0

        score_components = []

        # Utilization score (optimal is 60-80% range)
        avg_cpu = statistics.mean([m.cpu_utilization for m in metrics if m.cpu_utilization is not None])
        if avg_cpu is not None:
            if 60 <= avg_cpu <= 80:
                cpu_score = 100
            elif avg_cpu < 60:
                cpu_score = max(50, 100 - (60 - avg_cpu) * 1.5)
            else:
                cpu_score = max(0, 100 - (avg_cpu - 80) * 2)
            score_components.append(cpu_score)

        # Memory utilization score
        avg_memory = statistics.mean([m.memory_utilization for m in metrics if m.memory_utilization is not None])
        if avg_memory is not None:
            if avg_memory <= 85:
                memory_score = 100 - avg_memory * 0.5
            else:
                memory_score = max(0, 100 - (avg_memory - 85) * 4)
            score_components.append(memory_score)

        # Error rate score
        avg_error_rate = statistics.mean([m.error_rate for m in metrics if m.error_rate is not None])
        if avg_error_rate is not None:
            error_score = max(0, 100 - avg_error_rate * 20)
            score_components.append(error_score)

        # Latency score
        avg_latency = statistics.mean([m.latency_ms for m in metrics if m.latency_ms is not None])
        if avg_latency is not None:
            if avg_latency <= 100:
                latency_score = 100
            else:
                latency_score = max(0, 100 - (avg_latency - 100) * 0.1)
            score_components.append(latency_score)

        return statistics.mean(score_components) if score_components else 50.0

    def _generate_health_insights(self, metrics: List[ResourceMetrics]) -> List[str]:
        """Generate actionable health insights"""
        insights = []

        if not metrics:
            return insights

        # Analyze trends
        recent = metrics[-5:] if len(metrics) >= 5 else metrics
        older = metrics[-10:-5] if len(metrics) >= 10 else []

        # CPU utilization insights
        cpu_values = [m.cpu_utilization for m in recent if m.cpu_utilization is not None]
        if cpu_values:
            avg_cpu = statistics.mean(cpu_values)
            if avg_cpu > 90:
                insights.append("🔥 Critical: CPU utilization critically high - immediate action required")
            elif avg_cpu > 80:
                insights.append("⚠️  Warning: High CPU utilization - consider scaling")
            elif avg_cpu < 20:
                insights.append("💡 Optimization: Low CPU utilization - consider rightsizing")

        # Memory utilization insights
        memory_values = [m.memory_utilization for m in recent if m.memory_utilization is not None]
        if memory_values:
            avg_memory = statistics.mean(memory_values)
            if avg_memory > 95:
                insights.append("🚨 Critical: Memory exhaustion risk - immediate scaling needed")
            elif avg_memory > 85:
                insights.append("⚠️  Warning: High memory pressure detected")

        # Error rate insights
        error_values = [m.error_rate for m in recent if m.error_rate is not None]
        if error_values:
            avg_errors = statistics.mean(error_values)
            if avg_errors > 5:
                insights.append("🐛 Quality: High error rate detected - investigate failures")

        # Performance trend insights
        if older and recent:
            cpu_trend = statistics.mean([m.cpu_utilization for m in recent if m.cpu_utilization is not None]) - \
                       statistics.mean([m.cpu_utilization for m in older if m.cpu_utilization is not None])
            if abs(cpu_trend) > 10:
                direction = "increasing" if cpu_trend > 0 else "decreasing"
                insights.append(f"📈 Trend: CPU utilization {direction} by {abs(cpu_trend):.1f}%")

        return insights


class ResourceAnalyzer:
    """Advanced resource analysis and optimization engine"""

    def __init__(self, dashboard: InfrastructureDashboard):
        self.dashboard = dashboard

    def analyze_capacity_planning(self, resource_type: InfrastructureType = None,
                                 forecast_days: int = 90) -> List[CapacityForecast]:
        """Perform capacity planning analysis"""
        forecasts = []

        resource_types = [resource_type] if resource_type else list(InfrastructureType)

        for r_type in resource_types:
            # Find resources of this type
            type_resources = [
                resource_id for resource_id, info in self.dashboard.infrastructure_inventory.items()
                if info['resource_type'] == r_type
            ]

            if not type_resources:
                continue

            # Aggregate utilization data
            utilization_data = []
            with self.dashboard.collection_lock:
                for resource_id in type_resources:
                    metrics = list(self.dashboard.resource_metrics[resource_id])
                    for metric in metrics:
                        if metric.cpu_utilization is not None:
                            utilization_data.append({
                                'timestamp': metric.timestamp,
                                'utilization': metric.cpu_utilization,
                                'resource_id': resource_id
                            })

            if len(utilization_data) < 10:  # Need sufficient data
                continue

            # Perform trend analysis
            forecast = self._generate_capacity_forecast(utilization_data, r_type, forecast_days)
            if forecast:
                forecasts.append(forecast)

        return forecasts

    def _generate_capacity_forecast(self, utilization_data: List[Dict],
                                  resource_type: InfrastructureType,
                                  forecast_days: int) -> Optional[CapacityForecast]:
        """Generate capacity forecast using trend analysis"""
        if len(utilization_data) < 10:
            return None

        # Sort by timestamp
        utilization_data.sort(key=lambda x: x['timestamp'])

        # Calculate trend using linear regression
        timestamps = [d['timestamp'] for d in utilization_data]
        utilizations = [d['utilization'] for d in utilization_data]

        # Simple linear trend calculation
        n = len(timestamps)
        sum_t = sum(timestamps)
        sum_u = sum(utilizations)
        sum_tu = sum(t * u for t, u in zip(timestamps, utilizations))
        sum_t2 = sum(t * t for t in timestamps)

        # Linear regression: u = a + b*t
        b = (n * sum_tu - sum_t * sum_u) / (n * sum_t2 - sum_t * sum_t)
        a = (sum_u - b * sum_t) / n

        current_time = max(timestamps)
        current_utilization = a + b * current_time

        # Project forward
        future_30d = current_time + (30 * 24 * 3600)
        future_90d = current_time + (90 * 24 * 3600)

        projected_30d = a + b * future_30d
        projected_90d = a + b * future_90d

        # Estimate when capacity will be exhausted
        capacity_exhaustion_date = None
        if b > 0:  # Increasing trend
            time_to_100 = (100 - current_utilization) / (b * 24 * 3600)  # Days to reach 100%
            if time_to_100 > 0:
                capacity_exhaustion_date = datetime.fromtimestamp(current_time + time_to_100 * 24 * 3600)

        # Determine recommended action
        recommended_action = "none"
        if projected_30d > 85:
            recommended_action = "scale_up"
        elif projected_90d < 30:
            recommended_action = "scale_down"
        elif b > 0.1:  # Rapid growth
            recommended_action = "monitor_closely"

        # Calculate confidence based on data consistency
        utilization_variance = statistics.variance(utilizations) if len(utilizations) > 1 else 0
        confidence = max(0.3, min(0.95, 1.0 - (utilization_variance / 100)))

        return CapacityForecast(
            resource_type=resource_type,
            current_utilization=current_utilization,
            projected_utilization_30d=max(0, min(100, projected_30d)),
            projected_utilization_90d=max(0, min(100, projected_90d)),
            capacity_exhaustion_date=capacity_exhaustion_date,
            recommended_scaling_action=recommended_action,
            confidence_level=confidence
        )

    def generate_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """Generate cost and performance optimization recommendations"""
        recommendations = []

        with self.dashboard.collection_lock:
            for resource_id, metrics_deque in self.dashboard.resource_metrics.items():
                metrics = list(metrics_deque)
                if len(metrics) < 5:  # Need sufficient data
                    continue

                recent_metrics = metrics[-20:]  # Last 20 samples
                resource_info = self.dashboard.infrastructure_inventory.get(resource_id, {})

                # Analyze for rightsizing opportunities
                rightsizing_rec = self._analyze_rightsizing(resource_id, recent_metrics, resource_info)
                if rightsizing_rec:
                    recommendations.append(rightsizing_rec)

                # Analyze for scheduling optimizations
                scheduling_rec = self._analyze_scheduling(resource_id, recent_metrics, resource_info)
                if scheduling_rec:
                    recommendations.append(scheduling_rec)

                # Analyze for termination candidates
                termination_rec = self._analyze_termination(resource_id, recent_metrics, resource_info)
                if termination_rec:
                    recommendations.append(termination_rec)

        # Sort by estimated savings
        recommendations.sort(key=lambda r: r.estimated_savings, reverse=True)
        return recommendations

    def _analyze_rightsizing(self, resource_id: str, metrics: List[ResourceMetrics],
                           resource_info: Dict) -> Optional[OptimizationRecommendation]:
        """Analyze rightsizing opportunities"""
        if not metrics:
            return None

        avg_cpu = statistics.mean([m.cpu_utilization for m in metrics if m.cpu_utilization is not None])
        avg_memory = statistics.mean([m.memory_utilization for m in metrics if m.memory_utilization is not None])

        if avg_cpu is None or avg_memory is None:
            return None

        # Check for underutilization
        if avg_cpu < 25 and avg_memory < 25:
            return OptimizationRecommendation(
                recommendation_id=f"rightsize_{resource_id}_{int(time.time())}",
                resource_id=resource_id,
                optimization_type="rightsizing",
                current_state=resource_info.get('instance_type', 'unknown'),
                recommended_state="smaller_instance",
                estimated_savings=200.0,  # Estimate based on typical instance costs
                implementation_effort="low",
                risk_level="low",
                description=f"Resource consistently underutilized (CPU: {avg_cpu:.1f}%, Memory: {avg_memory:.1f}%)",
                implementation_steps=[
                    "1. Schedule maintenance window",
                    "2. Create snapshot/backup if needed",
                    "3. Resize to smaller instance type",
                    "4. Monitor performance after change"
                ]
            )

        # Check for overutilization
        elif avg_cpu > 80 or avg_memory > 85:
            return OptimizationRecommendation(
                recommendation_id=f"upsize_{resource_id}_{int(time.time())}",
                resource_id=resource_id,
                optimization_type="rightsizing",
                current_state=resource_info.get('instance_type', 'unknown'),
                recommended_state="larger_instance",
                estimated_savings=-150.0,  # Negative because it costs more but improves performance
                implementation_effort="medium",
                risk_level="low",
                description=f"Resource overutilized (CPU: {avg_cpu:.1f}%, Memory: {avg_memory:.1f}%)",
                implementation_steps=[
                    "1. Plan for increased costs",
                    "2. Schedule maintenance window",
                    "3. Resize to larger instance type",
                    "4. Verify improved performance"
                ]
            )

        return None

    def _analyze_scheduling(self, resource_id: str, metrics: List[ResourceMetrics],
                          resource_info: Dict) -> Optional[OptimizationRecommendation]:
        """Analyze scheduling optimization opportunities"""
        # This would analyze usage patterns to recommend scheduled scaling
        # For now, return None - could be expanded with time-series analysis
        return None

    def _analyze_termination(self, resource_id: str, metrics: List[ResourceMetrics],
                           resource_info: Dict) -> Optional[OptimizationRecommendation]:
        """Analyze resources that could be terminated"""
        if not metrics or len(metrics) < 10:
            return None

        recent_metrics = metrics[-10:]

        # Check for consistently zero utilization
        cpu_values = [m.cpu_utilization for m in recent_metrics if m.cpu_utilization is not None]
        memory_values = [m.memory_utilization for m in recent_metrics if m.memory_utilization is not None]

        if cpu_values and memory_values:
            max_cpu = max(cpu_values)
            max_memory = max(memory_values)

            if max_cpu < 5 and max_memory < 10:  # Essentially unused
                return OptimizationRecommendation(
                    recommendation_id=f"terminate_{resource_id}_{int(time.time())}",
                    resource_id=resource_id,
                    optimization_type="termination",
                    current_state="running",
                    recommended_state="terminated",
                    estimated_savings=500.0,  # Full cost savings
                    implementation_effort="low",
                    risk_level="medium",
                    description="Resource appears unused - consider termination",
                    implementation_steps=[
                        "1. Verify resource is truly unused",
                        "2. Check for dependencies",
                        "3. Create backup if needed",
                        "4. Terminate resource",
                        "5. Monitor for any issues"
                    ]
                )

        return None

    def generate_cost_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive cost analysis"""
        with self.dashboard.collection_lock:
            cost_data = list(self.dashboard.cost_history)

        if not cost_data:
            return {"error": "No cost data available"}

        # Current period cost analysis
        now = time.time()
        daily_cost = sum(entry['cost'] for entry in cost_data if now - entry['timestamp'] <= 86400)
        weekly_cost = sum(entry['cost'] for entry in cost_data if now - entry['timestamp'] <= 604800)
        monthly_projection = daily_cost * 30

        # Cost breakdown by resource type
        cost_by_type = defaultdict(float)
        for entry in cost_data:
            if now - entry['timestamp'] <= 86400:  # Last 24 hours
                cost_by_type[entry['resource_type']] += entry['cost']

        # Top cost contributors
        resource_costs = defaultdict(float)
        for entry in cost_data:
            if now - entry['timestamp'] <= 86400:
                resource_costs[entry['resource_id']] += entry['cost']

        top_resources = sorted(resource_costs.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "cost_summary": {
                "daily_cost": daily_cost,
                "weekly_cost": weekly_cost,
                "monthly_projection": monthly_projection
            },
            "cost_by_resource_type": dict(cost_by_type),
            "top_cost_resources": [{"resource_id": r[0], "daily_cost": r[1]} for r in top_resources],
            "analysis_timestamp": now
        }

    def generate_infrastructure_dashboard_html(self, output_file: str = "infrastructure_dashboard.html"):
        """Generate comprehensive infrastructure dashboard"""
        # Get current data
        capacity_forecasts = self.analyze_capacity_planning()
        optimization_recommendations = self.generate_optimization_recommendations()
        cost_analysis = self.generate_cost_analysis()

        # Get resource health for all resources
        resource_health = {}
        for resource_id in self.dashboard.infrastructure_inventory.keys():
            resource_health[resource_id] = self.dashboard.get_resource_health(resource_id)

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Infrastructure Observability Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        .header {{ text-align: center; color: white; margin-bottom: 30px; }}
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
        .metric-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin: 15px 0; }}
        .metric {{ text-align: center; padding: 15px; background: linear-gradient(135deg, #4CAF50, #45a049); color: white; border-radius: 8px; }}
        .metric.warning {{ background: linear-gradient(135deg, #FF9800, #F57C00); }}
        .metric.critical {{ background: linear-gradient(135deg, #f44336, #d32f2f); }}
        .resource-item {{ margin: 10px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #4CAF50; }}
        .resource-item.warning {{ border-left-color: #FF9800; }}
        .resource-item.critical {{ border-left-color: #f44336; }}
        .recommendation {{ margin: 10px 0; padding: 15px; background: #e3f2fd; border-radius: 8px; border-left: 4px solid #2196F3; }}
        .cost-breakdown {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }}
        .forecast-item {{ margin: 10px 0; padding: 12px; background: #f3e5f5; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️  Infrastructure Observability Dashboard</h1>
            <p>Real-time infrastructure monitoring and optimization</p>
        </div>

        <div class="dashboard-grid">
            <!-- Cost Analysis -->
            <div class="card">
                <h2>💰 Cost Analysis</h2>
"""

        if "error" not in cost_analysis:
            html_content += f"""
                <div class="metric-row">
                    <div class="metric">
                        <h3>${cost_analysis['cost_summary']['daily_cost']:.2f}</h3>
                        <p>Daily Cost</p>
                    </div>
                    <div class="metric">
                        <h3>${cost_analysis['cost_summary']['weekly_cost']:.2f}</h3>
                        <p>Weekly Cost</p>
                    </div>
                    <div class="metric">
                        <h3>${cost_analysis['cost_summary']['monthly_projection']:.2f}</h3>
                        <p>Monthly Projection</p>
                    </div>
                </div>
                <div class="cost-breakdown">
"""
            for resource_type, cost in cost_analysis['cost_by_resource_type'].items():
                html_content += f"""
                    <div style="text-align: center; padding: 10px; background: #e8f5e8; border-radius: 6px;">
                        <strong>{resource_type}</strong><br>
                        ${cost:.2f}/day
                    </div>
"""
            html_content += "</div>"
        else:
            html_content += "<p>No cost data available</p>"

        html_content += """
            </div>

            <!-- Resource Health -->
            <div class="card">
                <h2>🏥 Resource Health</h2>
"""

        healthy_count = warning_count = critical_count = 0
        for resource_id, health in resource_health.items():
            status = health.get('status', 'unknown')
            if status == 'healthy':
                healthy_count += 1
            elif status == 'warning':
                warning_count += 1
            elif status == 'critical':
                critical_count += 1

        html_content += f"""
                <div class="metric-row">
                    <div class="metric">
                        <h3>{healthy_count}</h3>
                        <p>Healthy</p>
                    </div>
                    <div class="metric warning">
                        <h3>{warning_count}</h3>
                        <p>Warning</p>
                    </div>
                    <div class="metric critical">
                        <h3>{critical_count}</h3>
                        <p>Critical</p>
                    </div>
                </div>
"""

        for resource_id, health in list(resource_health.items())[:5]:  # Show top 5
            status = health.get('status', 'unknown')
            health_score = health.get('health_score', 0)
            html_content += f"""
                <div class="resource-item {status}">
                    <strong>{resource_id}</strong> - Health Score: {health_score:.1f}/100<br>
                    <small>Status: {status.title()}</small>
                </div>
"""

        html_content += """
            </div>

            <!-- Capacity Forecasts -->
            <div class="card">
                <h2>📈 Capacity Planning</h2>
"""

        if capacity_forecasts:
            for forecast in capacity_forecasts[:3]:  # Show top 3
                html_content += f"""
                <div class="forecast-item">
                    <strong>{forecast.resource_type.value.title()}</strong><br>
                    Current: {forecast.current_utilization:.1f}%<br>
                    30-day projection: {forecast.projected_utilization_30d:.1f}%<br>
                    90-day projection: {forecast.projected_utilization_90d:.1f}%<br>
                    <small>Action: {forecast.recommended_scaling_action}</small>
                </div>
"""
        else:
            html_content += "<p>Insufficient data for capacity forecasting</p>"

        html_content += """
            </div>

            <!-- Optimization Recommendations -->
            <div class="card">
                <h2>🎯 Optimization Recommendations</h2>
"""

        if optimization_recommendations:
            for rec in optimization_recommendations[:5]:  # Show top 5
                savings_color = "color: green;" if rec.estimated_savings > 0 else "color: red;"
                html_content += f"""
                <div class="recommendation">
                    <strong>{rec.optimization_type.title()}: {rec.resource_id}</strong><br>
                    {rec.description}<br>
                    <span style="{savings_color}">
                        Estimated savings: ${rec.estimated_savings:.2f}/month
                    </span><br>
                    <small>Effort: {rec.implementation_effort} | Risk: {rec.risk_level}</small>
                </div>
"""
        else:
            html_content += "<p>No optimization opportunities identified</p>"

        html_content += """
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh every 5 minutes
        setTimeout(() => {
            location.reload();
        }, 300000);
    </script>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file