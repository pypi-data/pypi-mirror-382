"""
Cost Configuration Management System
===================================

Advanced configuration management for unit costs, pricing tiers, and cost calculation rules.
Supports multiple cloud providers, regions, and custom pricing configurations.

Features:
- Multi-cloud pricing configuration
- Regional cost variations
- Instance-type specific pricing
- Volume-based discounting
- Custom cost calculation rules
- Configuration versioning and history
- Cost estimation and forecasting
"""

# Copyright (c) 2025 Infinidatum
# Author: Duraimurugan Rajamanickam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import threading
from pathlib import Path

from .model_cost_attribution import ResourceType, UnitCostConfig


class CloudProvider(Enum):
    """Supported cloud providers"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREMISE = "on_premise"
    CUSTOM = "custom"


class PricingTier(Enum):
    """Pricing tiers for volume discounting"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class VolumeDiscount:
    """Volume-based discount configuration"""
    min_usage: float                     # Minimum usage to qualify for discount
    max_usage: Optional[float] = None    # Maximum usage for this tier (None = unlimited)
    discount_percentage: float = 0.0     # Discount percentage (0-100)
    discount_type: str = "percentage"    # "percentage" or "fixed_amount"
    discount_amount: Optional[float] = None  # Fixed discount amount if type is "fixed_amount"


@dataclass
class RegionalPricing:
    """Regional pricing variations"""
    region: str
    base_multiplier: float = 1.0         # Multiplier for base pricing
    resource_multipliers: Dict[ResourceType, float] = field(default_factory=dict)
    availability_zones: List[str] = field(default_factory=list)
    currency: str = "USD"
    tax_rate: float = 0.0               # Local tax rate


@dataclass
class InstanceTypeConfig:
    """Instance-specific configuration and pricing"""
    instance_type: str
    cloud_provider: CloudProvider
    vcpus: int
    memory_gb: float
    gpu_count: int = 0
    gpu_type: Optional[str] = None
    storage_gb: float = 0.0
    network_performance: str = "standard"
    hourly_cost: float = 0.0
    specialized_costs: Dict[ResourceType, float] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class CostCalculationRule:
    """Custom cost calculation rules"""
    rule_id: str
    name: str
    resource_type: ResourceType
    calculation_formula: str             # Python expression for cost calculation
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)  # Conditions for rule application
    priority: int = 0                   # Higher priority rules are applied first
    active: bool = True


@dataclass
class CostConfiguration:
    """Complete cost configuration"""
    config_id: str
    name: str
    version: str
    description: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    # Core pricing configurations
    unit_cost_configs: Dict[str, UnitCostConfig] = field(default_factory=dict)
    regional_pricing: Dict[str, RegionalPricing] = field(default_factory=dict)
    instance_configs: Dict[str, InstanceTypeConfig] = field(default_factory=dict)
    volume_discounts: Dict[ResourceType, List[VolumeDiscount]] = field(default_factory=dict)
    calculation_rules: Dict[str, CostCalculationRule] = field(default_factory=dict)

    # Global settings
    default_currency: str = "USD"
    default_region: str = "us-west-2"
    default_cloud_provider: CloudProvider = CloudProvider.AWS
    tax_inclusive: bool = False

    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)
    is_active: bool = True


