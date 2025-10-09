# OpenFinOps Plugin Architecture
## Building Extensible FinOps Solutions

**Version**: 1.0 (Draft)
**Status**: 🚧 Implementation in Progress (Q1 2025)

---

## 📖 Overview

OpenFinOps is designed to be deeply extensible through a powerful plugin architecture. This enables:

- **Custom Telemetry Collectors**: Integrate any cloud provider or data source
- **Custom Cost Attribution**: Implement organization-specific attribution logic
- **Custom Recommendations**: Build AI/ML models tailored to your infrastructure
- **Custom Dashboards**: Create role-specific or use-case-specific visualizations
- **Custom Integrations**: Connect to any external tool or workflow system

---

## 🏗️ Architecture Design

### Plugin Types

```python
# src/openfinops/plugins/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class PluginType(Enum):
    """Types of plugins supported by OpenFinOps"""
    TELEMETRY = "telemetry"           # Custom data collectors
    ATTRIBUTION = "attribution"        # Custom cost attribution
    RECOMMENDATION = "recommendation"  # Custom optimization rules
    DASHBOARD = "dashboard"           # Custom dashboard widgets
    EXPORT = "export"                 # Custom export formats
    INTEGRATION = "integration"       # External tool integrations
    NOTIFICATION = "notification"     # Custom notification channels
    POLICY = "policy"                 # Custom policy rules


@dataclass
class PluginMetadata:
    """Plugin metadata"""
    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    dependencies: List[str] = None
    config_schema: Dict[str, Any] = None
    homepage: str = None
    license: str = "Apache-2.0"


class PluginBase(ABC):
    """Base class for all OpenFinOps plugins"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._initialized = False

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the plugin"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Cleanup when plugin is unloaded"""
        pass

    def validate_config(self) -> bool:
        """Validate plugin configuration"""
        return True
```

### Plugin Registry

```python
# src/openfinops/plugins/registry.py

from typing import Dict, List, Type, Optional
import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for all plugins"""

    def __init__(self):
        self._plugins: Dict[str, PluginBase] = {}
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}

    def register(self, plugin_class: Type[PluginBase]) -> None:
        """Register a plugin class"""
        plugin = plugin_class()
        metadata = plugin.metadata

        if metadata.name in self._plugin_classes:
            logger.warning(f"Plugin {metadata.name} already registered. Overwriting.")

        self._plugin_classes[metadata.name] = plugin_class
        logger.info(f"Registered plugin: {metadata.name} v{metadata.version}")

    def load_plugin(
        self,
        plugin_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> PluginBase:
        """Load and initialize a plugin"""
        if plugin_name not in self._plugin_classes:
            raise ValueError(f"Plugin {plugin_name} not found in registry")

        plugin_class = self._plugin_classes[plugin_name]
        plugin = plugin_class(config=config)

        if not plugin.validate_config():
            raise ValueError(f"Invalid configuration for plugin {plugin_name}")

        plugin.initialize()
        self._plugins[plugin_name] = plugin

        logger.info(f"Loaded plugin: {plugin_name}")
        return plugin

    def unload_plugin(self, plugin_name: str) -> None:
        """Unload a plugin"""
        if plugin_name in self._plugins:
            plugin = self._plugins[plugin_name]
            plugin.shutdown()
            del self._plugins[plugin_name]
            logger.info(f"Unloaded plugin: {plugin_name}")

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get a loaded plugin instance"""
        return self._plugins.get(plugin_name)

    def list_plugins(
        self,
        plugin_type: Optional[PluginType] = None,
        loaded_only: bool = False
    ) -> List[PluginMetadata]:
        """List available plugins"""
        plugins = self._plugins if loaded_only else self._plugin_classes

        results = []
        for name, plugin_obj in plugins.items():
            if loaded_only:
                metadata = plugin_obj.metadata
            else:
                metadata = plugin_obj().metadata

            if plugin_type is None or metadata.plugin_type == plugin_type:
                results.append(metadata)

        return results

    def discover_plugins(self, package_name: str = "openfinops_plugins") -> None:
        """Auto-discover plugins from a package"""
        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.debug(f"Plugin package {package_name} not found")
            return

        for _, module_name, _ in pkgutil.iter_modules(package.__path__):
            full_module_name = f"{package_name}.{module_name}"
            try:
                module = importlib.import_module(full_module_name)

                # Look for plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        issubclass(attr, PluginBase) and
                        attr != PluginBase):
                        self.register(attr)

            except Exception as e:
                logger.error(f"Failed to load plugin module {full_module_name}: {e}")


# Global plugin registry
registry = PluginRegistry()
```

