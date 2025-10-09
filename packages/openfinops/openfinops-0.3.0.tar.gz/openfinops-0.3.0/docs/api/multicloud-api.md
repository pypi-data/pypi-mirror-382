# Multi-Cloud API Reference

OpenFinOps Multi-Cloud module for unified cost comparison and optimization across AWS, Azure, and GCP.

## Overview

The Multi-Cloud module provides:
- Unified interface for AWS, Azure, and GCP
- Cross-cloud cost comparison
- Workload placement optimization
- Migration planning and analysis
- Instance type selection

## Modules

- `openfinops.multicloud.cloud_provider` - Cloud provider interfaces
- `openfinops.multicloud.cost_comparator` - Cost comparison engine
- `openfinops.multicloud.optimizer` - Workload optimization

---

## Cloud Provider API

### Unified Provider Interface

All cloud providers implement the `CloudProviderInterface`.

#### `create_provider()`

Factory function to create cloud provider instances.

```python
from openfinops.multicloud import create_provider, CloudProvider

# Create AWS provider
aws = create_provider(CloudProvider.AWS)

# Create Azure provider
azure = create_provider(CloudProvider.AZURE)

# Create GCP provider
gcp = create_provider(CloudProvider.GCP)
```

**Parameters:**
- `provider` - CloudProvider enum value

**Returns:** Provider instance (AWSProvider, AzureProvider, or GCPProvider)

---

### `CloudProviderInterface`

Abstract base class for all cloud providers.

#### Methods

##### `list_regions() -> List[str]`

Get available regions for the provider.

```python
regions = aws.list_regions()
print(f"AWS regions: {regions}")
# Output: ['us-east-1', 'us-west-2', 'eu-west-1', ...]
```

**Returns:** List of region identifiers

---

##### `list_resources(resource_type: ResourceType, region: str) -> List[CloudResource]`

List resources of a specific type in a region.

```python
from openfinops.multicloud import ResourceType

# List compute instances
instances = aws.list_resources(
    resource_type=ResourceType.COMPUTE,
    region="us-east-1"
)

for instance in instances:
    print(f"{instance.name}: ${instance.cost_per_hour}/hr")
```

**Parameters:**
- `resource_type` - Type of resource to list
- `region` - Region to query

**Returns:** List of CloudResource objects

---

##### `get_pricing(service: str, instance_type: str, region: str) -> PricingData`

Get pricing information for a service/instance type.

```python
# AWS EC2 pricing
pricing = aws.get_pricing("ec2", "t3.micro", "us-east-1")
print(f"Hourly: ${pricing.price_per_hour:.4f}")
print(f"Monthly: ${pricing.price_per_month:.2f}")

# Azure VM pricing
pricing = azure.get_pricing("vm", "Standard_B1s", "eastus")

# GCP Compute pricing
pricing = gcp.get_pricing("compute", "f1-micro", "us-central1")
```

**Parameters:**
- `service` - Service name (ec2, vm, compute, database, etc.)
- `instance_type` - Instance type identifier
- `region` - Region for pricing

**Returns:** PricingData object

---

##### `get_cost_data(start_date: datetime, end_date: datetime) -> List[Dict]`

Get historical cost data.

```python
from datetime import datetime, timedelta

start = datetime.now() - timedelta(days=30)
end = datetime.now()

cost_data = aws.get_cost_data(start, end)
for entry in cost_data:
    print(f"{entry['date']}: ${entry['cost']:.2f}")
```

**Parameters:**
- `start_date` - Start of date range
- `end_date` - End of date range

**Returns:** List of cost data dictionaries

---

### Specific Provider Classes

#### `AWSProvider`

AWS-specific implementation.

```python
from openfinops.multicloud import AWSProvider

aws = AWSProvider()

# AWS-specific regions
regions = aws.list_regions()
# ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-west-1', ...]

# AWS instance types
pricing = aws.get_pricing("ec2", "t3.micro", "us-east-1")
```

**Supported Services:**
- `ec2` - EC2 compute instances
- `rds` - RDS databases
- `s3` - S3 storage
- `lambda` - Lambda functions
- `eks` - EKS clusters

