# SaaS Management API Reference

OpenFinOps SaaS Management module for tracking, optimizing, and managing SaaS application licenses and costs.

## Overview

The SaaS Management module provides comprehensive tools for:
- SaaS application discovery from billing and SSO data
- License management and optimization
- Usage tracking and reclamation
- Shadow IT detection and remediation

## Modules

- `openfinops.saas.saas_discovery` - Application discovery
- `openfinops.saas.license_manager` - License management
- `openfinops.saas.usage_tracker` - Usage tracking
- `openfinops.saas.shadow_it_detector` - Shadow IT detection

---

## SaaS Discovery API

### `SaaSDiscovery`

Discover and track SaaS applications across your organization.

#### Constructor

```python
from openfinops.saas import SaaSDiscovery

discovery = SaaSDiscovery()
```

#### Methods

##### `register_application(app: SaaSApplication) -> None`

Register a SaaS application manually.

```python
from openfinops.saas import SaaSApplication, ApplicationCategory

app = SaaSApplication(
    app_id="slack",
    name="Slack",
    vendor="Slack Technologies",
    category=ApplicationCategory.COLLABORATION,
    monthly_cost=15000.0,
    total_licenses=200,
    active_users=180
)

discovery.register_application(app)
```

---

##### `discover_from_billing(billing_data: List[Dict]) -> List[SaaSApplication]`

Discover applications from billing/expense data.

```python
billing_data = [
    {
        "vendor": "Slack",
        "amount": 15000,
        "date": "2025-01-01",
        "description": "Slack subscription"
    },
    {
        "vendor": "GitHub",
        "amount": 5000,
        "date": "2025-01-01",
        "description": "GitHub Enterprise"
    }
]

apps = discovery.discover_from_billing(billing_data)
for app in apps:
    print(f"{app.name}: ${app.monthly_cost}/month")
```

**Parameters:**
- `billing_data` - List of billing records with vendor, amount, date

**Returns:** List of discovered `SaaSApplication` objects

---

##### `discover_from_integrations(sso_data: Dict) -> List[SaaSApplication]`

Discover applications from SSO provider data.

```python
sso_data = {
    "provider": "okta",
    "applications": [
        {"name": "Slack", "users": 180},
        {"name": "GitHub", "users": 150}
    ]
}

apps = discovery.discover_from_integrations(sso_data)
```

**Parameters:**
- `sso_data` - SSO integration data (Okta, Azure AD, etc.)

**Returns:** List of discovered applications

---

##### `list_applications(category: Optional[ApplicationCategory] = None) -> List[SaaSApplication]`

List all discovered applications, optionally filtered by category.

```python
# All applications
all_apps = discovery.list_applications()

# Collaboration tools only
collab_apps = discovery.list_applications(
    category=ApplicationCategory.COLLABORATION
)
```

**Returns:** List of applications

---

##### `get_application(app_id: str) -> Optional[SaaSApplication]`

Get application by ID.

```python
app = discovery.get_application("slack")
if app:
    print(f"Utilization: {app.get_utilization_rate():.1f}%")
```

**Returns:** Application or None

---

##### `get_total_spend() -> float`

Get total monthly SaaS spending.

```python
total = discovery.get_total_spend()
print(f"Total SaaS spend: ${total:,.2f}/month")
```

**Returns:** Total monthly cost

---

##### `get_total_wasted_spend() -> float`

Calculate wasted spending on unused licenses.

```python
wasted = discovery.get_total_wasted_spend()
savings_opportunity = wasted * 12  # Annual savings
print(f"Potential annual savings: ${savings_opportunity:,.2f}")
```

**Returns:** Monthly wasted spend

---

##### `get_category_breakdown() -> Dict[str, float]`

Get spending breakdown by application category.

```python
breakdown = discovery.get_category_breakdown()
for category, cost in breakdown.items():
    print(f"{category}: ${cost:,.2f}/month")
```

**Returns:** Dictionary of category to cost

---

##### `get_optimization_opportunities() -> List[Dict]`

Get optimization recommendations.