### Plugin Decorators

```python
# src/openfinops/plugins/decorators.py

from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)


def plugin(plugin_type: PluginType):
    """Decorator to mark a class as a plugin"""
    def decorator(cls):
        cls._plugin_type = plugin_type
        return cls
    return decorator


def hook(event_name: str):
    """Decorator to register a function as a hook"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Executing hook: {event_name}")
            result = func(*args, **kwargs)
            logger.debug(f"Hook {event_name} completed")
            return result

        wrapper._is_hook = True
        wrapper._event_name = event_name
        return wrapper
    return decorator


def requires_config(*required_keys: str):
    """Decorator to validate required configuration keys"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            missing = [key for key in required_keys if key not in self.config]
            if missing:
                raise ValueError(
                    f"Missing required configuration: {', '.join(missing)}"
                )
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 🔌 Plugin Development Guide

### 1. Telemetry Plugin

Create custom telemetry collectors for any data source:

```python
# openfinops_plugins/oracle_cloud.py

from openfinops.plugins import TelemetryPlugin, PluginMetadata
from openfinops.observability.cost_observatory import CostEntry
from typing import List
import oci  # Oracle Cloud SDK


class OracleCloudTelemetryPlugin(TelemetryPlugin):
    """Telemetry plugin for Oracle Cloud Infrastructure"""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="oracle-cloud-telemetry",
            version="1.0.0",
            author="Your Name",
            description="Collect cost and usage data from Oracle Cloud",
            plugin_type=PluginType.TELEMETRY,
            dependencies=["oci>=2.0.0"],
            config_schema={
                "tenancy_ocid": {"type": "string", "required": True},
                "user_ocid": {"type": "string", "required": True},
                "region": {"type": "string", "required": True},
            },
        )

    def initialize(self) -> None:
        """Initialize OCI client"""
        config = oci.config.from_file()  # Or use self.config
        self.usage_client = oci.usage_api.UsageapiClient(config)
        self._initialized = True

    def collect_telemetry(self) -> List[CostEntry]:
        """Collect cost data from Oracle Cloud"""
        if not self._initialized:
            raise RuntimeError("Plugin not initialized")

        cost_entries = []

        # Query Oracle Cloud usage data
        usage_data = self._query_usage_data()

        for item in usage_data:
            entry = CostEntry(
                timestamp=item.time_usage_started.timestamp(),
                provider="oracle",
                service=item.service,
                resource_id=item.resource_id,
                cost_usd=float(item.computed_amount),
                region=self.config["region"],
                tags=self._extract_tags(item),
            )
            cost_entries.append(entry)

        return cost_entries

    def _query_usage_data(self):
        """Query usage data from OCI"""
        # Implementation details...
        pass

    def _extract_tags(self, item):
        """Extract tags from OCI resource"""
        # Implementation details...
        pass

    def shutdown(self) -> None:
        """Cleanup resources"""
        self.usage_client = None
        self._initialized = False
```

**Installation**:
```bash
pip install openfinops-plugin-oracle-cloud
```

**Configuration**:
```yaml
# openfinops.yaml
plugins:
  oracle-cloud-telemetry:
    enabled: true
    config:
      tenancy_ocid: "ocid1.tenancy.oc1..xxx"
      user_ocid: "ocid1.user.oc1..xxx"
      region: "us-ashburn-1"
    collection_interval: 3600  # 1 hour
```

**Usage**:
```python
from openfinops.plugins import registry

# Load plugin
plugin = registry.load_plugin("oracle-cloud-telemetry", config={
    "tenancy_ocid": "ocid1.tenancy.oc1..xxx",
    "user_ocid": "ocid1.user.oc1..xxx",
    "region": "us-ashburn-1",
})

# Collect data
cost_entries = plugin.collect_telemetry()

# Send to OpenFinOps
from openfinops.observability import CostObservatory
cost_obs = CostObservatory()
for entry in cost_entries:
    cost_obs.add_cost_entry(entry)
```

### 2. Attribution Plugin

Create custom cost attribution logic:

```python
# openfinops_plugins/activity_based_attribution.py

from openfinops.plugins import AttributionPlugin, PluginMetadata
from openfinops.observability.cost_observatory import CostEntry
from typing import Dict, List


