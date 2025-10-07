# IAM Configuration Usage Guide

## Overview

The OpenFinOps IAM system is now fully configurable through YAML configuration files and a command-line interface.

## Quick Start

### 1. List Available Roles and Personas

```bash
# List all configured roles
python src/openfinops/dashboard/iam_cli.py list-roles

# List all personas
python src/openfinops/dashboard/iam_cli.py list-personas
```

### 2. View Detailed Configuration

```bash
# View CFO role details
python src/openfinops/dashboard/iam_cli.py show-role cfo

# View CTO persona configuration
python src/openfinops/dashboard/iam_cli.py show-persona cto_persona
```

### 3. Create Users from Personas

```bash
# Create CFO user
python src/openfinops/dashboard/iam_cli.py create-user \
  --persona cfo_persona \
  --username john.doe \
  --email john.doe@company.com \
  --full-name "John Doe"

# Create CTO user
python src/openfinops/dashboard/iam_cli.py create-user \
  --persona cto_persona \
  --username jane.smith \
  --email jane.smith@company.com \
  --full-name "Jane Smith"
```

### 4. Validate Configuration

```bash
python src/openfinops/dashboard/iam_cli.py validate
```

## Available Personas

### Executive Personas
- **cfo_persona**: Chief Financial Officer - Full financial oversight
- **cto_persona**: Chief Technology Officer - Technical infrastructure leadership
- **coo_persona**: Chief Operating Officer - Operational excellence
- **ceo_persona**: Chief Executive Officer - Strategic leadership (all dashboard access)

### Management Personas
- **infrastructure_lead_persona**: Infrastructure management and optimization
- **finance_analyst_persona**: Detailed financial analysis and reporting
- **data_scientist_persona**: AI/ML model development and analysis

## Customization

### Adding Custom Roles

Create a YAML file (e.g., `custom_role.yaml`):

```yaml
custom_executive:
  display_name: "Custom Executive"
  description: "Custom executive role"
  data_access_level: RESTRICTED
  require_mfa: true
  session_timeout: 14400
  allowed_dashboards:
    - CFO_EXECUTIVE
    - CTO_TECHNICAL
  permissions:
    - name: view_all_dashboards
      resource_type: dashboard
      access_level: EXECUTIVE
```

Then add it:

```bash
python src/openfinops/dashboard/iam_cli.py add-role --config custom_role.yaml
```

### Adding Custom Personas

Create a YAML file (e.g., `custom_persona.yaml`):

```yaml
vp_finance_persona:
  roles:
    - cfo
    - finance_analyst
  department: Finance
  default_dashboard: CFO_EXECUTIVE
  notification_preferences:
    email: true
    slack: true
  custom_settings:
    cost_alert_threshold: 50000
```

Then add it:

```bash
python src/openfinops/dashboard/iam_cli.py add-persona --config custom_persona.yaml
```

### Export Configuration

```bash
python src/openfinops/dashboard/iam_cli.py export --output my_iam_config.yaml
```

## Configuration File Location

Default configuration: `src/openfinops/dashboard/iam_config.yaml`

Use custom configuration:

```bash
python src/openfinops/dashboard/iam_cli.py --config /path/to/custom_config.yaml list-roles
```

## Programmatic Usage

```python
from openfinops.dashboard.iam_config_loader import get_config_loader

# Load configuration
loader = get_config_loader()
loader.load_config()

# Get role configuration
cfo_config = loader.get_role_config('cfo')

# Get persona configuration
cfo_persona = loader.get_persona_config('cfo_persona')

# Create user from persona
user_config = loader.create_user_from_persona('cfo_persona', {
    'user_id': 'user-001',
    'username': 'john.doe',
    'email': 'john.doe@company.com',
    'full_name': 'John Doe'
})

# Validate configuration
errors = loader.validate_config()
if errors:
    print(f"Configuration errors: {errors}")
```

## Security Settings

Configure in `iam_config.yaml`:

```yaml
security_settings:
  session_timeout: 3600  # 1 hour default
  require_mfa_for_executives: true
  password_policy:
    min_length: 12
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
    require_special_chars: true
  max_failed_login_attempts: 5
  account_lockout_duration: 1800  # 30 minutes
```

## Data Classification Levels

- **PUBLIC**: Level 0 - Public information
- **INTERNAL**: Level 1 - Internal use only
- **CONFIDENTIAL**: Level 2 - Confidential business data
- **RESTRICTED**: Level 3 - Highly sensitive data (executive level)
