# Basic Usage Tutorial

Learn the fundamentals of OpenFinOps through hands-on examples.

## Prerequisites

- OpenFinOps installed (`pip install -e .`)
- Python 3.8+
- Basic Python knowledge

## Tutorial Overview

This tutorial covers:
1. Setting up monitoring
2. Tracking costs
3. Creating visualizations
4. Generating reports

---

## Part 1: Setting Up Monitoring

### Step 1: Initialize the Observability Hub

```python
from openfinops import ObservabilityHub

# Create the central observability hub
hub = ObservabilityHub()

print("✓ ObservabilityHub initialized")
```

The `ObservabilityHub` is the central component that orchestrates all monitoring activities.

### Step 2: Register Your Infrastructure

```python
# Register a compute cluster
hub.register_cluster(
    cluster_name="training-cluster-1",
    nodes=[
        "gpu-node-1.example.com",
        "gpu-node-2.example.com",
        "gpu-node-3.example.com",
        "gpu-node-4.example.com"
    ]
)

print("✓ Cluster registered with 4 nodes")
```

---

## Part 2: Tracking Costs

### Step 3: Track Cloud Costs

```python
from openfinops.observability import CostObservatory

# Initialize cost tracking
cost_obs = CostObservatory()

# Track AWS costs
cost_obs.track_cloud_cost(
    provider="aws",
    service="ec2",
    cost=125.50,
    region="us-west-2",
    instance_type="p3.2xlarge",
    team="ml-research"
)

# Track Azure costs
cost_obs.track_cloud_cost(
    provider="azure",
    service="virtual-machines",
    cost=98.75,
    region="westus",
    vm_size="Standard_NC6",
    team="ml-research"
)

# Track OpenAI API costs
cost_obs.track_api_cost(
    platform="openai",
    model="gpt-4",
    tokens_input=500,
    tokens_output=1200,
    cost=0.048
)

print("✓ Costs tracked for AWS, Azure, and OpenAI")
```

### Step 4: Get Cost Summary

```python
# Get total costs
total = cost_obs.get_total_cost(time_range="30d")
print(f"\n💰 Total cost (30 days): ${total:.2f}")

# Get breakdown by provider
breakdown = cost_obs.get_cost_breakdown_by_provider(time_range="30d")
print("\n📊 Cost by Provider:")
for provider, cost in breakdown.items():
    print(f"  {provider}: ${cost:.2f}")

# Get cost trend
trend = cost_obs.get_cost_trend(time_range="7d", granularity="daily")
print("\n📈 Daily Cost Trend (7 days):")
for date, cost in list(trend.items())[-7:]:
    print(f"  {date}: ${cost:.2f}")
```

---

## Part 3: Monitoring LLM Training

### Step 5: Set Up LLM Monitoring

```python
from openfinops import LLMObservabilityHub
import time

# Initialize LLM monitoring
llm_hub = LLMObservabilityHub()

# Register training cluster
llm_hub.register_training_cluster(
    cluster_name="llm-training-cluster",
    nodes=["gpu-1", "gpu-2", "gpu-3", "gpu-4"],
    config={
        "gpu_type": "A100",
        "gpu_count": 4,
        "interconnect": "nvlink"
    }
)

print("✓ LLM training cluster registered")
```

### Step 6: Track Training Metrics

```python
# Simulate a training loop
model_id = "gpt-custom-7b"
print(f"\n🤖 Training {model_id}...")

for epoch in range(1, 4):
    for step in range(1, 101):
        # Simulate training metrics
        loss = 2.0 / (epoch * step)
        gpu_memory = 40000 + (step % 10) * 100

        # Track metrics
        llm_hub.track_training_metrics(
            model_id=model_id,
            epoch=epoch,
            step=step,
            loss=loss,
            learning_rate=0.0001,
            gpu_memory_usage=gpu_memory,
            batch_size=32
        )

        if step % 20 == 0:
            print(f"  Epoch {epoch}, Step {step}: Loss = {loss:.6f}")

    print(f"✓ Epoch {epoch} completed")

# Get training summary
summary = llm_hub.get_training_summary(model_id=model_id, time_range="1h")
print(f"\n📊 Training Summary:")
print(f"  Total Steps: {summary['total_steps']}")
print(f"  Current Loss: {summary['current_loss']:.6f}")
print(f"  Best Loss: {summary['best_loss']:.6f}")
print(f"  Avg GPU Usage: {summary['avg_gpu_usage']:.1f}%")
```

---

## Part 4: Creating Visualizations

### Step 7: Create Cost Charts