class ActivityBasedAttributionPlugin(AttributionPlugin):
    """Custom activity-based cost attribution"""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="activity-based-attribution",
            version="1.0.0",
            author="Your Name",
            description="Attribute costs based on activity metrics",
            plugin_type=PluginType.ATTRIBUTION,
        )

    def initialize(self) -> None:
        self._activity_metrics = {}
        self._initialized = True

    def attribute_cost(
        self,
        cost_entry: CostEntry,
        activity_data: Dict[str, float]
    ) -> List[CostEntry]:
        """
        Split cost entry into multiple entries based on activity.

        Args:
            cost_entry: The cost entry to split
            activity_data: Dict mapping entity_id to activity volume

        Returns:
            List of attributed cost entries
        """
        total_activity = sum(activity_data.values())
        attributed_entries = []

        for entity_id, activity_volume in activity_data.items():
            proportion = activity_volume / total_activity
            attributed_cost = cost_entry.cost_usd * proportion

            new_entry = CostEntry(
                timestamp=cost_entry.timestamp,
                provider=cost_entry.provider,
                service=cost_entry.service,
                resource_id=cost_entry.resource_id,
                cost_usd=attributed_cost,
                region=cost_entry.region,
                tags={
                    **cost_entry.tags,
                    "attributed_to": entity_id,
                    "attribution_method": "activity_based",
                    "activity_proportion": f"{proportion:.2%}",
                },
            )
            attributed_entries.append(new_entry)

        return attributed_entries

    def shutdown(self) -> None:
        self._activity_metrics = {}
        self._initialized = False
```

**Usage**:
```python
from openfinops.plugins import registry

plugin = registry.load_plugin("activity-based-attribution")

# Shared database cost
db_cost_entry = CostEntry(
    timestamp=time.time(),
    provider="aws",
    service="rds",
    resource_id="rds-shared-prod",
    cost_usd=5000.0,
    region="us-west-2",
    tags={"environment": "production"},
)

# Activity data (e.g., query counts)
activity_data = {
    "user-service": 45000,
    "order-service": 35000,
    "analytics-service": 20000,
}

# Attribute costs
attributed_entries = plugin.attribute_cost(db_cost_entry, activity_data)

for entry in attributed_entries:
    print(f"{entry.tags['attributed_to']}: ${entry.cost_usd:.2f}")
# Output:
# user-service: $2250.00
# order-service: $1750.00
# analytics-service: $1000.00
```

### 3. Recommendation Plugin

Create custom optimization recommendations:

```python
# openfinops_plugins/ml_rightsizing.py

from openfinops.plugins import RecommendationPlugin, PluginMetadata
from openfinops.observability import ObservabilityHub
from typing import List
from dataclasses import dataclass


@dataclass
class Recommendation:
    """Optimization recommendation"""
    resource_id: str
    recommendation_type: str
    current_state: str
    recommended_state: str
    annual_savings: float
    confidence: float
    implementation_effort: str
    description: str


class MLRightsizingPlugin(RecommendationPlugin):
    """ML-powered instance rightsizing recommendations"""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ml-rightsizing",
            version="1.0.0",
            author="Your Name",
            description="ML-powered EC2 instance rightsizing",
            plugin_type=PluginType.RECOMMENDATION,
            dependencies=["scikit-learn>=1.0.0"],
        )

    def initialize(self) -> None:
        # Load pre-trained ML model
        self._load_model()
        self._initialized = True

    def generate_recommendations(
        self,
        hub: ObservabilityHub,
        lookback_days: int = 30
    ) -> List[Recommendation]:
        """Generate rightsizing recommendations"""
        recommendations = []

        # Get historical metrics
        metrics = hub.get_ec2_metrics(days=lookback_days)

        for instance_id, instance_metrics in metrics.items():
            # Use ML model to predict optimal instance type
            current_type = instance_metrics["instance_type"]
            recommended_type = self._predict_optimal_type(instance_metrics)

            if recommended_type != current_type:
                savings = self._calculate_savings(current_type, recommended_type)

                rec = Recommendation(
                    resource_id=instance_id,
                    recommendation_type="rightsize",
                    current_state=current_type,
                    recommended_state=recommended_type,
                    annual_savings=savings,
                    confidence=0.95,
                    implementation_effort="low",
                    description=(
                        f"Instance {instance_id} is over-provisioned. "
                        f"CPU avg: {instance_metrics['cpu_avg']:.1f}%, "
                        f"Memory avg: {instance_metrics['memory_avg']:.1f}%. "
                        f"Downsize to {recommended_type} for ${savings:,.0f}/year savings."
                    ),
                )
                recommendations.append(rec)

        return recommendations

    def _load_model(self):
        """Load ML model"""
        # Implementation...
        pass

    def _predict_optimal_type(self, metrics):
        """Predict optimal instance type"""
        # Use ML model
        pass

    def _calculate_savings(self, current, recommended):
        """Calculate annual savings"""
        # Implementation...
        pass

    def shutdown(self) -> None:
        self._model = None
        self._initialized = False
