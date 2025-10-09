# OpenFinOps IAM Configuration System

## Summary

The OpenFinOps IAM (Identity and Access Management) system is now fully configurable through YAML files and a command-line interface. This allows organizations to customize roles, permissions, and user personas to match their specific organizational structure.

## Architecture

### Components

1. **Configuration File** (`src/openfinops/dashboard/iam_config.yaml`)
   - Central YAML configuration defining all roles and personas
   - Security settings (MFA, password policies, session timeouts)
   - Data classification levels (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)
   - Dashboard access permissions

2. **Configuration Loader** (`src/openfinops/dashboard/iam_config_loader.py`)
   - Python API for loading and managing configurations
   - Programmatic access to roles and personas
   - User creation from persona templates
   - Configuration validation

3. **CLI Tool** (`src/openfinops/dashboard/iam_cli.py`)
   - Command-line interface for IAM management
   - Role and persona management
   - User creation and configuration
   - Configuration import/export

## Pre-configured Roles

### Executive Roles (C-Level)

| Role | Display Name | Access Level | MFA Required | Session Timeout |
|------|-------------|--------------|--------------|-----------------|
| `cfo` | Chief Financial Officer | RESTRICTED | Yes | 4 hours |
| `cto` | Chief Technology Officer | RESTRICTED | Yes | 4 hours |
| `coo` | Chief Operating Officer | RESTRICTED | Yes | 4 hours |
| `ceo` | Chief Executive Officer | RESTRICTED | Yes | 4 hours |

**CFO Permissions:**
- View financial dashboards (CFO_EXECUTIVE, CEO_STRATEGIC)
- View and approve budgets
- Access financial forecasts
- Export financial reports
- View audit trails and compliance reports

**CTO Permissions:**
- View technical dashboards (CTO_TECHNICAL, CEO_STRATEGIC)
- View infrastructure metrics
- Manage technical resources
- View security posture
- Manage cloud resources
- View AI model performance

**COO Permissions:**
- View operational dashboards (COO_OPERATIONAL, CEO_STRATEGIC)
- View operational and efficiency metrics
- Approve operational changes
- View team performance

**CEO Permissions:**
- Access ALL dashboards
- View all data across organization
- Approve strategic initiatives

### Management Roles

| Role | Display Name | Access Level | MFA Required | Session Timeout |
|------|-------------|--------------|--------------|-----------------|
| `infrastructure_leader` | Infrastructure Leader | CONFIDENTIAL | No | 8 hours |
| `finance_analyst` | Finance Analyst | CONFIDENTIAL | No | 8 hours |
| `data_scientist` | Data Scientist | CONFIDENTIAL | No | 8 hours |
| `security_leader` | Security Leader | RESTRICTED | Yes | 4 hours |
| `operations_manager` | Operations Manager | INTERNAL | No | 8 hours |

## Pre-configured Personas

Personas are templates for creating users with pre-defined roles and settings:

### Executive Personas

**cfo_persona**
- Role: CFO
- Department: Finance
- Default Dashboard: CFO_EXECUTIVE
- Notifications: Email + Slack
- Custom Settings:
  - Cost alert threshold: $10,000
  - Budget variance threshold: 5%

**cto_persona**
- Role: CTO
- Department: Engineering
- Default Dashboard: CTO_TECHNICAL
- Notifications: Email + Slack + PagerDuty
- Custom Settings:
  - Infrastructure alert priority: High
  - Performance monitoring: Enabled

**coo_persona**
- Role: COO
- Department: Operations
- Default Dashboard: COO_OPERATIONAL
- Notifications: Email + Slack

**ceo_persona**
- Role: CEO
- Department: Executive
- Default Dashboard: CEO_STRATEGIC
- Notifications: Email + Daily Executive Summary

### Management Personas

**infrastructure_lead_persona**
- Role: Infrastructure Leader
- Department: Engineering
- Default Dashboard: INFRASTRUCTURE_LEADER
- Notifications: Email + Slack + PagerDuty

**finance_analyst_persona**
- Role: Finance Analyst
- Department: Finance
- Default Dashboard: FINANCE_ANALYST
- Notifications: Email

**data_scientist_persona**
- Role: Data Scientist
- Department: AI/ML
- Default Dashboard: DATA_SCIENTIST
- Notifications: Email + Slack

## Quick Start Examples

### Create a CFO User

```bash
python src/openfinops/dashboard/iam_cli.py create-user \
  --persona cfo_persona \
  --username sarah.johnson \
  --email sarah.johnson@company.com \
  --full-name "Sarah Johnson"
```

### Create a CTO User

```bash
python src/openfinops/dashboard/iam_cli.py create-user \
  --persona cto_persona \
  --username mike.chen \
  --email mike.chen@company.com \
  --full-name "Mike Chen"
```

### List All Available Roles

```bash
python src/openfinops/dashboard/iam_cli.py list-roles
```

