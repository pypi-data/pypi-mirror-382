"""
Cost Observatory and Resource Optimization
==========================================

Advanced cost monitoring and optimization system for AI training infrastructure
with budget tracking, cost attribution, and optimization recommendations.

Features:
- Real-time cost tracking and attribution
- Budget monitoring and alerts
- Resource cost optimization recommendations
- Multi-cloud cost analysis
- Training run cost profiling
- ROI analysis for AI training investments
- Automated cost anomaly detection
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


class CostCategory(Enum):
    """Cost categorization"""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    MEMORY = "memory"
    SOFTWARE_LICENSES = "software_licenses"
    DATA_TRANSFER = "data_transfer"
    SUPPORT = "support"
    # Data Platform Services
    DATABRICKS = "databricks"
    DATABRICKS_DBU = "databricks_dbu"
    DATABRICKS_JOBS = "databricks_jobs"
    DATABRICKS_SQL = "databricks_sql"
    SNOWFLAKE = "snowflake"
    SNOWFLAKE_COMPUTE = "snowflake_compute"
    SNOWFLAKE_STORAGE = "snowflake_storage"
    # SaaS Services
    MONGODB_ATLAS = "mongodb_atlas"
    REDIS_CLOUD = "redis_cloud"
    GITHUB_ACTIONS = "github_actions"
    DATADOG = "datadog"
    ELASTICSEARCH = "elasticsearch"
    CONFLUENT_KAFKA = "confluent_kafka"
    # Database Services
    DATABASE = "database"
    DATABASE_COMPUTE = "database_compute"
    DATABASE_STORAGE = "database_storage"
    DATABASE_BACKUP = "database_backup"


class BudgetStatus(Enum):
    """Budget status"""
    UNDER_BUDGET = "under_budget"
    APPROACHING_LIMIT = "approaching_limit"
    OVER_BUDGET = "over_budget"
    BUDGET_EXHAUSTED = "budget_exhausted"


@dataclass
class CostEntry:
    """Individual cost entry"""
    entry_id: str
    timestamp: float
    resource_id: str
    category: CostCategory
    amount: float  # Cost in USD
    currency: str = "USD"
    region: str = "us-west-2"
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    billing_period: str = ""  # "hourly", "daily", "monthly"


@dataclass
class Budget:
    """Budget configuration and tracking"""
    budget_id: str
    name: str
    total_amount: float
    spent_amount: float = 0.0
    remaining_amount: Optional[float] = None
    start_date: float = field(default_factory=time.time)
    end_date: float = field(default_factory=lambda: time.time() + 30 * 24 * 3600)  # 30 days
    categories: List[CostCategory] = field(default_factory=list)
    resource_filters: Dict[str, str] = field(default_factory=dict)
    alert_thresholds: List[float] = field(default_factory=lambda: [0.5, 0.8, 0.9])  # 50%, 80%, 90%
    status: BudgetStatus = BudgetStatus.UNDER_BUDGET

    def __post_init__(self):
        if self.remaining_amount is None:
            self.remaining_amount = self.total_amount - self.spent_amount


@dataclass
class CostOptimizationRecommendation:
    """Cost optimization recommendation"""
    recommendation_id: str
    title: str
    description: str
    category: CostCategory
    affected_resources: List[str]
    current_monthly_cost: float
    potential_monthly_savings: float
    confidence_score: float  # 0-1
    implementation_effort: str  # "low", "medium", "high"
    risk_level: str  # "low", "medium", "high"
    implementation_steps: List[str] = field(default_factory=list)
    estimated_implementation_time: str = ""


class CostObservatory:
    """Cost monitoring and analysis system

    Args:
        collection_interval: Interval for cost collection (seconds)
        persistence_config: Optional persistence configuration for historical data storage
    """

    def __init__(
        self,
        collection_interval: float = 3600,
        persistence_config: Optional['PersistenceConfig'] = None
    ):
        self.collection_interval = collection_interval
        # In-memory storage for fast recent access
        self.cost_entries = deque(maxlen=100000)
        self.budgets: Dict[str, Budget] = {}
        self.is_monitoring = False
        self.monitoring_thread = None
        self.collection_lock = threading.Lock()

        # Cost analysis caches
        self.cost_by_category = defaultdict(float)
        self.cost_by_resource = defaultdict(float)
        self.cost_by_region = defaultdict(float)
        self.daily_costs = defaultdict(float)

        # Optimization tracking
        self.optimization_recommendations = []
        self.cost_anomalies = deque(maxlen=1000)

        # Training run cost tracking
        self.training_run_costs = defaultdict(lambda: {"start_time": None, "costs": [], "total_cost": 0.0})

        # Persistence layer for historical data
        self.persistence_backend: Optional[BasePersistenceBackend] = None
        if PERSISTENCE_AVAILABLE and persistence_config:
            self.persistence_backend = create_persistence_backend(persistence_config)
            self.persistence_backend.start_auto_flush()

    def add_cost_entry(self, cost_entry: CostEntry):
        """Add cost entry and update aggregations"""
        with self.collection_lock:
            # Store in memory for fast access
            self.cost_entries.append(cost_entry)

            # Store in persistent backend for historical analysis
            if self.persistence_backend:
                entry_dict = asdict(cost_entry)
                # Convert enum to string
                if 'category' in entry_dict and hasattr(entry_dict['category'], 'value'):
                    entry_dict['category'] = entry_dict['category'].value
                self.persistence_backend.store_cost_entry(entry_dict)

            # Update aggregations
            self._update_cost_aggregations(cost_entry)

            # Update budget tracking
            self._update_budget_tracking(cost_entry)

            # Check for anomalies
            self._detect_cost_anomalies(cost_entry)

    def _update_cost_aggregations(self, cost_entry: CostEntry):
        """Update cost aggregations"""
        self.cost_by_category[cost_entry.category.value] += cost_entry.amount
        self.cost_by_resource[cost_entry.resource_id] += cost_entry.amount
        self.cost_by_region[cost_entry.region] += cost_entry.amount

        # Daily cost tracking
        day_key = time.strftime("%Y-%m-%d", time.localtime(cost_entry.timestamp))
        self.daily_costs[day_key] += cost_entry.amount

    def _update_budget_tracking(self, cost_entry: CostEntry):
        """Update budget tracking with new cost entry"""
        for budget_id, budget in self.budgets.items():
            # Check if cost entry applies to this budget
            if self._cost_applies_to_budget(cost_entry, budget):
                budget.spent_amount += cost_entry.amount
                budget.remaining_amount = budget.total_amount - budget.spent_amount

                # Update budget status
                utilization = budget.spent_amount / budget.total_amount
                if utilization >= 1.0:
                    budget.status = BudgetStatus.BUDGET_EXHAUSTED
                elif utilization >= 0.9:
                    budget.status = BudgetStatus.OVER_BUDGET
                elif utilization >= 0.8:
                    budget.status = BudgetStatus.APPROACHING_LIMIT
                else:
                    budget.status = BudgetStatus.UNDER_BUDGET

    def _cost_applies_to_budget(self, cost_entry: CostEntry, budget: Budget) -> bool:
        """Check if cost entry applies to budget"""
        # Time range check
        if not (budget.start_date <= cost_entry.timestamp <= budget.end_date):
            return False

        # Category filter
        if budget.categories and cost_entry.category not in budget.categories:
            return False

        # Resource filters
        for filter_key, filter_value in budget.resource_filters.items():
            if filter_key in cost_entry.tags:
                if cost_entry.tags[filter_key] != filter_value:
                    return False
            elif filter_key == "resource_id" and cost_entry.resource_id != filter_value:
                return False

        return True

    def _detect_cost_anomalies(self, cost_entry: CostEntry):
        """Detect cost anomalies"""
        # Get recent costs for this resource/category combination
        recent_costs = [
            entry.amount for entry in list(self.cost_entries)[-100:]
            if (entry.resource_id == cost_entry.resource_id and
                entry.category == cost_entry.category and
                entry.timestamp > time.time() - 7 * 24 * 3600)  # Last 7 days
        ]

        if len(recent_costs) >= 10:  # Need enough data
            mean_cost = statistics.mean(recent_costs[:-1])  # Exclude current entry
            std_cost = statistics.pstdev(recent_costs[:-1])

            # Check for significant deviation
            if std_cost > 0:
                z_score = abs(cost_entry.amount - mean_cost) / std_cost
                if z_score > 3:  # 3 standard deviations
                    anomaly = {
                        "timestamp": cost_entry.timestamp,
                        "resource_id": cost_entry.resource_id,
                        "category": cost_entry.category.value,
                        "current_cost": cost_entry.amount,
                        "expected_cost": mean_cost,
                        "deviation_percent": ((cost_entry.amount - mean_cost) / mean_cost) * 100,
                        "severity": "high" if z_score > 4 else "medium"
                    }
                    self.cost_anomalies.append(anomaly)

    def create_budget(self, budget: Budget):
        """Create new budget"""
        self.budgets[budget.budget_id] = budget

    def update_budget(self, budget_id: str, **updates):
        """Update existing budget"""
        if budget_id in self.budgets:
            budget = self.budgets[budget_id]
            for key, value in updates.items():
                if hasattr(budget, key):
                    setattr(budget, key, value)

    def get_cost_summary(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get cost summary for specified time range"""
        cutoff_time = time.time() - time_range_hours * 3600

        with self.collection_lock:
            recent_entries = [
                entry for entry in self.cost_entries
                if entry.timestamp > cutoff_time
            ]

        if not recent_entries:
            return {"error": "No cost data available for specified time range"}

        total_cost = sum(entry.amount for entry in recent_entries)

        # Cost by category
        category_costs = defaultdict(float)
        for entry in recent_entries:
            category_costs[entry.category.value] += entry.amount

        # Cost by resource (top 10)
        resource_costs = defaultdict(float)
        for entry in recent_entries:
            resource_costs[entry.resource_id] += entry.amount

        top_resources = sorted(resource_costs.items(), key=lambda x: x[1], reverse=True)[:10]

        # Cost trend analysis
        hourly_costs = defaultdict(float)
        for entry in recent_entries:
            hour_key = int(entry.timestamp // 3600)
            hourly_costs[hour_key] += entry.amount

        cost_trend = "increasing" if len(hourly_costs) > 1 else "stable"
        if len(hourly_costs) >= 2:
            recent_avg = statistics.mean(list(hourly_costs.values())[-int(len(hourly_costs)/2):])
            earlier_avg = statistics.mean(list(hourly_costs.values())[:int(len(hourly_costs)/2)])
            if recent_avg > earlier_avg * 1.1:
                cost_trend = "increasing"
            elif recent_avg < earlier_avg * 0.9:
                cost_trend = "decreasing"

        return {
            "time_range_hours": time_range_hours,
            "total_cost": total_cost,
            "average_hourly_cost": total_cost / max(time_range_hours, 1),
            "projected_monthly_cost": (total_cost / time_range_hours) * 24 * 30,
            "cost_by_category": dict(category_costs),
            "top_resources": [{"resource_id": r[0], "cost": r[1]} for r in top_resources],
            "cost_trend": cost_trend,
            "total_entries": len(recent_entries)
        }

    def get_budget_status(self) -> Dict[str, Any]:
        """Get status of all budgets"""
        budget_summary = []

        for budget_id, budget in self.budgets.items():
            utilization = budget.spent_amount / budget.total_amount
            days_remaining = max(0, (budget.end_date - time.time()) / (24 * 3600))

            # Calculate burn rate
            budget_duration = budget.end_date - budget.start_date
            elapsed_time = time.time() - budget.start_date
            expected_spend = budget.total_amount * (elapsed_time / budget_duration)

            budget_info = {
                "budget_id": budget_id,
                "name": budget.name,
                "total_amount": budget.total_amount,
                "spent_amount": budget.spent_amount,
                "remaining_amount": budget.remaining_amount,
                "utilization_percent": utilization * 100,
                "status": budget.status.value,
                "days_remaining": days_remaining,
                "expected_spend": expected_spend,
                "over_under_budget": budget.spent_amount - expected_spend,
                "projected_total_spend": budget.spent_amount / max(elapsed_time / budget_duration, 0.01)
            }

            budget_summary.append(budget_info)

        return {
            "budgets": budget_summary,
            "total_budgets": len(self.budgets),
            "over_budget_count": len([b for b in self.budgets.values() if b.status in [BudgetStatus.OVER_BUDGET, BudgetStatus.BUDGET_EXHAUSTED]]),
            "approaching_limit_count": len([b for b in self.budgets.values() if b.status == BudgetStatus.APPROACHING_LIMIT])
        }

    def start_training_run_tracking(self, training_run_id: str):
        """Start tracking costs for a training run"""
        self.training_run_costs[training_run_id] = {
            "start_time": time.time(),
            "costs": [],
            "total_cost": 0.0
        }

    def stop_training_run_tracking(self, training_run_id: str):
        """Stop tracking costs for a training run"""
        if training_run_id in self.training_run_costs:
            run_data = self.training_run_costs[training_run_id]
            run_data["end_time"] = time.time()
            run_data["duration_hours"] = (run_data["end_time"] - run_data["start_time"]) / 3600

            # Calculate final cost
            with self.collection_lock:
                relevant_costs = [
                    entry for entry in self.cost_entries
                    if (entry.timestamp >= run_data["start_time"] and
                        "training_run_id" in entry.tags and
                        entry.tags["training_run_id"] == training_run_id)
                ]

            run_data["total_cost"] = sum(entry.amount for entry in relevant_costs)
            run_data["cost_per_hour"] = run_data["total_cost"] / max(run_data["duration_hours"], 0.1)

            return run_data

        return None

    def query_historical_costs(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        category: Optional[str] = None,
        resource_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query historical cost entries from persistence layer.

        Args:
            start_time: Start timestamp (unix time)
            end_time: End timestamp (unix time)
            category: Filter by cost category
            resource_id: Filter by resource ID
            limit: Maximum number of results

        Returns:
            List of historical cost entries
        """
        if not self.persistence_backend:
            # Fallback to in-memory data if persistence not available
            results = []
            for entry in list(self.cost_entries):
                entry_dict = asdict(entry) if hasattr(entry, '__dataclass_fields__') else entry
                if start_time and entry_dict.get('timestamp', 0) < start_time:
                    continue
                if end_time and entry_dict.get('timestamp', 0) > end_time:
                    continue
                if category and entry_dict.get('category') != category:
                    continue
                if resource_id and entry_dict.get('resource_id') != resource_id:
                    continue
                results.append(entry_dict)
            return results[-limit:]

        return self.persistence_backend.query_cost_entries(
            start_time=start_time,
            end_time=end_time,
            category=category,
            resource_id=resource_id,
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


class ResourceOptimizer:
    """Resource optimization recommendations engine"""

    def __init__(self, cost_observatory: CostObservatory):
        self.cost_observatory = cost_observatory

    def analyze_optimization_opportunities(self) -> List[CostOptimizationRecommendation]:
        """Analyze and generate cost optimization recommendations"""
        recommendations = []

        # Get recent cost data
        cost_summary = self.cost_observatory.get_cost_summary(time_range_hours=168)  # 7 days

        if "error" in cost_summary:
            return recommendations

        # 1. Underutilized resources
        underutilized_rec = self._analyze_underutilized_resources(cost_summary)
        if underutilized_rec:
            recommendations.extend(underutilized_rec)

        # 2. Reserved instance opportunities
        reserved_instance_rec = self._analyze_reserved_instance_opportunities(cost_summary)
        if reserved_instance_rec:
            recommendations.extend(reserved_instance_rec)

        # 3. Storage optimization
        storage_rec = self._analyze_storage_optimization(cost_summary)
        if storage_rec:
            recommendations.extend(storage_rec)

        # 4. Network optimization
        network_rec = self._analyze_network_optimization(cost_summary)
        if network_rec:
            recommendations.extend(network_rec)

        # 5. Scheduling optimization
        scheduling_rec = self._analyze_scheduling_optimization(cost_summary)
        if scheduling_rec:
            recommendations.extend(scheduling_rec)

        # Sort by potential savings
        recommendations.sort(key=lambda r: r.potential_monthly_savings, reverse=True)

        return recommendations

    def _analyze_underutilized_resources(self, cost_summary: Dict[str, Any]) -> List[CostOptimizationRecommendation]:
        """Analyze underutilized resources"""
        recommendations = []

        # Identify high-cost, potentially underutilized resources
        top_resources = cost_summary.get("top_resources", [])

        for resource_info in top_resources[:5]:  # Top 5 most expensive
            resource_id = resource_info["resource_id"]
            monthly_cost = resource_info["cost"] * (30 * 24 / 7)  # Project to monthly

            # Assume some utilization data analysis (simplified)
            estimated_utilization = 0.3  # This would come from actual metrics

            if estimated_utilization < 0.5:  # Less than 50% utilized
                potential_savings = monthly_cost * (1 - estimated_utilization) * 0.5

                rec = CostOptimizationRecommendation(
                    recommendation_id=f"underutilized_{resource_id}_{int(time.time())}",
                    title=f"Underutilized Resource: {resource_id}",
                    description=f"Resource {resource_id} appears to be underutilized ({estimated_utilization*100:.1f}% avg utilization)",
                    category=CostCategory.COMPUTE,
                    affected_resources=[resource_id],
                    current_monthly_cost=monthly_cost,
                    potential_monthly_savings=potential_savings,
                    confidence_score=0.7,
                    implementation_effort="medium",
                    risk_level="low",
                    implementation_steps=[
                        "1. Analyze detailed utilization patterns",
                        "2. Consider rightsizing to smaller instance",
                        "3. Implement auto-scaling if applicable",
                        "4. Monitor performance impact"
                    ],
                    estimated_implementation_time="1-2 weeks"
                )
                recommendations.append(rec)

        return recommendations

    def _analyze_reserved_instance_opportunities(self, cost_summary: Dict[str, Any]) -> List[CostOptimizationRecommendation]:
        """Analyze reserved instance opportunities"""
        recommendations = []

        # Calculate potential savings from reserved instances
        compute_cost = cost_summary.get("cost_by_category", {}).get("compute", 0)
        monthly_compute_cost = compute_cost * (30 * 24 / 7)

        if monthly_compute_cost > 1000:  # Significant compute spending
            potential_savings = monthly_compute_cost * 0.3  # 30% typical RI savings

            rec = CostOptimizationRecommendation(
                recommendation_id=f"reserved_instances_{int(time.time())}",
                title="Reserved Instance Opportunity",
                description=f"High compute spending ({monthly_compute_cost:.0f}/month) - consider reserved instances",
                category=CostCategory.COMPUTE,
                affected_resources=["compute-instances"],
                current_monthly_cost=monthly_compute_cost,
                potential_monthly_savings=potential_savings,
                confidence_score=0.8,
                implementation_effort="low",
                risk_level="low",
                implementation_steps=[
                    "1. Analyze compute usage patterns",
                    "2. Identify stable workloads suitable for RIs",
                    "3. Purchase appropriate reserved instances",
                    "4. Monitor savings realization"
                ],
                estimated_implementation_time="1 week"
            )
            recommendations.append(rec)

        return recommendations

    def _analyze_storage_optimization(self, cost_summary: Dict[str, Any]) -> List[CostOptimizationRecommendation]:
        """Analyze storage optimization opportunities"""
        recommendations = []

        storage_cost = cost_summary.get("cost_by_category", {}).get("storage", 0)
        monthly_storage_cost = storage_cost * (30 * 24 / 7)

        if monthly_storage_cost > 500:  # Significant storage spending
            potential_savings = monthly_storage_cost * 0.2  # 20% typical storage optimization

            rec = CostOptimizationRecommendation(
                recommendation_id=f"storage_optimization_{int(time.time())}",
                title="Storage Cost Optimization",
                description="Optimize storage costs through tiering and lifecycle management",
                category=CostCategory.STORAGE,
                affected_resources=["storage-volumes"],
                current_monthly_cost=monthly_storage_cost,
                potential_monthly_savings=potential_savings,
                confidence_score=0.6,
                implementation_effort="medium",
                risk_level="low",
                implementation_steps=[
                    "1. Analyze data access patterns",
                    "2. Implement intelligent tiering",
                    "3. Set up lifecycle policies",
                    "4. Clean up unused storage"
                ],
                estimated_implementation_time="2-3 weeks"
            )
            recommendations.append(rec)

        return recommendations

    def _analyze_network_optimization(self, cost_summary: Dict[str, Any]) -> List[CostOptimizationRecommendation]:
        """Analyze network optimization opportunities"""
        recommendations = []

        network_cost = cost_summary.get("cost_by_category", {}).get("network", 0)
        monthly_network_cost = network_cost * (30 * 24 / 7)

        if monthly_network_cost > 200:  # Significant network spending
            potential_savings = monthly_network_cost * 0.15  # 15% typical network optimization

            rec = CostOptimizationRecommendation(
                recommendation_id=f"network_optimization_{int(time.time())}",
                title="Network Cost Optimization",
                description="Optimize data transfer and network architecture",
                category=CostCategory.NETWORK,
                affected_resources=["network-transfers"],
                current_monthly_cost=monthly_network_cost,
                potential_monthly_savings=potential_savings,
                confidence_score=0.5,
                implementation_effort="high",
                risk_level="medium",
                implementation_steps=[
                    "1. Analyze data transfer patterns",
                    "2. Optimize data placement and caching",
                    "3. Implement CDN where appropriate",
                    "4. Review cross-region transfers"
                ],
                estimated_implementation_time="3-4 weeks"
            )
            recommendations.append(rec)

        return recommendations

    def _analyze_scheduling_optimization(self, cost_summary: Dict[str, Any]) -> List[CostOptimizationRecommendation]:
        """Analyze scheduling optimization opportunities"""
        recommendations = []

        # Assume some workloads can be scheduled during off-peak hours
        total_monthly_cost = cost_summary.get("projected_monthly_cost", 0)

        if total_monthly_cost > 2000:  # Significant total spending
            potential_savings = total_monthly_cost * 0.1  # 10% through scheduling

            rec = CostOptimizationRecommendation(
                recommendation_id=f"scheduling_optimization_{int(time.time())}",
                title="Workload Scheduling Optimization",
                description="Schedule non-urgent workloads during off-peak hours",
                category=CostCategory.COMPUTE,
                affected_resources=["scheduled-workloads"],
                current_monthly_cost=total_monthly_cost,
                potential_monthly_savings=potential_savings,
                confidence_score=0.4,
                implementation_effort="high",
                risk_level="medium",
                implementation_steps=[
                    "1. Identify delay-tolerant workloads",
                    "2. Implement scheduling system",
                    "3. Use spot instances for batch jobs",
                    "4. Monitor cost impact"
                ],
                estimated_implementation_time="4-6 weeks"
            )
            recommendations.append(rec)

        return recommendations

    def generate_cost_optimization_dashboard_html(self, output_file: str = "cost_optimization_dashboard.html"):
        """Generate cost optimization dashboard"""
        cost_summary = self.cost_observatory.get_cost_summary(time_range_hours=168)
        budget_status = self.cost_observatory.get_budget_status()
        recommendations = self.analyze_optimization_opportunities()

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cost Observatory Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .card {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2); }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; }}
        .metric {{ text-align: center; padding: 15px; background: rgba(255,255,255,0.15); border-radius: 8px; }}
        .metric.cost {{ background: rgba(76,175,80,0.3); }}
        .metric.savings {{ background: rgba(255,193,7,0.3); }}
        .metric.warning {{ background: rgba(255,152,0,0.3); }}
        .metric.critical {{ background: rgba(244,67,54,0.3); }}
        .recommendation {{ margin: 10px 0; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px; }}
        .budget-item {{ margin: 8px 0; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 6px; }}
        .budget-item.over_budget {{ border-left: 4px solid #f44336; }}
        .budget-item.approaching_limit {{ border-left: 4px solid #ff9800; }}
        .budget-item.under_budget {{ border-left: 4px solid #4caf50; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Cost Observatory Dashboard</h1>
            <p>AI Training Infrastructure Cost Monitoring & Optimization</p>
        </div>

        <div class="dashboard-grid">
            <!-- Cost Summary -->
            <div class="card">
                <h2>📊 Cost Summary (7 Days)</h2>
"""

        if "error" not in cost_summary:
            html_content += f"""
                <div class="metric-grid">
                    <div class="metric cost">
                        <h3>${cost_summary['total_cost']:.2f}</h3>
                        <p>Total Cost</p>
                    </div>
                    <div class="metric">
                        <h3>${cost_summary['average_hourly_cost']:.2f}</h3>
                        <p>Avg/Hour</p>
                    </div>
                    <div class="metric">
                        <h3>${cost_summary['projected_monthly_cost']:.2f}</h3>
                        <p>Monthly Projection</p>
                    </div>
                    <div class="metric">
                        <h3>{cost_summary['cost_trend'].title()}</h3>
                        <p>Trend</p>
                    </div>
                </div>

                <h4>Cost by Category:</h4>
"""
            for category, cost in cost_summary['cost_by_category'].items():
                html_content += f"<p>{category.title()}: <strong>${cost:.2f}</strong></p>"
        else:
            html_content += "<p>No cost data available</p>"

        html_content += """
            </div>

            <!-- Budget Status -->
            <div class="card">
                <h2>💳 Budget Status</h2>
"""

        if budget_status['budgets']:
            html_content += f"""
                <div class="metric-grid">
                    <div class="metric">
                        <h3>{budget_status['total_budgets']}</h3>
                        <p>Total Budgets</p>
                    </div>
                    <div class="metric warning">
                        <h3>{budget_status['approaching_limit_count']}</h3>
                        <p>Approaching Limit</p>
                    </div>
                    <div class="metric critical">
                        <h3>{budget_status['over_budget_count']}</h3>
                        <p>Over Budget</p>
                    </div>
                </div>
"""
            for budget in budget_status['budgets'][:5]:  # Show top 5
                status_class = budget['status'].replace('_', '-')
                html_content += f"""
                <div class="budget-item {budget['status']}">
                    <strong>{budget['name']}</strong><br>
                    <small>
                        ${budget['spent_amount']:.2f} / ${budget['total_amount']:.2f}
                        ({budget['utilization_percent']:.1f}%)
                    </small><br>
                    <small>Status: {budget['status'].replace('_', ' ').title()}</small>
                </div>
"""
        else:
            html_content += "<p>No budgets configured</p>"

        html_content += """
            </div>

            <!-- Optimization Recommendations -->
            <div class="card">
                <h2>🎯 Cost Optimization</h2>
"""

        total_potential_savings = sum(rec.potential_monthly_savings for rec in recommendations)
        html_content += f"""
                <div class="metric-grid">
                    <div class="metric savings">
                        <h3>${total_potential_savings:.0f}</h3>
                        <p>Potential Monthly Savings</p>
                    </div>
                    <div class="metric">
                        <h3>{len(recommendations)}</h3>
                        <p>Recommendations</p>
                    </div>
                </div>
"""

        for rec in recommendations[:5]:  # Show top 5 recommendations
            html_content += f"""
                <div class="recommendation">
                    <strong>{rec.title}</strong><br>
                    <p style="margin: 5px 0; font-size: 14px;">{rec.description}</p>
                    <small>
                        💰 Savings: ${rec.potential_monthly_savings:.0f}/month |
                        🔧 Effort: {rec.implementation_effort.title()} |
                        ⚠️ Risk: {rec.risk_level.title()} |
                        🎯 Confidence: {rec.confidence_score*100:.0f}%
                    </small>
                </div>
"""

        html_content += """
            </div>

            <!-- Top Cost Resources -->
            <div class="card">
                <h2>📈 Top Cost Resources</h2>
"""

        if "error" not in cost_summary and "top_resources" in cost_summary:
            for resource in cost_summary['top_resources'][:8]:
                html_content += f"""
                <div style="margin: 8px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 6px;">
                    <strong>{resource['resource_id']}</strong><br>
                    <small>${resource['cost']:.2f} (7 days)</small>
                </div>
"""
        else:
            html_content += "<p>No resource cost data available</p>"

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