```python
opportunities = discovery.get_optimization_opportunities()
for opp in opportunities:
    print(f"{opp['type']}: Save ${opp['savings']:.2f}/month")
    print(f"  Action: {opp['description']}")
```

**Returns:** List of optimization opportunities with:
- `type` - Opportunity type
- `app_id` - Application ID
- `description` - Action description
- `savings` - Monthly savings potential

---

### `SaaSApplication`

Represents a SaaS application.

#### Attributes

```python
@dataclass
class SaaSApplication:
    app_id: str
    name: str
    vendor: str
    category: ApplicationCategory
    monthly_cost: float
    total_licenses: int = 0
    active_users: int = 0
    contract_start: Optional[datetime] = None
    contract_end: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    tags: Dict[str, str] = field(default_factory=dict)
```

#### Methods

##### `get_utilization_rate() -> float`

Calculate license utilization rate.

```python
app = SaaSApplication(...)
utilization = app.get_utilization_rate()
print(f"Utilization: {utilization:.1f}%")
```

**Returns:** Utilization percentage (0-100)

---

##### `get_cost_per_user() -> float`

Calculate cost per active user.

```python
cost_per_user = app.get_cost_per_user()
print(f"Cost per user: ${cost_per_user:.2f}/month")
```

**Returns:** Monthly cost per active user

---

##### `get_wasted_spend() -> float`

Calculate wasted spending on unused licenses.

```python
wasted = app.get_wasted_spend()
print(f"Wasted spend: ${wasted:.2f}/month")
```

**Returns:** Monthly wasted cost

---

### `ApplicationCategory`

Application category enumeration.

```python
class ApplicationCategory(Enum):
    COLLABORATION = "collaboration"      # Slack, Teams, Zoom
    DEVELOPMENT = "development"          # GitHub, GitLab, Jira
    PRODUCTIVITY = "productivity"        # Google Workspace, Office 365
    SECURITY = "security"               # Okta, 1Password, Snyk
    ANALYTICS = "analytics"             # Tableau, Looker, DataDog
    MARKETING = "marketing"             # HubSpot, Mailchimp, Salesforce
    INFRASTRUCTURE = "infrastructure"   # AWS, Azure, GCP
    OTHER = "other"
```

---

## License Management API

### `LicenseManager`

Manage SaaS licenses and optimize allocation.

#### Constructor

```python
from openfinops.saas import LicenseManager

license_mgr = LicenseManager()
```

#### Methods

##### `add_license(app_id: str, license_type: LicenseType, total_seats: int, cost_per_seat: float, **kwargs) -> str`

Add a license pool for an application.

```python
from openfinops.saas import LicenseType

license_id = license_mgr.add_license(
    app_id="slack",
    license_type=LicenseType.SUBSCRIPTION,
    total_seats=200,
    cost_per_seat=15.00,
    billing_cycle="monthly",
    renewal_date=datetime(2025, 12, 31)
)
```

**Parameters:**
- `app_id` - Application identifier
- `license_type` - Type of license
- `total_seats` - Total number of seats/licenses
- `cost_per_seat` - Cost per seat per billing cycle
- `kwargs` - Additional metadata

**Returns:** License ID

---

##### `get_license(license_id: str) -> Optional[License]`

Get license by ID.

```python
license = license_mgr.get_license("slack-licenses")
print(f"Utilization: {license.get_utilization_rate():.1f}%")
```

---

##### `assign_license(license_id: str, user_id: str) -> bool`

Assign a license to a user.

```python
success = license_mgr.assign_license("slack-licenses", "user123")
if success:
    print("License assigned successfully")
```

**Returns:** True if assignment successful

---

##### `unassign_license(license_id: str, user_id: str) -> bool`

Unassign a license from a user.

```python
success = license_mgr.unassign_license("slack-licenses", "user123")
```

**Returns:** True if unassignment successful

---

##### `get_expiring_licenses(days: int = 30) -> List[License]`

Get licenses expiring within specified days.