### View CFO Role Details

```bash
python src/openfinops/dashboard/iam_cli.py show-role cfo --format yaml
```

### Validate Configuration

```bash
python src/openfinops/dashboard/iam_cli.py validate
```

## Customization

### Add Custom Role

1. Create `custom_role.yaml`:

```yaml
vp_engineering:
  display_name: "VP of Engineering"
  description: "Engineering leadership role"
  data_access_level: RESTRICTED
  require_mfa: true
  session_timeout: 14400
  allowed_dashboards:
    - CTO_TECHNICAL
    - INFRASTRUCTURE_LEADER
  permissions:
    - name: view_technical_dashboards
      resource_type: dashboard
      access_level: EXECUTIVE
    - name: manage_infrastructure
      resource_type: infrastructure
      access_level: WRITE
```

2. Add the role:

```bash
python src/openfinops/dashboard/iam_cli.py add-role --config custom_role.yaml
```

### Add Custom Persona

1. Create `custom_persona.yaml`:

```yaml
vp_engineering_persona:
  roles:
    - vp_engineering
    - infrastructure_leader
  department: Engineering
  default_dashboard: CTO_TECHNICAL
  notification_preferences:
    email: true
    slack: true
    pagerduty: true
  custom_settings:
    infrastructure_alert_priority: critical
    auto_scaling_enabled: true
```

2. Add the persona:

```bash
python src/openfinops/dashboard/iam_cli.py add-persona --config custom_persona.yaml
```

## Security Features

### Password Policy

```yaml
password_policy:
  min_length: 12
  require_uppercase: true
  require_lowercase: true
  require_numbers: true
  require_special_chars: true
```

### Account Lockout

- Maximum failed login attempts: 5
- Lockout duration: 30 minutes

### Multi-Factor Authentication (MFA)

- Required for all executive roles (CFO, CTO, COO, CEO)
- Required for Security Leader role
- Optional for management roles

### Session Management

- Executive roles: 4-hour sessions
- Management roles: 8-hour sessions
- Configurable per role

## Data Classification

| Level | Name | Access |
|-------|------|--------|
| 0 | PUBLIC | Public information |
| 1 | INTERNAL | Internal use only |
| 2 | CONFIDENTIAL | Confidential business data |
| 3 | RESTRICTED | Highly sensitive (executive level) |

## Dashboard Access

| Dashboard Type | CFO | CTO | COO | CEO | Infra Leader | Finance Analyst |
|---------------|-----|-----|-----|-----|--------------|-----------------|
| CFO_EXECUTIVE | ✓ | | | ✓ | | ✓ |
| CTO_TECHNICAL | | ✓ | | ✓ | ✓ | |
| COO_OPERATIONAL | | | ✓ | ✓ | | |
| CEO_STRATEGIC | ✓ | ✓ | ✓ | ✓ | | |
| INFRASTRUCTURE_LEADER | | | | | ✓ | |
| FINANCE_ANALYST | | | | | | ✓ |

## Programmatic API

```python
from openfinops.dashboard.iam_config_loader import get_config_loader
from openfinops.dashboard.iam_system import get_iam_manager

# Load configuration
loader = get_config_loader()
config = loader.load_config()

# Create user from persona
user_config = loader.create_user_from_persona('cfo_persona', {
    'user_id': 'user-001',
    'username': 'john.doe',
    'email': 'john.doe@company.com',
    'full_name': 'John Doe'
})

# Create user in IAM system
iam = get_iam_manager()
user = iam.create_user(user_config)

# Check permissions
can_access = iam.check_permission(
    user_id='user-001',
    resource_type='dashboard',
    resource_id='CFO_EXECUTIVE',
    action='view'
)
```

## Testing

All IAM components are fully tested:

```bash
python -m pytest tests/ -v
```

**Test Coverage:**
- ✅ 73/73 tests passing (100%)
- ✅ Dashboard IAM integration tests
- ✅ Role and persona configuration
- ✅ Permission validation
- ✅ User creation from personas

## Configuration File Location

- **Default:** `src/openfinops/dashboard/iam_config.yaml`
- **Custom:** Use `--config` flag with CLI commands

## Documentation

- **Usage Guide:** [IAM_USAGE.md](IAM_USAGE.md)
- **This Overview:** IAM_SYSTEM_OVERVIEW.md

## Benefits

✅ **Flexibility:** Customize roles and permissions for your organization
✅ **Security:** MFA, password policies, session management
✅ **Simplicity:** Create users from persona templates
✅ **Validation:** Built-in configuration validation
✅ **CLI & API:** Both command-line and programmatic access
✅ **Tested:** 100% test coverage

## Next Steps

1. Review the default configuration in `iam_config.yaml`
2. Customize roles and personas for your organization
3. Create users using the CLI or programmatic API
4. Integrate with your existing authentication system
5. Configure notification preferences
6. Set up custom dashboards