---

#### `AzureProvider`

Azure-specific implementation.

```python
from openfinops.multicloud import AzureProvider

azure = AzureProvider()

# Azure regions
regions = azure.list_regions()
# ['eastus', 'westus', 'centralus', 'northeurope', 'westeurope', ...]

# Azure instance types
pricing = azure.get_pricing("vm", "Standard_B1s", "eastus")
```

**Supported Services:**
- `vm` - Virtual machines
- `sql` - SQL databases
- `storage` - Blob storage
- `functions` - Azure Functions
- `aks` - AKS clusters

---

#### `GCPProvider`

GCP-specific implementation.

```python
from openfinops.multicloud import GCPProvider

gcp = GCPProvider()

# GCP regions
regions = gcp.list_regions()
# ['us-central1', 'us-east1', 'us-west1', 'europe-west1', ...]

# GCP instance types
pricing = gcp.get_pricing("compute", "f1-micro", "us-central1")
```

**Supported Services:**
- `compute` - Compute Engine instances
- `sql` - Cloud SQL
- `storage` - Cloud Storage
- `functions` - Cloud Functions
- `gke` - GKE clusters

---

### Data Models

#### `CloudResource`

Represents a cloud resource.

```python
from openfinops.multicloud import CloudResource, ResourceType, CloudProvider

resource = CloudResource(
    resource_id="i-1234567890",
    name="web-server-1",
    resource_type=ResourceType.COMPUTE,
    provider=CloudProvider.AWS,
    region="us-east-1",
    cost_per_hour=0.096,
    tags={"environment": "production", "team": "platform"}
)

# Calculate costs
monthly = resource.get_monthly_cost()    # 730 hours
annual = resource.get_annual_cost()      # 8,760 hours

print(f"Monthly cost: ${monthly:.2f}")
print(f"Annual cost: ${annual:.2f}")
```

**Attributes:**
- `resource_id` - Unique resource identifier
- `name` - Resource name
- `resource_type` - Type of resource
- `provider` - Cloud provider
- `region` - Region location
- `cost_per_hour` - Hourly cost in USD
- `tags` - Resource tags

**Methods:**
- `get_monthly_cost() -> float` - Calculate monthly cost (730 hours)
- `get_annual_cost() -> float` - Calculate annual cost (8,760 hours)

---

#### `PricingData`

Pricing information for a service/instance.

```python
from openfinops.multicloud import PricingData, CloudProvider

pricing = PricingData(
    provider=CloudProvider.AWS,
    service="ec2",
    region="us-east-1",
    instance_type="t3.micro",
    price_per_hour=0.0104,
    currency="USD"
)

# Auto-calculated monthly price
print(f"Monthly: ${pricing.price_per_month:.2f}")  # price_per_hour * 730
```

**Attributes:**
- `provider` - Cloud provider
- `service` - Service name
- `region` - Region
- `instance_type` - Instance type
- `price_per_hour` - Hourly price
- `price_per_month` - Auto-calculated monthly price
- `currency` - Currency code

---

#### `ResourceType`

Resource type enumeration.

```python
class ResourceType(Enum):
    COMPUTE = "compute"        # EC2, VMs, Compute Engine
    DATABASE = "database"      # RDS, SQL, Cloud SQL
    STORAGE = "storage"        # S3, Blob, Cloud Storage
    NETWORK = "network"        # VPC, VNet, VPC
    CONTAINER = "container"    # ECS, ACI, GKE
    SERVERLESS = "serverless"  # Lambda, Functions, Cloud Functions
```

---

#### `CloudProvider`

Cloud provider enumeration.

```python
class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
```

---

## Cost Comparison API

### `CloudCostComparator`

Compare workload costs across multiple cloud providers.

#### Constructor

```python
from openfinops.multicloud import CloudCostComparator

comparator = CloudCostComparator()
```

#### Methods

##### `add_provider(provider: CloudProvider) -> None`

Add a cloud provider to the comparison.

