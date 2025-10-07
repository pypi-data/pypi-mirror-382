# OpenFinOps Telemetry Agents

Comprehensive collection of telemetry agents for tracking costs across cloud providers, data platforms, and SaaS services.

## 📁 Available Agents

### Cloud Providers
- **AWS Telemetry Agent** (`aws_telemetry_agent.py`) - EC2, EKS, Lambda, RDS, S3 costs
- **Azure Telemetry Agent** (`azure_telemetry_agent.py`) - VMs, AKS, Functions, Storage costs
- **GCP Telemetry Agent** (`gcp_telemetry_agent.py`) - Compute Engine, GKE, Cloud Functions costs

### Data Platforms
- **Databricks Telemetry Agent** (`databricks_telemetry_agent.py`) - DBU tracking, cluster costs, job execution
- **Snowflake Telemetry Agent** (`snowflake_telemetry_agent.py`) - Credit consumption, warehouse costs, storage

### SaaS Services
- **SaaS Services Agent** (`saas_services_telemetry_agent.py`) - Multi-service monitoring:
  - MongoDB Atlas
  - Redis Cloud
  - GitHub Actions
  - DataDog
  - And more

### Generic
- **Generic Telemetry Agent** (`generic_telemetry_agent.py`) - Custom metrics, on-premise infrastructure

## 🚀 Quick Start

### 1. Databricks Cost Tracking

Track Databricks DBU consumption, cluster costs, and job execution metrics:

```bash
pip install databricks-sdk requests

python agents/databricks_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --databricks-host https://your-workspace.cloud.databricks.com \
  --databricks-token dapi*** \
  --interval 300
```

**Features:**
- Automatic DBU cost calculation by cluster type
- Job-level cost attribution
- SQL warehouse cost tracking
- Delta Live Tables monitoring
- Real-time cluster status

**Cost Calculation:**
- All-Purpose clusters: $0.40/DBU
- Jobs clusters: $0.15/DBU
- SQL Pro: $0.55/DBU
- Serverless SQL: $0.70/DBU

### 2. Snowflake Cost Tracking

Monitor Snowflake credit consumption, warehouse usage, and storage costs:

```bash
pip install snowflake-connector-python requests

# Set credentials
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password

python agents/snowflake_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --snowflake-account xy12345.us-east-1 \
  --snowflake-warehouse COMPUTE_WH \
  --edition enterprise \
  --interval 300
```

**Metrics Collected:**
- Warehouse credit consumption (compute + cloud services)
- Storage usage (database + failsafe)
- Query execution patterns
- User-level cost attribution
- Warehouse efficiency analysis

**Cost Models:**
- Standard Edition: $2/credit
- Enterprise Edition: $3/credit
- Business Critical: $4/credit
- Storage: $40/TB/month

### 3. MongoDB Atlas Monitoring

Track MongoDB Atlas cluster costs, storage, and performance:

```bash
python agents/saas_services_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --config mongodb_config.json
```

**Configuration** (`mongodb_config.json`):
```json
{
  "mongodb_atlas": {
    "enabled": true,
    "public_key": "your_public_key",
    "private_key": "your_private_key",
    "project_id": "your_project_id"
  }
}
```

**Metrics:**
- Cluster instance size and costs
- Replication factor
- Shard count
- Storage usage
- Regional deployment costs

### 4. Redis Cloud Tracking

Monitor Redis Cloud subscriptions and database costs:

```json
{
  "redis_cloud": {
    "enabled": true,
    "api_key": "your_api_key",
    "secret_key": "your_secret_key",
    "account_id": "your_account_id"
  }
}
```

### 5. GitHub Actions Minutes

Track GitHub Actions workflow minutes and costs:

```json
{
  "github_actions": {
    "enabled": true,
    "token": "ghp_your_token",
    "org_name": "your_org"
  }
}
```

**Cost Calculation:**
- Linux: $0.008/minute
- Windows: $0.016/minute
- macOS: $0.08/minute

### 6. DataDog Infrastructure Monitoring

