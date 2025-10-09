"""
Finance Analyst Insight Generator
==================================

Generate insights tailored for Finance Analysts.

Focus areas:
- Variance analysis
- Cost forecasting
- Budget tracking
- Trend analysis
- Financial reporting
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List
from ..insight_engine import InsightGenerator, Insight, InsightPriority, InsightCategory


class FinanceInsightGenerator(InsightGenerator):
    """Generate Finance Analyst-specific insights."""

    def generate(self, hub, cost_obs, time_range: str = "30d") -> List[Insight]:
        """Generate Finance insights."""
        insights = []

        # Generate insights (using mock data for now)
        # In production, use real cost_obs data
        insights.extend(self._analyze_variance(cost_obs, time_range))
        insights.extend(self._analyze_forecasts(cost_obs, time_range))
        insights.extend(self._analyze_cost_breakdown(cost_obs, time_range))
        insights.extend(self._analyze_trends(cost_obs, time_range))

        return insights

    def _analyze_variance(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze actual vs forecast variance."""
        insights = []

        insights.append(
            Insight(
                title="Q1 Forecast Variance Analysis",
                description=(
                    "Q1 cloud spend forecast was $234K, current trend shows $256K "
                    "(+9.4% variance). Primary drivers: AWS EC2 ($12K over due to "
                    "Black Friday surge), Databricks ($8K over from new ML projects)."
                ),
                priority=InsightPriority.HIGH,
                category=InsightCategory.FORECAST,
                impact="High - Budget reallocation needed",
                recommendation=(
                    "Submit budget amendment request for $22K additional allocation. "
                    "Adjust Q2 forecast models to account for sustained higher usage."
                ),
                metadata={
                    "forecast": 234000,
                    "trending": 256000,
                    "variance": 22000,
                    "variance_pct": 9.4,
                    "drivers": {
                        "aws_ec2": 12000,
                        "databricks": 8000,
                        "other": 2000,
                    },
                },
                confidence=0.93,
            )
        )

        return insights

    def _analyze_forecasts(self, cost_obs, time_range: str) -> List[Insight]:
        """Generate cost forecasts."""
        insights = []

        insights.append(
            Insight(
                title="End-of-Month Forecast",
                description=(
                    "Based on current trajectory, month-end cloud spend will reach "
                    "$88,500 vs budget of $85,000 (+4.1% over). Snowflake costs "
                    "trending $2.5K over budget, AWS within budget."
                ),
                priority=InsightPriority.MEDIUM,
                category=InsightCategory.FORECAST,
                impact="Medium - Minor budget overrun expected",
                recommendation=(
                    "Investigate Snowflake query patterns for optimization opportunities. "
                    "Defer non-critical workloads to next month if possible."
                ),
                metadata={
                    "budget_monthly": 85000,
                    "forecast_eom": 88500,
                    "variance": 3500,
                    "days_remaining": 8,
                },
                confidence=0.88,
            )
        )

        return insights

    def _analyze_cost_breakdown(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze cost distribution."""
        insights = []

        insights.append(
            Insight(
                title="Cost Distribution by Service",
                description=(
                    "AWS: $52K (58%), Azure: $25K (28%), Databricks: $8K (9%), "
                    "Snowflake: $4.5K (5%). AWS costs down 5% month-over-month but "
                    "Azure up 23% due to new ML workloads."
                ),
                priority=InsightPriority.LOW,
                category=InsightCategory.COST_OPTIMIZATION,
                impact="Informational - Normal distribution",
                recommendation=(
                    "Monitor Azure cost growth. If trend continues, negotiate volume "
                    "discounts or consider Azure Reserved Instances."
                ),
                metadata={
                    "aws": 52000,
                    "azure": 25000,
                    "databricks": 8000,
                    "snowflake": 4500,
                    "aws_change_pct": -5,
                    "azure_change_pct": 23,
                },
                confidence=0.95,
            )
        )

        return insights

    def _analyze_trends(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze cost trends."""
        insights = []

        insights.append(
            Insight(
                title="Quarterly Cost Trend",
                description=(
                    "Cloud costs growing 8% quarter-over-quarter, in line with "
                    "15% user growth. Cost per user declining from $2.20 to $2.05. "
                    "Trend is sustainable and indicates good scaling efficiency."
                ),
                priority=InsightPriority.LOW,
                category=InsightCategory.EFFICIENCY,
                impact="Positive - Healthy growth pattern",
                recommendation=(
                    "Continue current trajectory. Document optimization strategies "
                    "for replication across other departments."
                ),
                metadata={
                    "cost_growth_qoq_pct": 8,
                    "user_growth_qoq_pct": 15,
                    "cost_per_user_previous": 2.20,
                    "cost_per_user_current": 2.05,
                },
                confidence=0.90,
            )
        )

        return insights
