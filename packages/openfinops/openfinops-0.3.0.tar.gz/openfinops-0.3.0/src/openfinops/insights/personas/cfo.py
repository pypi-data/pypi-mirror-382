"""
CFO Insight Generator
=====================

Generate insights tailored for Chief Financial Officers.

Focus areas:
- Unit economics
- ROI and margins
- Budget variance
- Financial forecasting
- Cost trends
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List
from ..insight_engine import InsightGenerator, Insight, InsightPriority, InsightCategory


class CFOInsightGenerator(InsightGenerator):
    """Generate CFO-specific insights."""

    def generate(self, hub, cost_obs, time_range: str = "30d") -> List[Insight]:
        """
        Generate CFO insights.

        Args:
            hub: ObservabilityHub instance
            cost_obs: CostObservatory instance
            time_range: Time range for analysis

        Returns:
            List of CFO-focused insights
        """
        insights = []

        # Generate insights (using mock data for now)
        # In production, use real cost_obs data
        insights.extend(self._analyze_cost_trends(cost_obs, time_range))
        insights.extend(self._analyze_budget_variance(cost_obs, time_range))
        insights.extend(self._analyze_unit_economics(cost_obs, time_range))
        insights.extend(self._analyze_roi(cost_obs, time_range))

        return insights

    def _analyze_cost_trends(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze cost trends for executive summary."""
        insights = []

        # Mock analysis - in production, use real data
        # Example: Cloud spend increased but revenue per customer improved
        insights.append(
            Insight(
                title="Cloud Spend Efficiency Improving",
                description=(
                    "Cloud infrastructure costs increased 15% this month to $125,000, "
                    "but revenue per customer improved 22%, indicating better unit economics. "
                    "The cost increase is driven by 30% user growth and new product launches."
                ),
                priority=InsightPriority.MEDIUM,
                category=InsightCategory.COST_OPTIMIZATION,
                impact="Positive - Improving cost efficiency despite growth",
                recommendation=(
                    "Continue current optimization efforts. Consider increasing "
                    "Reserved Instance coverage to lock in current pricing."
                ),
                metadata={
                    "cost_change_pct": 15,
                    "revenue_per_customer_change_pct": 22,
                    "total_spend": 125000,
                },
                confidence=0.9,
            )
        )

        return insights

    def _analyze_budget_variance(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze budget vs actual spending."""
        insights = []

        # Mock analysis
        insights.append(
            Insight(
                title="Infrastructure Budget Variance",
                description=(
                    "Infrastructure spending is at $118,500 against a budget of $120,000 "
                    "(98.8% utilized). ML training costs are tracking 12% under budget "
                    "due to successful Spot instance optimization."
                ),
                priority=InsightPriority.LOW,
                category=InsightCategory.BUDGET,
                impact="On track - Budget well-managed",
                recommendation=(
                    "Current budget allocation is appropriate. Reallocate $5K saved "
                    "from ML training to expand data analytics capacity."
                ),
                metadata={
                    "budget": 120000,
                    "actual": 118500,
                    "variance_pct": 1.2,
                },
                confidence=0.95,
            )
        )

        return insights

    def _analyze_unit_economics(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze cost per customer/transaction."""
        insights = []

        # Mock analysis
        insights.append(
            Insight(
                title="Unit Economics Trending Favorably",
                description=(
                    "Cost per active user decreased from $2.15 to $1.87 (13% reduction) "
                    "while maintaining service quality. Infrastructure costs are scaling "
                    "sub-linearly with user growth."
                ),
                priority=InsightPriority.MEDIUM,
                category=InsightCategory.EFFICIENCY,
                impact="High - Improved profitability per customer",
                recommendation=(
                    "Document and replicate optimization strategies across other services. "
                    "Target: Reduce to $1.50 per user by Q2."
                ),
                metadata={
                    "cost_per_user_previous": 2.15,
                    "cost_per_user_current": 1.87,
                    "reduction_pct": 13,
                },
                confidence=0.92,
            )
        )

        return insights

    def _analyze_roi(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze return on infrastructure investment."""
        insights = []

        # Mock analysis
        insights.append(
            Insight(
                title="AI/ML Infrastructure ROI Analysis",
                description=(
                    "AI/ML infrastructure costs $45K/month but generates $152K in "
                    "additional revenue through recommendations and personalization. "
                    "ROI: 238% ($3.38 revenue per $1 spent)."
                ),
                priority=InsightPriority.HIGH,
                category=InsightCategory.RECOMMENDATION,
                impact="Excellent - Strong positive ROI on AI investment",
                recommendation=(
                    "Increase AI/ML infrastructure budget by 25% to expand capabilities. "
                    "Expected revenue increase: $50K/month with similar ROI."
                ),
                metadata={
                    "monthly_cost": 45000,
                    "monthly_revenue": 152000,
                    "roi_pct": 238,
                    "revenue_per_dollar": 3.38,
                },
                confidence=0.88,
            )
        )

        return insights
