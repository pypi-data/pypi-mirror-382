# Dashboard API Reference

Complete API reference for OpenFinOps role-based dashboards.

## Overview

OpenFinOps provides role-based dashboards tailored for different stakeholders:
- **CFO Dashboard**: Financial metrics and cost optimization
- **COO Dashboard**: Operational metrics and efficiency
- **Infrastructure Leader Dashboard**: Technical metrics and resource utilization
- **Finance Analyst Dashboard**: Detailed cost attribution and analysis

## Table of Contents

- [CFO Dashboard](#cfo-dashboard)
- [COO Dashboard](#coo-dashboard)
- [Infrastructure Leader Dashboard](#infrastructure-leader-dashboard)
- [Finance Analyst Dashboard](#finance-analyst-dashboard)
- [IAM System](#iam-system)
- [Dashboard Router](#dashboard-router)

---

## CFO Dashboard

Financial overview and strategic cost insights.

### Class: `CFODashboard`

**Location**: `openfinops.dashboard.cfo_dashboard`

```python
from openfinops.dashboard import CFODashboard

dashboard = CFODashboard(user_id="cfo@company.com")
```

#### Methods

##### `get_financial_summary(time_range="30d")`

Get comprehensive financial summary.

```python
summary = dashboard.get_financial_summary(time_range="30d")

print(f"Total Spend: ${summary['total_spend']:.2f}")
print(f"Budget: ${summary['budget']:.2f}")
print(f"Budget Utilization: {summary['budget_utilization']:.1f}%")
print(f"Forecast (30d): ${summary['forecast_30d']:.2f}")
print(f"YoY Growth: {summary['yoy_growth']:.1f}%")
print(f"Top Cost Driver: {summary['top_cost_driver']}")
```

**Returns:**
```python
{
    'total_spend': 125000.00,
    'budget': 150000.00,
    'budget_utilization': 83.3,
    'forecast_30d': 135000.00,
    'yoy_growth': 15.5,
    'top_cost_driver': 'GPU Compute',
    'savings_opportunities': 25000.00,
    'cost_efficiency_score': 78.5
}
```

---

##### `get_cost_breakdown(dimension='provider', time_range="30d")`

Get cost breakdown by various dimensions.

```python
# By provider
provider_breakdown = dashboard.get_cost_breakdown(dimension='provider')

# By service
service_breakdown = dashboard.get_cost_breakdown(dimension='service')

# By team
team_breakdown = dashboard.get_cost_breakdown(dimension='team')

# By project
project_breakdown = dashboard.get_cost_breakdown(dimension='project')
```

**Dimensions:** `'provider'`, `'service'`, `'team'`, `'project'`, `'cost_center'`

---

##### `get_roi_analysis(project_id=None)`

Get ROI analysis for AI/ML initiatives.

```python
roi = dashboard.get_roi_analysis(project_id="llm-training-2025")

print(f"Total Investment: ${roi['total_investment']:.2f}")
print(f"Revenue Impact: ${roi['revenue_impact']:.2f}")
print(f"ROI: {roi['roi_percentage']:.1f}%")
print(f"Payback Period: {roi['payback_months']} months")
print(f"NPV: ${roi['npv']:.2f}")
```

---

##### `get_budget_alerts()`

Get budget alerts and warnings.

```python
alerts = dashboard.get_budget_alerts()

for alert in alerts:
    print(f"[{alert['severity']}] {alert['budget_name']}")
    print(f"  Budget: ${alert['budget']:.2f}")
    print(f"  Spent: ${alert['spent']:.2f}")
    print(f"  Status: {alert['status']}")
    print(f"  Projected: ${alert['projected_eom']:.2f}")
```

---

##### `generate_executive_report(format='pdf', time_range="30d")`

Generate executive financial report.

```python
report = dashboard.generate_executive_report(
    format='pdf',
    time_range="quarterly"
)

# Save report
with open("executive_report_q1.pdf", "wb") as f:
    f.write(report)
```

**Formats:** `'pdf'`, `'pptx'`, `'excel'`, `'html'`

---

## COO Dashboard

Operational metrics and efficiency insights.

### Class: `COODashboard`

**Location**: `openfinops.dashboard.coo_dashboard`

```python
from openfinops.dashboard import COODashboard

dashboard = COODashboard(user_id="coo@company.com")
```

#### Methods

##### `get_operational_metrics(time_range="24h")`

Get real-time operational metrics.

```python
metrics = dashboard.get_operational_metrics(time_range="24h")

print(f"System Uptime: {metrics['uptime']:.2f}%")
print(f"Active Workloads: {metrics['active_workloads']}")
print(f"Completed Jobs: {metrics['completed_jobs']}")
print(f"Failed Jobs: {metrics['failed_jobs']}")
print(f"Avg Job Duration: {metrics['avg_duration_hours']:.1f}h")
print(f"Resource Utilization: {metrics['resource_utilization']:.1f}%")
```

---

##### `get_efficiency_metrics()`

Get infrastructure efficiency metrics.

```python
efficiency = dashboard.get_efficiency_metrics()

print(f"GPU Efficiency: {efficiency['gpu_efficiency']:.1f}%")
print(f"CPU Efficiency: {efficiency['cpu_efficiency']:.1f}%")
print(f"Storage Efficiency: {efficiency['storage_efficiency']:.1f}%")
print(f"Cost per Workload: ${efficiency['cost_per_workload']:.2f}")
print(f"Idle Resource Cost: ${efficiency['idle_cost']:.2f}")
```

---

##### `get_capacity_planning(horizon_days=90)`

Get capacity planning recommendations.

```python
planning = dashboard.get_capacity_planning(horizon_days=90)

for resource_type, forecast in planning.items():
    print(f"{resource_type}:")
    print(f"  Current Capacity: {forecast['current_capacity']}")
    print(f"  Projected Need: {forecast['projected_need']}")
    print(f"  Shortfall: {forecast['shortfall']}")
    print(f"  Recommendation: {forecast['recommendation']}")
```

---

##### `get_incident_summary(time_range="7d")`

Get incident and alert summary.

```python
incidents = dashboard.get_incident_summary(time_range="7d")

print(f"Total Incidents: {incidents['total']}")
print(f"Critical: {incidents['critical']}")
print(f"High: {incidents['high']}")
print(f"Medium: {incidents['medium']}")
print(f"MTTR: {incidents['mttr_hours']:.1f}h")
print(f"MTBF: {incidents['mtbf_hours']:.1f}h")
```

---

## Infrastructure Leader Dashboard

Technical metrics and resource optimization.

### Class: `InfrastructureLeaderDashboard`

**Location**: `openfinops.dashboard.infrastructure_leader_dashboard`

```python
from openfinops.dashboard import InfrastructureLeaderDashboard

dashboard = InfrastructureLeaderDashboard(user_id="infra@company.com")
```

#### Methods

##### `get_infrastructure_overview()`

Get comprehensive infrastructure overview.

```python
overview = dashboard.get_infrastructure_overview()

print(f"Total Clusters: {overview['total_clusters']}")
print(f"Total Nodes: {overview['total_nodes']}")
print(f"Total GPUs: {overview['total_gpus']}")
print(f"Total vCPUs: {overview['total_vcpus']}")
print(f"Total Memory: {overview['total_memory_gb']} GB")
print(f"Total Storage: {overview['total_storage_tb']} TB")
print(f"Avg Utilization: {overview['avg_utilization']:.1f}%")
```

---

##### `get_cluster_health(cluster_id=None)`

Get cluster health status.

```python
# All clusters
health = dashboard.get_cluster_health()

# Specific cluster
health = dashboard.get_cluster_health(cluster_id="training-cluster-1")

for cluster, status in health.items():
    print(f"{cluster}:")
    print(f"  Status: {status['status']}")
    print(f"  Healthy Nodes: {status['healthy_nodes']}/{status['total_nodes']}")
    print(f"  CPU Avg: {status['cpu_avg']:.1f}%")
    print(f"  GPU Avg: {status['gpu_avg']:.1f}%")
    print(f"  Memory Avg: {status['memory_avg']:.1f}%")
```

---

##### `get_resource_allocation()`

Get resource allocation by team/project.

```python
allocation = dashboard.get_resource_allocation()

for team, resources in allocation.items():
    print(f"{team}:")
    print(f"  GPUs: {resources['gpus']}")
    print(f"  CPU: {resources['vcpus']} vCPUs")
    print(f"  Memory: {resources['memory_gb']} GB")
    print(f"  Storage: {resources['storage_tb']} TB")
    print(f"  Utilization: {resources['utilization']:.1f}%")
```

---

##### `get_optimization_recommendations()`

Get infrastructure optimization recommendations.

```python
recommendations = dashboard.get_optimization_recommendations()

for rec in recommendations:
    print(f"[{rec['priority']}] {rec['title']}")
    print(f"  Type: {rec['type']}")
    print(f"  Impact: {rec['impact']}")
    print(f"  Savings: ${rec['estimated_savings']:.2f}/month")
    print(f"  Action: {rec['recommended_action']}")
```

---

##### `get_performance_metrics(resource_type='gpu', time_range="24h")`

Get detailed performance metrics.

```python
metrics = dashboard.get_performance_metrics(
    resource_type='gpu',
    time_range="24h"
)

print(f"Avg Utilization: {metrics['avg_utilization']:.1f}%")
print(f"Peak Utilization: {metrics['peak_utilization']:.1f}%")
print(f"Idle Time: {metrics['idle_time_pct']:.1f}%")
print(f"Throughput: {metrics['throughput']}")
print(f"Efficiency Score: {metrics['efficiency_score']:.1f}")
```

---

## Finance Analyst Dashboard

Detailed cost attribution and analysis.

### Class: `FinanceAnalystDashboard`

**Location**: `openfinops.dashboard.finance_analyst_dashboard`

```python
from openfinops.dashboard import FinanceAnalystDashboard

dashboard = FinanceAnalystDashboard(user_id="analyst@company.com")
```

#### Methods

##### `get_detailed_cost_report(time_range="30d", group_by='day')`

Get detailed cost breakdown.

```python
report = dashboard.get_detailed_cost_report(
    time_range="30d",
    group_by='day'  # or 'hour', 'week', 'month'
)

for date, costs in report.items():
    print(f"{date}:")
    print(f"  Total: ${costs['total']:.2f}")
    print(f"  Compute: ${costs['compute']:.2f}")
    print(f"  Storage: ${costs['storage']:.2f}")
    print(f"  Network: ${costs['network']:.2f}")
    print(f"  API: ${costs['api']:.2f}")
```

---

##### `get_cost_attribution(dimension, time_range="30d")`

Get granular cost attribution.

```python
# By team
team_costs = dashboard.get_cost_attribution(
    dimension='team',
    time_range="30d"
)

# By project
project_costs = dashboard.get_cost_attribution(
    dimension='project',
    time_range="30d"
)

# By cost center
cc_costs = dashboard.get_cost_attribution(
    dimension='cost_center',
    time_range="30d"
)
```

---

##### `get_variance_analysis(time_range="30d")`

Get budget vs. actual variance analysis.

```python
variance = dashboard.get_variance_analysis(time_range="30d")

for category, data in variance.items():
    print(f"{category}:")
    print(f"  Budget: ${data['budget']:.2f}")
    print(f"  Actual: ${data['actual']:.2f}")
    print(f"  Variance: ${data['variance']:.2f}")
    print(f"  Variance %: {data['variance_pct']:.1f}%")
    print(f"  Status: {data['status']}")
```

---

##### `export_cost_data(format='csv', time_range="30d")`

Export detailed cost data.

```python
# Export to CSV
csv_data = dashboard.export_cost_data(format='csv', time_range="30d")
with open("cost_data.csv", "w") as f:
    f.write(csv_data)

# Export to Excel
excel_data = dashboard.export_cost_data(format='excel', time_range="30d")
with open("cost_data.xlsx", "wb") as f:
    f.write(excel_data)
```

**Formats:** `'csv'`, `'excel'`, `'json'`, `'parquet'`

---

## IAM System

Identity and access management for dashboards.

### Class: `IAMSystem`

**Location**: `openfinops.dashboard.iam_system`

```python
from openfinops.dashboard import IAMSystem

iam = IAMSystem()
```

#### Methods

##### `create_user(user_id, role, metadata=None)`

Create a new user with role.

```python
iam.create_user(
    user_id="analyst1@company.com",
    role="finance_analyst",
    metadata={
        "name": "Jane Doe",
        "department": "Finance",
        "cost_center": "CC-12345"
    }
)
```

**Roles:** `'cfo'`, `'coo'`, `'infrastructure_leader'`, `'finance_analyst'`, `'viewer'`

---

##### `check_permission(user_id, resource, action)`

Check if user has permission.

```python
has_access = iam.check_permission(
    user_id="analyst1@company.com",
    resource="cost_reports",
    action="read"
)

if has_access:
    report = dashboard.get_detailed_cost_report()
```

---

##### `get_user_permissions(user_id)`

Get all permissions for a user.

```python
permissions = iam.get_user_permissions("analyst1@company.com")

for resource, actions in permissions.items():
    print(f"{resource}: {', '.join(actions)}")
```

---

## Dashboard Router

Route users to appropriate dashboards.

### Class: `DashboardRouter`

**Location**: `openfinops.dashboard.dashboard_router`

```python
from openfinops.dashboard import DashboardRouter

router = DashboardRouter()
```

#### Methods

##### `get_dashboard_for_user(user_id)`

Get appropriate dashboard for user based on role.

```python
dashboard = router.get_dashboard_for_user("cfo@company.com")

# Returns CFODashboard, COODashboard, etc. based on role
summary = dashboard.get_financial_summary()
```

---

##### `register_custom_dashboard(role, dashboard_class)`

Register a custom dashboard for a role.

```python
class CustomCTODashboard:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_tech_metrics(self):
        # Custom implementation
        pass

router.register_custom_dashboard('cto', CustomCTODashboard)
```

---

## Complete Example

### Multi-Dashboard Application

```python
from openfinops.dashboard import (
    CFODashboard,
    COODashboard,
    InfrastructureLeaderDashboard,
    IAMSystem,
    DashboardRouter
)

# Initialize IAM
iam = IAMSystem()

# Create users
iam.create_user("cfo@company.com", role="cfo")
iam.create_user("coo@company.com", role="coo")
iam.create_user("infra@company.com", role="infrastructure_leader")

# Initialize router
router = DashboardRouter()

# Get user-specific dashboard
def get_user_dashboard(user_email):
    return router.get_dashboard_for_user(user_email)

# CFO View
cfo_dashboard = get_user_dashboard("cfo@company.com")
financial_summary = cfo_dashboard.get_financial_summary(time_range="30d")
roi_analysis = cfo_dashboard.get_roi_analysis()

print("=== CFO Dashboard ===")
print(f"Total Spend: ${financial_summary['total_spend']:.2f}")
print(f"Budget Utilization: {financial_summary['budget_utilization']:.1f}%")
print(f"Savings Opportunities: ${financial_summary['savings_opportunities']:.2f}")

# COO View
coo_dashboard = get_user_dashboard("coo@company.com")
operational_metrics = coo_dashboard.get_operational_metrics(time_range="24h")
efficiency = coo_dashboard.get_efficiency_metrics()

print("\n=== COO Dashboard ===")
print(f"System Uptime: {operational_metrics['uptime']:.2f}%")
print(f"Resource Utilization: {operational_metrics['resource_utilization']:.1f}%")
print(f"GPU Efficiency: {efficiency['gpu_efficiency']:.1f}%")

# Infrastructure Leader View
infra_dashboard = get_user_dashboard("infra@company.com")
overview = infra_dashboard.get_infrastructure_overview()
recommendations = infra_dashboard.get_optimization_recommendations()

print("\n=== Infrastructure Dashboard ===")
print(f"Total GPUs: {overview['total_gpus']}")
print(f"Avg Utilization: {overview['avg_utilization']:.1f}%")
print(f"\nOptimization Recommendations:")
for rec in recommendations[:3]:
    print(f"  - {rec['title']}: Save ${rec['estimated_savings']:.2f}/month")
```

## See Also

- [Observability API](observability-api.md) - Data collection
- [VizlyChart API](vizlychart-api.md) - Visualization
- [IAM Guide](../guides/security.md) - Security and access control
- [Tutorials](../tutorials/custom-dashboards.md) - Dashboard creation