```python
from openfinops.multicloud import CloudProvider

comparator.add_provider(CloudProvider.AWS)
comparator.add_provider(CloudProvider.AZURE)
comparator.add_provider(CloudProvider.GCP)
```

---

##### `compare_workload(workload: WorkloadSpec, regions: Optional[Dict] = None) -> List[CostEstimate]`

Compare workload costs across all added providers.

```python
from openfinops.multicloud import WorkloadSpec

workload = WorkloadSpec(
    name="Web Application",
    compute_instances=10,
    cpu_cores=2,
    memory_gb=4,
    storage_gb=500,
    network_gb_month=1000
)

# Compare across default regions
estimates = comparator.compare_workload(workload)

# Compare across specific regions
regions = {
    CloudProvider.AWS: "us-east-1",
    CloudProvider.AZURE: "eastus",
    CloudProvider.GCP: "us-central1"
}
estimates = comparator.compare_workload(workload, regions)

# Results sorted by cost (cheapest first)
for est in estimates:
    print(f"{est.provider.value} ({est.region}): ${est.monthly_cost:,.2f}/month")
```

**Parameters:**
- `workload` - Workload specification
- `regions` - Optional region mapping per provider

**Returns:** List of CostEstimate objects, sorted by cost

---

##### `get_cost_savings(estimates: List[CostEstimate]) -> Dict[str, Any]`

Calculate potential cost savings.

```python
estimates = comparator.compare_workload(workload)
savings = comparator.get_cost_savings(estimates)

print(f"Cheapest: {savings['cheapest_provider']}")
print(f"Most expensive: {savings['most_expensive_provider']}")
print(f"Monthly savings: ${savings['monthly_savings']:,.2f}")
print(f"Annual savings: ${savings['annual_savings']:,.2f}")
print(f"Percentage savings: {savings['percentage_savings']:.1f}%")
```

**Returns:** Dictionary with:
- `cheapest_provider` - Provider with lowest cost
- `cheapest_cost` - Lowest monthly cost
- `most_expensive_provider` - Provider with highest cost
- `most_expensive_cost` - Highest monthly cost
- `monthly_savings` - Monthly savings potential
- `annual_savings` - Annual savings potential
- `percentage_savings` - Savings as percentage

---

##### `compare_regions(provider: CloudProvider, workload: WorkloadSpec) -> List[Dict]`

Compare costs across regions for a single provider.

```python
regional_costs = comparator.compare_regions(CloudProvider.AWS, workload)

for region_data in regional_costs:
    print(f"{region_data['region']}: ${region_data['monthly_cost']:,.2f}")
```

**Returns:** List of dictionaries with region costs, sorted by cost

---

##### `get_comparison_report(workload: WorkloadSpec, regions: Optional[Dict] = None) -> Dict[str, Any]`

Generate comprehensive comparison report.

```python
report = comparator.get_comparison_report(workload)

print(f"Workload: {report['workload']}")
print(f"\nCost Estimates:")
for est in report['estimates']:
    print(f"  {est['provider']} ({est['region']}): ${est['monthly_cost']:,.2f}/month")
    print(f"    Breakdown: {est['breakdown']}")

print(f"\nSavings Analysis:")
savings = report['savings_analysis']
print(f"  Cheapest: {savings['cheapest_provider']}")
print(f"  Annual savings: ${savings['annual_savings']:,.2f}")

print(f"\nRecommendation:")
print(f"  {report['recommendation']}")
```

**Returns:** Comprehensive report dictionary

---

### `quick_compare()`

Quick comparison utility function.

```python
from openfinops.multicloud import quick_compare

report = quick_compare(
    workload_name="Production API",
    instances=20,
    cpu=4,
    memory=16,
    providers=[CloudProvider.AWS, CloudProvider.AZURE, CloudProvider.GCP]
)

print(report['recommendation'])
```

**Parameters:**
- `workload_name` - Workload name
- `instances` - Number of instances
- `cpu` - CPU cores per instance (default: 2)
- `memory` - Memory GB per instance (default: 4)
- `providers` - Providers to compare (default: all)

**Returns:** Comparison report dictionary

---

### Data Models

#### `WorkloadSpec`

