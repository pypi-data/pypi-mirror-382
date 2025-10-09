"""
Multi-Cloud Optimizer
======================

Optimize workload placement and costs across multiple cloud providers.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

from .cloud_provider import CloudProvider, CloudResource, ResourceType
from .cost_comparator import WorkloadSpec, CloudCostComparator, CostEstimate

logger = logging.getLogger(__name__)


class OptimizationStrategy(Enum):
    """Optimization strategies."""

    COST = "cost"  # Minimize cost
    PERFORMANCE = "performance"  # Maximize performance
    BALANCED = "balanced"  # Balance cost and performance
    RELIABILITY = "reliability"  # Maximize reliability/availability


@dataclass
class OptimizationRecommendation:
    """
    Optimization recommendation.

    Attributes:
        recommendation_id: Recommendation ID
        recommendation_type: Type of recommendation
        current_state: Current configuration
        recommended_state: Recommended configuration
        estimated_savings: Monthly savings estimate
        impact: Impact description
        confidence: Confidence score (0-1)
        priority: Priority (high, medium, low)
    """

    recommendation_id: str
    recommendation_type: str
    current_state: Dict[str, Any]
    recommended_state: Dict[str, Any]
    estimated_savings: float
    impact: str = ""
    confidence: float = 0.8
    priority: str = "medium"


class MultiCloudOptimizer:
    """
    Optimize workloads across multiple cloud providers.
    """

    def __init__(self, strategy: OptimizationStrategy = OptimizationStrategy.COST):
        """
        Initialize optimizer.

        Args:
            strategy: Optimization strategy
        """
        self.strategy = strategy
        self._comparator = CloudCostComparator()

    def analyze_current_deployment(
        self, resources: List[CloudResource]
    ) -> Dict[str, Any]:
        """
        Analyze current multi-cloud deployment.

        Args:
            resources: List of cloud resources

        Returns:
            Analysis results
        """
        # Group resources by provider
        by_provider = {}
        total_cost = 0.0

        for resource in resources:
            provider = resource.provider.value
            if provider not in by_provider:
                by_provider[provider] = {
                    "count": 0,
                    "cost": 0.0,
                    "resources": []
                }

            by_provider[provider]["count"] += 1
            by_provider[provider]["cost"] += resource.get_monthly_cost()
            by_provider[provider]["resources"].append(resource)
            total_cost += resource.get_monthly_cost()

        # Calculate provider distribution
        provider_distribution = {
            provider: {
                "percentage": (data["cost"] / total_cost * 100) if total_cost > 0 else 0,
                "cost": data["cost"],
                "resources": data["count"],
            }
            for provider, data in by_provider.items()
        }

        return {
            "total_resources": len(resources),
            "total_monthly_cost": total_cost,
            "providers": list(by_provider.keys()),
            "provider_distribution": provider_distribution,
            "by_provider": by_provider,
        }

    def get_optimization_recommendations(
        self, resources: List[CloudResource]
    ) -> List[OptimizationRecommendation]:
        """
        Get optimization recommendations for current deployment.

        Args:
            resources: List of cloud resources

        Returns:
            List of recommendations
        """
        recommendations = []

        # Group by resource type
        by_type = {}
        for resource in resources:
            res_type = resource.resource_type
            if res_type not in by_type:
                by_type[res_type] = []
            by_type[res_type].append(resource)

        # Analyze each resource type
        for res_type, res_list in by_type.items():
            if res_type == ResourceType.COMPUTE:
                recommendations.extend(self._analyze_compute_resources(res_list))

        # Cross-provider optimization
        recommendations.extend(self._analyze_cross_provider_opportunities(resources))

        # Sort by estimated savings
        recommendations.sort(key=lambda x: x.estimated_savings, reverse=True)

        return recommendations

    def _analyze_compute_resources(
        self, resources: List[CloudResource]
    ) -> List[OptimizationRecommendation]:
        """Analyze compute resources for optimization."""
        recommendations = []

        # Group by provider
        by_provider = {}
        for resource in resources:
            provider = resource.provider
            if provider not in by_provider:
                by_provider[provider] = []
            by_provider[provider].append(resource)

        # Check if consolidating to single provider would save costs
        if len(by_provider) > 1:
            # Create workload spec from current resources
            total_instances = len(resources)

            workload = WorkloadSpec(
                name="Current Compute Workload",
                compute_instances=total_instances,
                cpu_cores=2,  # Average
                memory_gb=4,  # Average
            )

            # Compare costs
            for provider in by_provider.keys():
                self._comparator.add_provider(provider)

            estimates = self._comparator.compare_workload(workload)

            if estimates:
                current_cost = sum(r.get_monthly_cost() for r in resources)
                cheapest = estimates[0]

                if cheapest.monthly_cost < current_cost * 0.9:  # >10% savings
                    recommendations.append(OptimizationRecommendation(
                        recommendation_id=f"consolidate-compute-{cheapest.provider.value}",
                        recommendation_type="consolidate_provider",
                        current_state={
                            "providers": [p.value for p in by_provider.keys()],
                            "total_instances": total_instances,
                            "monthly_cost": current_cost,
                        },
                        recommended_state={
                            "provider": cheapest.provider.value,
                            "total_instances": total_instances,
                            "monthly_cost": cheapest.monthly_cost,
                        },
                        estimated_savings=current_cost - cheapest.monthly_cost,
                        impact=f"Consolidate {total_instances} instances to {cheapest.provider.value}",
                        priority="high" if current_cost - cheapest.monthly_cost > 500 else "medium",
                    ))

        return recommendations

    def _analyze_cross_provider_opportunities(
        self, resources: List[CloudResource]
    ) -> List[OptimizationRecommendation]:
        """Analyze cross-provider optimization opportunities."""
        recommendations = []

        # Check for unused resources across providers
        providers_used = set(r.provider for r in resources)

        if len(providers_used) > 2:
            # Recommendation: Simplify multi-cloud strategy
            total_cost = sum(r.get_monthly_cost() for r in resources)

            recommendations.append(OptimizationRecommendation(
                recommendation_id="simplify-multicloud",
                recommendation_type="simplify_strategy",
                current_state={
                    "providers": [p.value for p in providers_used],
                    "complexity": "high",
                },
                recommended_state={
                    "providers": "2 primary providers recommended",
                    "complexity": "medium",
                },
                estimated_savings=total_cost * 0.05,  # Est. 5% overhead from complexity
                impact="Reduce operational complexity and potential savings from simplified architecture",
                confidence=0.6,
                priority="low",
            ))

        return recommendations

    def optimize_workload_placement(
        self,
        workload: WorkloadSpec,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Determine optimal provider and configuration for a workload.

        Args:
            workload: Workload specification
            constraints: Placement constraints (regions, compliance, etc.)

        Returns:
            Optimization result with recommended placement
        """
        # Add all providers for comparison
        for provider in [CloudProvider.AWS, CloudProvider.AZURE, CloudProvider.GCP]:
            self._comparator.add_provider(provider)

        # Get cost estimates
        region_constraints = constraints.get("regions") if constraints else None
        estimates = self._comparator.compare_workload(workload, region_constraints)

        if not estimates:
            return {"error": "No cost estimates available"}

        # Apply strategy
        if self.strategy == OptimizationStrategy.COST:
            # Choose cheapest
            recommended = estimates[0]
        elif self.strategy == OptimizationStrategy.PERFORMANCE:
            # In production, factor in performance benchmarks
            # For now, assume AWS has best performance
            aws_estimate = next((e for e in estimates if e.provider == CloudProvider.AWS), estimates[0])
            recommended = aws_estimate
        else:
            # Balanced strategy - weight cost and other factors
            recommended = estimates[0]

        savings = self._comparator.get_cost_savings(estimates)

        return {
            "workload": workload.name,
            "strategy": self.strategy.value,
            "recommended_provider": recommended.provider.value,
            "recommended_region": recommended.region,
            "estimated_monthly_cost": recommended.monthly_cost,
            "estimated_annual_cost": recommended.monthly_cost * 12,
            "cost_breakdown": recommended.breakdown,
            "instance_details": recommended.instance_details,
            "alternatives": [
                {
                    "provider": e.provider.value,
                    "region": e.region,
                    "monthly_cost": e.monthly_cost,
                }
                for e in estimates[1:3]  # Show top 3
            ],
            "potential_savings": savings,
        }

    def get_migration_plan(
        self,
        current_resources: List[CloudResource],
        target_provider: CloudProvider,
        target_region: str,
    ) -> Dict[str, Any]:
        """
        Generate migration plan to target provider.

        Args:
            current_resources: Current resources
            target_provider: Target cloud provider
            target_region: Target region

        Returns:
            Migration plan
        """
        # Analyze current state
        current_analysis = self.analyze_current_deployment(current_resources)

        # Group resources by type for migration
        migration_groups = {}
        for resource in current_resources:
            res_type = resource.resource_type.value
            if res_type not in migration_groups:
                migration_groups[res_type] = []
            migration_groups[res_type].append(resource)

        # Estimate migration effort and cost
        migration_steps = []
        estimated_downtime_hours = 0.0

        for res_type, resources in migration_groups.items():
            steps_for_type = self._generate_migration_steps(
                res_type, resources, target_provider, target_region
            )
            migration_steps.extend(steps_for_type)

            # Estimate downtime
            if res_type == "compute":
                estimated_downtime_hours += len(resources) * 0.5  # 30 min per instance

        current_monthly_cost = current_analysis["total_monthly_cost"]

        # Estimate target cost (simplified)
        workload = WorkloadSpec(
            name="Migration Target",
            compute_instances=sum(1 for r in current_resources if r.resource_type == ResourceType.COMPUTE),
        )

        self._comparator.add_provider(target_provider)
        target_estimate = self._comparator._estimate_workload_cost(
            workload,
            self._comparator._providers[target_provider],
            target_region,
        )

        return {
            "current_state": current_analysis,
            "target_provider": target_provider.value,
            "target_region": target_region,
            "migration_steps": migration_steps,
            "estimated_duration_days": len(migration_steps) * 2,  # 2 days per step
            "estimated_downtime_hours": estimated_downtime_hours,
            "current_monthly_cost": current_monthly_cost,
            "target_monthly_cost": target_estimate.monthly_cost,
            "estimated_savings": current_monthly_cost - target_estimate.monthly_cost,
            "roi_months": 3,  # Simplified ROI calculation
        }

    def _generate_migration_steps(
        self,
        resource_type: str,
        resources: List[CloudResource],
        target_provider: CloudProvider,
        target_region: str,
    ) -> List[Dict[str, Any]]:
        """Generate migration steps for resource type."""
        steps = []

        steps.append({
            "step": 1,
            "phase": "preparation",
            "action": f"Audit and document {len(resources)} {resource_type} resources",
            "duration_days": 1,
        })

        steps.append({
            "step": 2,
            "phase": "setup",
            "action": f"Provision {resource_type} resources in {target_provider.value} {target_region}",
            "duration_days": 2,
        })

        steps.append({
            "step": 3,
            "phase": "migration",
            "action": f"Migrate data and configurations for {resource_type}",
            "duration_days": 3,
        })

        steps.append({
            "step": 4,
            "phase": "validation",
            "action": f"Validate {resource_type} migration and run tests",
            "duration_days": 2,
        })

        steps.append({
            "step": 5,
            "phase": "cutover",
            "action": f"Cutover traffic to new {resource_type} resources",
            "duration_days": 1,
        })

        return steps