class CostConfigurationManager:
    """Advanced cost configuration management system"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "cost_configurations.json"
        self.configurations: Dict[str, CostConfiguration] = {}
        self.active_config_id: Optional[str] = None
        self.config_lock = threading.Lock()

        # Load configurations if file exists
        self._load_configurations()

        # Initialize with default configuration if none exists
        if not self.configurations:
            self._create_default_configuration()

    def _load_configurations(self):
        """Load configurations from file"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)

                # Deserialize configurations
                for config_id, config_data in data.get('configurations', {}).items():
                    config = self._deserialize_configuration(config_data)
                    self.configurations[config_id] = config

                self.active_config_id = data.get('active_config_id')

        except Exception as e:
            print(f"Error loading cost configurations: {e}")

    def _save_configurations(self):
        """Save configurations to file"""
        try:
            data = {
                'active_config_id': self.active_config_id,
                'configurations': {
                    config_id: self._serialize_configuration(config)
                    for config_id, config in self.configurations.items()
                },
                'last_updated': time.time()
            }

            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error saving cost configurations: {e}")

    def _serialize_configuration(self, config: CostConfiguration) -> Dict[str, Any]:
        """Serialize configuration to JSON-compatible format"""
        data = asdict(config)

        # Convert enums to strings
        data['default_cloud_provider'] = config.default_cloud_provider.value

        # Handle nested enums and complex types
        serialized_unit_costs = {}
        for key, unit_config in config.unit_cost_configs.items():
            unit_data = asdict(unit_config)
            unit_data['resource_type'] = unit_config.resource_type.value
            serialized_unit_costs[key] = unit_data
        data['unit_cost_configs'] = serialized_unit_costs

        # Handle regional pricing
        serialized_regional = {}
        for region, pricing in config.regional_pricing.items():
            pricing_data = asdict(pricing)
            # Convert ResourceType keys to strings
            resource_mult = {}
            for resource_type, mult in pricing.resource_multipliers.items():
                resource_mult[resource_type.value] = mult
            pricing_data['resource_multipliers'] = resource_mult
            serialized_regional[region] = pricing_data
        data['regional_pricing'] = serialized_regional

        # Handle instance configs
        serialized_instances = {}
        for key, instance_config in config.instance_configs.items():
            instance_data = asdict(instance_config)
            instance_data['cloud_provider'] = instance_config.cloud_provider.value
            # Handle specialized_costs ResourceType keys
            specialized = {}
            for resource_type, cost in instance_config.specialized_costs.items():
                specialized[resource_type.value] = cost
            instance_data['specialized_costs'] = specialized
            serialized_instances[key] = instance_data
        data['instance_configs'] = serialized_instances

        # Handle volume discounts
        serialized_discounts = {}
        for resource_type, discounts in config.volume_discounts.items():
            serialized_discounts[resource_type.value] = [asdict(d) for d in discounts]
        data['volume_discounts'] = serialized_discounts

        # Handle calculation rules
        serialized_rules = {}
        for rule_id, rule in config.calculation_rules.items():
            rule_data = asdict(rule)
            rule_data['resource_type'] = rule.resource_type.value
            serialized_rules[rule_id] = rule_data
        data['calculation_rules'] = serialized_rules

        return data

    def _deserialize_configuration(self, data: Dict[str, Any]) -> CostConfiguration:
        """Deserialize configuration from JSON data"""
        # Convert enum strings back to enums
        data['default_cloud_provider'] = CloudProvider(data.get('default_cloud_provider', 'aws'))

        # Handle unit cost configs
        unit_configs = {}
        for key, unit_data in data.get('unit_cost_configs', {}).items():
            unit_data['resource_type'] = ResourceType(unit_data['resource_type'])
            unit_configs[key] = UnitCostConfig(**unit_data)
        data['unit_cost_configs'] = unit_configs

        # Handle regional pricing
        regional_pricing = {}
        for region, pricing_data in data.get('regional_pricing', {}).items():
            resource_mult = {}
            for resource_str, mult in pricing_data.get('resource_multipliers', {}).items():
                resource_mult[ResourceType(resource_str)] = mult
            pricing_data['resource_multipliers'] = resource_mult
            regional_pricing[region] = RegionalPricing(**pricing_data)
        data['regional_pricing'] = regional_pricing

        # Handle instance configs
        instance_configs = {}
        for key, instance_data in data.get('instance_configs', {}).items():
            instance_data['cloud_provider'] = CloudProvider(instance_data['cloud_provider'])
            specialized = {}
            for resource_str, cost in instance_data.get('specialized_costs', {}).items():
                specialized[ResourceType(resource_str)] = cost
            instance_data['specialized_costs'] = specialized
            instance_configs[key] = InstanceTypeConfig(**instance_data)
        data['instance_configs'] = instance_configs

        # Handle volume discounts
        volume_discounts = {}
        for resource_str, discount_list in data.get('volume_discounts', {}).items():
            resource_type = ResourceType(resource_str)
            discounts = [VolumeDiscount(**d) for d in discount_list]
            volume_discounts[resource_type] = discounts
        data['volume_discounts'] = volume_discounts

        # Handle calculation rules
        calculation_rules = {}
        for rule_id, rule_data in data.get('calculation_rules', {}).items():
            rule_data['resource_type'] = ResourceType(rule_data['resource_type'])
            calculation_rules[rule_id] = CostCalculationRule(**rule_data)
        data['calculation_rules'] = calculation_rules

        return CostConfiguration(**data)

    def _create_default_configuration(self):
        """Create default cost configuration"""
        config_id = str(uuid.uuid4())
        config = CostConfiguration(
            config_id=config_id,
            name="Default Configuration",
            version="1.0.0",
            description="Default cost configuration with standard cloud provider pricing"
        )

        # Add default unit cost configurations
        self._add_default_unit_costs(config)
        self._add_default_regional_pricing(config)
        self._add_default_instance_configs(config)
        self._add_default_volume_discounts(config)

        self.configurations[config_id] = config
        self.active_config_id = config_id
        self._save_configurations()

    def _add_default_unit_costs(self, config: CostConfiguration):
        """Add default unit cost configurations"""
        defaults = [
            # AWS GPU instances
            UnitCostConfig(ResourceType.COMPUTE_GPU, 3.06, region="us-west-2", cloud_provider="aws",
                          instance_type="p3.2xlarge", description="Tesla V100 GPU"),
            UnitCostConfig(ResourceType.COMPUTE_GPU, 1.25, region="us-west-2", cloud_provider="aws",
                          instance_type="g4dn.xlarge", description="T4 GPU"),

            # GCP GPU instances
            UnitCostConfig(ResourceType.COMPUTE_GPU, 2.48, region="us-west1", cloud_provider="gcp",
                          instance_type="n1-standard-4-k80", description="K80 GPU"),

            # Azure GPU instances
            UnitCostConfig(ResourceType.COMPUTE_GPU, 3.20, region="eastus", cloud_provider="azure",
                          instance_type="Standard_NC6", description="K80 GPU"),

            # CPU instances
            UnitCostConfig(ResourceType.COMPUTE_CPU, 0.0464, region="us-west-2", cloud_provider="aws",
                          instance_type="c5.large", description="2 vCPU, 4GB RAM"),

            # Memory pricing
            UnitCostConfig(ResourceType.MEMORY, 0.0116, region="us-west-2", cloud_provider="aws",
                          description="Memory per GB-hour"),

            # Storage
            UnitCostConfig(ResourceType.STORAGE_SSD, 0.10, region="us-west-2", cloud_provider="aws",
                          description="EBS SSD storage per GB-month"),
            UnitCostConfig(ResourceType.STORAGE_OBJECT, 0.023, region="us-west-2", cloud_provider="aws",
                          description="S3 Standard storage per GB-month"),

            # Network
            UnitCostConfig(ResourceType.NETWORK_EGRESS, 0.09, region="us-west-2", cloud_provider="aws",
                          description="Data egress per GB"),

            # Inference
            UnitCostConfig(ResourceType.INFERENCE_REQUEST, 0.0001, region="us-west-2", cloud_provider="aws",
                          description="Per inference request")
        ]

        for unit_config in defaults:
            key = f"{unit_config.resource_type.value}_{unit_config.region}_{unit_config.cloud_provider}"
            if unit_config.instance_type:
                key += f"_{unit_config.instance_type}"
            config.unit_cost_configs[key] = unit_config

    def _add_default_regional_pricing(self, config: CostConfiguration):
        """Add default regional pricing variations"""
        regions = [
            RegionalPricing("us-west-2", 1.0, currency="USD"),
            RegionalPricing("us-east-1", 0.95, currency="USD"),  # Slightly cheaper
            RegionalPricing("eu-west-1", 1.1, currency="USD"),   # European pricing
            RegionalPricing("ap-northeast-1", 1.15, currency="USD"),  # Asia-Pacific pricing
        ]

        for region_config in regions:
            config.regional_pricing[region_config.region] = region_config

    def _add_default_instance_configs(self, config: CostConfiguration):
        """Add default instance type configurations"""
        instances = [
            InstanceTypeConfig("p3.2xlarge", CloudProvider.AWS, 8, 61, 1, "V100", 0, "Up to 10 Gbps", 3.06),
            InstanceTypeConfig("p3.8xlarge", CloudProvider.AWS, 32, 244, 4, "V100", 0, "10 Gbps", 12.24),
            InstanceTypeConfig("g4dn.xlarge", CloudProvider.AWS, 4, 16, 1, "T4", 125, "Up to 25 Gbps", 1.25),
            InstanceTypeConfig("c5.large", CloudProvider.AWS, 2, 4, 0, None, 0, "Up to 10 Gbps", 0.085),
        ]

        for instance in instances:
            key = f"{instance.cloud_provider.value}_{instance.instance_type}"
            config.instance_configs[key] = instance

    def _add_default_volume_discounts(self, config: CostConfiguration):
        """Add default volume discount configurations"""
        # GPU compute discounts
        gpu_discounts = [
            VolumeDiscount(0, 100, 0.0),      # 0-100 hours: no discount
            VolumeDiscount(100, 500, 5.0),    # 100-500 hours: 5% discount
            VolumeDiscount(500, 1000, 10.0),  # 500-1000 hours: 10% discount
            VolumeDiscount(1000, None, 15.0), # 1000+ hours: 15% discount
        ]
        config.volume_discounts[ResourceType.COMPUTE_GPU] = gpu_discounts

        # Storage discounts
        storage_discounts = [
            VolumeDiscount(0, 1000, 0.0),     # 0-1TB: no discount
            VolumeDiscount(1000, 5000, 3.0),  # 1-5TB: 3% discount
            VolumeDiscount(5000, None, 8.0),  # 5TB+: 8% discount
        ]
        config.volume_discounts[ResourceType.STORAGE_OBJECT] = storage_discounts

    def create_configuration(self, name: str, description: str,
                           base_config_id: Optional[str] = None) -> str:
        """Create a new cost configuration"""
        config_id = str(uuid.uuid4())

        if base_config_id and base_config_id in self.configurations:
            # Clone existing configuration
            base_config = self.configurations[base_config_id]
            config = CostConfiguration(
                config_id=config_id,
                name=name,
                version="1.0.0",
                description=description,
                unit_cost_configs=base_config.unit_cost_configs.copy(),
                regional_pricing=base_config.regional_pricing.copy(),
                instance_configs=base_config.instance_configs.copy(),
                volume_discounts=base_config.volume_discounts.copy(),
                calculation_rules=base_config.calculation_rules.copy(),
                default_currency=base_config.default_currency,
                default_region=base_config.default_region,
                default_cloud_provider=base_config.default_cloud_provider
            )
        else:
            # Create new configuration
            config = CostConfiguration(
                config_id=config_id,
                name=name,
                version="1.0.0",
                description=description
            )

        with self.config_lock:
            self.configurations[config_id] = config
            self._save_configurations()

        return config_id

    def get_configuration(self, config_id: str) -> Optional[CostConfiguration]:
        """Get a configuration by ID"""
        return self.configurations.get(config_id)

    def get_active_configuration(self) -> Optional[CostConfiguration]:
        """Get the currently active configuration"""
        if self.active_config_id:
            return self.configurations.get(self.active_config_id)
        return None

    def set_active_configuration(self, config_id: str) -> bool:
        """Set the active configuration"""
        if config_id in self.configurations:
            with self.config_lock:
                self.active_config_id = config_id
                self._save_configurations()
            return True
        return False

    def update_unit_cost(self, config_id: str, resource_type: ResourceType,
                        region: str, cloud_provider: str, unit_price: float,
                        instance_type: Optional[str] = None) -> bool:
        """Update unit cost in a configuration"""
        config = self.configurations.get(config_id)
        if not config:
            return False

        key = f"{resource_type.value}_{region}_{cloud_provider}"
        if instance_type:
            key += f"_{instance_type}"

        # Update existing or create new
        if key in config.unit_cost_configs:
            config.unit_cost_configs[key].unit_price = unit_price
            config.unit_cost_configs[key].effective_date = time.time()
        else:
            config.unit_cost_configs[key] = UnitCostConfig(
                resource_type=resource_type,
                unit_price=unit_price,
                region=region,
                cloud_provider=cloud_provider,
                instance_type=instance_type
            )

        config.updated_at = time.time()

        with self.config_lock:
            self._save_configurations()

        return True

    def add_volume_discount(self, config_id: str, resource_type: ResourceType,
                          discount: VolumeDiscount) -> bool:
        """Add volume discount to a configuration"""
        config = self.configurations.get(config_id)
        if not config:
            return False

        if resource_type not in config.volume_discounts:
            config.volume_discounts[resource_type] = []

        config.volume_discounts[resource_type].append(discount)

        # Sort by min_usage for proper application
        config.volume_discounts[resource_type].sort(key=lambda x: x.min_usage)

        config.updated_at = time.time()

        with self.config_lock:
            self._save_configurations()

        return True

    def calculate_cost_with_discounts(self, config_id: str, resource_type: ResourceType,
                                   usage_amount: float, base_cost: float) -> float:
        """Calculate cost with volume discounts applied"""
        config = self.configurations.get(config_id)
        if not config or resource_type not in config.volume_discounts:
            return base_cost

        # Find applicable discount
        applicable_discount = None
        for discount in config.volume_discounts[resource_type]:
            if usage_amount >= discount.min_usage:
                if discount.max_usage is None or usage_amount <= discount.max_usage:
                    applicable_discount = discount
                    break

        if not applicable_discount:
            return base_cost

        # Apply discount
        if applicable_discount.discount_type == "percentage":
            discount_amount = base_cost * (applicable_discount.discount_percentage / 100)
        else:
            discount_amount = applicable_discount.discount_amount or 0

        return max(0, base_cost - discount_amount)

    def export_configuration(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Export configuration to JSON format"""
        config = self.configurations.get(config_id)
        if not config:
            return None

        return self._serialize_configuration(config)

    def import_configuration(self, config_data: Dict[str, Any]) -> str:
        """Import configuration from JSON data"""
        # Generate new ID to avoid conflicts
        config_data['config_id'] = str(uuid.uuid4())
        config_data['created_at'] = time.time()
        config_data['updated_at'] = time.time()

        config = self._deserialize_configuration(config_data)

        with self.config_lock:
            self.configurations[config.config_id] = config
            self._save_configurations()

        return config.config_id

    def list_configurations(self) -> List[Dict[str, Any]]:
        """List all configurations with metadata"""
        return [
            {
                "config_id": config.config_id,
                "name": config.name,
                "version": config.version,
                "description": config.description,
                "created_at": config.created_at,
                "updated_at": config.updated_at,
                "is_active": config.config_id == self.active_config_id,
                "unit_cost_count": len(config.unit_cost_configs),
                "region_count": len(config.regional_pricing),
                "instance_count": len(config.instance_configs)
            }
            for config in self.configurations.values()
        ]


# Global cost configuration manager instance
_cost_config_manager = None

def get_cost_configuration_manager() -> CostConfigurationManager:
    """Get global cost configuration manager instance"""
    global _cost_config_manager
    if _cost_config_manager is None:
        _cost_config_manager = CostConfigurationManager()
    return _cost_config_manager