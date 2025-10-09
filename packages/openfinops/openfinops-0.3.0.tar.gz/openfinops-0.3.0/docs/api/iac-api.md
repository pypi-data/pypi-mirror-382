# FinOps-as-Code API Reference

OpenFinOps Infrastructure as Code (IaC) module for managing FinOps resources programmatically.

## Overview

The IaC module enables declarative management of OpenFinOps resources including budgets, policies, alerts, and dashboards. It supports Terraform HCL generation and provides a complete plan/apply/destroy workflow.

## Modules

- `openfinops.iac.provider` - Provider and configuration
- `openfinops.iac.resources` - Resource definitions
- `openfinops.iac.terraform_generator` - Terraform HCL generation
- `openfinops.iac.client` - API client

---

## Provider API

### `OpenFinOpsProvider`

Manages OpenFinOps resources with IaC workflow.

#### Constructor

```python
from openfinops.iac import OpenFinOpsProvider

provider = OpenFinOpsProvider(
    endpoint: str = "http://localhost:8080",
    api_key: Optional[str] = None,
    config: Optional[ProviderConfig] = None
)
```

**Parameters:**
- `endpoint` - OpenFinOps API endpoint URL
- `api_key` - API authentication key (optional)
- `config` - Provider configuration (optional)

#### Methods

##### `initialize() -> bool`

Initialize provider and validate connection.

```python
provider = OpenFinOpsProvider(endpoint="https://finops.company.com")
success = provider.initialize()
```

**Returns:** `bool` - True if initialization successful

---

##### `register_resource(resource_type: str, resource_id: str, resource: Any) -> None`

Register a resource with the provider.

```python
provider.register_resource("budget", "prod-budget", budget_resource)
```

**Parameters:**
- `resource_type` - Type of resource (budget, policy, alert, dashboard)
- `resource_id` - Unique resource identifier
- `resource` - Resource object

---

##### `validate() -> Dict[str, Any]`

Validate all registered resources.

```python
validation_result = provider.validate()
if validation_result["valid"]:
    print("All resources valid")
else:
    print(f"Errors: {validation_result['errors']}")
```

**Returns:** `Dict` with keys:
- `valid` - Boolean indicating validation status
- `errors` - List of validation errors
- `warnings` - List of warnings

---

##### `plan() -> Dict[str, Any]`

Generate execution plan showing planned changes.

```python
plan = provider.plan()
print(f"Resources to create: {plan['to_create']}")
print(f"Resources to update: {plan['to_update']}")
print(f"Resources to delete: {plan['to_delete']}")
```

**Returns:** `Dict` with planned changes

---

##### `apply(auto_approve: bool = False) -> Dict[str, Any]`

Apply changes to create/update/delete resources.

```python
# Interactive approval
result = provider.apply()

# Auto-approve (use with caution)
result = provider.apply(auto_approve=True)
```

**Parameters:**
- `auto_approve` - Skip confirmation prompt

**Returns:** `Dict` with execution results

---

##### `destroy() -> Dict[str, Any]`

Destroy all managed resources.

```python
result = provider.destroy()
```

**Returns:** `Dict` with destruction results

---

### `ProviderConfig`

Provider configuration settings.

```python
from openfinops.iac import ProviderConfig

config = ProviderConfig(
    endpoint: str = "http://localhost:8080",
    api_key: Optional[str] = None,
    timeout: int = 30,
    verify_ssl: bool = True,
    tags: Optional[Dict[str, str]] = None
)
```

**Attributes:**
- `endpoint` - API endpoint URL
- `api_key` - Authentication key
- `timeout` - Request timeout in seconds
- `verify_ssl` - Verify SSL certificates
- `tags` - Default tags for all resources

---

## Resource API

### Base Resource

All resources inherit from the `Resource` base class.

```python
class Resource(ABC):
    def __init__(self, name: str, provider: OpenFinOpsProvider):
        self.name = name
        self.provider = provider
        self.state = ResourceState.PENDING
```