Workload specification for cost estimation.

```python
from openfinops.multicloud import WorkloadSpec

workload = WorkloadSpec(
    name="Web Application",
    compute_instances=10,
    cpu_cores=4,
    memory_gb=16,
    storage_gb=1000,
    network_gb_month=2000,
    database_instances=2,
    requirements={"sla": "99.9%", "compliance": "SOC2"}
)
```

**Attributes:**
- `name` - Workload name
- `compute_instances` - Number of compute instances
- `cpu_cores` - CPU cores per instance
- `memory_gb` - Memory GB per instance
- `storage_gb` - Total storage in GB
- `network_gb_month` - Monthly network traffic in GB
- `database_instances` - Number of database instances
- `requirements` - Additional requirements dictionary

---

#### `CostEstimate`

Cost estimate for a workload on a provider.

```python
from openfinops.multicloud import CostEstimate

estimate = CostEstimate(
    provider=CloudProvider.AWS,
    workload_name="Web Application",
    monthly_cost=5000.0,
    breakdown={
        "compute": 3500.0,
        "storage": 800.0,
        "network": 500.0,
        "database": 200.0
    },
    instance_details={
        "compute": {
            "instance_type": "t3.xlarge",
            "count": 10,
            "hourly_cost": 0.1664
        }
    },
    region="us-east-1",
    confidence=0.9
)
```

**Attributes:**
- `provider` - Cloud provider
- `workload_name` - Workload name
- `monthly_cost` - Total monthly cost
- `breakdown` - Cost breakdown by service
- `instance_details` - Instance configuration details
- `region` - Region used for estimate
- `confidence` - Estimate confidence (0-1)

---

## Optimization API

### `MultiCloudOptimizer`

Optimize workload placement and costs across clouds.

#### Constructor

```python
from openfinops.multicloud import MultiCloudOptimizer, OptimizationStrategy

# Cost optimization (default)
optimizer = MultiCloudOptimizer()

# Performance optimization
optimizer = MultiCloudOptimizer(strategy=OptimizationStrategy.PERFORMANCE)

# Balanced optimization
optimizer = MultiCloudOptimizer(strategy=OptimizationStrategy.BALANCED)

# Reliability optimization
optimizer = MultiCloudOptimizer(strategy=OptimizationStrategy.RELIABILITY)
```

**Parameters:**
- `strategy` - Optimization strategy (default: COST)

---

#### Methods

##### `analyze_current_deployment(resources: List[CloudResource]) -> Dict[str, Any]`

Analyze current multi-cloud deployment.

```python
from openfinops.multicloud import CloudResource, ResourceType, CloudProvider

resources = [
    CloudResource(
        resource_id="i-123",
        name="web-1",
        resource_type=ResourceType.COMPUTE,
        provider=CloudProvider.AWS,
        region="us-east-1",
        cost_per_hour=0.096
    ),
    CloudResource(
        resource_id="vm-456",
        name="web-2",
        resource_type=ResourceType.COMPUTE,
        provider=CloudProvider.AZURE,
        region="eastus",
        cost_per_hour=0.120
    )
]

analysis = optimizer.analyze_current_deployment(resources)

print(f"Total resources: {analysis['total_resources']}")
print(f"Total monthly cost: ${analysis['total_monthly_cost']:,.2f}")
print(f"Providers: {analysis['providers']}")
print(f"\nProvider distribution:")
for provider, data in analysis['provider_distribution'].items():
    print(f"  {provider}: {data['percentage']:.1f}% (${data['cost']:,.2f}/month)")
```

**Returns:** Analysis dictionary with:
- `total_resources` - Total resource count
- `total_monthly_cost` - Total monthly cost
- `providers` - List of providers used
- `provider_distribution` - Cost distribution by provider
- `by_provider` - Detailed breakdown by provider

---

##### `get_optimization_recommendations(resources: List[CloudResource]) -> List[OptimizationRecommendation]`

Get optimization recommendations for current deployment.

