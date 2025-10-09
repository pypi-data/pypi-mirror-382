"""
Cloud Provider Abstraction
===========================

Unified interface for multi-cloud operations (AWS, Azure, GCP).
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Supported cloud providers."""

    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ALIBABA = "alibaba"
    ORACLE = "oracle"


class ResourceType(Enum):
    """Cloud resource types."""

    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORKING = "networking"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    AI_ML = "ai_ml"


@dataclass
class CloudResource:
    """
    Unified cloud resource representation.

    Attributes:
        resource_id: Resource identifier
        name: Resource name
        resource_type: Type of resource
        provider: Cloud provider
        region: Cloud region
        cost_per_hour: Hourly cost in USD
        tags: Resource tags
        metadata: Additional metadata
    """

    resource_id: str
    name: str
    resource_type: ResourceType
    provider: CloudProvider
    region: str
    cost_per_hour: float = 0.0
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_monthly_cost(self) -> float:
        """Calculate monthly cost (730 hours/month)."""
        return self.cost_per_hour * 730

    def get_annual_cost(self) -> float:
        """Calculate annual cost."""
        return self.get_monthly_cost() * 12


@dataclass
class PricingData:
    """
    Cloud service pricing data.

    Attributes:
        provider: Cloud provider
        service: Service name
        region: Region
        instance_type: Instance/SKU type
        price_per_hour: Hourly price in USD
        price_per_month: Monthly price in USD
        pricing_model: Pricing model (on-demand, reserved, spot)
        currency: Currency code
        last_updated: Last update timestamp
    """

    provider: CloudProvider
    service: str
    region: str
    instance_type: str
    price_per_hour: float
    price_per_month: Optional[float] = None
    pricing_model: str = "on-demand"
    currency: str = "USD"
    last_updated: Optional[float] = None

    def __post_init__(self):
        """Initialize pricing data."""
        if self.price_per_month is None:
            self.price_per_month = self.price_per_hour * 730
        if self.last_updated is None:
            self.last_updated = datetime.now().timestamp()


