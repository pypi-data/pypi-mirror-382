"""
Multi-Cloud Cost Comparator
=============================

Compare costs across cloud providers for workload optimization.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .cloud_provider import CloudProvider, CloudProviderInterface, PricingData, create_provider

logger = logging.getLogger(__name__)


@dataclass
class WorkloadSpec:
    """
    Workload specification for cost comparison.

    Attributes:
        name: Workload name
        compute_instances: Number of compute instances
        cpu_cores: CPU cores per instance
        memory_gb: Memory in GB per instance
        storage_gb: Storage in GB
        network_gb_month: Network traffic in GB/month
        database_instances: Number of database instances
        requirements: Additional requirements
    """

    name: str
    compute_instances: int = 0
    cpu_cores: int = 2
    memory_gb: int = 4
    storage_gb: int = 100
    network_gb_month: float = 100.0
    database_instances: int = 0
    requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CostEstimate:
    """
    Cost estimate for a workload on a cloud provider.

    Attributes:
        provider: Cloud provider
        workload_name: Workload name
        monthly_cost: Estimated monthly cost
        breakdown: Cost breakdown by service
        instance_details: Instance configuration details
        region: Region used for estimate
        confidence: Confidence level (0-1)
    """

    provider: CloudProvider
    workload_name: str
    monthly_cost: float
    breakdown: Dict[str, float] = field(default_factory=dict)
    instance_details: Dict[str, Any] = field(default_factory=dict)
    region: str = ""
    confidence: float = 0.9


class CloudCostComparator:
    """
    Compare costs across multiple cloud providers.
    """

    def __init__(self):
        """Initialize cost comparator."""
        self._providers: Dict[CloudProvider, CloudProviderInterface] = {}

    def add_provider(self, provider: CloudProvider):
        """
        Add cloud provider to comparison.

        Args:
            provider: Cloud provider
        """
        if provider not in self._providers:
            self._providers[provider] = create_provider(provider)
            logger.info(f"Added provider: {provider.value}")

    def compare_workload(
        self, workload: WorkloadSpec, regions: Optional[Dict[CloudProvider, str]] = None
    ) -> List[CostEstimate]:
        """
        Compare workload costs across providers.

        Args:
            workload: Workload specification
            regions: Region per provider (optional)

        Returns:
            List of cost estimates per provider
        """
        estimates = []

        for provider, provider_interface in self._providers.items():
            region = regions.get(provider) if regions else None
            if not region:
                # Use default region
                available_regions = provider_interface.list_regions()
                region = available_regions[0] if available_regions else "default"

            estimate = self._estimate_workload_cost(workload, provider_interface, region)
            estimates.append(estimate)

        return sorted(estimates, key=lambda x: x.monthly_cost)

    def _estimate_workload_cost(
        self, workload: WorkloadSpec, provider: CloudProviderInterface, region: str
    ) -> CostEstimate:
        """
        Estimate cost for a workload on a specific provider.

        Args:
            workload: Workload specification
            provider: Cloud provider interface
            region: Region

        Returns:
            Cost estimate
        """
        breakdown = {}
        instance_details = {}

        # Compute cost
        if workload.compute_instances > 0:
            instance_type = self._select_instance_type(
                provider, workload.cpu_cores, workload.memory_gb
            )

            compute_pricing = provider.get_pricing("compute", instance_type, region)
            if compute_pricing:
                monthly_compute = (
                    compute_pricing.price_per_hour * 730 * workload.compute_instances
                )
                breakdown["compute"] = monthly_compute
                instance_details["compute"] = {
                    "instance_type": instance_type,
                    "count": workload.compute_instances,
                    "hourly_cost": compute_pricing.price_per_hour,
                }

        # Storage cost
        if workload.storage_gb > 0:
            storage_cost_per_gb = self._get_storage_cost(provider.provider, region)
            breakdown["storage"] = workload.storage_gb * storage_cost_per_gb

        # Network cost
        if workload.network_gb_month > 0:
            network_cost_per_gb = self._get_network_cost(provider.provider, region)
            breakdown["network"] = workload.network_gb_month * network_cost_per_gb

        # Database cost
        if workload.database_instances > 0:
            db_cost = self._estimate_database_cost(
                provider, region, workload.database_instances
            )
            breakdown["database"] = db_cost

        total_cost = sum(breakdown.values())

        return CostEstimate(
            provider=provider.provider,
            workload_name=workload.name,
            monthly_cost=total_cost,
            breakdown=breakdown,
            instance_details=instance_details,
            region=region,
        )

    def _select_instance_type(
        self, provider: CloudProviderInterface, cpu_cores: int, memory_gb: int
    ) -> str:
        """
        Select appropriate instance type based on requirements.

        Args:
            provider: Cloud provider
            cpu_cores: Required CPU cores
            memory_gb: Required memory in GB

        Returns:
            Instance type identifier
        """
        # Simplified instance selection - in production, use comprehensive instance database
        if provider.provider == CloudProvider.AWS:
            if cpu_cores <= 1:
                return "t3.micro" if memory_gb <= 1 else "t3.small"
            elif cpu_cores <= 2:
                return "t3.medium" if memory_gb <= 4 else "t3.large"
            else:
                return "t3.xlarge"

        elif provider.provider == CloudProvider.AZURE:
            if cpu_cores <= 1:
                return "Standard_B1s" if memory_gb <= 1 else "Standard_B1ms"
            elif cpu_cores <= 2:
                return "Standard_B2s" if memory_gb <= 4 else "Standard_D2s_v3"
            else:
                return "Standard_D4s_v3"

        elif provider.provider == CloudProvider.GCP:
            if cpu_cores <= 1:
                return "f1-micro" if memory_gb <= 0.6 else "g1-small"
            elif cpu_cores <= 2:
                return "n1-standard-1" if memory_gb <= 3.75 else "n1-standard-2"
            else:
                return "n1-standard-4"

        return "unknown"

    def _get_storage_cost(self, provider: CloudProvider, region: str) -> float:
        """Get storage cost per GB per month."""
        # Simplified pricing - actual costs vary by storage type
        storage_costs = {
            CloudProvider.AWS: 0.023,  # S3 Standard
            CloudProvider.AZURE: 0.020,  # Azure Blob Storage
            CloudProvider.GCP: 0.020,  # Cloud Storage Standard
        }
        return storage_costs.get(provider, 0.025)

    def _get_network_cost(self, provider: CloudProvider, region: str) -> float:
        """Get network cost per GB."""
        # Simplified egress pricing
        network_costs = {
            CloudProvider.AWS: 0.09,  # First 10 TB
            CloudProvider.AZURE: 0.087,  # First 5 GB free, then $0.087
            CloudProvider.GCP: 0.12,  # First GB free, then varies
        }
        return network_costs.get(provider, 0.10)

    def _estimate_database_cost(
        self, provider: CloudProviderInterface, region: str, instances: int
    ) -> float:
        """Estimate database cost."""
        # Simplified database pricing for small instance
        db_type = "db.t3.micro" if provider.provider == CloudProvider.AWS else "db-f1-micro"

        pricing = provider.get_pricing("database", db_type, region)
        if pricing:
            return pricing.price_per_hour * 730 * instances

        # Fallback estimate
        return 15.0 * instances  # ~$15/month per small instance

    def get_cost_savings(self, estimates: List[CostEstimate]) -> Dict[str, Any]:
        """
        Calculate potential savings by choosing cheapest provider.

        Args:
            estimates: List of cost estimates

        Returns:
            Savings analysis
        """
        if len(estimates) < 2:
            return {"savings": 0, "message": "Need at least 2 providers to compare"}

        sorted_estimates = sorted(estimates, key=lambda x: x.monthly_cost)
        cheapest = sorted_estimates[0]
        most_expensive = sorted_estimates[-1]

        monthly_savings = most_expensive.monthly_cost - cheapest.monthly_cost
        annual_savings = monthly_savings * 12
        percentage_savings = (
            (monthly_savings / most_expensive.monthly_cost * 100)
            if most_expensive.monthly_cost > 0
            else 0
        )

        return {
            "cheapest_provider": cheapest.provider.value,
            "cheapest_cost": cheapest.monthly_cost,
            "most_expensive_provider": most_expensive.provider.value,
            "most_expensive_cost": most_expensive.monthly_cost,
            "monthly_savings": monthly_savings,
            "annual_savings": annual_savings,
            "percentage_savings": percentage_savings,
        }

    def compare_regions(
        self, provider: CloudProvider, workload: WorkloadSpec
    ) -> List[Dict[str, Any]]:
        """
        Compare costs across regions for a single provider.

        Args:
            provider: Cloud provider
            workload: Workload specification

        Returns:
            Region comparison data
        """
        if provider not in self._providers:
            self.add_provider(provider)

        provider_interface = self._providers[provider]
        regions = provider_interface.list_regions()

        comparisons = []
        for region in regions:
            estimate = self._estimate_workload_cost(workload, provider_interface, region)
            comparisons.append({
                "region": region,
                "monthly_cost": estimate.monthly_cost,
                "breakdown": estimate.breakdown,
            })

        return sorted(comparisons, key=lambda x: x["monthly_cost"])

    def get_comparison_report(
        self, workload: WorkloadSpec, regions: Optional[Dict[CloudProvider, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive comparison report.

        Args:
            workload: Workload specification
            regions: Region per provider

        Returns:
            Comparison report
        """
        estimates = self.compare_workload(workload, regions)
        savings = self.get_cost_savings(estimates)

        return {
            "workload": workload.name,
            "timestamp": datetime.now().isoformat(),
            "estimates": [
                {
                    "provider": e.provider.value,
                    "region": e.region,
                    "monthly_cost": e.monthly_cost,
                    "annual_cost": e.monthly_cost * 12,
                    "breakdown": e.breakdown,
                    "instance_details": e.instance_details,
                }
                for e in estimates
            ],
            "savings_analysis": savings,
            "recommendation": self._generate_recommendation(estimates, savings),
        }

    def _generate_recommendation(
        self, estimates: List[CostEstimate], savings: Dict[str, Any]
    ) -> str:
        """Generate cost recommendation."""
        if not estimates:
            return "No cost data available for comparison"

        cheapest = estimates[0]
        percentage_savings = savings.get("percentage_savings", 0)

        if percentage_savings > 20:
            return (
                f"Strong recommendation: Migrate to {cheapest.provider.value} "
                f"in {cheapest.region} for {percentage_savings:.1f}% cost savings "
                f"(${savings['annual_savings']:.2f}/year)"
            )
        elif percentage_savings > 10:
            return (
                f"Consider migrating to {cheapest.provider.value} "
                f"for {percentage_savings:.1f}% cost savings"
            )
        else:
            return (
                f"Costs are similar across providers. "
                f"Current choice of {cheapest.provider.value} is optimal."
            )


def quick_compare(
    workload_name: str,
    instances: int,
    cpu: int = 2,
    memory: int = 4,
    providers: Optional[List[CloudProvider]] = None,
) -> Dict[str, Any]:
    """
    Quick cost comparison across providers.

    Args:
        workload_name: Workload name
        instances: Number of instances
        cpu: CPU cores per instance
        memory: Memory GB per instance
        providers: List of providers to compare (defaults to AWS, Azure, GCP)

    Returns:
        Comparison report
    """
    workload = WorkloadSpec(
        name=workload_name,
        compute_instances=instances,
        cpu_cores=cpu,
        memory_gb=memory,
    )

    comparator = CloudCostComparator()

    if providers is None:
        providers = [CloudProvider.AWS, CloudProvider.AZURE, CloudProvider.GCP]

    for provider in providers:
        comparator.add_provider(provider)

    return comparator.get_comparison_report(workload)
