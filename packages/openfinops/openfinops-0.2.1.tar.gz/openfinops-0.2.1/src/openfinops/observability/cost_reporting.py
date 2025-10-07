"""
Model Cost Reporting and Analytics System
=========================================

Advanced reporting and analytics for model-level cost attribution with comprehensive
dashboards, cost analysis, and financial insights.

Features:
- Build vs Production cost separation and analysis
- Model ROI calculation and trending
- Cost forecasting and budget planning
- Multi-dimensional cost analytics
- Executive summary reports
- Cost anomaly detection
- Resource optimization recommendations
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
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import threading

from .model_cost_attribution import (
    ModelCostAttribution, ModelMetadata, ModelCostSummary,
    ModelLifecyclePhase, ResourceType, ModelCostEntry
)
from .cost_configuration import CostConfigurationManager


class ReportPeriod(Enum):
    """Reporting time periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class CostTrendDirection(Enum):
    """Cost trend directions"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class BuildVsProductionAnalysis:
    """Analysis of build vs production cost breakdown"""
    model_id: str
    model_name: str
    total_cost: float
    build_cost: float
    production_cost: float
    build_percentage: float
    production_percentage: float

    # Build phase breakdown
    development_cost: float = 0.0
    training_cost: float = 0.0
    validation_cost: float = 0.0
    deployment_prep_cost: float = 0.0

    # Production phase breakdown
    inference_cost: float = 0.0
    monitoring_cost: float = 0.0
    retraining_cost: float = 0.0

    # Efficiency metrics
    cost_per_inference: float = 0.0
    daily_production_cost: float = 0.0
    model_roi: Optional[float] = None
    payback_period_days: Optional[float] = None

    # Time periods
    build_duration_days: float = 0.0
    production_duration_days: float = 0.0


@dataclass
class ModelROIAnalysis:
    """Model return on investment analysis"""
    model_id: str
    model_name: str

    # Costs
    total_investment: float              # Total cost invested (build + production)
    build_investment: float              # Build phase investment
    operational_cost: float              # Ongoing operational costs

    # Revenue/Value metrics
    revenue_generated: float = 0.0       # Revenue attributed to model
    cost_savings: float = 0.0           # Cost savings from model
    efficiency_gains: float = 0.0       # Value from efficiency improvements

    # ROI calculations
    roi_percentage: float = 0.0          # Overall ROI percentage
    monthly_roi: float = 0.0            # Monthly ROI
    payback_period_months: float = 0.0   # Time to recover investment

    # Trends
    roi_trend: CostTrendDirection = CostTrendDirection.STABLE
    monthly_cost_trend: CostTrendDirection = CostTrendDirection.STABLE

    # Projections
    projected_annual_cost: float = 0.0
    projected_annual_roi: float = 0.0


@dataclass
class CostForecast:
    """Cost forecasting for models"""
    model_id: str
    forecast_period_days: int

    # Historical data
    historical_daily_avg: float
    historical_trend: CostTrendDirection

    # Forecasted costs
    forecasted_total_cost: float
    forecasted_daily_cost: float
    confidence_interval_low: float
    confidence_interval_high: float

    # Phase-specific forecasts
    build_phase_forecast: float = 0.0
    production_phase_forecast: float = 0.0

    # Assumptions and factors
    seasonal_factors: Dict[str, float] = field(default_factory=dict)
    growth_assumptions: float = 0.0      # Expected growth rate
    model_lifecycle_stage: str = "stable"  # "growth", "stable", "declining"


@dataclass
class ExecutiveCostSummary:
    """Executive-level cost summary"""
    report_period: ReportPeriod
    start_date: float
    end_date: float

    # Overall metrics
    total_ai_investment: float
    total_build_cost: float
    total_production_cost: float
    active_models_count: int

    # Top performers
    top_cost_models: List[Dict[str, Any]] = field(default_factory=list)
    top_roi_models: List[Dict[str, Any]] = field(default_factory=list)
    most_efficient_models: List[Dict[str, Any]] = field(default_factory=list)

    # Trends
    cost_trend: CostTrendDirection = CostTrendDirection.STABLE
    cost_growth_rate: float = 0.0
    budget_utilization: float = 0.0

    # Resource utilization
    compute_cost_percentage: float = 0.0
    storage_cost_percentage: float = 0.0
    network_cost_percentage: float = 0.0

    # Forecasts
    next_month_forecast: float = 0.0
    next_quarter_forecast: float = 0.0

    # Recommendations
    optimization_opportunities: List[str] = field(default_factory=list)
    budget_alerts: List[str] = field(default_factory=list)


class ModelCostReporter:
    """Advanced model cost reporting and analytics system"""

    def __init__(self, cost_tracker: ModelCostAttribution,
                 config_manager: CostConfigurationManager):
        self.cost_tracker = cost_tracker
        self.config_manager = config_manager

        # Caching for performance
        self.report_cache = {}
        self.cache_timeout = 300  # 5 minutes
        self.report_lock = threading.Lock()

        # Analysis parameters
        self.roi_calculation_enabled = True
        self.forecast_enabled = True
        self.anomaly_detection_enabled = True

    def generate_build_vs_production_analysis(
        self, model_id: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[BuildVsProductionAnalysis]:
        """Generate comprehensive build vs production cost analysis"""

        if model_id:
            model_ids = [model_id]
        else:
            model_ids = list(self.cost_tracker.models.keys())

        analyses = []

        for mid in model_ids:
            summary = self.cost_tracker.get_model_cost_summary(mid, start_time, end_time)
            if not summary:
                continue

            model_metadata = self.cost_tracker.models[mid]

            # Calculate build vs production breakdown
            build_phases = [
                ModelLifecyclePhase.DEVELOPMENT,
                ModelLifecyclePhase.TRAINING,
                ModelLifecyclePhase.VALIDATION,
                ModelLifecyclePhase.DEPLOYMENT_PREP
            ]

            production_phases = [
                ModelLifecyclePhase.PRODUCTION,
                ModelLifecyclePhase.MONITORING,
                ModelLifecyclePhase.RETRAINING
            ]

            build_cost = sum(summary.cost_by_phase.get(phase, 0.0) for phase in build_phases)
            production_cost = sum(summary.cost_by_phase.get(phase, 0.0) for phase in production_phases)
            total_cost = build_cost + production_cost

            # Calculate percentages
            build_percentage = (build_cost / total_cost * 100) if total_cost > 0 else 0
            production_percentage = (production_cost / total_cost * 100) if total_cost > 0 else 0

            # Detailed phase breakdown
            development_cost = summary.cost_by_phase.get(ModelLifecyclePhase.DEVELOPMENT, 0.0)
            training_cost = summary.cost_by_phase.get(ModelLifecyclePhase.TRAINING, 0.0)
            validation_cost = summary.cost_by_phase.get(ModelLifecyclePhase.VALIDATION, 0.0)
            deployment_prep_cost = summary.cost_by_phase.get(ModelLifecyclePhase.DEPLOYMENT_PREP, 0.0)

            inference_cost = summary.cost_by_phase.get(ModelLifecyclePhase.PRODUCTION, 0.0)
            monitoring_cost = summary.cost_by_phase.get(ModelLifecyclePhase.MONITORING, 0.0)
            retraining_cost = summary.cost_by_phase.get(ModelLifecyclePhase.RETRAINING, 0.0)

            # Calculate efficiency metrics
            inference_requests = self._get_inference_request_count(mid, start_time, end_time)
            cost_per_inference = (inference_cost / inference_requests) if inference_requests > 0 else 0

            # Calculate durations
            build_duration_days = self._calculate_phase_duration(mid, build_phases, start_time, end_time)
            production_duration_days = self._calculate_phase_duration(mid, production_phases, start_time, end_time)
            daily_production_cost = (production_cost / production_duration_days) if production_duration_days > 0 else 0

            # ROI calculation (simplified - would need revenue data for full calculation)
            model_roi = self._calculate_simple_roi(build_cost, production_cost, production_duration_days)
            payback_period_days = self._calculate_payback_period(build_cost, daily_production_cost)

            analysis = BuildVsProductionAnalysis(
                model_id=mid,
                model_name=model_metadata.model_name,
                total_cost=total_cost,
                build_cost=build_cost,
                production_cost=production_cost,
                build_percentage=build_percentage,
                production_percentage=production_percentage,
                development_cost=development_cost,
                training_cost=training_cost,
                validation_cost=validation_cost,
                deployment_prep_cost=deployment_prep_cost,
                inference_cost=inference_cost,
                monitoring_cost=monitoring_cost,
                retraining_cost=retraining_cost,
                cost_per_inference=cost_per_inference,
                daily_production_cost=daily_production_cost,
                model_roi=model_roi,
                payback_period_days=payback_period_days,
                build_duration_days=build_duration_days,
                production_duration_days=production_duration_days
            )

            analyses.append(analysis)

        return analyses

    def generate_model_roi_analysis(
        self, model_id: str,
        revenue_data: Optional[Dict[str, float]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Optional[ModelROIAnalysis]:
        """Generate comprehensive ROI analysis for a model"""

        summary = self.cost_tracker.get_model_cost_summary(model_id, start_time, end_time)
        if not summary:
            return None

        model_metadata = self.cost_tracker.models[model_id]

        # Calculate investments
        build_investment = summary.get_build_phase_cost()
        operational_cost = summary.get_production_phase_cost()
        total_investment = build_investment + operational_cost

        # Revenue/value metrics (use provided data or defaults)
        revenue_generated = revenue_data.get('revenue', 0.0) if revenue_data else 0.0
        cost_savings = revenue_data.get('cost_savings', 0.0) if revenue_data else 0.0
        efficiency_gains = revenue_data.get('efficiency_gains', 0.0) if revenue_data else 0.0

        total_value = revenue_generated + cost_savings + efficiency_gains

        # ROI calculations
        roi_percentage = ((total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0

        # Calculate time-based ROI
        duration_months = (summary.end_date - summary.start_date) / (30 * 24 * 3600)
        monthly_roi = roi_percentage / duration_months if duration_months > 0 else 0

        # Payback period
        monthly_value = total_value / duration_months if duration_months > 0 else 0
        payback_period_months = total_investment / monthly_value if monthly_value > 0 else float('inf')

        # Trend analysis
        roi_trend = self._calculate_roi_trend(model_id, start_time, end_time)
        cost_trend = self._calculate_cost_trend(model_id, start_time, end_time)

        # Projections
        projected_annual_cost = operational_cost * (365 / duration_months * 30) if duration_months > 0 else 0
        projected_annual_value = total_value * (365 / duration_months * 30) if duration_months > 0 else 0
        projected_annual_roi = ((projected_annual_value - projected_annual_cost) / build_investment * 100) if build_investment > 0 else 0

        return ModelROIAnalysis(
            model_id=model_id,
            model_name=model_metadata.model_name,
            total_investment=total_investment,
            build_investment=build_investment,
            operational_cost=operational_cost,
            revenue_generated=revenue_generated,
            cost_savings=cost_savings,
            efficiency_gains=efficiency_gains,
            roi_percentage=roi_percentage,
            monthly_roi=monthly_roi,
            payback_period_months=payback_period_months,
            roi_trend=roi_trend,
            monthly_cost_trend=cost_trend,
            projected_annual_cost=projected_annual_cost,
            projected_annual_roi=projected_annual_roi
        )

    def generate_cost_forecast(
        self, model_id: str,
        forecast_days: int = 30,
        confidence_level: float = 0.95
    ) -> Optional[CostForecast]:
        """Generate cost forecast for a model"""

        if not self.forecast_enabled:
            return None

        # Get historical cost data
        cutoff_time = time.time() - (60 * 24 * 3600)  # 60 days of history
        historical_entries = [
            entry for entry in self.cost_tracker.model_cost_entries
            if entry.model_id == model_id and entry.timestamp >= cutoff_time
        ]

        if len(historical_entries) < 7:  # Need at least a week of data
            return None

        # Calculate daily costs
        daily_costs = defaultdict(float)
        for entry in historical_entries:
            day_key = time.strftime("%Y-%m-%d", time.localtime(entry.timestamp))
            daily_costs[day_key] += entry.calculated_cost

        cost_values = list(daily_costs.values())
        if not cost_values:
            return None

        # Statistical analysis
        historical_daily_avg = statistics.mean(cost_values)
        cost_std = statistics.stdev(cost_values) if len(cost_values) > 1 else 0

        # Trend analysis
        trend = self._analyze_cost_trend(cost_values)

        # Simple forecasting (linear extrapolation with trend)
        if trend == CostTrendDirection.INCREASING:
            growth_rate = 0.05  # 5% growth assumption
        elif trend == CostTrendDirection.DECREASING:
            growth_rate = -0.03  # 3% decrease assumption
        else:
            growth_rate = 0.0

        # Calculate forecast
        forecasted_daily_cost = historical_daily_avg * (1 + growth_rate * (forecast_days / 30))
        forecasted_total_cost = forecasted_daily_cost * forecast_days

        # Confidence intervals
        z_score = 1.96 if confidence_level >= 0.95 else 1.645  # 95% or 90% confidence
        margin_of_error = z_score * cost_std

        confidence_interval_low = max(0, forecasted_total_cost - (margin_of_error * forecast_days))
        confidence_interval_high = forecasted_total_cost + (margin_of_error * forecast_days)

        # Phase-specific forecasts (simplified)
        recent_build_ratio = self._get_recent_build_production_ratio(model_id)
        build_phase_forecast = forecasted_total_cost * recent_build_ratio
        production_phase_forecast = forecasted_total_cost * (1 - recent_build_ratio)

        return CostForecast(
            model_id=model_id,
            forecast_period_days=forecast_days,
            historical_daily_avg=historical_daily_avg,
            historical_trend=trend,
            forecasted_total_cost=forecasted_total_cost,
            forecasted_daily_cost=forecasted_daily_cost,
            confidence_interval_low=confidence_interval_low,
            confidence_interval_high=confidence_interval_high,
            build_phase_forecast=build_phase_forecast,
            production_phase_forecast=production_phase_forecast,
            growth_assumptions=growth_rate
        )

    def generate_executive_summary(
        self, period: ReportPeriod = ReportPeriod.MONTHLY,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> ExecutiveCostSummary:
        """Generate executive-level cost summary"""

        # Determine time period
        if not start_time or not end_time:
            end_time = time.time()
            if period == ReportPeriod.MONTHLY:
                start_time = end_time - (30 * 24 * 3600)
            elif period == ReportPeriod.WEEKLY:
                start_time = end_time - (7 * 24 * 3600)
            elif period == ReportPeriod.QUARTERLY:
                start_time = end_time - (90 * 24 * 3600)
            else:  # Daily
                start_time = end_time - (24 * 3600)

        # Get all model summaries for the period
        summaries = self.cost_tracker.get_all_models_cost_summary(start_time, end_time)

        if not summaries:
            return ExecutiveCostSummary(
                report_period=period,
                start_date=start_time,
                end_date=end_time,
                total_ai_investment=0.0,
                total_build_cost=0.0,
                total_production_cost=0.0,
                active_models_count=0
            )

        # Calculate overall metrics
        total_build_cost = sum(s.get_build_phase_cost() for s in summaries)
        total_production_cost = sum(s.get_production_phase_cost() for s in summaries)
        total_ai_investment = total_build_cost + total_production_cost
        active_models_count = len(summaries)

        # Top performers analysis
        top_cost_models = sorted(summaries, key=lambda x: x.total_cost, reverse=True)[:5]
        top_cost_list = [
            {
                "model_id": s.model_id,
                "model_name": s.model_metadata.model_name,
                "total_cost": s.total_cost,
                "cost_percentage": (s.total_cost / total_ai_investment * 100) if total_ai_investment > 0 else 0
            }
            for s in top_cost_models
        ]

        # Calculate resource utilization percentages
        total_compute_cost = sum(
            s.cost_by_resource_type.get(ResourceType.COMPUTE_GPU, 0) +
            s.cost_by_resource_type.get(ResourceType.COMPUTE_CPU, 0)
            for s in summaries
        )
        total_storage_cost = sum(
            s.cost_by_resource_type.get(ResourceType.STORAGE_SSD, 0) +
            s.cost_by_resource_type.get(ResourceType.STORAGE_HDD, 0) +
            s.cost_by_resource_type.get(ResourceType.STORAGE_OBJECT, 0)
            for s in summaries
        )
        total_network_cost = sum(
            s.cost_by_resource_type.get(ResourceType.NETWORK_EGRESS, 0) +
            s.cost_by_resource_type.get(ResourceType.NETWORK_INGRESS, 0)
            for s in summaries
        )

        compute_percentage = (total_compute_cost / total_ai_investment * 100) if total_ai_investment > 0 else 0
        storage_percentage = (total_storage_cost / total_ai_investment * 100) if total_ai_investment > 0 else 0
        network_percentage = (total_network_cost / total_ai_investment * 100) if total_ai_investment > 0 else 0

        # Trend analysis
        cost_trend = self._calculate_portfolio_cost_trend(start_time, end_time)
        cost_growth_rate = self._calculate_cost_growth_rate(start_time, end_time)

        # Forecasts
        next_month_forecast = self._calculate_portfolio_forecast(30)
        next_quarter_forecast = self._calculate_portfolio_forecast(90)

        # Generate recommendations
        optimization_opportunities = self._generate_optimization_recommendations(summaries)
        budget_alerts = self._generate_budget_alerts(summaries, total_ai_investment)

        return ExecutiveCostSummary(
            report_period=period,
            start_date=start_time,
            end_date=end_time,
            total_ai_investment=total_ai_investment,
            total_build_cost=total_build_cost,
            total_production_cost=total_production_cost,
            active_models_count=active_models_count,
            top_cost_models=top_cost_list,
            cost_trend=cost_trend,
            cost_growth_rate=cost_growth_rate,
            compute_cost_percentage=compute_percentage,
            storage_cost_percentage=storage_percentage,
            network_cost_percentage=network_percentage,
            next_month_forecast=next_month_forecast,
            next_quarter_forecast=next_quarter_forecast,
            optimization_opportunities=optimization_opportunities,
            budget_alerts=budget_alerts
        )

    # Helper methods for calculations
    def _get_inference_request_count(self, model_id: str, start_time: Optional[float], end_time: Optional[float]) -> int:
        """Get count of inference requests for a model"""
        entries = [
            entry for entry in self.cost_tracker.model_cost_entries
            if entry.model_id == model_id and
               entry.resource_usage.resource_type == ResourceType.INFERENCE_REQUEST and
               (start_time is None or entry.timestamp >= start_time) and
               (end_time is None or entry.timestamp <= end_time)
        ]
        return sum(int(entry.resource_usage.usage_amount) for entry in entries)

    def _calculate_phase_duration(self, model_id: str, phases: List[ModelLifecyclePhase],
                                start_time: Optional[float], end_time: Optional[float]) -> float:
        """Calculate duration in days for specific phases"""
        entries = [
            entry for entry in self.cost_tracker.model_cost_entries
            if entry.model_id == model_id and
               entry.phase in phases and
               (start_time is None or entry.timestamp >= start_time) and
               (end_time is None or entry.timestamp <= end_time)
        ]

        if not entries:
            return 0.0

        timestamps = [entry.timestamp for entry in entries]
        duration_seconds = max(timestamps) - min(timestamps)
        return duration_seconds / (24 * 3600)  # Convert to days

    def _calculate_simple_roi(self, build_cost: float, production_cost: float, duration_days: float) -> Optional[float]:
        """Calculate simplified ROI based on cost efficiency"""
        if build_cost == 0 or duration_days == 0:
            return None

        # Simple efficiency metric: production value vs build investment
        daily_production_value = production_cost / duration_days if duration_days > 0 else 0

        # Assume production generates 2x its cost in value (simplified)
        estimated_value = daily_production_value * 2 * duration_days

        roi = ((estimated_value - build_cost) / build_cost * 100) if build_cost > 0 else 0
        return roi

    def _calculate_payback_period(self, build_cost: float, daily_production_cost: float) -> Optional[float]:
        """Calculate payback period in days"""
        if daily_production_cost <= 0:
            return None

        # Assume daily production generates 1.5x its cost in value
        daily_value = daily_production_cost * 1.5
        daily_profit = daily_value - daily_production_cost

        if daily_profit <= 0:
            return None

        return build_cost / daily_profit

    def _calculate_roi_trend(self, model_id: str, start_time: Optional[float], end_time: Optional[float]) -> CostTrendDirection:
        """Calculate ROI trend direction"""
        # Simplified implementation - would need more sophisticated analysis
        return CostTrendDirection.STABLE

    def _calculate_cost_trend(self, model_id: str, start_time: Optional[float], end_time: Optional[float]) -> CostTrendDirection:
        """Calculate cost trend direction"""
        # Get recent cost entries
        entries = [
            entry for entry in self.cost_tracker.model_cost_entries
            if entry.model_id == model_id and
               (start_time is None or entry.timestamp >= start_time) and
               (end_time is None or entry.timestamp <= end_time)
        ]

        if len(entries) < 14:  # Need at least 2 weeks of data
            return CostTrendDirection.STABLE

        # Group by week and calculate trend
        weekly_costs = defaultdict(float)
        for entry in entries:
            week_key = time.strftime("%Y-W%U", time.localtime(entry.timestamp))
            weekly_costs[week_key] += entry.calculated_cost

        cost_values = list(weekly_costs.values())
        if len(cost_values) < 2:
            return CostTrendDirection.STABLE

        return self._analyze_cost_trend(cost_values)

    def _analyze_cost_trend(self, cost_values: List[float]) -> CostTrendDirection:
        """Analyze trend from cost values"""
        if len(cost_values) < 2:
            return CostTrendDirection.STABLE

        # Simple trend analysis
        first_half = cost_values[:len(cost_values)//2]
        second_half = cost_values[len(cost_values)//2:]

        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)

        change_percentage = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0

        if change_percentage > 10:
            return CostTrendDirection.INCREASING
        elif change_percentage < -10:
            return CostTrendDirection.DECREASING
        else:
            return CostTrendDirection.STABLE

    def _get_recent_build_production_ratio(self, model_id: str) -> float:
        """Get recent build vs production cost ratio"""
        cutoff_time = time.time() - (30 * 24 * 3600)  # Last 30 days
        recent_summary = self.cost_tracker.get_model_cost_summary(model_id, cutoff_time, None)

        if not recent_summary:
            return 0.5  # Default 50/50 split

        build_cost = recent_summary.get_build_phase_cost()
        total_cost = recent_summary.total_cost

        return (build_cost / total_cost) if total_cost > 0 else 0.5

    def _calculate_portfolio_cost_trend(self, start_time: float, end_time: float) -> CostTrendDirection:
        """Calculate overall portfolio cost trend"""
        # Group all costs by week
        weekly_costs = defaultdict(float)

        for entry in self.cost_tracker.model_cost_entries:
            if start_time <= entry.timestamp <= end_time:
                week_key = time.strftime("%Y-W%U", time.localtime(entry.timestamp))
                weekly_costs[week_key] += entry.calculated_cost

        cost_values = list(weekly_costs.values())
        return self._analyze_cost_trend(cost_values)

    def _calculate_cost_growth_rate(self, start_time: float, end_time: float) -> float:
        """Calculate cost growth rate"""
        # Compare first and last week costs
        weekly_costs = defaultdict(float)

        for entry in self.cost_tracker.model_cost_entries:
            if start_time <= entry.timestamp <= end_time:
                week_key = time.strftime("%Y-W%U", time.localtime(entry.timestamp))
                weekly_costs[week_key] += entry.calculated_cost

        if len(weekly_costs) < 2:
            return 0.0

        sorted_weeks = sorted(weekly_costs.keys())
        first_week_cost = weekly_costs[sorted_weeks[0]]
        last_week_cost = weekly_costs[sorted_weeks[-1]]

        if first_week_cost == 0:
            return 0.0

        return ((last_week_cost - first_week_cost) / first_week_cost * 100)

    def _calculate_portfolio_forecast(self, days: int) -> float:
        """Calculate portfolio-wide cost forecast"""
        # Simple implementation - sum of individual model forecasts
        total_forecast = 0.0

        for model_id in self.cost_tracker.models.keys():
            forecast = self.generate_cost_forecast(model_id, days)
            if forecast:
                total_forecast += forecast.forecasted_total_cost

        return total_forecast

    def _generate_optimization_recommendations(self, summaries: List[ModelCostSummary]) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []

        # Analyze high-cost models
        if summaries:
            avg_cost = statistics.mean(s.total_cost for s in summaries)
            high_cost_models = [s for s in summaries if s.total_cost > avg_cost * 2]

            if high_cost_models:
                recommendations.append(
                    f"Review {len(high_cost_models)} high-cost models that exceed 2x average cost"
                )

        # Analyze resource utilization
        total_gpu_cost = sum(
            s.cost_by_resource_type.get(ResourceType.COMPUTE_GPU, 0) for s in summaries
        )
        total_cost = sum(s.total_cost for s in summaries)

        if total_cost > 0 and total_gpu_cost / total_cost > 0.7:
            recommendations.append("GPU costs are >70% of total - consider GPU optimization")

        return recommendations

    def _generate_budget_alerts(self, summaries: List[ModelCostSummary], total_cost: float) -> List[str]:
        """Generate budget alerts"""
        alerts = []

        # Example budget threshold (would be configurable in real implementation)
        monthly_budget = 50000  # $50K monthly budget

        if total_cost > monthly_budget * 0.9:
            alerts.append(f"Approaching monthly budget limit: ${total_cost:.2f} / ${monthly_budget:.2f}")

        return alerts

    def export_cost_report(self, report_type: str, **kwargs) -> Dict[str, Any]:
        """Export comprehensive cost report"""
        export_data = {
            "report_type": report_type,
            "generated_at": time.time(),
            "parameters": kwargs
        }

        if report_type == "build_vs_production":
            analysis = self.generate_build_vs_production_analysis(**kwargs)
            export_data["analysis"] = [
                {
                    "model_id": a.model_id,
                    "model_name": a.model_name,
                    "total_cost": a.total_cost,
                    "build_cost": a.build_cost,
                    "production_cost": a.production_cost,
                    "build_percentage": a.build_percentage,
                    "production_percentage": a.production_percentage,
                    "cost_per_inference": a.cost_per_inference,
                    "model_roi": a.model_roi,
                    "payback_period_days": a.payback_period_days
                }
                for a in analysis
            ]

        elif report_type == "executive_summary":
            summary = self.generate_executive_summary(**kwargs)
            export_data["summary"] = {
                "total_ai_investment": summary.total_ai_investment,
                "total_build_cost": summary.total_build_cost,
                "total_production_cost": summary.total_production_cost,
                "active_models_count": summary.active_models_count,
                "cost_trend": summary.cost_trend.value,
                "cost_growth_rate": summary.cost_growth_rate,
                "top_cost_models": summary.top_cost_models,
                "optimization_opportunities": summary.optimization_opportunities,
                "budget_alerts": summary.budget_alerts
            }

        return export_data