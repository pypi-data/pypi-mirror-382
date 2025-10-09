# IAM Quick Reference Card

## Common Commands

### View Roles and Personas

```bash
# List all roles
python src/openfinops/dashboard/iam_cli.py list-roles

# List all personas
python src/openfinops/dashboard/iam_cli.py list-personas

# View CFO role details
python src/openfinops/dashboard/iam_cli.py show-role cfo

# View CTO persona details
python src/openfinops/dashboard/iam_cli.py show-persona cto_persona
```

### Create Users

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
  --email jane.smith@company.com

# Create Infrastructure Leader
python src/openfinops/dashboard/iam_cli.py create-user \
  --persona infrastructure_lead_persona \
  --username bob.wilson \
  --email bob.wilson@company.com
```

### Configuration Management

```bash
# Validate configuration
python src/openfinops/dashboard/iam_cli.py validate

# Export configuration
python src/openfinops/dashboard/iam_cli.py export --output backup.yaml

# Use custom config
python src/openfinops/dashboard/iam_cli.py --config custom.yaml list-roles
```

### Add Custom Roles/Personas

```bash
# Add custom role
python src/openfinops/dashboard/iam_cli.py add-role --config my_role.yaml

# Add custom persona
python src/openfinops/dashboard/iam_cli.py add-persona --config my_persona.yaml
```

## Role Quick Reference

| Role | MFA | Access Level | Default Timeout |
|------|-----|--------------|-----------------|
| CFO | ✓ | RESTRICTED | 4 hours |
| CTO | ✓ | RESTRICTED | 4 hours |
| COO | ✓ | RESTRICTED | 4 hours |
| CEO | ✓ | RESTRICTED | 4 hours |
| Infrastructure Leader | - | CONFIDENTIAL | 8 hours |
| Finance Analyst | - | CONFIDENTIAL | 8 hours |
| Data Scientist | - | CONFIDENTIAL | 8 hours |
| Security Leader | ✓ | RESTRICTED | 4 hours |
| Operations Manager | - | INTERNAL | 8 hours |

## Persona Quick Reference

| Persona | Role | Department | Dashboard |
|---------|------|------------|-----------|
| cfo_persona | CFO | Finance | CFO_EXECUTIVE |
| cto_persona | CTO | Engineering | CTO_TECHNICAL |
| coo_persona | COO | Operations | COO_OPERATIONAL |
| ceo_persona | CEO | Executive | CEO_STRATEGIC |
| infrastructure_lead_persona | Infrastructure Leader | Engineering | INFRASTRUCTURE_LEADER |
| finance_analyst_persona | Finance Analyst | Finance | FINANCE_ANALYST |
| data_scientist_persona | Data Scientist | AI/ML | DATA_SCIENTIST |

## Programmatic Usage

```python
from openfinops.dashboard.iam_config_loader import get_config_loader
from openfinops.dashboard.iam_system import get_iam_manager

# Load configuration
loader = get_config_loader()
loader.load_config()

# Get role config
cfo_role = loader.get_role_config('cfo')

# Create user from persona
user_config = loader.create_user_from_persona('cfo_persona', {
    'user_id': 'user-001',
    'username': 'john.doe',
    'email': 'john.doe@company.com'
})

# Create user in system
iam = get_iam_manager()
user = iam.create_user(user_config)

# Check permissions
has_access = iam.check_permission(
    user_id='user-001',
    resource_type='dashboard',
    resource_id='CFO_EXECUTIVE',
    action='view'
)
```

## Configuration File Structure

```yaml
# Security settings
security_settings:
  session_timeout: 3600
  require_mfa_for_executives: true
  password_policy:
    min_length: 12

# Data classifications
data_classifications:
  PUBLIC: 0
  INTERNAL: 1
  CONFIDENTIAL: 2
  RESTRICTED: 3

# Roles
roles:
  custom_role:
    display_name: "Custom Role"
    data_access_level: CONFIDENTIAL
    require_mfa: false
    allowed_dashboards:
      - CUSTOM_DASHBOARD
    permissions:
      - name: view_dashboard
        resource_type: dashboard
        access_level: READ

# Personas
personas:
  custom_persona:
    roles:
      - custom_role
    department: Custom
    default_dashboard: CUSTOM_DASHBOARD
    notification_preferences:
      email: true
```

## Data Classification Levels

- **PUBLIC (0)**: Public information
- **INTERNAL (1)**: Internal use only  
- **CONFIDENTIAL (2)**: Confidential business data
- **RESTRICTED (3)**: Highly sensitive executive data

## Files

- **Config:** `src/openfinops/dashboard/iam_config.yaml`
- **Loader:** `src/openfinops/dashboard/iam_config_loader.py`
- **CLI:** `src/openfinops/dashboard/iam_cli.py`

## Support

See full documentation:
- [IAM Usage Guide](IAM_USAGE.md)
- [IAM System Overview](IAM_SYSTEM_OVERVIEW.md)