```python
from openfinops.vizlychart.charts import LineChart, BarChart
import numpy as np

# Create cost trend chart
trend_chart = LineChart(width=800, height=600)

days = list(range(1, 31))
costs = [100 + np.random.randn() * 10 + i * 2 for i in days]

trend_chart.plot(
    days, costs,
    color='blue',
    linewidth=2,
    label='Daily Cost'
)

trend_chart.set_title("Monthly Cost Trend")
trend_chart.set_xlabel("Day of Month")
trend_chart.set_ylabel("Cost ($)")
trend_chart.add_legend()
trend_chart.add_grid(alpha=0.3)

trend_chart.save("cost_trend.png", dpi=300)
print("\n✓ Cost trend chart saved as 'cost_trend.png'")

# Create provider comparison chart
provider_chart = BarChart()

providers = ['AWS', 'Azure', 'GCP', 'OpenAI']
costs = [2500, 1800, 2100, 450]
colors = ['#FF9900', '#008AD7', '#4285F4', '#10A37F']

provider_chart.bar(
    providers,
    costs,
    color=colors,
    edgecolor='black',
    linewidth=1
)

provider_chart.set_title("Cost by Provider")
provider_chart.set_ylabel("Cost ($)")
provider_chart.add_value_labels(format='${:.0f}')

provider_chart.save("cost_by_provider.png", dpi=300)
print("✓ Provider comparison chart saved as 'cost_by_provider.png'")
```

### Step 8: Create Training Loss Chart

```python
from openfinops.vizlychart.charts import LineChart

loss_chart = LineChart(width=1000, height=600)

# Sample training data
steps = list(range(1, 301))
losses = [2.0 / (step ** 0.5) for step in steps]

loss_chart.plot(
    steps, losses,
    color='red',
    linewidth=2,
    label='Training Loss'
)

loss_chart.set_title(f"Training Loss - {model_id}")
loss_chart.set_xlabel("Training Step")
loss_chart.set_ylabel("Loss")
loss_chart.set_yscale('log')  # Log scale for loss
loss_chart.add_legend()
loss_chart.add_grid(alpha=0.3, linestyle='--')

loss_chart.save("training_loss.png", dpi=300)
print("✓ Training loss chart saved as 'training_loss.png'")
```

---

## Part 5: Working with Dashboards

### Step 9: Access Role-Based Dashboards

```python
from openfinops.dashboard import CFODashboard, COODashboard

# CFO Dashboard
cfo_dashboard = CFODashboard(user_id="cfo@company.com")

# Get financial summary
financial_summary = cfo_dashboard.get_financial_summary(time_range="30d")

print("\n📊 CFO Dashboard - Financial Summary:")
print(f"  Total Spend: ${financial_summary['total_spend']:.2f}")
print(f"  Budget: ${financial_summary['budget']:.2f}")
print(f"  Utilization: {financial_summary['budget_utilization']:.1f}%")
print(f"  Savings Opportunities: ${financial_summary['savings_opportunities']:.2f}")

# COO Dashboard
coo_dashboard = COODashboard(user_id="coo@company.com")

# Get operational metrics
ops_metrics = coo_dashboard.get_operational_metrics(time_range="24h")

print("\n⚙️  COO Dashboard - Operational Metrics:")
print(f"  System Uptime: {ops_metrics['uptime']:.2f}%")
print(f"  Active Workloads: {ops_metrics['active_workloads']}")
print(f"  Resource Utilization: {ops_metrics['resource_utilization']:.1f}%")
```

---

## Part 6: AI-Powered Recommendations

### Step 10: Get Optimization Recommendations

```python
from openfinops.observability import AIRecommendationEngine

# Initialize AI recommendation engine
ai_rec = AIRecommendationEngine()

# Get recommendations
recommendations = ai_rec.get_optimization_recommendations(scope="all")

print("\n💡 AI-Powered Optimization Recommendations:")
for i, rec in enumerate(recommendations[:5], 1):
    print(f"\n{i}. {rec['title']}")
    print(f"   Priority: {rec['priority']}")
    print(f"   Estimated Savings: ${rec['estimated_savings']:.2f}/month")
    print(f"   Confidence: {rec['confidence']}%")
    print(f"   Action: {rec['recommended_action']}")
```

---

## Part 7: Setting Up Alerts

### Step 11: Configure Alerts