**Common Methods:**
- `validate() -> List[str]` - Validate resource configuration
- `create() -> Dict[str, Any]` - Create resource
- `read() -> Dict[str, Any]` - Read resource state
- `update(updates: Dict) -> Dict[str, Any]` - Update resource
- `delete() -> Dict[str, Any]` - Delete resource
- `to_terraform() -> str` - Generate Terraform HCL

---

### `BudgetResource`

Manage cost budgets with alerts.

#### Constructor

```python
from openfinops.iac import budget

budget_resource = budget(
    name: str,
    provider: OpenFinOpsProvider,
    amount: float = 0.0,
    period: str = "monthly",
    scope: Optional[Dict[str, Any]] = None,
    alerts: Optional[List[Dict[str, Any]]] = None,
    notifications: Optional[List[str]] = None,
    tags: Optional[Dict[str, str]] = None
)
```

**Parameters:**
- `name` - Budget name
- `provider` - OpenFinOps provider instance
- `amount` - Budget amount in USD
- `period` - Budget period (monthly, quarterly, annual)
- `scope` - Budget scope filters (environment, team, project)
- `alerts` - Alert thresholds (e.g., `[{"threshold": 80, "type": "percentage"}]`)
- `notifications` - Email addresses for notifications
- `tags` - Resource tags

#### Example

```python
from openfinops.iac import OpenFinOpsProvider, budget

provider = OpenFinOpsProvider(endpoint="https://finops.company.com")

prod_budget = budget(
    name="production-budget",
    provider=provider,
    amount=10000.0,
    period="monthly",
    scope={"environment": "production"},
    alerts=[
        {"threshold": 80, "type": "percentage"},
        {"threshold": 95, "type": "percentage"}
    ],
    notifications=["finops@company.com"],
    tags={"team": "platform", "cost-center": "engineering"}
)

# Validate
errors = prod_budget.validate()

# Create
result = prod_budget.create()
```

---

### `PolicyResource`

Define and enforce cost policies.

#### Constructor

```python
from openfinops.iac import policy

policy_resource = policy(
    name: str,
    provider: OpenFinOpsProvider,
    policy_type: str,
    rules: Dict[str, Any],
    enabled: bool = True,
    enforcement: str = "advisory",
    scope: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, str]] = None
)
```

**Parameters:**
- `name` - Policy name
- `provider` - OpenFinOps provider instance
- `policy_type` - Type (budget, tagging, compliance, lifecycle)
- `rules` - Policy rules dictionary
- `enabled` - Enable policy enforcement
- `enforcement` - Enforcement mode (advisory, blocking)
- `scope` - Policy scope filters
- `tags` - Resource tags

#### Example

```python
from openfinops.iac import policy

cost_policy = policy(
    name="max-spend-policy",
    provider=provider,
    policy_type="budget",
    rules={
        "max_monthly_spend": 10000,
        "max_daily_spend": 500,
        "notify_at_threshold": 80
    },
    enforcement="blocking",
    scope={"environment": "production"}
)
```

---

### `AlertResource`

Configure cost and resource alerts.

#### Constructor

```python
from openfinops.iac import alert

alert_resource = alert(
    name: str,
    provider: OpenFinOpsProvider,
    metric: str,
    threshold: float,
    comparison: str = "greater_than",
    period: str = "5m",
    notifications: Optional[List[str]] = None,
    enabled: bool = True,
    tags: Optional[Dict[str, str]] = None
)
```

**Parameters:**
- `name` - Alert name
- `provider` - OpenFinOps provider instance
- `metric` - Metric to monitor (cost, cpu_usage, memory_usage)
- `threshold` - Alert threshold value
- `comparison` - Comparison operator (greater_than, less_than, equal_to)
- `period` - Evaluation period
- `notifications` - Notification channels
- `enabled` - Enable alert
- `tags` - Resource tags

#### Example

```python
from openfinops.iac import alert

daily_cost_alert = alert(
    name="daily-cost-spike",
    provider=provider,
    metric="daily_cost",
    threshold=1000.0,
    comparison="greater_than",
    period="1d",
    notifications=["slack://finops-alerts", "email://team@company.com"],
    enabled=True
)
```

---

### `DashboardResource`

Create custom dashboards.

#### Constructor