```python
expiring = license_mgr.get_expiring_licenses(days=30)
for license in expiring:
    days_left = (license.renewal_date - datetime.now()).days
    print(f"{license.app_id}: Expires in {days_left} days")
```

**Returns:** List of expiring licenses

---

##### `get_optimization_recommendations() -> List[Dict]`

Get license optimization recommendations.

```python
recommendations = license_mgr.get_optimization_recommendations()
for rec in recommendations:
    print(f"{rec['type']}: {rec['description']}")
    print(f"  Potential savings: ${rec['savings']:.2f}/month")
```

**Returns:** List of recommendations with:
- `type` - Recommendation type (reduce_licenses, reclaim_unused, etc.)
- `license_id` - License ID
- `description` - Recommendation description
- `savings` - Estimated monthly savings

---

##### `get_license_metrics() -> Dict[str, Any]`

Get comprehensive license metrics.

```python
metrics = license_mgr.get_license_metrics()
print(f"Total licenses: {metrics['total_licenses']}")
print(f"Assigned: {metrics['assigned_licenses']}")
print(f"Available: {metrics['available_licenses']}")
print(f"Utilization: {metrics['utilization_rate']:.1f}%")
print(f"Total cost: ${metrics['total_monthly_cost']:,.2f}/month")
```

**Returns:** Dictionary with license metrics

---

##### `optimize_allocation(app_id: str) -> Dict[str, Any]`

Optimize license allocation for an application.

```python
result = license_mgr.optimize_allocation("slack")
print(f"Current seats: {result['current_seats']}")
print(f"Recommended seats: {result['recommended_seats']}")
print(f"Potential savings: ${result['monthly_savings']:.2f}/month")
```

**Returns:** Optimization analysis

---

### `License`

Represents a license pool.

#### Attributes

```python
@dataclass
class License:
    license_id: str
    app_id: str
    license_type: LicenseType
    total_seats: int
    assigned_seats: int = 0
    cost_per_seat: float = 0.0
    billing_cycle: str = "monthly"
    renewal_date: Optional[datetime] = None
    assigned_users: Set[str] = field(default_factory=set)
```

#### Methods

##### `get_utilization_rate() -> float`

```python
utilization = license.get_utilization_rate()
```

**Returns:** Utilization percentage

---

##### `get_total_cost() -> float`

```python
total_cost = license.get_total_cost()
```

**Returns:** Total monthly/annual cost

---

##### `get_wasted_cost() -> float`

```python
wasted = license.get_wasted_cost()
```

**Returns:** Cost of unused licenses

---

##### `get_status() -> LicenseStatus`

```python
status = license.get_status()
if status == LicenseStatus.OVERUTILIZED:
    print("Need more licenses!")
```

**Returns:** License status (AVAILABLE, FULL, OVERUTILIZED, EXPIRING)

---

### `LicenseType`

License type enumeration.

```python
class LicenseType(Enum):
    PERPETUAL = "perpetual"              # One-time purchase
    SUBSCRIPTION = "subscription"        # Recurring subscription
    USAGE_BASED = "usage_based"         # Pay-per-use
    CONCURRENT = "concurrent"            # Concurrent user licenses
    NAMED_USER = "named_user"           # Specific user assignments
    FREEMIUM = "freemium"               # Free tier with limits
```

---

## Usage Tracking API

### `UsageTracker`

Track and analyze SaaS application usage.

#### Constructor

```python
from openfinops.saas import UsageTracker

tracker = UsageTracker()
```

#### Methods

##### `record_login(user_id: str, app_id: str, timestamp: Optional[datetime] = None) -> None`

Record user login to application.

```python
tracker.record_login("user123", "slack")
```

---

##### `record_session(user_id: str, app_id: str, duration_seconds: int, timestamp: Optional[datetime] = None) -> None`

Record usage session.

```python
tracker.record_session("user123", "slack", duration_seconds=3600)
```

---

##### `get_app_users(app_id: str) -> List[UserActivity]`

Get all users of an application.

```python
users = tracker.get_app_users("slack")
for user in users:
    print(f"{user.user_id}: {user.get_activity_level()}")
```