Track DataDog host count and estimated costs:

```json
{
  "datadog": {
    "enabled": true,
    "api_key": "your_api_key",
    "app_key": "your_app_key"
  }
}
```

## 🔧 Agent Configuration

### Environment Variables

All agents support environment variables for sensitive credentials:

```bash
# Databricks
export DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi***

# Snowflake
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_ACCOUNT=xy12345.us-east-1

# MongoDB Atlas
export MONGODB_ATLAS_PUBLIC_KEY=your_key
export MONGODB_ATLAS_PRIVATE_KEY=your_key

# Redis Cloud
export REDIS_CLOUD_API_KEY=your_key
export REDIS_CLOUD_SECRET_KEY=your_key
```

### Collection Intervals

Recommended intervals based on service:

| Service | Recommended Interval | Reason |
|---------|---------------------|---------|
| Databricks | 5 minutes (300s) | Frequent cluster changes |
| Snowflake | 5 minutes (300s) | Real-time credit tracking |
| MongoDB Atlas | 15 minutes (900s) | Relatively stable |
| GitHub Actions | 1 hour (3600s) | Billing data updates hourly |
| DataDog | 1 hour (3600s) | Usage aggregated hourly |

## 📊 Cost Attribution

All agents support tagging and cost attribution:

### By Team/Department

```python
# Databricks clusters with team tags
cluster_tags = {
    "team": "data-engineering",
    "cost_center": "analytics",
    "environment": "production"
}

# Snowflake queries tagged by user/role
# Automatic attribution by USER_NAME and ROLE_NAME
```

### By Project

```python
# MongoDB Atlas clusters by project
project_id = "your_project_id"

# Databricks jobs by job_id and creator
job_attribution = {
    "job_id": "123",
    "creator": "user@company.com",
    "project": "ml-training"
}
```

## 🔒 Security Best Practices

### 1. Use IAM Roles (Cloud Agents)

```bash
# AWS - use IAM role instead of access keys
python agents/aws_telemetry_agent.py \
  --openfinops-endpoint http://localhost:8080 \
  --aws-region us-west-2
  # No --aws-access-key needed with IAM role
```

### 2. Least Privilege Access

**Databricks:**
```
Required permissions:
- clusters:list
- clusters:get
- jobs:list
- sql:list
```

**Snowflake:**
```sql
-- Create read-only role for telemetry
CREATE ROLE OPENFINOPS_READER;
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE OPENFINOPS_READER;
GRANT ROLE OPENFINOPS_READER TO USER telemetry_user;
```

### 3. Rotate Credentials

```bash
# Use short-lived tokens
# Databricks - generate token with 90-day expiration
# Snowflake - rotate passwords quarterly
# SaaS services - use OAuth when available
```

## 🐳 Docker Deployment

### Dockerfile for All Agents

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install requests boto3 azure-identity google-cloud-monitoring \
    databricks-sdk snowflake-connector-python

# Copy agents
COPY agents/ /app/agents/