```python
recommendations = optimizer.get_optimization_recommendations(resources)

for rec in recommendations:
    print(f"\n{rec.recommendation_type.upper()}")
    print(f"  Priority: {rec.priority}")
    print(f"  Savings: ${rec.estimated_savings:,.2f}/month")
    print(f"  Impact: {rec.impact}")
    print(f"  Current: {rec.current_state}")
    print(f"  Recommended: {rec.recommended_state}")
```

**Returns:** List of OptimizationRecommendation objects, sorted by savings

---

##### `optimize_workload_placement(workload: WorkloadSpec, constraints: Optional[Dict] = None) -> Dict[str, Any]`

Determine optimal provider and configuration for a workload.

```python
workload = WorkloadSpec(
    name="New Application",
    compute_instances=20,
    cpu_cores=4,
    memory_gb=16
)

# With constraints
constraints = {
    "regions": ["us-east-1", "eastus", "us-central1"],
    "compliance": "HIPAA"
}

result = optimizer.optimize_workload_placement(workload, constraints)

print(f"Strategy: {result['strategy']}")
print(f"Recommended provider: {result['recommended_provider']}")
print(f"Recommended region: {result['recommended_region']}")
print(f"Monthly cost: ${result['estimated_monthly_cost']:,.2f}")
print(f"Annual cost: ${result['estimated_annual_cost']:,.2f}")
print(f"\nCost breakdown:")
for service, cost in result['cost_breakdown'].items():
    print(f"  {service}: ${cost:,.2f}")

print(f"\nAlternatives:")
for alt in result['alternatives']:
    print(f"  {alt['provider']} ({alt['region']}): ${alt['monthly_cost']:,.2f}")
```

**Parameters:**
- `workload` - Workload specification
- `constraints` - Optional constraints (regions, compliance, etc.)

**Returns:** Optimization result dictionary

---

##### `get_migration_plan(current_resources: List[CloudResource], target_provider: CloudProvider, target_region: str) -> Dict[str, Any]`

Generate migration plan to target provider.

```python
plan = optimizer.get_migration_plan(
    current_resources=resources,
    target_provider=CloudProvider.GCP,
    target_region="us-central1"
)

print(f"Migration to: {plan['target_provider']} ({plan['target_region']})")
print(f"Estimated duration: {plan['estimated_duration_days']} days")
print(f"Estimated downtime: {plan['estimated_downtime_hours']} hours")
print(f"\nCost comparison:")
print(f"  Current: ${plan['current_monthly_cost']:,.2f}/month")
print(f"  Target: ${plan['target_monthly_cost']:,.2f}/month")
print(f"  Savings: ${plan['estimated_savings']:,.2f}/month")

print(f"\nMigration steps:")
for step in plan['migration_steps']:
    print(f"  {step['step']}. {step['phase']}: {step['action']}")
    print(f"     Duration: {step['duration_days']} days")
```

**Returns:** Migration plan dictionary with:
- `current_state` - Current deployment analysis
- `target_provider` - Target provider
- `target_region` - Target region
- `migration_steps` - Step-by-step migration plan
- `estimated_duration_days` - Total migration duration
- `estimated_downtime_hours` - Expected downtime
- `current_monthly_cost` - Current monthly cost
- `target_monthly_cost` - Target monthly cost
- `estimated_savings` - Monthly savings
- `roi_months` - ROI timeframe

---

### Data Models

#### `OptimizationStrategy`

Optimization strategy enumeration.

```python
class OptimizationStrategy(Enum):
    COST = "cost"                    # Minimize cost
    PERFORMANCE = "performance"      # Maximize performance
    BALANCED = "balanced"            # Balance cost and performance
    RELIABILITY = "reliability"      # Maximize reliability
```

---

#### `OptimizationRecommendation`

Optimization recommendation.

```python
from openfinops.multicloud import OptimizationRecommendation

recommendation = OptimizationRecommendation(
    recommendation_id="opt-001",
    recommendation_type="consolidate_provider",
    current_state={
        "providers": ["aws", "azure"],
        "total_instances": 20,
        "monthly_cost": 5000.0
    },
    recommended_state={
        "provider": "aws",
        "total_instances": 20,
        "monthly_cost": 4200.0
    },
    estimated_savings=800.0,
    impact="Consolidate 20 instances to AWS",
    confidence=0.9,
    priority="high"
)
```

