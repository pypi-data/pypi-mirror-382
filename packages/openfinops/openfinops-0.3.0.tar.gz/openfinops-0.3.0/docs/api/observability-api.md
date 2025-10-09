# Observability API Reference

Complete API reference for the OpenFinOps Observability Platform.

## Table of Contents

- [ObservabilityHub](#observabilityhub)
- [LLMObservabilityHub](#llmobservabilityhub)
- [CostObservatory](#costobservatory)
- [Architecture Overview](#architecture-overview)

---

## Architecture Overview

**IMPORTANT**: OpenFinOps uses an **agent-based architecture** for cost tracking:

1. **Telemetry Agents** (separate processes) run on your infrastructure or cloud accounts
2. Agents **automatically** query cloud provider APIs (AWS CloudWatch, Azure Monitor, GCP Billing)
3. Agents **automatically calculate costs** based on instance types and usage
4. Agents send telemetry data to the OpenFinOps server via REST API
5. **ObservabilityHub** receives and processes telemetry data
6. **Dashboards** display real-time metrics and costs

**You do NOT manually track costs** - the agents do this automatically.

---

## ObservabilityHub

The central hub for receiving and processing telemetry data.

### Class: `ObservabilityHub`

**Location**: `openfinops.observability.observability_hub`

```python
from openfinops.observability import ObservabilityHub

hub = ObservabilityHub()
```

#### Methods

##### `register_cluster(cluster_id, nodes, region="us-east-1")`

Register a compute cluster for monitoring.

```python
hub.register_cluster(
    cluster_id="gpu-cluster-1",
    nodes=["node-1", "node-2", "node-3"],
    region="us-west-2"
)
```

**Parameters:**
- `cluster_id` (str): Unique cluster identifier
- `nodes` (list[str]): List of node hostnames or IPs
- `region` (str): Cloud region (default: "us-east-1")

**Returns:** `dict` - Registration confirmation

---

##### `register_service(service_name, cluster_id, dependencies=None)`

Register a service for monitoring.

```python
hub.register_service(
    service_name="training-api",
    cluster_id="gpu-cluster-1",
    dependencies=["database", "cache"]
)
```

**Parameters:**
- `service_name` (str): Service identifier
- `cluster_id` (str): Associated cluster ID
- `dependencies` (list[str], optional): List of service dependencies

---

##### `collect_system_metrics(metrics)`

Collect system-level metrics (typically called by telemetry agents).

```python
from openfinops.observability.observability_hub import SystemMetrics

metrics = SystemMetrics(
    timestamp=time.time(),
    cpu_usage=75.5,
    memory_usage=68.2,
    disk_usage=45.0,
    gpu_usage=92.3,
    cluster_id="gpu-cluster-1",
    node_id="node-1"
)

hub.collect_system_metrics(metrics)
```

**Parameters:**
- `metrics` (SystemMetrics): System metrics dataclass

---

##### `collect_service_metrics(metrics)`

Collect service-level metrics.

```python
from openfinops.observability.observability_hub import ServiceMetrics

metrics = ServiceMetrics(
    service_name="training-api",
    timestamp=time.time(),
    request_count=1000,
    success_rate=99.5,
    avg_response_time=45.2,
    status="running"
)

hub.collect_service_metrics(metrics)
```

**Parameters:**
- `metrics` (ServiceMetrics): Service metrics dataclass

---

##### `get_cluster_health_summary()`

Get health summary for all registered clusters.

```python
summary = hub.get_cluster_health_summary()

for cluster_id, health in summary.items():
    print(f"{cluster_id}:")
    print(f"  Status: {health['health_status']}")
    print(f"  Total Nodes: {health['total_nodes']}")
    print(f"  Healthy Nodes: {health['healthy_nodes']}")
    print(f"  Avg CPU: {health['avg_cpu_usage']:.1f}%")
    print(f"  Avg GPU: {health['avg_gpu_usage']:.1f}%")
```

**Returns:** `dict` - Cluster health metrics

---

## LLMObservabilityHub

Specialized monitoring for LLM training and RAG pipelines.

### Class: `LLMObservabilityHub`

**Location**: `openfinops.observability.llm_observability`

```python
from openfinops.observability.llm_observability import LLMObservabilityHub

llm_hub = LLMObservabilityHub()
```

#### Methods

##### `collect_llm_training_metrics(metrics)`

Collect LLM training metrics.

```python
from openfinops.observability.llm_observability import LLMTrainingMetrics

metrics = LLMTrainingMetrics(
    run_id="llm-training-001",
    model_name="gpt-custom-7b",
    epoch=5,
    step=1000,
    training_loss=0.245,
    validation_loss=0.289,
    learning_rate=0.0001,
    gpu_memory_mb=42000,
    batch_size=32,
    throughput_samples_per_sec=128.5,
    timestamp=time.time()
)

llm_hub.collect_llm_training_metrics(metrics)
```

**Parameters:**
- `metrics` (LLMTrainingMetrics): Training metrics dataclass

---

##### `collect_rag_pipeline_metrics(metrics)`

Collect RAG pipeline metrics.

```python
from openfinops.observability.llm_observability import RAGPipelineMetrics

metrics = RAGPipelineMetrics(
    pipeline_id="production-rag",
    query="What is machine learning?",
    retrieval_time_ms=45.2,
    generation_time_ms=120.5,
    total_time_ms=165.7,
    relevance_score=0.95,
    num_retrieved_docs=5,
    embedding_tokens=50,
    generation_tokens=150,
    timestamp=time.time()
)

llm_hub.collect_rag_pipeline_metrics(metrics)
```

**Parameters:**
- `metrics` (RAGPipelineMetrics): RAG metrics dataclass

---

##### `get_training_summary(run_id)`

Get training summary for a specific run.

```python
summary = llm_hub.get_training_summary("llm-training-001")

print(f"Model: {summary['model_name']}")
print(f"Total Steps: {summary['total_steps']}")
print(f"Current Loss: {summary['current_loss']:.4f}")
print(f"Best Loss: {summary['best_loss']:.4f}")
print(f"GPU Utilization: {summary['avg_gpu_usage']:.1f}%")
```

**Parameters:**
- `run_id` (str): Training run identifier

**Returns:** `dict` - Training summary

---

##### `get_rag_pipeline_summary(pipeline_id)`

Get RAG pipeline performance summary.

```python
summary = llm_hub.get_rag_pipeline_summary("production-rag")

print(f"Total Queries: {summary['total_queries']}")
print(f"Avg Retrieval Time: {summary['avg_retrieval_time_ms']:.2f}ms")
print(f"Avg Relevance: {summary['avg_relevance_score']:.2f}")
```

**Parameters:**
- `pipeline_id` (str): RAG pipeline identifier

**Returns:** `dict` - Pipeline summary

---

## CostObservatory

Centralized cost tracking and budget management. Receives cost data from telemetry agents.

### Class: `CostObservatory`

**Location**: `openfinops.observability.cost_observatory`

```python
from openfinops.observability.cost_observatory import CostObservatory

cost_obs = CostObservatory()
```

#### Methods

##### `add_cost_entry(cost_entry)`

Add a cost entry (typically called by telemetry agents, not directly by users).

```python
from openfinops.observability.cost_observatory import CostEntry

entry = CostEntry(
    timestamp=time.time(),
    provider="aws",
    service="ec2",
    resource_id="i-1234567890abcdef0",
    cost_usd=3.50,  # hourly cost
    region="us-west-2",
    tags={"team": "ml-research", "project": "llm-training"}
)

cost_obs.add_cost_entry(entry)
```

**Parameters:**
- `cost_entry` (CostEntry): Cost entry dataclass

---

##### `create_budget(budget)`

Create a cost budget with alerts.

```python
from openfinops.observability.cost_observatory import Budget

budget = Budget(
    budget_id="monthly-ai-budget",
    name="AI/ML Monthly Budget",
    amount_usd=50000.0,
    period="monthly",
    scope={
        "provider": "aws",
        "tags": {"team": "ml-research"}
    },
    alert_threshold=0.8  # Alert at 80%
)

cost_obs.create_budget(budget)
```

**Parameters:**
- `budget` (Budget): Budget configuration dataclass

---

##### `get_cost_summary(time_range_hours=24)`

Get cost summary for a time period.

```python
# Last 24 hours
summary = cost_obs.get_cost_summary(time_range_hours=24)

print(f"Total Cost: ${summary['total_cost']:.2f}")
print(f"By Provider:")
for provider, cost in summary['by_provider'].items():
    print(f"  {provider}: ${cost:.2f}")

print(f"By Service:")
for service, cost in summary['by_service'].items():
    print(f"  {service}: ${cost:.2f}")

print(f"Top Resources:")
for resource in summary['top_resources'][:5]:
    print(f"  {resource['resource_id']}: ${resource['cost']:.2f}")
```

**Parameters:**
- `time_range_hours` (int): Time range in hours (default: 24)

**Returns:** `dict` - Cost summary with breakdowns

---

##### `get_budget_status()`

Get status of all budgets.

```python
status = cost_obs.get_budget_status()

for budget_id, info in status.items():
    print(f"{info['name']}:")
    print(f"  Budget: ${info['amount']:.2f}")
    print(f"  Spent: ${info['spent']:.2f}")
    print(f"  Remaining: ${info['remaining']:.2f}")
    print(f"  Percentage: {info['percentage_used']:.1f}%")
    print(f"  Status: {info['status']}")  # ok, warning, exceeded
```

**Returns:** `dict` - Budget status for all budgets

---

## Complete Example: Using Telemetry Agents

Here's how OpenFinOps actually works in practice:

### Step 1: Deploy Telemetry Agent

```python
# agents/deploy_aws_agent.py
from agents.aws_telemetry_agent import AWSTelemetryAgent
import time

# Initialize agent pointing to your OpenFinOps server
agent = AWSTelemetryAgent(
    openfinops_endpoint="http://localhost:8080",
    aws_region="us-west-2"
)

# Register with server
if agent.register_agent():
    print("✓ Agent registered")

    # Run continuous collection (every 5 minutes)
    agent.run_continuous(interval_seconds=300)
else:
    print("✗ Agent registration failed")
```

The agent will automatically:
1. Discover EC2 instances, EKS clusters, Lambda functions, etc.
2. Query CloudWatch for CPU, memory, network metrics
3. Calculate costs based on instance types and usage
4. Send telemetry to `http://localhost:8080/api/v1/telemetry/ingest`

### Step 2: Access Data via ObservabilityHub

```python
# In your application
from openfinops.observability import ObservabilityHub
from openfinops.observability.cost_observatory import CostObservatory

# Initialize components
hub = ObservabilityHub()
cost_obs = CostObservatory()

# Get cluster health (populated by agents)
health = hub.get_cluster_health_summary()
for cluster_id, metrics in health.items():
    print(f"{cluster_id}: {metrics['health_status']}")

# Get cost summary (populated by agents)
costs = cost_obs.get_cost_summary(time_range_hours=24)
print(f"Total 24h cost: ${costs['total_cost']:.2f}")
```

### Step 3: View Dashboards

```bash
# Start the web server
openfinops-dashboard --port 8080

# Access dashboards at:
# http://localhost:8080/dashboard/cfo
# http://localhost:8080/dashboard/coo
# http://localhost:8080/dashboard/infrastructure
```

---

## Manual Metric Injection (Advanced)

If you need to inject custom metrics not from cloud providers:

```python
from openfinops.observability import ObservabilityHub
from openfinops.observability.observability_hub import SystemMetrics
import time

hub = ObservabilityHub()

# Inject custom system metrics
metrics = SystemMetrics(
    timestamp=time.time(),
    cpu_usage=75.5,
    memory_usage=68.2,
    disk_usage=45.0,
    gpu_usage=92.3,
    cluster_id="on-prem-cluster",
    node_id="server-001"
)

hub.collect_system_metrics(metrics)
```

---

## See Also

- [Telemetry Agents API](telemetry-agents.md) - Agent deployment guide
- [Dashboard API](dashboard-api.md) - Dashboard components
- [TELEMETRY_AGENT_DEPLOYMENT](../TELEMETRY_AGENT_DEPLOYMENT.md) - Deployment guide
