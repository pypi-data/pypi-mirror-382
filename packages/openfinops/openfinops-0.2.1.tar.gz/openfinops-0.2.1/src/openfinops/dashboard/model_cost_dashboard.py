"""
Model Cost Attribution Dashboard
===============================

Interactive web dashboard for model-level cost attribution, analysis, and reporting.
Provides comprehensive visualizations for build vs production costs, ROI analysis,
cost trends, and resource optimization insights.

Features:
- Real-time cost tracking and visualization
- Build vs Production cost breakdown charts
- Model ROI analysis and trending
- Resource utilization dashboards
- Cost forecasting and budget monitoring
- Executive summary reports
- Interactive cost exploration tools
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
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import logging

from ..observability.model_cost_attribution import (
    ModelCostAttribution, ModelMetadata, ResourceType, ModelLifecyclePhase,
    create_model_cost_tracker, track_training_cost, track_inference_cost
)
from ..observability.cost_configuration import (
    CostConfigurationManager, get_cost_configuration_manager
)
from ..observability.cost_reporting import (
    ModelCostReporter, ReportPeriod
)


class ModelCostDashboard:
    """Interactive model cost attribution dashboard"""

    def __init__(self):
        self.cost_tracker = create_model_cost_tracker()
        self.config_manager = get_cost_configuration_manager()
        self.reporter = ModelCostReporter(self.cost_tracker, self.config_manager)

        # Dashboard state
        self.dashboard_data = {}
        self.last_update = 0
        self.update_interval = 60  # Update every minute

        # Initialize with demo data
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Initialize dashboard with demonstration data"""
        # Register demo models
        demo_models = [
            ModelMetadata(
                model_id="gpt-4-customer-support",
                model_name="GPT-4 Customer Support",
                model_version="v2.1",
                model_type="transformer",
                owner="ai-team",
                project_id="customer-support",
                description="Customer support chatbot with GPT-4"
            ),
            ModelMetadata(
                model_id="sentiment-analyzer",
                model_name="Sentiment Analyzer",
                model_version="v1.5",
                model_type="bert",
                owner="nlp-team",
                project_id="sentiment-analysis",
                description="BERT-based sentiment analysis model"
            ),
            ModelMetadata(
                model_id="fraud-detection-ensemble",
                model_name="Fraud Detection Ensemble",
                model_version="v3.0",
                model_type="ensemble",
                owner="security-team",
                project_id="fraud-prevention",
                description="Multi-model fraud detection system"
            ),
            ModelMetadata(
                model_id="recommendation-engine",
                model_name="Product Recommendation Engine",
                model_version="v2.3",
                model_type="collaborative_filtering",
                owner="ml-platform",
                project_id="recommendations",
                description="Personalized product recommendation system"
            )
        ]

        for model in demo_models:
            self.cost_tracker.register_model(model)

        # Generate demo cost data
        self._generate_demo_costs()

    def _generate_demo_costs(self):
        """Generate realistic demo cost data"""
        current_time = time.time()

        # Demo cost scenarios for different models
        cost_scenarios = {
            "gpt-4-customer-support": {
                "training_gpu_hours": 240,
                "production_requests": 150000,
                "training_instance": "p3.8xlarge",
                "development_days": 45
            },
            "sentiment-analyzer": {
                "training_gpu_hours": 96,
                "production_requests": 50000,
                "training_instance": "p3.2xlarge",
                "development_days": 20
            },
            "fraud-detection-ensemble": {
                "training_gpu_hours": 480,
                "production_requests": 25000,
                "training_instance": "p3.16xlarge",
                "development_days": 90
            },
            "recommendation-engine": {
                "training_gpu_hours": 180,
                "production_requests": 300000,
                "training_instance": "p3.8xlarge",
                "development_days": 60
            }
        }

        # Generate costs for each model over the last 90 days
        for model_id, scenario in cost_scenarios.items():
            # Development phase (historical)
            dev_start = current_time - (scenario["development_days"] * 24 * 3600)
            self._add_development_costs(model_id, dev_start, scenario["development_days"])

            # Training phase
            training_start = dev_start + (scenario["development_days"] * 0.7 * 24 * 3600)
            self._add_training_costs(model_id, training_start, scenario)

            # Production phase (ongoing)
            production_start = current_time - (30 * 24 * 3600)  # Last 30 days
            self._add_production_costs(model_id, production_start, scenario)

    def _add_development_costs(self, model_id: str, start_time: float, duration_days: int):
        """Add development phase costs"""
        from ..observability.model_cost_attribution import ResourceUsage
        import uuid

        # CPU development costs over time
        daily_cpu_hours = 16  # 2 developers * 8 hours/day
        cpu_cost_per_hour = 0.10  # Approximate development environment cost

        for day in range(duration_days):
            timestamp = start_time + (day * 24 * 3600)

            usage = ResourceUsage(
                usage_id=str(uuid.uuid4()),
                model_id=model_id,
                phase=ModelLifecyclePhase.DEVELOPMENT,
                resource_type=ResourceType.COMPUTE_CPU,
                usage_amount=daily_cpu_hours,
                usage_duration=daily_cpu_hours * 3600,
                timestamp=timestamp,
                region="us-west-2",
                cloud_provider="aws",
                tags={"phase": "development", "team": "ai-team"}
            )

            self.cost_tracker.track_resource_usage(usage)

    def _add_training_costs(self, model_id: str, start_time: float, scenario: Dict[str, Any]):
        """Add training phase costs"""
        from ..observability.model_cost_attribution import ResourceUsage
        import uuid

        total_gpu_hours = scenario["training_gpu_hours"]
        instance_type = scenario["training_instance"]

        # Distribute training over several days
        training_days = max(1, total_gpu_hours // 24)  # Assume 24 hours max per day
        daily_gpu_hours = total_gpu_hours / training_days

        for day in range(int(training_days)):
            timestamp = start_time + (day * 24 * 3600)

            # GPU training cost
            gpu_usage = ResourceUsage(
                usage_id=str(uuid.uuid4()),
                model_id=model_id,
                phase=ModelLifecyclePhase.TRAINING,
                resource_type=ResourceType.COMPUTE_GPU,
                usage_amount=daily_gpu_hours,
                usage_duration=daily_gpu_hours * 3600,
                timestamp=timestamp,
                instance_id=f"{instance_type}-{day+1}",
                region="us-west-2",
                cloud_provider="aws",
                tags={"phase": "training", "instance_type": instance_type},
                metadata={"instance_type": instance_type}
            )

            self.cost_tracker.track_resource_usage(gpu_usage)

            # Storage costs for training data
            storage_usage = ResourceUsage(
                usage_id=str(uuid.uuid4()),
                model_id=model_id,
                phase=ModelLifecyclePhase.TRAINING,
                resource_type=ResourceType.STORAGE_SSD,
                usage_amount=500,  # 500 GB training data
                usage_duration=24 * 3600,  # Daily storage
                timestamp=timestamp,
                region="us-west-2",
                cloud_provider="aws",
                tags={"phase": "training", "data_type": "training_data"}
            )

            self.cost_tracker.track_resource_usage(storage_usage)

    def _add_production_costs(self, model_id: str, start_time: float, scenario: Dict[str, Any]):
        """Add production phase costs"""
        from ..observability.model_cost_attribution import ResourceUsage
        import uuid

        total_requests = scenario["production_requests"]
        production_days = 30
        daily_requests = total_requests / production_days

        for day in range(production_days):
            timestamp = start_time + (day * 24 * 3600)

            # Inference request costs
            inference_usage = ResourceUsage(
                usage_id=str(uuid.uuid4()),
                model_id=model_id,
                phase=ModelLifecyclePhase.PRODUCTION,
                resource_type=ResourceType.INFERENCE_REQUEST,
                usage_amount=daily_requests,
                usage_duration=0,  # Instantaneous
                timestamp=timestamp,
                region="us-west-2",
                cloud_provider="aws",
                tags={"phase": "production", "service": "inference"}
            )

            self.cost_tracker.track_resource_usage(inference_usage)

            # CPU costs for inference serving
            cpu_usage = ResourceUsage(
                usage_id=str(uuid.uuid4()),
                model_id=model_id,
                phase=ModelLifecyclePhase.PRODUCTION,
                resource_type=ResourceType.COMPUTE_CPU,
                usage_amount=24,  # 24 hours of CPU per day
                usage_duration=24 * 3600,
                timestamp=timestamp,
                region="us-west-2",
                cloud_provider="aws",
                tags={"phase": "production", "service": "inference"}
            )

            self.cost_tracker.track_resource_usage(cpu_usage)

    def get_dashboard_data(self, refresh: bool = False) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        current_time = time.time()

        # Check if we need to update
        if not refresh and (current_time - self.last_update) < self.update_interval:
            return self.dashboard_data

        # Generate comprehensive dashboard data
        self.dashboard_data = {
            "overview": self._get_overview_data(),
            "build_vs_production": self._get_build_vs_production_data(),
            "model_analytics": self._get_model_analytics_data(),
            "resource_utilization": self._get_resource_utilization_data(),
            "cost_trends": self._get_cost_trends_data(),
            "forecasting": self._get_forecasting_data(),
            "executive_summary": self._get_executive_summary_data(),
            "last_updated": current_time
        }

        self.last_update = current_time
        return self.dashboard_data

    def _get_overview_data(self) -> Dict[str, Any]:
        """Get overview metrics"""
        # Get all models cost summary for last 30 days
        end_time = time.time()
        start_time = end_time - (30 * 24 * 3600)
        summaries = self.cost_tracker.get_all_models_cost_summary(start_time, end_time)

        total_cost = sum(s.total_cost for s in summaries)
        total_build_cost = sum(s.get_build_phase_cost() for s in summaries)
        total_production_cost = sum(s.get_production_phase_cost() for s in summaries)

        return {
            "total_models": len(self.cost_tracker.models),
            "active_models": len(summaries),
            "total_cost_30d": round(total_cost, 2),
            "build_cost_30d": round(total_build_cost, 2),
            "production_cost_30d": round(total_production_cost, 2),
            "avg_cost_per_model": round(total_cost / len(summaries), 2) if summaries else 0,
            "build_vs_production_ratio": {
                "build": round((total_build_cost / total_cost * 100), 1) if total_cost > 0 else 0,
                "production": round((total_production_cost / total_cost * 100), 1) if total_cost > 0 else 0
            }
        }

    def _get_build_vs_production_data(self) -> Dict[str, Any]:
        """Get build vs production analysis data"""
        analysis = self.reporter.generate_build_vs_production_analysis()

        # Convert to dashboard format
        model_data = []
        for a in analysis:
            model_data.append({
                "model_id": a.model_id,
                "model_name": a.model_name,
                "total_cost": round(a.total_cost, 2),
                "build_cost": round(a.build_cost, 2),
                "production_cost": round(a.production_cost, 2),
                "build_percentage": round(a.build_percentage, 1),
                "production_percentage": round(a.production_percentage, 1),
                "cost_per_inference": round(a.cost_per_inference, 6),
                "daily_production_cost": round(a.daily_production_cost, 2),
                "phase_breakdown": {
                    "development": round(a.development_cost, 2),
                    "training": round(a.training_cost, 2),
                    "validation": round(a.validation_cost, 2),
                    "deployment_prep": round(a.deployment_prep_cost, 2),
                    "inference": round(a.inference_cost, 2),
                    "monitoring": round(a.monitoring_cost, 2),
                    "retraining": round(a.retraining_cost, 2)
                }
            })

        # Summary statistics
        if analysis:
            avg_build_ratio = statistics.mean([a.build_percentage for a in analysis])
            avg_production_ratio = statistics.mean([a.production_percentage for a in analysis])
        else:
            avg_build_ratio = avg_production_ratio = 0

        return {
            "models": model_data,
            "summary": {
                "avg_build_percentage": round(avg_build_ratio, 1),
                "avg_production_percentage": round(avg_production_ratio, 1),
                "total_models": len(analysis)
            }
        }

    def _get_model_analytics_data(self) -> Dict[str, Any]:
        """Get detailed model analytics"""
        models_data = []

        for model_id, model_metadata in self.cost_tracker.models.items():
            # Get cost summary
            summary = self.cost_tracker.get_model_cost_summary(model_id)
            if not summary:
                continue

            # Get ROI analysis (simplified without revenue data)
            roi_analysis = self.reporter.generate_model_roi_analysis(model_id)

            models_data.append({
                "model_id": model_id,
                "model_name": model_metadata.model_name,
                "model_type": model_metadata.model_type,
                "version": model_metadata.model_version,
                "owner": model_metadata.owner,
                "project": model_metadata.project_id,
                "total_cost": round(summary.total_cost, 2),
                "cost_by_resource": {
                    resource.value: round(cost, 2)
                    for resource, cost in summary.cost_by_resource_type.items()
                },
                "roi_metrics": {
                    "roi_percentage": round(roi_analysis.roi_percentage, 1) if roi_analysis else 0,
                    "monthly_roi": round(roi_analysis.monthly_roi, 1) if roi_analysis else 0,
                    "payback_period_months": round(roi_analysis.payback_period_months, 1) if roi_analysis else 0
                } if roi_analysis else None,
                "efficiency_metrics": {
                    "cost_per_inference": self._calculate_cost_per_inference(model_id),
                    "resource_efficiency": self._calculate_resource_efficiency(summary)
                }
            })

        return {
            "models": models_data,
            "total_models": len(models_data)
        }

    def _get_resource_utilization_data(self) -> Dict[str, Any]:
        """Get resource utilization breakdown"""
        # Get all cost entries for analysis
        all_entries = list(self.cost_tracker.model_cost_entries)

        resource_costs = defaultdict(float)
        resource_usage = defaultdict(float)

        for entry in all_entries:
            resource_type = entry.resource_usage.resource_type
            resource_costs[resource_type.value] += entry.calculated_cost
            resource_usage[resource_type.value] += entry.resource_usage.usage_amount

        total_cost = sum(resource_costs.values())

        # Convert to percentages and format
        resource_breakdown = {}
        for resource_type, cost in resource_costs.items():
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            resource_breakdown[resource_type] = {
                "cost": round(cost, 2),
                "percentage": round(percentage, 1),
                "usage": round(resource_usage[resource_type], 2)
            }

        return {
            "resource_breakdown": resource_breakdown,
            "total_cost": round(total_cost, 2),
            "top_resources": sorted(
                resource_breakdown.items(),
                key=lambda x: x[1]["cost"],
                reverse=True
            )[:5]
        }

    def _get_cost_trends_data(self) -> Dict[str, Any]:
        """Get cost trend analysis"""
        # Get trends for all models
        all_trends = self.cost_tracker.get_cost_trends(days=30)

        # Global cost trends
        daily_totals = defaultdict(float)
        for entry in all_trends["daily_costs"]:
            daily_totals[entry["date"]] += entry["total_cost"]

        trend_data = [
            {"date": date, "total_cost": round(cost, 2)}
            for date, cost in sorted(daily_totals.items())
        ]

        # Phase trends
        phase_trends = {}
        for entry in all_trends["daily_phase_costs"]:
            date = entry["date"]
            if date not in phase_trends:
                phase_trends[date] = defaultdict(float)

            for phase, cost in entry.items():
                if phase != "date":
                    phase_trends[date][phase] += cost

        phase_trend_data = []
        for date in sorted(phase_trends.keys()):
            data_point = {"date": date}
            data_point.update({
                phase: round(cost, 2)
                for phase, cost in phase_trends[date].items()
            })
            phase_trend_data.append(data_point)

        return {
            "daily_costs": trend_data,
            "phase_trends": phase_trend_data,
            "cost_growth_rate": self._calculate_growth_rate(trend_data)
        }

    def _get_forecasting_data(self) -> Dict[str, Any]:
        """Get cost forecasting data"""
        forecasts = {}

        for model_id in self.cost_tracker.models.keys():
            forecast = self.reporter.generate_cost_forecast(model_id, forecast_days=30)
            if forecast:
                forecasts[model_id] = {
                    "model_name": self.cost_tracker.models[model_id].model_name,
                    "forecasted_monthly_cost": round(forecast.forecasted_total_cost, 2),
                    "confidence_low": round(forecast.confidence_interval_low, 2),
                    "confidence_high": round(forecast.confidence_interval_high, 2),
                    "trend": forecast.historical_trend.value,
                    "growth_rate": round(forecast.growth_assumptions * 100, 1)
                }

        total_forecast = sum(f["forecasted_monthly_cost"] for f in forecasts.values())

        return {
            "model_forecasts": forecasts,
            "total_monthly_forecast": round(total_forecast, 2),
            "forecast_confidence": "medium"  # Simplified
        }

    def _get_executive_summary_data(self) -> Dict[str, Any]:
        """Get executive summary data"""
        summary = self.reporter.generate_executive_summary(ReportPeriod.MONTHLY)

        return {
            "period": "monthly",
            "total_ai_investment": round(summary.total_ai_investment, 2),
            "build_vs_production": {
                "build_cost": round(summary.total_build_cost, 2),
                "production_cost": round(summary.total_production_cost, 2)
            },
            "active_models": summary.active_models_count,
            "cost_trend": summary.cost_trend.value,
            "growth_rate": round(summary.cost_growth_rate, 1),
            "resource_utilization": {
                "compute": round(summary.compute_cost_percentage, 1),
                "storage": round(summary.storage_cost_percentage, 1),
                "network": round(summary.network_cost_percentage, 1)
            },
            "top_cost_models": summary.top_cost_models[:3],
            "forecasts": {
                "next_month": round(summary.next_month_forecast, 2),
                "next_quarter": round(summary.next_quarter_forecast, 2)
            },
            "recommendations": summary.optimization_opportunities,
            "alerts": summary.budget_alerts
        }

    # Helper methods
    def _calculate_cost_per_inference(self, model_id: str) -> float:
        """Calculate cost per inference for a model"""
        # Get production costs and inference requests
        production_entries = [
            entry for entry in self.cost_tracker.model_cost_entries
            if entry.model_id == model_id and
               entry.phase == ModelLifecyclePhase.PRODUCTION
        ]

        total_cost = sum(entry.calculated_cost for entry in production_entries)
        total_requests = sum(
            entry.resource_usage.usage_amount
            for entry in production_entries
            if entry.resource_usage.resource_type == ResourceType.INFERENCE_REQUEST
        )

        return (total_cost / total_requests) if total_requests > 0 else 0

    def _calculate_resource_efficiency(self, summary) -> float:
        """Calculate resource efficiency score"""
        # Simplified efficiency calculation
        gpu_cost = summary.cost_by_resource_type.get(ResourceType.COMPUTE_GPU, 0)
        total_cost = summary.total_cost

        # Higher GPU ratio often indicates more efficient AI workloads
        gpu_ratio = (gpu_cost / total_cost) if total_cost > 0 else 0

        # Score from 0-100 based on resource mix
        efficiency_score = min(100, gpu_ratio * 150)  # GPU usage boosts efficiency score

        return round(efficiency_score, 1)

    def _calculate_growth_rate(self, trend_data: List[Dict[str, Any]]) -> float:
        """Calculate cost growth rate from trend data"""
        if len(trend_data) < 7:  # Need at least a week of data
            return 0.0

        # Compare first week vs last week
        first_week = trend_data[:7]
        last_week = trend_data[-7:]

        first_avg = statistics.mean([d["total_cost"] for d in first_week])
        last_avg = statistics.mean([d["total_cost"] for d in last_week])

        if first_avg == 0:
            return 0.0

        growth_rate = ((last_avg - first_avg) / first_avg * 100)
        return round(growth_rate, 1)

    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific model"""
        if model_id not in self.cost_tracker.models:
            return {}

        model_metadata = self.cost_tracker.models[model_id]
        summary = self.cost_tracker.get_model_cost_summary(model_id)
        roi_analysis = self.reporter.generate_model_roi_analysis(model_id)
        forecast = self.reporter.generate_cost_forecast(model_id)

        return {
            "metadata": asdict(model_metadata),
            "cost_summary": {
                "total_cost": round(summary.total_cost, 2),
                "cost_by_phase": {
                    phase.value: round(cost, 2)
                    for phase, cost in summary.cost_by_phase.items()
                },
                "cost_by_resource": {
                    resource.value: round(cost, 2)
                    for resource, cost in summary.cost_by_resource_type.items()
                }
            } if summary else None,
            "roi_analysis": asdict(roi_analysis) if roi_analysis else None,
            "forecast": asdict(forecast) if forecast else None,
            "trends": self.cost_tracker.get_cost_trends(model_id=model_id, days=30)
        }

    def update_cost_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Update cost configuration"""
        try:
            # Update configuration through config manager
            active_config = self.config_manager.get_active_configuration()
            if not active_config:
                return False

            # Update unit costs if provided
            if "unit_costs" in config_data:
                for resource_type_str, pricing_data in config_data["unit_costs"].items():
                    try:
                        resource_type = ResourceType(resource_type_str)
                        self.config_manager.update_unit_cost(
                            active_config.config_id,
                            resource_type,
                            pricing_data.get("region", "us-west-2"),
                            pricing_data.get("cloud_provider", "aws"),
                            pricing_data["unit_price"],
                            pricing_data.get("instance_type")
                        )
                    except (ValueError, KeyError) as e:
                        logging.warning(f"Failed to update unit cost for {resource_type_str}: {e}")
                        continue

            return True

        except Exception as e:
            logging.error(f"Failed to update cost configuration: {e}")
            return False

    def export_dashboard_data(self, format: str = "json") -> str:
        """Export dashboard data in specified format"""
        dashboard_data = self.get_dashboard_data(refresh=True)

        if format.lower() == "json":
            return json.dumps(dashboard_data, indent=2, default=str)
        else:
            # Could add CSV, Excel export here
            return json.dumps(dashboard_data, indent=2, default=str)


# Global dashboard instance
_model_cost_dashboard = None

def get_model_cost_dashboard() -> ModelCostDashboard:
    """Get global model cost dashboard instance"""
    global _model_cost_dashboard
    if _model_cost_dashboard is None:
        _model_cost_dashboard = ModelCostDashboard()
    return _model_cost_dashboard