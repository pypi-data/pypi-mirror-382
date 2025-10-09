"""
Engineer Insight Generator
===========================

Generate insights tailored for Engineers and DevOps teams.

Focus areas:
- Resource efficiency
- Idle resources
- Optimization opportunities
- Performance vs cost
- Technical recommendations
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List
from ..insight_engine import InsightGenerator, Insight, InsightPriority, InsightCategory


class EngineerInsightGenerator(InsightGenerator):
    """Generate Engineer-specific insights."""

    def generate(self, hub, cost_obs, time_range: str = "30d") -> List[Insight]:
        """
        Generate Engineer insights.

        Args:
            hub: ObservabilityHub instance
            cost_obs: CostObservatory instance
            time_range: Time range for analysis

        Returns:
            List of Engineer-focused insights
        """
        insights = []

        # Generate insights (using mock data for now)
        # In production, use real hub and cost_obs data
        insights.extend(self._analyze_idle_resources(hub, time_range))
        insights.extend(self._analyze_resource_utilization(hub, time_range))
        insights.extend(self._analyze_optimization_opportunities(hub, time_range))
        insights.extend(self._analyze_cost_spikes(cost_obs, time_range))

        return insights

    def _analyze_idle_resources(self, hub, time_range: str) -> List[Insight]:
        """Detect idle or underutilized resources."""
        insights = []

        # Mock analysis
        insights.append(
            Insight(
                title="Idle Production Resources Detected",
                description=(
                    "prod-cluster-3 has 23 idle pods consuming $1,200/day. "
                    "Average CPU usage: 8%, Memory usage: 12%. These pods have "
                    "been idle for 72+ hours with no traffic."
                ),
                priority=InsightPriority.HIGH,
                category=InsightCategory.COST_OPTIMIZATION,
                impact="High - Wasting $36K/month on unused resources",
                recommendation=(
                    "Immediate: Scale down prod-cluster-3 to minimum required capacity. "
                    "Long-term: Implement auto-scaling based on traffic patterns. "
                    "Estimated savings: $30K/month."
                ),
                metadata={
                    "cluster": "prod-cluster-3",
                    "idle_pods": 23,
                    "daily_cost": 1200,
                    "cpu_avg": 8,
                    "memory_avg": 12,
                    "idle_hours": 72,
                },
                confidence=0.95,
            )
        )

        return insights

    def _analyze_resource_utilization(self, hub, time_range: str) -> List[Insight]:
        """Analyze resource utilization patterns."""
        insights = []

        # Mock analysis
        insights.append(
            Insight(
                title="Database Oversized for Workload",
                description=(
                    "RDS instance db-prod-main is provisioned as db.r5.4xlarge "
                    "but CPU averages only 18% and memory 25%. Connections average "
                    "45 out of 500 max."
                ),
                priority=InsightPriority.MEDIUM,
                category=InsightCategory.COST_OPTIMIZATION,
                impact="Medium - $650/month in potential savings",
                recommendation=(
                    "Downsize to db.r5.2xlarge. Test during off-peak hours first. "
                    "Monitor for 1 week before finalizing. Annual savings: $7,800."
                ),
                metadata={
                    "resource": "db-prod-main",
                    "current_type": "db.r5.4xlarge",
                    "recommended_type": "db.r5.2xlarge",
                    "cpu_avg": 18,
                    "memory_avg": 25,
                    "monthly_savings": 650,
                },
                confidence=0.90,
            )
        )

        return insights

    def _analyze_optimization_opportunities(self, hub, time_range: str) -> List[Insight]:
        """Identify optimization opportunities."""
        insights = []

        # Mock analysis
        insights.append(
            Insight(
                title="ARM-Based Instances Opportunity",
                description=(
                    "15 EC2 instances running on x86 (m5.xlarge) could switch to "
                    "ARM-based Graviton2 (m6g.xlarge) for 20% cost savings with "
                    "same performance. Workloads are compatible (containerized apps)."
                ),
                priority=InsightPriority.MEDIUM,
                category=InsightCategory.RECOMMENDATION,
                impact="Medium - $2,400/month savings, improved sustainability",
                recommendation=(
                    "Migrate workloads to m6g.xlarge instances. Start with dev/staging "
                    "environments, then gradually move production. Timeline: 2-3 weeks."
                ),
                metadata={
                    "instance_count": 15,
                    "current_type": "m5.xlarge",
                    "recommended_type": "m6g.xlarge",
                    "savings_pct": 20,
                    "monthly_savings": 2400,
                },
                confidence=0.85,
            )
        )

        return insights

    def _analyze_cost_spikes(self, cost_obs, time_range: str) -> List[Insight]:
        """Detect unexpected cost spikes."""
        insights = []

        # Mock analysis
        insights.append(
            Insight(
                title="Data Transfer Costs Spike Detected",
                description=(
                    "Data transfer costs increased 340% in last 6 hours from $12/hour "
                    "to $53/hour. Spike corresponds with new feature deployment in "
                    "service-api-v2 that's fetching large datasets from external APIs."
                ),
                priority=InsightPriority.CRITICAL,
                category=InsightCategory.ANOMALY,
                impact="Critical - Unexpected $1,000/day cost increase",
                recommendation=(
                    "URGENT: Review service-api-v2 data fetching logic. Implement caching "
                    "for external API responses. Add rate limiting to prevent runaway costs."
                ),
                metadata={
                    "service": "service-api-v2",
                    "cost_increase_pct": 340,
                    "baseline_hourly": 12,
                    "current_hourly": 53,
                    "duration_hours": 6,
                },
                confidence=0.98,
            )
        )

        return insights