```python
from openfinops.iac import dashboard

dashboard_resource = dashboard(
    name: str,
    provider: OpenFinOpsProvider,
    layout: List[Dict[str, Any]],
    refresh_interval: int = 60,
    permissions: Optional[Dict[str, List[str]]] = None,
    tags: Optional[Dict[str, str]] = None
)
```

**Parameters:**
- `name` - Dashboard name
- `provider` - OpenFinOps provider instance
- `layout` - Dashboard widget layout
- `refresh_interval` - Auto-refresh interval in seconds
- `permissions` - Role-based access permissions
- `tags` - Resource tags

#### Example

```python
from openfinops.iac import dashboard

exec_dashboard = dashboard(
    name="executive-dashboard",
    provider=provider,
    layout=[
        {"type": "cost_summary", "position": {"x": 0, "y": 0, "w": 6, "h": 4}},
        {"type": "budget_status", "position": {"x": 6, "y": 0, "w": 6, "h": 4}},
        {"type": "cost_trend", "position": {"x": 0, "y": 4, "w": 12, "h": 6}}
    ],
    refresh_interval=300,
    permissions={"view": ["cfo", "finance", "executive"]}
)
```

---

## Terraform Generator API

### `TerraformGenerator`

Generate Terraform HCL from OpenFinOps resources.

#### Constructor

```python
from openfinops.iac import TerraformGenerator

generator = TerraformGenerator(
    provider_config: ProviderConfig
)
```

#### Methods

##### `add_resource(resource: Resource) -> None`

Add a resource to the generator.

```python
generator.add_resource(budget_resource)
generator.add_resource(policy_resource)
```

---

##### `generate() -> str`

Generate complete Terraform configuration.

```python
hcl = generator.generate()
print(hcl)
```

**Returns:** Terraform HCL configuration string

---

##### `save(output_path: str) -> None`

Save Terraform configuration to file.

```python
generator.save("main.tf")
```

---

### `generate_terraform()`

Helper function for quick Terraform generation.

```python
from openfinops.iac import generate_terraform

hcl = generate_terraform(
    provider_config=config,
    resources=[budget_resource, policy_resource],
    output_path="openfinops.tf"  # Optional
)
```

**Parameters:**
- `provider_config` - Provider configuration
- `resources` - List of resources
- `output_path` - Optional output file path

**Returns:** Terraform HCL string

---

### `generate_module()`

Generate a Terraform module.

```python
from openfinops.iac import generate_module

module = generate_module(
    module_name="finops-budgets",
    resources=[budget1, budget2],
    variables={
        "environment": {"type": "string", "description": "Environment name"}
    },
    outputs={
        "budget_ids": {"value": "${openfinops_budget.*.id}"}
    }
)
```

**Returns:** `Dict` containing:
- `main.tf` - Main configuration
- `variables.tf` - Variable definitions
- `outputs.tf` - Output values

---

## Client API

### `OpenFinOpsClient`

HTTP client for OpenFinOps API.

#### Constructor

```python
from openfinops.iac import OpenFinOpsClient

client = OpenFinOpsClient(
    endpoint: str = "http://localhost:8080",
    api_key: Optional[str] = None,
    timeout: int = 30
)
```

#### Budget Methods

```python
# Create budget
budget = client.create_budget({
    "name": "prod-budget",
    "amount": 10000.0,
    "period": "monthly"
})

# Get budget
budget = client.get_budget("budget-id")

# Update budget
updated = client.update_budget("budget-id", {"amount": 15000.0})

# Delete budget
client.delete_budget("budget-id")

# List budgets
budgets = client.list_budgets()
```

#### Policy Methods

```python
# Create policy
policy = client.create_policy({
    "name": "tagging-policy",
    "policy_type": "tagging",
    "rules": {"required_tags": ["environment", "team"]}
})

# Get policy
policy = client.get_policy("policy-id")

# Update policy
updated = client.update_policy("policy-id", {"enabled": False})

# Delete policy
client.delete_policy("policy-id")

# List policies
policies = client.list_policies()
```

#### Alert Methods

