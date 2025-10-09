# Quick Start Guide

Get started with OpenFinOps in 10 minutes!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)
- Cloud provider credentials (AWS, Azure, or GCP) - optional for local testing

## Installation

### Install from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/rdmurugan/OpenFinOps.git
cd OpenFinOps

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Install with Cloud Provider Support

```bash
# Install with AWS support
pip install -e ".[aws]"

# Install with all cloud providers
pip install -e ".[aws,azure,gcp]"

# Install with everything (recommended)
pip install -e ".[all]"
```

---

## Understanding OpenFinOps Architecture

OpenFinOps uses an **agent-based architecture**:

1. **Server** - Central OpenFinOps server (runs on your infrastructure)
2. **Agents** - Deployed in cloud accounts to collect metrics automatically
3. **Dashboards** - Web UI for visualizing costs and metrics

**Key Point**: You don't manually track costs. Agents automatically discover resources, collect metrics, calculate costs, and send data to the server.

---

## Option 1: Quick Demo (No Cloud Credentials)

Run the included quickstart example to see OpenFinOps in action:

```bash
# Run the quickstart demo
python examples/quickstart.py
```

Output:
```
============================================================
OpenFinOps Quick Start
============================================================

1. Initializing ObservabilityHub...
   ✓ ObservabilityHub initialized

2. Initializing LLMObservabilityHub...
   ✓ LLMObservabilityHub initialized

3. Registering training cluster...
   ✓ Training cluster 'gpu-cluster-demo' registered

4. Tracking training metrics...
   ✓ Epoch 1 metrics tracked
   ✓ Epoch 2 metrics tracked
   ✓ Epoch 3 metrics tracked

============================================================
Quick Start Complete!
============================================================
```

---

## Option 2: Full Setup with AWS

### Step 1: Start the OpenFinOps Server

```bash
# Start the web dashboard server
openfinops-dashboard --port 8080

# Server will be available at http://localhost:8080
```

You should see:
```
🚀 Starting OpenFinOps Web UI Server...
   Host: 127.0.0.1
   Port: 8080

   Dashboard will be available at:
   http://127.0.0.1:8080

✅ OpenFinOps Web UI loaded successfully

📊 Available Dashboards:
   • Overview Dashboard:     http://127.0.0.1:8080/
   • CFO Executive:          http://127.0.0.1:8080/dashboard/cfo
   • COO Operational:        http://127.0.0.1:8080/dashboard/coo
   • Infrastructure Leader:  http://127.0.0.1:8080/dashboard/infrastructure

Press Ctrl+C to stop the server
```

### Step 2: Deploy AWS Telemetry Agent

Create a new file `deploy_aws_agent.py`:

```python
from agents.aws_telemetry_agent import AWSTelemetryAgent

# Initialize the agent
agent = AWSTelemetryAgent(
    openfinops_endpoint="http://localhost:8080",
    aws_region="us-west-2"  # Change to your region
)

# Register the agent with the server
if agent.register_agent():
    print("✓ Agent registered successfully")
    print("Starting continuous telemetry collection...")
    print("Collecting metrics every 5 minutes")
    print("Press Ctrl+C to stop")

    # Run continuous collection
    agent.run_continuous(interval_seconds=300)
else:
    print("✗ Agent registration failed")
    print("Make sure the OpenFinOps server is running at http://localhost:8080")
```

### Step 3: Configure AWS Credentials

```bash
# Option 1: Use AWS CLI configuration
aws configure

# Option 2: Set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

### Step 4: Run the Agent

```bash
python deploy_aws_agent.py
```

The agent will:
- Automatically discover EC2 instances, EKS clusters, Lambda functions, RDS, S3
- Query CloudWatch for CPU, memory, network metrics
- Calculate costs based on instance types and usage
- Send telemetry to the server every 5 minutes

### Step 5: View the Dashboards

Open your browser and navigate to:
- http://localhost:8080/ - Overview dashboard
- http://localhost:8080/dashboard/cfo - CFO executive dashboard
- http://localhost:8080/dashboard/coo - COO operational dashboard
- http://localhost:8080/dashboard/infrastructure - Infrastructure leader dashboard

---

## Option 3: Manual Metric Injection (For Testing)

If you don't have cloud credentials, you can manually inject metrics:

```python
from openfinops.observability import ObservabilityHub
from openfinops.observability.observability_hub import SystemMetrics
from openfinops.observability.cost_observatory import CostObservatory, CostEntry
import time

# Initialize components
hub = ObservabilityHub()
cost_obs = CostObservatory()

# Register a test cluster
hub.register_cluster(
    cluster_id="test-cluster",
    nodes=["node-1", "node-2"],
    region="us-west-2"
)
print("✓ Cluster registered")