# Run specific agent
CMD ["python", "agents/databricks_telemetry_agent.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  databricks-agent:
    build: .
    command: python agents/databricks_telemetry_agent.py --openfinops-endpoint http://openfinops:8080 --databricks-host ${DATABRICKS_HOST} --databricks-token ${DATABRICKS_TOKEN}
    environment:
      - DATABRICKS_HOST
      - DATABRICKS_TOKEN
    restart: always

  snowflake-agent:
    build: .
    command: python agents/snowflake_telemetry_agent.py --openfinops-endpoint http://openfinops:8080 --snowflake-account ${SNOWFLAKE_ACCOUNT}
    environment:
      - SNOWFLAKE_USER
      - SNOWFLAKE_PASSWORD
      - SNOWFLAKE_ACCOUNT
    restart: always

  saas-agent:
    build: .
    command: python agents/saas_services_telemetry_agent.py --openfinops-endpoint http://openfinops:8080 --config /app/config.json
    volumes:
      - ./saas_config.json:/app/config.json:ro
    restart: always
```

## ☸️ Kubernetes Deployment

### Databricks Agent Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: databricks-telemetry-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: databricks-agent
  template:
    metadata:
      labels:
        app: databricks-agent
    spec:
      containers:
      - name: agent
        image: openfinops/databricks-agent:latest
        env:
        - name: OPENFINOPS_ENDPOINT
          value: "http://openfinops-server:8080"
        - name: DATABRICKS_HOST
          valueFrom:
            secretKeyRef:
              name: databricks-creds
              key: host
        - name: DATABRICKS_TOKEN
          valueFrom:
            secretKeyRef:
              name: databricks-creds
              key: token
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
```

### Create Secrets

```bash
# Databricks
kubectl create secret generic databricks-creds \
  --from-literal=host=https://your-workspace.cloud.databricks.com \
  --from-literal=token=dapi***

# Snowflake
kubectl create secret generic snowflake-creds \
  --from-literal=user=your_user \
  --from-literal=password=your_password \
  --from-literal=account=xy12345.us-east-1
```

## 📈 Cost Analysis Examples

### Databricks Cost Breakdown

```python
from openfinops import ObservabilityHub

hub = ObservabilityHub()

# Get Databricks costs by cluster type
databricks_costs = hub.get_costs_by_category('databricks')
print(f"All-Purpose: ${databricks_costs['all_purpose']:.2f}")
print(f"Jobs: ${databricks_costs['jobs']:.2f}")
print(f"SQL: ${databricks_costs['sql']:.2f}")

# Get job-level attribution
job_costs = hub.get_databricks_job_costs(hours_lookback=24)
for job in job_costs:
    print(f"Job {job['job_id']}: ${job['cost']:.2f}")
```

### Snowflake Credit Analysis

```python
# Get Snowflake costs by warehouse
warehouse_costs = hub.get_snowflake_warehouse_costs(hours_lookback=24)
for warehouse in warehouse_costs:
    print(f"{warehouse['name']}: {warehouse['credits']:.2f} credits (${warehouse['cost']:.2f})")

# Storage analysis
storage = hub.get_snowflake_storage_metrics()
print(f"Total Storage: {storage['total_tb']:.4f} TB")
print(f"Monthly Cost: ${storage['monthly_cost']:.2f}")
```

### SaaS Services Summary

```python
# Get all SaaS costs
saas_costs = hub.get_saas_service_costs()
print(f"MongoDB Atlas: ${saas_costs['mongodb_atlas']:.2f}")
print(f"Redis Cloud: ${saas_costs['redis_cloud']:.2f}")
print(f"GitHub Actions: ${saas_costs['github_actions']:.2f}")
print(f"DataDog: ${saas_costs['datadog']:.2f}")
```

## 🔍 Troubleshooting

### Databricks Agent

**Issue:** Agent fails to connect
```bash
# Check connectivity
curl -H "Authorization: Bearer dapi***" \
  https://your-workspace.cloud.databricks.com/api/2.0/clusters/list

# Verify token permissions
# Token must have cluster:list, jobs:list permissions
```

### Snowflake Agent

**Issue:** Permission denied
```sql
-- Grant necessary permissions
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE TO ROLE YOUR_ROLE;

-- Verify access
USE ROLE YOUR_ROLE;
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY LIMIT 1;
```

### SaaS Services Agent

**Issue:** API rate limiting
```python
# Increase collection interval
--interval 7200  # 2 hours instead of 1 hour

# Or implement exponential backoff in config
```

## 📚 Additional Resources

- [Databricks Pricing](https://databricks.com/product/pricing)
- [Snowflake Pricing](https://www.snowflake.com/pricing/)
- [MongoDB Atlas Pricing](https://www.mongodb.com/pricing)
- [GitHub Actions Pricing](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)

## 🤝 Contributing

To add a new service agent:

1. Create new agent file following the pattern
2. Implement cost calculation logic
3. Add to cost categories in `cost_observatory.py`
4. Update this README
5. Add documentation to website

## 📄 License

Apache-2.0 License - See LICENSE file in project root.