```

### 4. Dashboard Widget Plugin

Create custom dashboard widgets:

```python
# openfinops_plugins/carbon_footprint_widget.py

from openfinops.plugins import DashboardPlugin, PluginMetadata
from openfinops.vizlychart import Figure


class CarbonFootprintWidget(DashboardPlugin):
    """Dashboard widget showing carbon footprint"""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="carbon-footprint-widget",
            version="1.0.0",
            author="Your Name",
            description="Display carbon emissions from cloud infrastructure",
            plugin_type=PluginType.DASHBOARD,
        )

    def initialize(self) -> None:
        self._carbon_factors = {
            "us-west-2": 0.4,  # kg CO2 per kWh
            "us-east-1": 0.5,
            "eu-west-1": 0.3,
        }
        self._initialized = True

    def render(self, cost_obs, time_range="30d") -> Figure:
        """Render carbon footprint widget"""
        # Get cost data
        costs = cost_obs.get_costs_by_region(time_range=time_range)

        # Calculate carbon emissions
        emissions = {}
        for region, cost in costs.items():
            # Estimate kWh from cost (simplified)
            kwh = cost * 10  # $1 = ~10 kWh (rough estimate)
            carbon_factor = self._carbon_factors.get(region, 0.5)
            emissions[region] = kwh * carbon_factor

        # Create visualization
        fig = Figure(figsize=(10, 6))
        fig.bar(
            x=list(emissions.keys()),
            y=list(emissions.values()),
            title="Carbon Footprint by Region",
            xlabel="Region",
            ylabel="CO2 Emissions (kg)",
        )

        return fig

    def shutdown(self) -> None:
        self._carbon_factors = {}
        self._initialized = False
```

**Usage in Dashboard**:
```python
from openfinops.plugins import registry
from openfinops.dashboard import Dashboard

# Load plugin
widget = registry.load_plugin("carbon-footprint-widget")

# Add to dashboard
dashboard = Dashboard(name="Sustainability Dashboard")
dashboard.add_widget(widget.render(cost_obs, time_range="90d"))
dashboard.show()
```

---

## 🎣 Hook System

Hooks allow plugins to intercept and modify OpenFinOps behavior:

```python
# Available hooks
HOOKS = [
    "pre_collect_metrics",      # Before metric collection
    "post_collect_metrics",     # After metric collection
    "cost_entry_received",      # When cost entry is added
    "budget_threshold_exceeded", # When budget is exceeded
    "recommendation_generated",  # When recommendation is created
    "dashboard_render",         # Before dashboard renders
    "alert_triggered",          # When alert is triggered
]
```

**Example Hook Plugin**:

```python
# openfinops_plugins/cost_enrichment_hook.py

from openfinops.plugins import hook
from openfinops.observability.cost_observatory import CostEntry


@hook("cost_entry_received")
def enrich_cost_entry(entry: CostEntry) -> CostEntry:
    """
    Enrich cost entries with additional metadata.
    This hook is called every time a cost entry is received.
    """
    # Add business unit mapping
    business_units = {
        "team-ml": "R&D",
        "team-web": "Product",
        "team-analytics": "Business Intelligence",
    }

    team = entry.tags.get("team")
    if team in business_units:
        entry.tags["business_unit"] = business_units[team]

    # Add cost category
    if entry.service in ["ec2", "ecs", "eks"]:
        entry.tags["cost_category"] = "compute"
    elif entry.service in ["s3", "ebs", "efs"]:
        entry.tags["cost_category"] = "storage"
    elif entry.service in ["rds", "dynamodb", "elasticache"]:
        entry.tags["cost_category"] = "database"

    return entry


@hook("budget_threshold_exceeded")
def send_custom_alert(budget, current_spend):
    """Send custom alert when budget is exceeded"""
    import slack_sdk

    client = slack_sdk.WebClient(token=os.getenv("SLACK_TOKEN"))

    message = (
        f"🚨 Budget Alert!\n\n"
        f"Budget: {budget.name}\n"
        f"Limit: ${budget.amount:,.0f}\n"
        f"Current: ${current_spend:,.0f}\n"
        f"Overage: ${current_spend - budget.amount:,.0f}"
    )

    client.chat_postMessage(
        channel="#finops-alerts",
        text=message,
    )
