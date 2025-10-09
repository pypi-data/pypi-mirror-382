"""
Multi-Cloud Support
====================

Unified interface and cost optimization across multiple cloud providers.

This module provides:
- Unified cloud provider interface (AWS, Azure, GCP)
- Multi-cloud cost comparison
- Workload optimization and placement recommendations
- Migration planning
- Cross-cloud analytics

Example:
    >>> from openfinops.multicloud import CloudCostComparator, WorkloadSpec, CloudProvider
    >>>
    >>> # Compare costs across providers
    >>> comparator = CloudCostComparator()
    >>> comparator.add_provider(CloudProvider.AWS)
    >>> comparator.add_provider(CloudProvider.AZURE)
    >>>
    >>> workload = WorkloadSpec(
    ...     name="Web Application",
    ...     compute_instances=10,
    ...     cpu_cores=2,
    ...     memory_gb=4
    ... )
    >>>
    >>> report = comparator.get_comparison_report(workload)
    >>> print(report['savings_analysis'])
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from .cloud_provider import (
    CloudProvider,
    CloudProviderInterface,
    CloudResource,
    PricingData,
    ResourceType,
    AWSProvider,
    AzureProvider,
    GCPProvider,
    create_provider,
)
from .cost_comparator import (
    CloudCostComparator,
    WorkloadSpec,
    CostEstimate,
    quick_compare,
)
from .optimizer import (
    MultiCloudOptimizer,
    OptimizationStrategy,
    OptimizationRecommendation,
)

__all__ = [
    # Cloud Provider
    "CloudProvider",
    "CloudProviderInterface",
    "CloudResource",
    "PricingData",
    "ResourceType",
    "AWSProvider",
    "AzureProvider",
    "GCPProvider",
    "create_provider",
    # Cost Comparator
    "CloudCostComparator",
    "WorkloadSpec",
    "CostEstimate",
    "quick_compare",
    # Optimizer
    "MultiCloudOptimizer",
    "OptimizationStrategy",
    "OptimizationRecommendation",
]