---

##### `get_inactive_users(app_id: str, days: int = 30) -> List[UserActivity]`

Get users inactive for specified days.

```python
inactive = tracker.get_inactive_users("slack", days=30)
print(f"Found {len(inactive)} inactive users")
```

---

##### `get_usage_summary(app_id: str) -> Dict[str, Any]`

Get usage summary for application.

```python
summary = tracker.get_usage_summary("slack")
print(f"Total users: {summary['total_users']}")
print(f"Active (7d): {summary['active_7d']}")
print(f"Active (30d): {summary['active_30d']}")
print(f"Never used: {summary['never_used']}")
```

---

##### `get_reclamation_candidates(app_id: str) -> List[Dict]`

Get candidates for license reclamation.

```python
candidates = tracker.get_reclamation_candidates("slack")
for candidate in candidates:
    print(f"User: {candidate['user_id']}")
    print(f"  Last login: {candidate['last_login']}")
    print(f"  Activity level: {candidate['activity_level']}")
    print(f"  Recommendation: {candidate['recommendation']}")
```

---

##### `get_engagement_trends(app_id: str) -> Dict[str, Any]`

Analyze engagement trends.

```python
trends = tracker.get_engagement_trends("slack")
print(f"Engagement score: {trends['engagement_score']}")
print(f"Trend: {trends['trend']}")  # increasing, stable, decreasing
```

---

### `UserActivity`

User activity data.

#### Attributes

```python
@dataclass
class UserActivity:
    user_id: str
    app_id: str
    first_login: Optional[datetime] = None
    last_login: Optional[datetime] = None
    total_logins: int = 0
    total_session_time: int = 0  # seconds
```

#### Methods

##### `get_activity_level() -> ActivityLevel`

```python
activity = user_activity.get_activity_level()
if activity == ActivityLevel.NEVER_USED:
    print("License can be reclaimed")
```

**Returns:** Activity level enum value

---

##### `days_since_last_login() -> Optional[int]`

```python
days = user_activity.days_since_last_login()
if days and days > 90:
    print("User inactive for 90+ days")
```

**Returns:** Days since last login or None

---

### `ActivityLevel`

User activity level enumeration.

```python
class ActivityLevel(Enum):
    ACTIVE = "active"              # Used within 7 days
    OCCASIONAL = "occasional"      # Used within 30 days
    INACTIVE = "inactive"          # Used within 90 days
    NEVER_USED = "never_used"      # Never used
```

---

## Shadow IT Detection API

### `ShadowITDetector`

Detect and manage unapproved SaaS applications.

#### Constructor

```python
from openfinops.saas import ShadowITDetector

detector = ShadowITDetector()
```

#### Methods

##### `add_approved_vendor(vendor: str) -> None`

Add vendor to approved list.

```python
detector.add_approved_vendor("Slack")
detector.add_approved_vendor("GitHub")
```

---

##### `detect_from_expenses(expense_data: List[Dict]) -> List[ShadowITApplication]`

Detect shadow IT from expense reports.

```python
expense_data = [
    {"vendor": "Unknown SaaS Tool", "amount": 500, "user": "user123"},
    {"vendor": "Unapproved Service", "amount": 200, "user": "user456"}
]

shadow_apps = detector.detect_from_expenses(expense_data)
for app in shadow_apps:
    print(f"Found: {app.name}")
    print(f"  Risk: {app.risk_level}")
    print(f"  Users: {len(app.users)}")
```

---

##### `detect_from_network(network_data: List[Dict]) -> List[ShadowITApplication]`

Detect shadow IT from network traffic analysis.

```python
network_data = [
    {"domain": "unauthorized-service.com", "user": "user123", "bytes": 1000000}
]

shadow_apps = detector.detect_from_network(network_data)
```

---

##### `list_shadow_apps(risk_level: Optional[RiskLevel] = None) -> List[ShadowITApplication]`

List detected shadow IT applications.

```python
# All shadow IT
all_shadow = detector.list_shadow_apps()

# Critical risk only
critical = detector.list_shadow_apps(risk_level=RiskLevel.CRITICAL)
```

