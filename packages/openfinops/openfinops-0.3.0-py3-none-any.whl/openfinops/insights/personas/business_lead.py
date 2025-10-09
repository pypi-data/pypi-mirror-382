"""
Business Lead Insight Generator
================================

Generate insights tailored for Business Leaders and Executives.

Focus areas:
- High-level KPIs
- Strategic trends
- Business impact
- Growth metrics
- Executive summary
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List
from ..insight_engine import InsightGenerator, Insight, InsightPriority, InsightCategory


class BusinessLeadInsightGenerator(InsightGenerator):
    """Generate Business Leader-specific insights."""

    def generate(self, hub, cost_obs, time_range: str = "30d") -> List[Insight]:
        """Generate Business Leader insights."""
        insights = []

        # Generate insights (using mock data for now)
        # In production, use real cost_obs data
        insights.extend(self._analyze_strategic_metrics(cost_obs, time_range))
        insights.extend(self._analyze_growth_efficiency(cost_obs, time_range))
        insights.extend(self._analyze_business_impact(cost_obs, time_range))

        return insights

    def _analyze_strategic_metrics(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze strategic KPIs."""
        insights = []

        insights.append(
            Insight(
                title="Infrastructure Efficiency Metrics",
                description=(
                    "Cloud infrastructure supporting 30% user growth while costs "
                    "increased only 8%. Infrastructure cost as % of revenue decreased "
                    "from 18% to 15%. System reliability maintained at 99.95% uptime."
                ),
                priority=InsightPriority.MEDIUM,
                category=InsightCategory.EFFICIENCY,
                impact="Positive - Strong operational efficiency",
                recommendation=(
                    "Communicate infrastructure team's success in earnings call. "
                    "Consider increasing tech budget allocation for continued growth."
                ),
                metadata={
                    "user_growth_pct": 30,
                    "cost_growth_pct": 8,
                    "cost_to_revenue_previous": 18,
                    "cost_to_revenue_current": 15,
                    "uptime_pct": 99.95,
                },
                confidence=0.92,
            )
        )

        return insights

    def _analyze_growth_efficiency(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze growth vs infrastructure scaling."""
        insights = []

        insights.append(
            Insight(
                title="Sustainable Growth Pattern",
                description=(
                    "Infrastructure costs scaling sub-linearly with business growth. "
                    "Customer acquisition cost (CAC) decreased 12% while lifetime value "
                    "(LTV) increased 18%. Infrastructure supporting this growth efficiently."
                ),
                priority=InsightPriority.HIGH,
                category=InsightCategory.RECOMMENDATION,
                impact="Excellent - Business metrics improving",
                recommendation=(
                    "Maintain current growth trajectory. Infrastructure capacity "
                    "supports 50% additional growth without major investment."
                ),
                metadata={
                    "cac_change_pct": -12,
                    "ltv_change_pct": 18,
                    "capacity_headroom_pct": 50,
                },
                confidence=0.89,
            )
        )

        return insights

    def _analyze_business_impact(self, cost_obs, time_range: str) -> List[Insight]:
        """Analyze business impact of infrastructure."""
        insights = []

        insights.append(
            Insight(
                title="Infrastructure ROI Summary",
                description=(
                    "Total cloud spend: $890K annually. Enables $12.5M in revenue "
                    "(ROI: 1,304%). Key value drivers: 99.95% uptime, <200ms response "
                    "time, support for 2.5M monthly active users."
                ),
                priority=InsightPriority.MEDIUM,
                category=InsightCategory.RECOMMENDATION,
                impact="Excellent - Strong value creation",
                recommendation=(
                    "Invest an additional $200K in infrastructure improvements for "
                    "international expansion. Expected revenue increase: $3M annually."
                ),
                metadata={
                    "annual_cost": 890000,
                    "annual_revenue": 12500000,
                    "roi_pct": 1304,
                    "uptime": 99.95,
                    "response_time_ms": 200,
                    "mau": 2500000,
                },
                confidence=0.90,
            )
        )

        return insights