class CloudProviderInterface(ABC):
    """
    Abstract interface for cloud providers.
    """

    def __init__(self, provider: CloudProvider):
        """
        Initialize cloud provider interface.

        Args:
            provider: Cloud provider type
        """
        self.provider = provider

    @abstractmethod
    def list_regions(self) -> List[str]:
        """
        List available regions.

        Returns:
            List of region identifiers
        """
        pass

    @abstractmethod
    def list_resources(
        self, resource_type: Optional[ResourceType] = None, region: Optional[str] = None
    ) -> List[CloudResource]:
        """
        List cloud resources.

        Args:
            resource_type: Filter by resource type
            region: Filter by region

        Returns:
            List of cloud resources
        """
        pass

    @abstractmethod
    def get_pricing(
        self, service: str, instance_type: str, region: str
    ) -> Optional[PricingData]:
        """
        Get pricing for a service.

        Args:
            service: Service name
            instance_type: Instance/SKU type
            region: Region

        Returns:
            Pricing data or None
        """
        pass

    @abstractmethod
    def get_cost_data(
        self, start_date: datetime, end_date: datetime, granularity: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Get historical cost data.

        Args:
            start_date: Start date
            end_date: End date
            granularity: Data granularity (hourly, daily, monthly)

        Returns:
            Cost data records
        """
        pass

    def get_provider_name(self) -> str:
        """Get provider name."""
        return self.provider.value


class AWSProvider(CloudProviderInterface):
    """AWS cloud provider implementation."""

    def __init__(self):
        """Initialize AWS provider."""
        super().__init__(CloudProvider.AWS)
        self._regions = [
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1"
        ]

    def list_regions(self) -> List[str]:
        """List AWS regions."""
        return self._regions.copy()

    def list_resources(
        self, resource_type: Optional[ResourceType] = None, region: Optional[str] = None
    ) -> List[CloudResource]:
        """List AWS resources."""
        # In production, use boto3 to query actual resources
        # For now, return sample data
        resources = []

        if not resource_type or resource_type == ResourceType.COMPUTE:
            resources.append(CloudResource(
                resource_id="i-1234567890abcdef0",
                name="web-server-1",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AWS,
                region=region or "us-east-1",
                cost_per_hour=0.096,  # t3.large
                tags={"env": "production", "app": "web"},
            ))

        return resources

    def get_pricing(
        self, service: str, instance_type: str, region: str
    ) -> Optional[PricingData]:
        """Get AWS pricing."""
        # Simplified pricing - in production, use AWS Price List API
        pricing_map = {
            ("ec2", "t3.micro"): 0.0104,
            ("ec2", "t3.small"): 0.0208,
            ("ec2", "t3.medium"): 0.0416,
            ("ec2", "t3.large"): 0.0832,
            ("rds", "db.t3.micro"): 0.017,
            ("rds", "db.t3.small"): 0.034,
        }

        price = pricing_map.get((service, instance_type))
        if price is None:
            return None

        return PricingData(
            provider=CloudProvider.AWS,
            service=service,
            region=region,
            instance_type=instance_type,
            price_per_hour=price,
        )

    def get_cost_data(
        self, start_date: datetime, end_date: datetime, granularity: str = "daily"
    ) -> List[Dict[str, Any]]:
        """Get AWS cost data."""
        # In production, use AWS Cost Explorer API
        return [{
            "date": start_date.isoformat(),
            "service": "EC2",
            "cost": 150.00,
            "provider": "aws",
        }]


class AzureProvider(CloudProviderInterface):
    """Azure cloud provider implementation."""

    def __init__(self):
        """Initialize Azure provider."""
        super().__init__(CloudProvider.AZURE)
        self._regions = [
            "eastus", "eastus2", "westus", "westus2",
            "northeurope", "westeurope", "southeastasia", "japaneast"
        ]

    def list_regions(self) -> List[str]:
        """List Azure regions."""
        return self._regions.copy()

    def list_resources(
        self, resource_type: Optional[ResourceType] = None, region: Optional[str] = None
    ) -> List[CloudResource]:
        """List Azure resources."""
        resources = []

        if not resource_type or resource_type == ResourceType.COMPUTE:
            resources.append(CloudResource(
                resource_id="/subscriptions/xxx/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1",
                name="web-server-1",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.AZURE,
                region=region or "eastus",
                cost_per_hour=0.096,  # Standard_D2s_v3
                tags={"env": "production", "app": "web"},
            ))

        return resources

    def get_pricing(
        self, service: str, instance_type: str, region: str
    ) -> Optional[PricingData]:
        """Get Azure pricing."""
        pricing_map = {
            ("vm", "Standard_B1s"): 0.0104,
            ("vm", "Standard_B2s"): 0.0416,
            ("vm", "Standard_D2s_v3"): 0.096,
            ("sql", "Basic"): 0.007,
            ("sql", "Standard_S0"): 0.020,
        }

        price = pricing_map.get((service, instance_type))
        if price is None:
            return None

        return PricingData(
            provider=CloudProvider.AZURE,
            service=service,
            region=region,
            instance_type=instance_type,
            price_per_hour=price,
        )

    def get_cost_data(
        self, start_date: datetime, end_date: datetime, granularity: str = "daily"
    ) -> List[Dict[str, Any]]:
        """Get Azure cost data."""
        return [{
            "date": start_date.isoformat(),
            "service": "Virtual Machines",
            "cost": 120.00,
            "provider": "azure",
        }]


class GCPProvider(CloudProviderInterface):
    """GCP cloud provider implementation."""

    def __init__(self):
        """Initialize GCP provider."""
        super().__init__(CloudProvider.GCP)
        self._regions = [
            "us-central1", "us-east1", "us-west1",
            "europe-west1", "europe-west2", "asia-east1", "asia-southeast1"
        ]

    def list_regions(self) -> List[str]:
        """List GCP regions."""
        return self._regions.copy()

    def list_resources(
        self, resource_type: Optional[ResourceType] = None, region: Optional[str] = None
    ) -> List[CloudResource]:
        """List GCP resources."""
        resources = []

        if not resource_type or resource_type == ResourceType.COMPUTE:
            resources.append(CloudResource(
                resource_id="projects/my-project/zones/us-central1-a/instances/web-server-1",
                name="web-server-1",
                resource_type=ResourceType.COMPUTE,
                provider=CloudProvider.GCP,
                region=region or "us-central1",
                cost_per_hour=0.095,  # n1-standard-2
                tags={"env": "production", "app": "web"},
            ))

        return resources

    def get_pricing(
        self, service: str, instance_type: str, region: str
    ) -> Optional[PricingData]:
        """Get GCP pricing."""
        pricing_map = {
            ("compute", "f1-micro"): 0.0076,
            ("compute", "g1-small"): 0.0257,
            ("compute", "n1-standard-1"): 0.0475,
            ("compute", "n1-standard-2"): 0.0950,
            ("sql", "db-f1-micro"): 0.0150,
            ("sql", "db-g1-small"): 0.0500,
        }

        price = pricing_map.get((service, instance_type))
        if price is None:
            return None

        return PricingData(
            provider=CloudProvider.GCP,
            service=service,
            region=region,
            instance_type=instance_type,
            price_per_hour=price,
        )

    def get_cost_data(
        self, start_date: datetime, end_date: datetime, granularity: str = "daily"
    ) -> List[Dict[str, Any]]:
        """Get GCP cost data."""
        return [{
            "date": start_date.isoformat(),
            "service": "Compute Engine",
            "cost": 100.00,
            "provider": "gcp",
        }]


def create_provider(provider: CloudProvider) -> CloudProviderInterface:
    """
    Create cloud provider interface.

    Args:
        provider: Cloud provider type

    Returns:
        Cloud provider interface

    Raises:
        ValueError: If provider not supported
    """
    providers = {
        CloudProvider.AWS: AWSProvider,
        CloudProvider.AZURE: AzureProvider,
        CloudProvider.GCP: GCPProvider,
    }

    if provider not in providers:
        raise ValueError(f"Unsupported provider: {provider}")

    return providers[provider]()