---

##### `get_shadow_it_summary() -> Dict[str, Any]`

Get shadow IT summary and statistics.

```python
summary = detector.get_shadow_it_summary()
print(f"Total shadow apps: {summary['total_shadow_apps']}")
print(f"Total users: {summary['total_users']}")
print(f"Monthly cost: ${summary['total_monthly_cost']:,.2f}")
print(f"Risk breakdown: {summary['risk_breakdown']}")
```

---

##### `get_remediation_plan() -> List[Dict]`

Get remediation recommendations.

```python
plan = detector.get_remediation_plan()
for step in plan:
    print(f"Priority: {step['priority']}")
    print(f"App: {step['app_name']}")
    print(f"Action: {step['action']}")
    print(f"Risk: {step['risk_level']}")
```

---

### `ShadowITApplication`

Shadow IT application data.

#### Attributes

```python
@dataclass
class ShadowITApplication:
    name: str
    vendor: str
    monthly_cost: float
    users: Set[str]
    first_detected: datetime
    risk_level: RiskLevel
    data_sensitivity: str = "unknown"
    compliance_concerns: List[str] = field(default_factory=list)
```

---

### `RiskLevel`

Risk level enumeration.

```python
class RiskLevel(Enum):
    CRITICAL = "critical"      # Immediate action required
    HIGH = "high"             # Action required soon
    MEDIUM = "medium"         # Monitor and evaluate
    LOW = "low"              # Low priority
```

---

## Complete Workflow Example

```python
from openfinops.saas import (
    SaaSDiscovery,
    LicenseManager,
    UsageTracker,
    ShadowITDetector,
    ApplicationCategory,
    LicenseType
)
from datetime import datetime, timedelta

# 1. Discover SaaS applications
discovery = SaaSDiscovery()

billing_data = [
    {"vendor": "Slack", "amount": 15000, "date": "2025-01"},
    {"vendor": "GitHub", "amount": 5000, "date": "2025-01"}
]

apps = discovery.discover_from_billing(billing_data)
print(f"Discovered {len(apps)} applications")

# 2. Set up license management
license_mgr = LicenseManager()

slack_license = license_mgr.add_license(
    app_id="slack",
    license_type=LicenseType.SUBSCRIPTION,
    total_seats=200,
    cost_per_seat=15.00,
    renewal_date=datetime(2025, 12, 31)
)

# 3. Track usage
tracker = UsageTracker()
tracker.record_login("user123", "slack")

# 4. Get optimization recommendations
optimization_recs = license_mgr.get_optimization_recommendations()
for rec in optimization_recs:
    print(f"{rec['type']}: Save ${rec['savings']:.2f}/month")

# 5. Check for inactive users
inactive_users = tracker.get_inactive_users("slack", days=90)
print(f"Found {len(inactive_users)} inactive users")

# 6. Detect shadow IT
detector = ShadowITDetector()
detector.add_approved_vendor("Slack")
detector.add_approved_vendor("GitHub")

expense_data = [
    {"vendor": "Unknown SaaS Tool", "amount": 500, "user": "user456"}
]

shadow_apps = detector.detect_from_expenses(expense_data)
if shadow_apps:
    remediation = detector.get_remediation_plan()
    print(f"Shadow IT detected: {len(shadow_apps)} applications")
    print(f"Remediation steps: {len(remediation)}")

# 7. Generate comprehensive report
total_spend = discovery.get_total_spend()
wasted_spend = discovery.get_total_wasted_spend()
potential_savings = wasted_spend * 12

print(f"\n=== SaaS Management Summary ===")
print(f"Total monthly spend: ${total_spend:,.2f}")
print(f"Wasted spend: ${wasted_spend:,.2f}/month")
print(f"Potential annual savings: ${potential_savings:,.2f}")
```

---

## See Also

- [FinOps-as-Code API](iac-api.md)
- [Multi-Cloud API](multicloud-api.md)
- [Observability API](observability-api.md)