```

**Register Hooks**:
```yaml
# openfinops.yaml
plugins:
  cost-enrichment-hook:
    enabled: true
    hooks:
      - cost_entry_received
      - budget_threshold_exceeded
```

---

## 📦 Plugin Distribution

### PyPI Package

Create a standard Python package:

```
openfinops-plugin-oracle-cloud/
├── setup.py
├── README.md
├── LICENSE
└── openfinops_plugins/
    └── oracle_cloud.py
```

**setup.py**:
```python
from setuptools import setup, find_packages

setup(
    name="openfinops-plugin-oracle-cloud",
    version="1.0.0",
    description="Oracle Cloud telemetry plugin for OpenFinOps",
    author="Your Name",
    author_email="you@example.com",
    url="https://github.com/yourusername/openfinops-plugin-oracle-cloud",
    packages=find_packages(),
    install_requires=[
        "openfinops>=0.2.0",
        "oci>=2.0.0",
    ],
    entry_points={
        "openfinops.plugins": [
            "oracle-cloud = openfinops_plugins.oracle_cloud:OracleCloudTelemetryPlugin",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
```

**Publish**:
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

**Install**:
```bash
pip install openfinops-plugin-oracle-cloud
```

### GitHub Plugin Repository

Tag your repository with `openfinops-plugin` topic for discoverability.

---

## 🧪 Testing Plugins

```python
# tests/test_my_plugin.py

import pytest
from openfinops.plugins import registry
from openfinops_plugins.my_plugin import MyPlugin


def test_plugin_metadata():
    """Test plugin metadata"""
    plugin = MyPlugin()
    metadata = plugin.metadata

    assert metadata.name == "my-plugin"
    assert metadata.version is not None
    assert metadata.plugin_type is not None


def test_plugin_initialization():
    """Test plugin initialization"""
    plugin = MyPlugin(config={"api_key": "test"})
    plugin.initialize()

    assert plugin._initialized is True


def test_plugin_functionality():
    """Test plugin core functionality"""
    plugin = MyPlugin(config={"api_key": "test"})
    plugin.initialize()

    result = plugin.collect_telemetry()

    assert isinstance(result, list)
    assert len(result) > 0


def test_plugin_shutdown():
    """Test plugin cleanup"""
    plugin = MyPlugin(config={"api_key": "test"})
    plugin.initialize()
    plugin.shutdown()

    assert plugin._initialized is False
```

---

## 📚 Best Practices

### 1. Configuration Management
- Use config schema validation
- Provide sensible defaults
- Support environment variables
- Document all config options

### 2. Error Handling
- Catch and log errors gracefully
- Provide meaningful error messages
- Support retry logic for API calls
- Validate inputs

### 3. Performance
- Use caching where appropriate
- Batch API calls when possible
- Implement rate limiting
- Monitor memory usage

### 4. Security
- Never log sensitive credentials
- Use secure credential storage
- Validate all inputs
- Follow least-privilege principle

### 5. Documentation
- Write comprehensive README
- Provide usage examples
- Document configuration options
- Include troubleshooting guide

---

## 🤝 Community Plugins

Share your plugins with the community!

### Plugin Marketplace

Browse community plugins:
- [GitHub Topic: openfinops-plugin](https://github.com/topics/openfinops-plugin)

### Featured Plugins

**Coming Soon**:
- openfinops-plugin-digitalocean
- openfinops-plugin-alicloud
- openfinops-plugin-carbon-footprint
- openfinops-plugin-slack-approvals
- openfinops-plugin-grafana

### Contribute Your Plugin

1. Build your plugin
2. Publish to PyPI
3. Tag repo with `openfinops-plugin`
4. Submit to plugin directory
5. Share in community discussions

---

## 📞 Support

- **Documentation**: [docs.openfinops.io/plugins](https://docs.openfinops.io/plugins)
- **Examples**: [github.com/openfinops/plugin-examples](https://github.com/openfinops/plugin-examples)
- **Discussions**: [GitHub Discussions](https://github.com/openfinops/openfinops/discussions)
- **Issues**: [Report bugs](https://github.com/openfinops/openfinops/issues)

---

**Start building plugins today! 🚀**