```python
from openfinops.observability import AlertingEngine

# Initialize alerting
alerting = AlertingEngine()

# Create budget alert
alerting.create_alert_rule(
    name="monthly_budget_exceeded",
    condition="monthly_cost > 5000",
    severity="critical",
    channels=["email", "slack"]
)

# Create GPU utilization alert
alerting.create_alert_rule(
    name="low_gpu_utilization",
    condition="gpu_utilization < 50",
    severity="warning",
    channels=["email"]
)

# Create high cost alert
alerting.create_alert_rule(
    name="hourly_cost_spike",
    condition="hourly_cost > hourly_average * 2",
    severity="warning",
    channels=["email", "slack"]
)

print("\n🔔 Alert rules configured:")
print("  ✓ Monthly budget exceeded")
print("  ✓ Low GPU utilization")
print("  ✓ Hourly cost spike")

# Check active alerts
active_alerts = alerting.get_active_alerts()
print(f"\n📢 Active alerts: {len(active_alerts)}")
```

---

## Complete Example

Here's a complete script combining all the concepts:

```python
#!/usr/bin/env python3
"""
Complete OpenFinOps Basic Usage Example
"""

from openfinops import ObservabilityHub, LLMObservabilityHub
from openfinops.observability import CostObservatory, AIRecommendationEngine
from openfinops.vizlychart.charts import LineChart, BarChart
from openfinops.dashboard import CFODashboard
import numpy as np

def main():
    print("=" * 60)
    print("OpenFinOps Basic Usage Example")
    print("=" * 60)

    # 1. Initialize core components
    print("\n1. Initializing components...")
    hub = ObservabilityHub()
    llm_hub = LLMObservabilityHub()
    cost_obs = CostObservatory()
    ai_rec = AIRecommendationEngine()

    # 2. Register infrastructure
    print("\n2. Registering infrastructure...")
    llm_hub.register_training_cluster(
        cluster_name="production-cluster",
        nodes=["gpu-1", "gpu-2", "gpu-3", "gpu-4"]
    )

    # 3. Track costs
    print("\n3. Tracking costs...")
    cost_obs.track_cloud_cost("aws", "ec2", 500.00, region="us-west-2")
    cost_obs.track_cloud_cost("azure", "vm", 350.00, region="westus")
    cost_obs.track_api_cost("openai", "gpt-4", 1000, 2000, 0.12)

    # 4. Track training
    print("\n4. Tracking LLM training...")
    for step in range(1, 101):
        llm_hub.track_training_metrics(
            model_id="llm-v1",
            epoch=1,
            step=step,
            loss=2.0 / step,
            gpu_memory_usage=40000
        )

    # 5. Create visualizations
    print("\n5. Creating visualizations...")
    chart = BarChart()
    chart.bar(['AWS', 'Azure', 'OpenAI'], [500, 350, 120],
              color=['#FF9900', '#008AD7', '#10A37F'])
    chart.set_title("Monthly Costs by Provider")
    chart.save("costs.png")

    # 6. Get recommendations
    print("\n6. Getting AI recommendations...")
    recommendations = ai_rec.get_optimization_recommendations()
    print(f"   Found {len(recommendations)} optimization opportunities")
    total_savings = sum(r['estimated_savings'] for r in recommendations)
    print(f"   Potential savings: ${total_savings:.2f}/month")

    # 7. Generate dashboard
    print("\n7. Generating CFO dashboard...")
    cfo_dash = CFODashboard(user_id="cfo@example.com")
    summary = cfo_dash.get_financial_summary(time_range="30d")
    print(f"   Total spend: ${summary['total_spend']:.2f}")
    print(f"   Budget utilization: {summary['budget_utilization']:.1f}%")

    print("\n" + "=" * 60)
    print("✓ Example completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

---

## Next Steps

Now that you understand the basics:

1. **[Advanced Monitoring](llm-monitoring.md)** - Deep dive into LLM monitoring
2. **[Multi-Cloud Setup](multi-cloud.md)** - Configure multiple cloud providers
3. **[Custom Dashboards](custom-dashboards.md)** - Build your own dashboards
4. **[Cost Attribution](cost-attribution.md)** - Track costs by team/project
5. **[API Reference](../api/observability-api.md)** - Complete API documentation

## Troubleshooting

### Common Issues

**ImportError**: Make sure OpenFinOps is installed:
```bash
pip install -e .
```

**No metrics showing**: Ensure you've tracked some data first before querying.

**Permission errors**: Check file permissions for saving charts and reports.

## Get Help

- **Documentation**: [docs/README.md](../README.md)
- **Examples**: [examples/](../../examples/)
- **Issues**: [GitHub Issues](https://github.com/rdmurugan/OpenFinOps/issues)
