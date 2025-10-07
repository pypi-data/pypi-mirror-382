# Telemetry Agents API Reference

Complete API reference for OpenFinOps multi-cloud telemetry agents.

## Overview

OpenFinOps provides telemetry agents for automatically collecting metrics and costs from cloud providers:
- **AWS Telemetry Agent**: Amazon Web Services (EC2, EKS, Lambda, RDS, S3)
- **Azure Telemetry Agent**: Microsoft Azure (VMs, AKS, Functions, SQL, Storage)
- **GCP Telemetry Agent**: Google Cloud Platform (Compute, GKE, Functions, SQL, Storage)
- **Generic Telemetry Agent**: Custom data sources and on-premises infrastructure

**Key Concept**: Agents run as **separate processes** that automatically discover resources, collect metrics, calculate costs, and send data to your OpenFinOps server.

## Table of Contents

- [AWS Telemetry Agent](#aws-telemetry-agent)
- [Azure Telemetry Agent](#azure-telemetry-agent)
- [GCP Telemetry Agent](#gcp-telemetry-agent)
- [Generic Telemetry Agent](#generic-telemetry-agent)
- [Deployment Guide](#deployment-guide)

---

## AWS Telemetry Agent

Automatically collect metrics and costs from AWS.

### Class: `AWSTelemetryAgent`

**Location**: `agents.aws_telemetry_agent`

```python
from agents.aws_telemetry_agent import AWSTelemetryAgent

agent = AWSTelemetryAgent(
    openfinops_endpoint="http://localhost:8080",
    aws_region="us-west-2"
)
```

#### Constructor Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `openfinops_endpoint` | str | No | OpenFinOps server URL (default: http://localhost:8080) |
| `server_url` | str | No | Alias for openfinops_endpoint |
| `aws_region` | str | No | AWS region (default: us-east-1) |
| `region` | str | No | Alias for aws_region |
| `agent_id` | str | No | Agent identifier (auto-generated if not provided) |

**Authentication**: Uses boto3 default credential chain (environment variables, AWS config, IAM role, etc.)

#### Methods

##### `register_agent()`

Register the agent with the OpenFinOps server.

```python
if agent.register_agent():
    print("✓ Agent registered successfully")
else:
    print("✗ Registration failed")
```

**Returns:** `bool` - Registration success

---

##### `collect_telemetry_data()`

Collect telemetry data from AWS (one-time collection).

```python
data = agent.collect_telemetry_data()

print(f"Collected from {len(data['services'])} services")
print(f"Total EC2 instances: {data['services']['ec2']['total_instances']}")
print(f"Total hourly cost: ${data['summary']['total_hourly_cost']:.2f}")
```

**Returns:** `dict` - Telemetry data including:
- EC2 instances with CPU usage and costs
- EKS clusters and node groups
- Lambda functions and invocations
- RDS databases
- S3 buckets and storage costs

---

##### `send_telemetry_data(data)`

Send telemetry data to OpenFinOps server.

```python
success = agent.send_telemetry_data(data)
```

**Parameters:**
- `data` (dict): Telemetry data to send

**Returns:** `bool` - Send success

---

##### `run_once()`

Run one complete telemetry collection cycle.

```python
# Collect and send data once
if agent.run_once():
    print("✓ Telemetry sent successfully")
```

**Returns:** `bool` - Success status

---

##### `run_continuous(interval_seconds=300)`

Run continuous telemetry collection.

```python
# Collect and send every 5 minutes
agent.run_continuous(interval_seconds=300)

# This blocks and runs forever
# Press Ctrl+C to stop
```

**Parameters:**
- `interval_seconds` (int): Collection interval in seconds (default: 300)

---

### What the AWS Agent Collects

The agent automatically discovers and collects:

**EC2 Instances:**
- Instance ID, type, state
- CPU utilization (from CloudWatch)
- Memory usage (if CloudWatch agent installed)
- Network I/O
- **Hourly cost** (calculated from instance type)
- Tags (for cost attribution)

**EKS Clusters:**
- Cluster name, status, version
- Node groups and scaling config
- Node instance types
- **Cluster costs** (control plane + nodes)

**Lambda Functions:**
- Function name, runtime, memory
- Invocation count
- Average duration
- **Calculated costs** (from invocations × duration × memory)

**RDS Databases:**
- Instance identifier, class, engine
- CPU, memory, connections
- **Hourly cost**

**S3 Buckets:**
- Bucket name, region
- Storage size, object count
- **Monthly storage cost**

---

## Azure Telemetry Agent

Automatically collect metrics and costs from Azure.

### Class: `AzureTelemetryAgent`

**Location**: `agents.azure_telemetry_agent`

```python
from agents.azure_telemetry_agent import AzureTelemetryAgent

agent = AzureTelemetryAgent(
    openfinops_endpoint="http://localhost:8080",
    subscription_id="your-subscription-id",
    resource_group="ml-resources"  # Optional
)
```

#### Constructor Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `openfinops_endpoint` | str | Yes | OpenFinOps server URL |
| `subscription_id` | str | No | Azure subscription ID (or from AZURE_SUBSCRIPTION_ID env var) |
| `resource_group` | str | No | Limit collection to specific resource group |

**Authentication**: Uses Azure DefaultAzureCredential (environment variables, managed identity, Azure CLI, etc.)

#### Methods

Same pattern as AWS agent:
- `register_agent()`
- `collect_telemetry_data()`
- `send_telemetry_data(data)`
- `run_once()`
- `run_continuous(interval_seconds=300)`

### What the Azure Agent Collects

- **Virtual Machines**: CPU, memory, disk, network, costs
- **AKS Clusters**: Node pools, pod counts, costs
- **Functions**: Invocations, duration, costs
- **SQL Databases**: DTU usage, storage, costs
- **Storage Accounts**: Blob storage size, costs

---

## GCP Telemetry Agent

Automatically collect metrics and costs from Google Cloud.

### Class: `GCPTelemetryAgent`

**Location**: `agents.gcp_telemetry_agent`

```python
from agents.gcp_telemetry_agent import GCPTelemetryAgent

agent = GCPTelemetryAgent(
    openfinops_endpoint="http://localhost:8080",
    project_id="your-project-id",
    region="us-central1"
)
```

#### Constructor Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `openfinops_endpoint` | str | Yes | OpenFinOps server URL |
| `project_id` | str | No | GCP project ID (auto-detected if not provided) |
| `region` | str | No | Default region (default: us-central1) |

**Authentication**: Uses Google Application Default Credentials (service account key, gcloud CLI, etc.)

#### Methods

Same pattern as AWS and Azure agents:
- `register_agent()`
- `collect_telemetry_data()`
- `send_telemetry_data(data)`
- `run_once()`
- `run_continuous(interval_seconds=300)`

### What the GCP Agent Collects

- **Compute Engine**: Instances, CPU, memory, GPU, costs
- **GKE Clusters**: Node pools, workloads, costs
- **Cloud Functions**: Invocations, duration, costs
- **Cloud SQL**: CPU, storage, connections, costs
- **Cloud Storage**: Bucket sizes, costs

---

## Generic Telemetry Agent

For custom data sources and on-premises infrastructure.

### Class: `GenericTelemetryAgent`

**Location**: `agents.generic_telemetry_agent`

```python
from agents.generic_telemetry_agent import GenericTelemetryAgent

agent = GenericTelemetryAgent(
    openfinops_endpoint="http://localhost:8080",
    config_file="telemetry_config.yaml"  # Optional
)
```

#### Custom Metric Collection

The generic agent allows you to define custom metric collectors:

```python
# Define a custom collector function
def collect_custom_gpu_metrics():
    """Collect metrics from on-prem GPU cluster"""
    import subprocess

    # Example: Use nvidia-smi
    result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,memory.used',
                            '--format=csv,noheader'], capture_output=True, text=True)

    metrics = []
    for line in result.stdout.strip().split('\n'):
        gpu_util, mem_used = line.split(',')
        metrics.append({
            'gpu_utilization': float(gpu_util.strip().replace('%', '')),
            'memory_used_mb': float(mem_used.strip().replace(' MiB', ''))
        })

    return {
        'source': 'on-prem-gpu-cluster',
        'timestamp': time.time(),
        'gpu_metrics': metrics
    }

# Register the collector
agent.register_metric_collector('gpu_cluster', collect_custom_gpu_metrics)

# Run continuous collection
agent.run_continuous(interval_seconds=60)
```

---

## Deployment Guide

### Option 1: Run as Python Script

```python
# deploy_aws_agent.py
from agents.aws_telemetry_agent import AWSTelemetryAgent

agent = AWSTelemetryAgent(
    openfinops_endpoint="http://your-server:8080",
    aws_region="us-west-2"
)

if agent.register_agent():
    print("Starting AWS telemetry collection...")
    agent.run_continuous(interval_seconds=300)
```

Run:
```bash
python deploy_aws_agent.py
```

---

### Option 2: Docker Container

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agents/ ./agents/

# Agent will use AWS credentials from environment or IAM role
CMD ["python", "-c", "from agents.aws_telemetry_agent import AWSTelemetryAgent; \
     agent = AWSTelemetryAgent(openfinops_endpoint='http://openfinops-server:8080'); \
     agent.register_agent(); \
     agent.run_continuous(300)"]
```

**Build and run:**
```bash
docker build -t openfinops-aws-agent .

docker run -d --name aws-agent \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_DEFAULT_REGION=us-west-2 \
  openfinops-aws-agent
```

---

### Option 3: Kubernetes Deployment

**k8s/aws-agent-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openfinops-aws-agent
  namespace: openfinops
spec:
  replicas: 1
  selector:
    matchLabels:
      app: aws-telemetry-agent
  template:
    metadata:
      labels:
        app: aws-telemetry-agent
    spec:
      containers:
      - name: agent
        image: openfinops/aws-agent:latest
        env:
        - name: OPENFINOPS_ENDPOINT
          value: "http://openfinops-server:8080"
        - name: AWS_REGION
          value: "us-west-2"
        - name: COLLECTION_INTERVAL
          value: "300"
        # Use IAM roles for service accounts (IRSA) for authentication
        # Or provide credentials via secrets
      serviceAccountName: aws-telemetry-agent
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: aws-telemetry-agent
  namespace: openfinops
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::ACCOUNT:role/openfinops-agent-role
```

Deploy:
```bash
kubectl apply -f k8s/aws-agent-deployment.yaml
```

---

### Option 4: Systemd Service

**/etc/systemd/system/openfinops-aws-agent.service:**
```ini
[Unit]
Description=OpenFinOps AWS Telemetry Agent
After=network.target

[Service]
Type=simple
User=openfinops
WorkingDirectory=/opt/openfinops
Environment="OPENFINOPS_ENDPOINT=http://localhost:8080"
Environment="AWS_REGION=us-west-2"
Environment="AWS_SHARED_CREDENTIALS_FILE=/home/openfinops/.aws/credentials"
ExecStart=/usr/bin/python3 -c "from agents.aws_telemetry_agent import AWSTelemetryAgent; agent = AWSTelemetryAgent(openfinops_endpoint='http://localhost:8080'); agent.register_agent(); agent.run_continuous(300)"
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable openfinops-aws-agent
sudo systemctl start openfinops-aws-agent
sudo systemctl status openfinops-aws-agent
```

---

## Multi-Cloud Example

Deploy agents for all three cloud providers:

```python
# deploy_all_agents.py
from agents.aws_telemetry_agent import AWSTelemetryAgent
from agents.azure_telemetry_agent import AzureTelemetryAgent
from agents.gcp_telemetry_agent import GCPTelemetryAgent
import threading
import time

OPENFINOPS_SERVER = "http://your-server:8080"

def run_aws_agent():
    agent = AWSTelemetryAgent(
        openfinops_endpoint=OPENFINOPS_SERVER,
        aws_region="us-west-2"
    )
    agent.register_agent()
    agent.run_continuous(interval_seconds=300)

def run_azure_agent():
    agent = AzureTelemetryAgent(
        openfinops_endpoint=OPENFINOPS_SERVER,
        subscription_id="your-sub-id"
    )
    agent.register_agent()
    agent.run_continuous(interval_seconds=300)

def run_gcp_agent():
    agent = GCPTelemetryAgent(
        openfinops_endpoint=OPENFINOPS_SERVER,
        project_id="your-project"
    )
    agent.register_agent()
    agent.run_continuous(interval_seconds=300)

if __name__ == "__main__":
    # Run all agents in parallel
    threads = [
        threading.Thread(target=run_aws_agent, daemon=True),
        threading.Thread(target=run_azure_agent, daemon=True),
        threading.Thread(target=run_gcp_agent, daemon=True)
    ]

    for t in threads:
        t.start()

    print("All telemetry agents started")

    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down agents...")
```

---

## Troubleshooting

### Agent Can't Connect to OpenFinOps Server

```bash
# Check network connectivity
curl http://your-server:8080/health

# Verify endpoint in agent config
```

### AWS Authentication Issues

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check IAM permissions (needs CloudWatch, EC2, Cost Explorer read access)
```

### High CPU Usage from Agent

```bash
# Increase collection interval
agent.run_continuous(interval_seconds=600)  # 10 minutes instead of 5
```

### Missing Metrics

- Ensure the agent has proper IAM/RBAC permissions
- Check CloudWatch agent is installed for detailed EC2 metrics
- Verify resources are in the specified region

---

## See Also

- [Observability API](observability-api.md) - Server-side API reference
- [TELEMETRY_AGENT_DEPLOYMENT](../TELEMETRY_AGENT_DEPLOYMENT.md) - Detailed deployment guide
- [Dashboard API](dashboard-api.md) - Viewing collected data
