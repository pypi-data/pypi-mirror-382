"""
Tests for Multi-Cloud Support System
======================================

Test cloud provider interfaces, cost comparison, and optimization.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
from datetime import datetime, timedelta
from openfinops.multicloud import (
    # Cloud Provider
    CloudProvider,
    CloudProviderInterface,
    CloudResource,
    PricingData,
    ResourceType,
    AWSProvider,
    AzureProvider,
    GCPProvider,
    create_provider,
    # Cost Comparator
    CloudCostComparator,
    WorkloadSpec,
    CostEstimate,
    quick_compare,
    # Optimizer
    MultiCloudOptimizer,
    OptimizationStrategy,
    OptimizationRecommendation,
)


class TestCloudProvider:
    """Test cloud provider interfaces."""

    def test_create_aws_provider(self):
        """Test creating AWS provider."""
        provider = create_provider(CloudProvider.AWS)

        assert isinstance(provider, AWSProvider)
        assert provider.provider == CloudProvider.AWS

    def test_create_azure_provider(self):
        """Test creating Azure provider."""
        provider = create_provider(CloudProvider.AZURE)

        assert isinstance(provider, AzureProvider)
        assert provider.provider == CloudProvider.AZURE

    def test_create_gcp_provider(self):
        """Test creating GCP provider."""
        provider = create_provider(CloudProvider.GCP)

        assert isinstance(provider, GCPProvider)
        assert provider.provider == CloudProvider.GCP

    def test_list_regions_aws(self):
        """Test listing AWS regions."""
        provider = AWSProvider()
        regions = provider.list_regions()

        assert len(regions) > 0
        assert "us-east-1" in regions

    def test_list_regions_azure(self):
        """Test listing Azure regions."""
        provider = AzureProvider()
        regions = provider.list_regions()

        assert len(regions) > 0
        assert "eastus" in regions

    def test_list_regions_gcp(self):
        """Test listing GCP regions."""
        provider = GCPProvider()
        regions = provider.list_regions()

        assert len(regions) > 0
        assert "us-central1" in regions

    def test_list_resources(self):
        """Test listing resources."""
        provider = AWSProvider()
        resources = provider.list_resources(
            resource_type=ResourceType.COMPUTE,
            region="us-east-1"
        )

        assert isinstance(resources, list)
        if resources:
            assert resources[0].provider == CloudProvider.AWS

    def test_get_pricing_aws(self):
        """Test getting AWS pricing."""
        provider = AWSProvider()
        pricing = provider.get_pricing("ec2", "t3.micro", "us-east-1")

        assert pricing is not None
        assert pricing.provider == CloudProvider.AWS
        assert pricing.price_per_hour > 0

    def test_get_pricing_azure(self):
        """Test getting Azure pricing."""
        provider = AzureProvider()
        pricing = provider.get_pricing("vm", "Standard_B1s", "eastus")

        assert pricing is not None
        assert pricing.provider == CloudProvider.AZURE
        assert pricing.price_per_hour > 0

    def test_get_pricing_gcp(self):
        """Test getting GCP pricing."""
        provider = GCPProvider()
        pricing = provider.get_pricing("compute", "f1-micro", "us-central1")

        assert pricing is not None
        assert pricing.provider == CloudProvider.GCP
        assert pricing.price_per_hour > 0

    def test_get_cost_data(self):
        """Test getting cost data."""
        provider = AWSProvider()
        start = datetime.now() - timedelta(days=7)
        end = datetime.now()

        cost_data = provider.get_cost_data(start, end)

        assert isinstance(cost_data, list)


class TestCloudResource:
    """Test CloudResource class."""

    def test_resource_creation(self):
        """Test creating a cloud resource."""
        resource = CloudResource(
            resource_id="i-123",
            name="web-server",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            region="us-east-1",
            cost_per_hour=0.096,
        )

        assert resource.resource_id == "i-123"
        assert resource.provider == CloudProvider.AWS

    def test_get_monthly_cost(self):
        """Test monthly cost calculation."""
        resource = CloudResource(
            resource_id="i-123",
            name="web-server",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            region="us-east-1",
            cost_per_hour=0.096,
        )

        monthly_cost = resource.get_monthly_cost()
        assert monthly_cost == 0.096 * 730

    def test_get_annual_cost(self):
        """Test annual cost calculation."""
        resource = CloudResource(
            resource_id="i-123",
            name="web-server",
            resource_type=ResourceType.COMPUTE,
            provider=CloudProvider.AWS,
            region="us-east-1",
            cost_per_hour=0.096,
        )

        annual_cost = resource.get_annual_cost()
        assert annual_cost == 0.096 * 730 * 12


class TestPricingData:
    """Test PricingData class."""

    def test_pricing_creation(self):
        """Test creating pricing data."""
        pricing = PricingData(
            provider=CloudProvider.AWS,
            service="ec2",
            region="us-east-1",
            instance_type="t3.micro",
            price_per_hour=0.0104,
        )

        assert pricing.provider == CloudProvider.AWS
        assert pricing.price_per_hour == 0.0104

    def test_monthly_price_calculation(self):
        """Test automatic monthly price calculation."""
        pricing = PricingData(
            provider=CloudProvider.AWS,
            service="ec2",
            region="us-east-1",
            instance_type="t3.micro",
            price_per_hour=0.0104,
        )

        assert pricing.price_per_month == 0.0104 * 730


class TestWorkloadSpec:
    """Test WorkloadSpec class."""

    def test_workload_creation(self):
        """Test creating workload specification."""
        workload = WorkloadSpec(
            name="Web Application",
            compute_instances=10,
            cpu_cores=2,
            memory_gb=4,
            storage_gb=500,
        )

        assert workload.name == "Web Application"
        assert workload.compute_instances == 10


class TestCloudCostComparator:
    """Test CloudCostComparator class."""

    def test_initialization(self):
        """Test comparator initialization."""
        comparator = CloudCostComparator()

        assert comparator is not None

    def test_add_provider(self):
        """Test adding providers."""
        comparator = CloudCostComparator()

        comparator.add_provider(CloudProvider.AWS)
        comparator.add_provider(CloudProvider.AZURE)

        assert CloudProvider.AWS in comparator._providers
        assert CloudProvider.AZURE in comparator._providers

    def test_compare_workload(self):
        """Test workload comparison."""
        comparator = CloudCostComparator()

        comparator.add_provider(CloudProvider.AWS)
        comparator.add_provider(CloudProvider.AZURE)
        comparator.add_provider(CloudProvider.GCP)

        workload = WorkloadSpec(
            name="Test Workload",
            compute_instances=5,
            cpu_cores=2,
            memory_gb=4,
        )

        estimates = comparator.compare_workload(workload)

        assert len(estimates) == 3
        assert all(isinstance(e, CostEstimate) for e in estimates)
        # Should be sorted by cost (cheapest first)
        assert estimates[0].monthly_cost <= estimates[1].monthly_cost

    def test_get_cost_savings(self):
        """Test cost savings calculation."""
        comparator = CloudCostComparator()

        comparator.add_provider(CloudProvider.AWS)
        comparator.add_provider(CloudProvider.AZURE)

        workload = WorkloadSpec(
            name="Test Workload",
            compute_instances=10,
            cpu_cores=2,
            memory_gb=4,
        )

        estimates = comparator.compare_workload(workload)
        savings = comparator.get_cost_savings(estimates)

        assert "cheapest_provider" in savings
        assert "monthly_savings" in savings
        assert "percentage_savings" in savings
        assert savings["monthly_savings"] >= 0

    def test_compare_regions(self):
        """Test region comparison."""
        comparator = CloudCostComparator()

        workload = WorkloadSpec(
            name="Test Workload",
            compute_instances=5,
        )

        regions = comparator.compare_regions(CloudProvider.AWS, workload)

        assert len(regions) > 0
        assert all("region" in r for r in regions)
        assert all("monthly_cost" in r for r in regions)

    def test_get_comparison_report(self):
        """Test comparison report generation."""
        comparator = CloudCostComparator()

        comparator.add_provider(CloudProvider.AWS)
        comparator.add_provider(CloudProvider.AZURE)

        workload = WorkloadSpec(
            name="Production App",
            compute_instances=10,
            cpu_cores=2,
            memory_gb=4,
        )

        report = comparator.get_comparison_report(workload)

        assert report["workload"] == "Production App"
        assert "estimates" in report
        assert "savings_analysis" in report
        assert "recommendation" in report

    def test_quick_compare(self):
        """Test quick comparison function."""
        report = quick_compare(
            workload_name="Quick Test",
            instances=5,
            cpu=2,
            memory=4,
        )

        assert report["workload"] == "Quick Test"
        assert len(report["estimates"]) == 3  # AWS, Azure, GCP


class TestCostEstimate:
    """Test CostEstimate class."""

    def test_estimate_creation(self):
        """Test creating cost estimate."""
        estimate = CostEstimate(
            provider=CloudProvider.AWS,
            workload_name="Test",
            monthly_cost=500.0,
            breakdown={"compute": 400, "storage": 100},
            region="us-east-1",
        )

        assert estimate.provider == CloudProvider.AWS
        assert estimate.monthly_cost == 500.0
        assert estimate.breakdown["compute"] == 400


class TestMultiCloudOptimizer:
    """Test MultiCloudOptimizer class."""

    def test_initialization(self):
        """Test optimizer initialization."""
        optimizer = MultiCloudOptimizer()

        assert optimizer.strategy == OptimizationStrategy.COST

    def test_initialization_with_strategy(self):
        """Test optimizer with specific strategy."""
        optimizer = MultiCloudOptimizer(strategy=OptimizationStrategy.PERFORMANCE)

        assert optimizer.strategy == OptimizationStrategy.PERFORMANCE

    def test_analyze_current_deployment(self):
        """Test deployment analysis."""
        optimizer = MultiCloudOptimizer()

        resources = [
            CloudResource(
                resource_id="i-1",
                name="server-1",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AWS,
                region="us-east-1",
                cost_per_hour=0.096,
            ),
            CloudResource(
                resource_id="i-2",
                name="server-2",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AZURE,
                region="eastus",
                cost_per_hour=0.096,
            ),
        ]

        analysis = optimizer.analyze_current_deployment(resources)

        assert analysis["total_resources"] == 2
        assert len(analysis["providers"]) == 2
        assert "aws" in [p.lower() for p in analysis["providers"]]

    def test_get_optimization_recommendations(self):
        """Test optimization recommendations."""
        optimizer = MultiCloudOptimizer()

        resources = [
            CloudResource(
                resource_id="i-1",
                name="server-1",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AWS,
                region="us-east-1",
                cost_per_hour=0.096,
            ),
            CloudResource(
                resource_id="i-2",
                name="server-2",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AZURE,
                region="eastus",
                cost_per_hour=0.120,
            ),
        ]

        recommendations = optimizer.get_optimization_recommendations(resources)

        assert isinstance(recommendations, list)
        if recommendations:
            assert all(isinstance(r, OptimizationRecommendation) for r in recommendations)

    def test_optimize_workload_placement(self):
        """Test workload placement optimization."""
        optimizer = MultiCloudOptimizer(strategy=OptimizationStrategy.COST)

        workload = WorkloadSpec(
            name="New Application",
            compute_instances=10,
            cpu_cores=2,
            memory_gb=4,
        )

        result = optimizer.optimize_workload_placement(workload)

        assert "recommended_provider" in result
        assert "estimated_monthly_cost" in result
        assert "alternatives" in result

    def test_get_migration_plan(self):
        """Test migration plan generation."""
        optimizer = MultiCloudOptimizer()

        resources = [
            CloudResource(
                resource_id="i-1",
                name="server-1",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AWS,
                region="us-east-1",
                cost_per_hour=0.096,
            ),
        ]

        plan = optimizer.get_migration_plan(
            current_resources=resources,
            target_provider=CloudProvider.GCP,
            target_region="us-central1",
        )

        assert "current_state" in plan
        assert "target_provider" in plan
        assert "migration_steps" in plan
        assert "estimated_duration_days" in plan
        assert plan["target_provider"] == "gcp"


class TestOptimizationRecommendation:
    """Test OptimizationRecommendation class."""

    def test_recommendation_creation(self):
        """Test creating optimization recommendation."""
        recommendation = OptimizationRecommendation(
            recommendation_id="opt-001",
            recommendation_type="consolidate",
            current_state={"providers": ["aws", "azure"]},
            recommended_state={"provider": "aws"},
            estimated_savings=500.0,
            priority="high",
        )

        assert recommendation.recommendation_id == "opt-001"
        assert recommendation.estimated_savings == 500.0


class TestIntegration:
    """Integration tests for multi-cloud support."""

    def test_complete_comparison_workflow(self):
        """Test complete cost comparison workflow."""
        # Create workload
        workload = WorkloadSpec(
            name="Production Workload",
            compute_instances=20,
            cpu_cores=4,
            memory_gb=8,
            storage_gb=1000,
            network_gb_month=500,
        )

        # Compare costs
        comparator = CloudCostComparator()
        comparator.add_provider(CloudProvider.AWS)
        comparator.add_provider(CloudProvider.AZURE)
        comparator.add_provider(CloudProvider.GCP)

        report = comparator.get_comparison_report(workload)

        # Verify report
        assert report["workload"] == "Production Workload"
        assert len(report["estimates"]) == 3

        # All estimates should have costs
        for estimate in report["estimates"]:
            assert estimate["monthly_cost"] > 0
            assert "breakdown" in estimate

        # Should have savings analysis
        savings = report["savings_analysis"]
        assert "cheapest_provider" in savings
        assert "potential_savings" in savings or "percentage_savings" in savings

    def test_optimization_workflow(self):
        """Test complete optimization workflow."""
        # Current deployment
        resources = [
            CloudResource(
                resource_id="aws-1",
                name="web-1",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AWS,
                region="us-east-1",
                cost_per_hour=0.096,
            ),
            CloudResource(
                resource_id="aws-2",
                name="web-2",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AWS,
                region="us-east-1",
                cost_per_hour=0.096,
            ),
            CloudResource(
                resource_id="azure-1",
                name="db-1",
                resource_type=ResourceType.DATABASE,
                provider=CloudProvider.AZURE,
                region="eastus",
                cost_per_hour=0.120,
            ),
        ]

        # Analyze deployment
        optimizer = MultiCloudOptimizer()
        analysis = optimizer.analyze_current_deployment(resources)

        assert analysis["total_resources"] == 3
        assert len(analysis["providers"]) == 2

        # Get recommendations
        recommendations = optimizer.get_optimization_recommendations(resources)

        # Should have at least some recommendations
        assert isinstance(recommendations, list)

    def test_migration_planning_workflow(self):
        """Test migration planning workflow."""
        # Current AWS resources
        aws_resources = [
            CloudResource(
                resource_id=f"i-{i}",
                name=f"server-{i}",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AWS,
                region="us-east-1",
                cost_per_hour=0.096,
            )
            for i in range(5)
        ]

        # Plan migration to GCP
        optimizer = MultiCloudOptimizer()
        plan = optimizer.get_migration_plan(
            current_resources=aws_resources,
            target_provider=CloudProvider.GCP,
            target_region="us-central1",
        )

        # Verify plan
        assert plan["target_provider"] == "gcp"
        assert len(plan["migration_steps"]) > 0
        assert plan["estimated_duration_days"] > 0

        # Should have cost comparison
        assert "current_monthly_cost" in plan
        assert "target_monthly_cost" in plan


# Run quick test
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