# Inject system metrics
metrics = SystemMetrics(
    timestamp=time.time(),
    cpu_usage=75.5,
    memory_usage=68.2,
    disk_usage=45.0,
    gpu_usage=92.3,
    cluster_id="test-cluster",
    node_id="node-1"
)
hub.collect_system_metrics(metrics)
print("✓ System metrics collected")

# Inject cost data
entry = CostEntry(
    timestamp=time.time(),
    provider="aws",
    service="ec2",
    resource_id="i-test123",
    cost_usd=3.50,
    region="us-west-2",
    tags={"team": "ml-research"}
)
cost_obs.add_cost_entry(entry)
print("✓ Cost entry added")

# Get cost summary
summary = cost_obs.get_cost_summary(time_range_hours=24)
print(f"\n💰 Total cost (24h): ${summary['total_cost']:.2f}")
```

---

## LLM Training Monitoring Example

Monitor LLM training metrics:

```python
from openfinops.observability.llm_observability import LLMObservabilityHub, LLMTrainingMetrics
import time

# Initialize LLM monitoring
llm_hub = LLMObservabilityHub()

# Simulate training loop
for epoch in range(1, 6):
    for step in range(1, 101):
        # Track training metrics
        metrics = LLMTrainingMetrics(
            run_id="llm-training-001",
            model_name="gpt-custom-7b",
            epoch=epoch,
            step=step,
            training_loss=1.0 / (step + epoch * 10),  # Simulated decreasing loss
            validation_loss=1.2 / (step + epoch * 10),
            learning_rate=0.0001,
            gpu_memory_mb=42000,
            batch_size=32,
            throughput_samples_per_sec=128.5,
            timestamp=time.time()
        )

        llm_hub.collect_llm_training_metrics(metrics)

        if step % 20 == 0:
            print(f"Epoch {epoch}, Step {step}: Loss = {metrics.training_loss:.4f}")

# Get training summary
summary = llm_hub.get_training_summary("llm-training-001")
print(f"\n✓ Training summary:")
print(f"  Total steps: {summary.get('total_steps', 0)}")
print(f"  Best loss: {summary.get('best_loss', 0):.4f}")
```

---

## Cost Budgets Example

Set up cost budgets with alerts:

```python
from openfinops.observability.cost_observatory import CostObservatory, Budget
import time

cost_obs = CostObservatory()

# Create a monthly budget
budget = Budget(
    budget_id="monthly-ai-budget",
    name="AI/ML Monthly Budget",
    amount_usd=50000.0,
    period="monthly",
    start_time=time.time(),
    scope={
        "provider": "aws",
        "tags": {"team": "ml-research"}
    },
    alert_threshold=0.8  # Alert at 80%
)

cost_obs.create_budget(budget)
print("✓ Budget created")

# Check budget status
status = cost_obs.get_budget_status()
for budget_id, info in status.items():
    print(f"\n{info['name']}:")
    print(f"  Budget: ${info['amount']:.2f}")
    print(f"  Spent: ${info['spent']:.2f}")
    print(f"  Remaining: ${info['remaining']:.2f}")
    print(f"  Status: {info['status']}")
```

---

## Next Steps

Now that you have OpenFinOps running, explore more features:

1. **[API Reference](../api/observability-api.md)** - Detailed API documentation
2. **[Telemetry Agents Guide](../api/telemetry-agents.md)** - Deploy agents for Azure and GCP
3. **[Deployment Guide](../TELEMETRY_AGENT_DEPLOYMENT.md)** - Production deployment
4. **[Examples](../../examples/README.md)** - More code examples

---

## Common Commands

```bash
# Start the dashboard server
openfinops-dashboard --port 8080

# Start with custom host
openfinops-dashboard --host 0.0.0.0 --port 8080

# Get version
openfinops --version

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/openfinops --cov-report=html
```

---

## Troubleshooting

### Import Errors

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall in development mode
pip install -e .
```

### Server Won't Start

```bash
# Check if port is already in use
lsof -i :8080

# Use a different port
openfinops-dashboard --port 8081
```

### Agent Can't Connect to Server

```bash
# Verify server is running
curl http://localhost:8080/health

# Check firewall settings
# Ensure agents can reach the server on port 8080
```

### AWS Agent Not Collecting Data

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Check IAM permissions
# Agent needs read access to: EC2, CloudWatch, Cost Explorer, EKS, Lambda, RDS, S3
```

---

## Getting Help

- **Documentation**: [docs/README.md](../README.md)
- **Examples**: Check the `examples/` directory
- **Issues**: [GitHub Issues](https://github.com/rdmurugan/OpenFinOps/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rdmurugan/OpenFinOps/discussions)

---

## What's Included?

This quickstart covered:
- ✅ Installing OpenFinOps
- ✅ Starting the dashboard server
- ✅ Deploying telemetry agents
- ✅ Viewing cost dashboards
- ✅ Tracking LLM training metrics
- ✅ Setting up cost budgets

Happy monitoring! 🎉