**Attributes:**
- `recommendation_id` - Unique ID
- `recommendation_type` - Type of recommendation
- `current_state` - Current configuration
- `recommended_state` - Recommended configuration
- `estimated_savings` - Monthly savings
- `impact` - Impact description
- `confidence` - Confidence score (0-1)
- `priority` - Priority level (high, medium, low)

---

## Complete Workflow Example

```python
from openfinops.multicloud import (
    CloudProvider,
    CloudCostComparator,
    MultiCloudOptimizer,
    OptimizationStrategy,
    WorkloadSpec,
    CloudResource,
    ResourceType,
    quick_compare
)

# 1. Quick comparison for new workload
print("=== Quick Comparison ===")
report = quick_compare(
    workload_name="Production API",
    instances=20,
    cpu=4,
    memory=16
)

print(f"Recommendation: {report['recommendation']}")
print(f"\nCosts:")
for est in report['estimates']:
    print(f"  {est['provider']}: ${est['monthly_cost']:,.2f}/month")

# 2. Detailed workload comparison
print("\n=== Detailed Comparison ===")
comparator = CloudCostComparator()
comparator.add_provider(CloudProvider.AWS)
comparator.add_provider(CloudProvider.AZURE)
comparator.add_provider(CloudProvider.GCP)

workload = WorkloadSpec(
    name="E-commerce Platform",
    compute_instances=50,
    cpu_cores=4,
    memory_gb=16,
    storage_gb=5000,
    network_gb_month=3000,
    database_instances=5
)

estimates = comparator.compare_workload(workload)
savings = comparator.get_cost_savings(estimates)

print(f"Potential savings: ${savings['annual_savings']:,.2f}/year")
print(f"Percentage: {savings['percentage_savings']:.1f}%")

# 3. Analyze current deployment
print("\n=== Current Deployment Analysis ===")
optimizer = MultiCloudOptimizer(strategy=OptimizationStrategy.COST)

current_resources = [
    CloudResource(
        resource_id=f"aws-{i}",
        name=f"web-{i}",
        resource_type=ResourceType.COMPUTE,
        provider=CloudProvider.AWS,
        region="us-east-1",
        cost_per_hour=0.1664
    )
    for i in range(30)
] + [
    CloudResource(
        resource_id=f"azure-{i}",
        name=f"api-{i}",
        resource_type=ResourceType.COMPUTE,
        provider=CloudProvider.AZURE,
        region="eastus",
        cost_per_hour=0.192
    )
    for i in range(20)
]

analysis = optimizer.analyze_current_deployment(current_resources)
print(f"Total monthly cost: ${analysis['total_monthly_cost']:,.2f}")
print(f"Providers: {analysis['providers']}")

# 4. Get optimization recommendations
print("\n=== Optimization Recommendations ===")
recommendations = optimizer.get_optimization_recommendations(current_resources)

for rec in recommendations[:3]:  # Top 3
    print(f"\n{rec.recommendation_type}:")
    print(f"  Savings: ${rec.estimated_savings:,.2f}/month")
    print(f"  Priority: {rec.priority}")
    print(f"  Impact: {rec.impact}")

# 5. Plan migration
print("\n=== Migration Plan ===")
plan = optimizer.get_migration_plan(
    current_resources=current_resources,
    target_provider=CloudProvider.AWS,
    target_region="us-east-1"
)

print(f"Duration: {plan['estimated_duration_days']} days")
print(f"Downtime: {plan['estimated_downtime_hours']} hours")
print(f"Monthly savings: ${plan['estimated_savings']:,.2f}")
print(f"ROI: {plan['roi_months']} months")

print(f"\nMigration steps: {len(plan['migration_steps'])}")
for step in plan['migration_steps'][:5]:  # First 5 steps
    print(f"  {step['step']}. {step['action']}")
```

---

## See Also

- [FinOps-as-Code API](iac-api.md)
- [SaaS Management API](saas-api.md)
- [Observability API](observability-api.md)