```python
# Create alert
alert = client.create_alert({
    "name": "high-cost-alert",
    "metric": "daily_cost",
    "threshold": 1000.0
})

# Get alert
alert = client.get_alert("alert-id")

# Update alert
updated = client.update_alert("alert-id", {"threshold": 1500.0})

# Delete alert
client.delete_alert("alert-id")

# List alerts
alerts = client.list_alerts()
```

#### Dashboard Methods

```python
# Create dashboard
dashboard = client.create_dashboard({
    "name": "team-dashboard",
    "layout": [...]
})

# Get dashboard
dashboard = client.get_dashboard("dashboard-id")

# Update dashboard
updated = client.update_dashboard("dashboard-id", {"refresh_interval": 120})

# Delete dashboard
client.delete_dashboard("dashboard-id")

# List dashboards
dashboards = client.list_dashboards()
```

---

## Complete Workflow Example

```python
from openfinops.iac import (
    OpenFinOpsProvider,
    budget,
    policy,
    alert,
    dashboard,
    generate_terraform
)

# Initialize provider
provider = OpenFinOpsProvider(
    endpoint="https://finops.company.com",
    api_key="your-api-key"
)

# Create resources
prod_budget = budget(
    name="production-budget",
    provider=provider,
    amount=50000.0,
    period="monthly",
    scope={"environment": "production"},
    alerts=[{"threshold": 80, "type": "percentage"}]
)

tagging_policy = policy(
    name="required-tags-policy",
    provider=provider,
    policy_type="tagging",
    rules={"required_tags": ["environment", "team", "cost-center"]},
    enforcement="blocking"
)

cost_alert = alert(
    name="daily-cost-threshold",
    provider=provider,
    metric="daily_cost",
    threshold=2000.0,
    notifications=["slack://finops-alerts"]
)

# Validate resources
provider.initialize()
validation = provider.validate()
if not validation["valid"]:
    print(f"Validation errors: {validation['errors']}")
    exit(1)

# Generate execution plan
plan = provider.plan()
print(f"Plan: {plan['summary']}")

# Apply changes
if input("Apply changes? (yes/no): ").lower() == "yes":
    result = provider.apply()
    print(f"Applied: {result['summary']}")

# Generate Terraform HCL
hcl = generate_terraform(
    provider_config=provider.config,
    resources=[prod_budget, tagging_policy, cost_alert],
    output_path="openfinops.tf"
)
print("Terraform configuration saved to openfinops.tf")
```

---

## Resource State

Resources progress through the following states:

- `PENDING` - Resource defined but not created
- `CREATING` - Resource creation in progress
- `ACTIVE` - Resource created and active
- `UPDATING` - Resource update in progress
- `DELETING` - Resource deletion in progress
- `DELETED` - Resource deleted
- `FAILED` - Operation failed

---

## Error Handling

```python
from openfinops.iac import OpenFinOpsProvider, IaCException

try:
    provider = OpenFinOpsProvider(endpoint="https://finops.company.com")
    provider.initialize()

    # ... create resources ...

    result = provider.apply()

except IaCException as e:
    print(f"IaC error: {e.message}")
    print(f"Failed resource: {e.resource_id}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Best Practices

1. **Always validate before applying:**
   ```python
   validation = provider.validate()
   if validation["valid"]:
       provider.apply()
   ```

2. **Use tags for resource organization:**
   ```python
   budget(name="...", tags={"team": "platform", "env": "prod"})
   ```

3. **Review plans before applying:**
   ```python
   plan = provider.plan()
   # Review plan details
   provider.apply()
   ```

4. **Use environment variables for credentials:**
   ```python
   import os
   provider = OpenFinOpsProvider(
       endpoint=os.getenv("OPENFINOPS_ENDPOINT"),
       api_key=os.getenv("OPENFINOPS_API_KEY")
   )
   ```

5. **Generate Terraform for version control:**
   ```python
   generate_terraform(
       provider_config=config,
       resources=resources,
       output_path="infrastructure/openfinops.tf"
   )
   ```

---

## See Also

- [SaaS Management API](saas-api.md)
- [Multi-Cloud API](multicloud-api.md)
- [Observability API](observability-api.md)
