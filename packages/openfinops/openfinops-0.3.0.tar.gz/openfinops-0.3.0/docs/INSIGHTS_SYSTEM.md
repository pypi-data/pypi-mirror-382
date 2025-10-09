# Persona-Specific Insights System

**Feature #2 of the OpenFinOps 2025 Roadmap**

The Persona-Specific Insights System provides intelligent, context-aware cost insights tailored to different organizational roles. Each persona receives actionable recommendations optimized for their decision-making needs.

## Overview

Instead of generic "cost alerts," this system delivers:

- **CFO**: Unit economics, ROI analysis, budget variance, strategic financial metrics
- **Engineer**: Idle resources, optimization opportunities, cost spikes, technical recommendations
- **Finance Analyst**: Forecast variance, trend analysis, cost breakdowns, budget tracking
- **Business Leader**: Strategic KPIs, growth efficiency, business impact metrics

## Architecture

```
┌──────────────────┐
│  InsightEngine   │  ← Generates persona-specific insights
└────────┬─────────┘
         │
         ├── CFO Generator
         ├── Engineer Generator
         ├── Finance Generator
         └── Business Lead Generator

┌──────────────────────┐
│ DeliveryEngine       │  ← Routes insights to channels
└────────┬─────────────┘
         │
         ├── Slack Handler
         ├── Email Handler
         ├── Teams Handler
         └── Custom Handlers
```

## Quick Start

### 1. Basic Usage

```python
from openfinops.insights import InsightEngine
from openfinops.observability import ObservabilityHub, CostObservatory

# Initialize components
hub = ObservabilityHub()
cost_obs = CostObservatory()
engine = InsightEngine(hub=hub, cost_obs=cost_obs)

# Generate CFO insights
insights = engine.generate_insights(persona="cfo", time_range="30d")

for insight in insights:
    print(f"{insight.title}: {insight.description}")
    print(f"Priority: {insight.priority.value}")
    print(f"Recommendation: {insight.recommendation}")
```

### 2. Filtering Insights

```python
from openfinops.insights import InsightPriority, InsightCategory

# High-priority insights only
critical_insights = engine.generate_insights(
    persona="engineer",
    min_priority=InsightPriority.HIGH
)

# Cost optimization insights
cost_insights = engine.generate_insights(
    persona="finance",
    categories=[InsightCategory.COST_OPTIMIZATION]
)

# Combined filters
urgent_forecasts = engine.generate_insights(
    persona="finance",
    min_priority=InsightPriority.MEDIUM,
    categories=[InsightCategory.FORECAST]
)
```

### 3. Notification Delivery

```python
from openfinops.insights import (
    InsightDeliveryEngine,
    DeliveryChannel,
    ChannelConfig,
    PersonaNotificationPreferences,
)

# Initialize delivery engine
delivery = InsightDeliveryEngine()

# Register notification handlers
def slack_handler(insight, config):
    # Send to Slack using webhooks or API
    slack_client.post_message(
        channel=config["channel"],
        text=f"{insight.title}: {insight.description}"
    )
    return True

delivery.register_channel_handler(DeliveryChannel.SLACK, slack_handler)

# Configure persona preferences
cfo_prefs = PersonaNotificationPreferences(
    persona="cfo",
    channels=[
        ChannelConfig(
            channel=DeliveryChannel.EMAIL,
            priority_threshold=InsightPriority.LOW,
            batch_size=5,  # Batch low-priority emails
        ),
        ChannelConfig(
            channel=DeliveryChannel.SLACK,
            priority_threshold=InsightPriority.HIGH,  # High-priority to Slack
            config={"channel": "#executive-alerts"}
        ),
    ],
    quiet_hours_start=22,  # 10 PM
    quiet_hours_end=7,  # 7 AM
)

delivery.configure_persona_preferences(cfo_prefs)

# Deliver insights
for insight in insights:
    receipts = delivery.deliver_insight(insight, "cfo", "cfo@company.com")
    for receipt in receipts:
        print(f"{receipt.channel}: {receipt.status}")
```

## Personas

### CFO (Chief Financial Officer)

**Focus**: Strategic financial metrics, unit economics, ROI

**Insights**:
- Cloud spend efficiency trends
- Budget variance analysis
- Unit economics (cost per user/transaction)
- Infrastructure ROI analysis

**Example**:
```
Title: Cloud Spend Efficiency Improving
Description: Cloud infrastructure costs increased 15% this month to $125,000,
but revenue per customer improved 22%, indicating better unit economics.
Impact: Positive - Improving cost efficiency despite growth
Recommendation: Continue current optimization efforts. Consider increasing
Reserved Instance coverage to lock in current pricing.
```

### Engineer / DevOps

**Focus**: Resource optimization, performance, technical actions

**Insights**:
- Idle resource detection
- Resource utilization analysis
- Optimization opportunities (ARM instances, reserved capacity)
- Cost spike detection and root cause

**Example**:
```
Title: Data Transfer Costs Spike Detected
Description: Data transfer costs increased 340% in last 6 hours from $12/hour
to $53/hour. Spike corresponds with new feature deployment in service-api-v2.
Impact: Critical - Unexpected $1,000/day cost increase
Recommendation: URGENT: Review service-api-v2 data fetching logic. Implement
caching for external API responses. Add rate limiting.
```

### Finance Analyst

**Focus**: Forecasting, variance analysis, budget tracking

**Insights**:
- Forecast variance analysis
- Month-end/quarter-end projections
- Cost distribution breakdowns
- Trend analysis

**Example**:
```
Title: Q1 Forecast Variance Analysis
Description: Q1 cloud spend forecast was $234K, current trend shows $256K
(+9.4% variance). Primary drivers: AWS EC2 ($12K over), Databricks ($8K over).
Impact: High - Budget reallocation needed
Recommendation: Submit budget amendment request for $22K additional allocation.
Adjust Q2 forecast models to account for sustained higher usage.
```

### Business Leader

**Focus**: Strategic KPIs, growth metrics, business impact

**Insights**:
- Infrastructure efficiency vs user growth
- Sustainable growth patterns
- Capacity headroom analysis
- Revenue-to-infrastructure ROI

**Example**:
```
Title: Sustainable Growth Pattern
Description: Infrastructure costs scaling sub-linearly with business growth.
CAC decreased 12% while LTV increased 18%. Infrastructure supporting this
growth efficiently.
Impact: Excellent - Business metrics improving
Recommendation: Maintain current growth trajectory. Infrastructure capacity
supports 50% additional growth without major investment.
```

## Configuration

### Insight Priority Levels

```python
class InsightPriority:
    LOW      # Informational, can be batched
    MEDIUM   # Important, should be delivered soon
    HIGH     # Urgent, deliver immediately
    CRITICAL # Emergency, bypass all batching/quiet hours
```

### Insight Categories

```python
class InsightCategory:
    COST_OPTIMIZATION  # Cost savings opportunities
    EFFICIENCY         # Resource utilization improvements
    BUDGET             # Budget tracking and variance
    ANOMALY            # Unusual patterns or spikes
    FORECAST           # Future predictions and projections
    COMPLIANCE         # Policy and compliance issues
    SECURITY           # Security-related cost impacts
    RECOMMENDATION     # General recommendations
```

### Delivery Channels

```python
class DeliveryChannel:
    SLACK      # Slack webhooks or API
    EMAIL      # Email notifications
    TEAMS      # Microsoft Teams
    PAGERDUTY  # PagerDuty alerts
    WEBHOOK    # Custom webhooks
    SMS        # SMS notifications
    IN_APP     # In-application notifications
```

### Channel Configuration

```python
ChannelConfig(
    channel=DeliveryChannel.EMAIL,
    enabled=True,
    priority_threshold=InsightPriority.LOW,  # Minimum priority to send
    batch_size=10,                           # Batch size for low-priority
    batch_interval_seconds=3600,             # Batch interval (1 hour)
    rate_limit_per_hour=100,                 # Max sends per hour
    config={                                 # Channel-specific config
        "smtp_host": "smtp.gmail.com",
        "from": "insights@company.com"
    }
)
```

## Examples

### Complete Examples

See the `examples/insights/` directory:

1. **`complete_insight_system_example.py`** - Full end-to-end demonstration
2. **`slack_insight_notifier.py`** - Slack notification plugin
3. **`email_insight_notifier.py`** - Email notification plugin

### Running Examples

```bash
# Complete system demo
python examples/insights/complete_insight_system_example.py

# Slack notifier example
python examples/insights/slack_insight_notifier.py

# Email notifier example
python examples/insights/email_insight_notifier.py
```

## Custom Personas

You can create custom persona generators:

```python
from openfinops.insights import InsightGenerator, Insight, InsightPriority, InsightCategory

class SecurityLeadInsightGenerator(InsightGenerator):
    """Generate Security Lead-specific insights."""

    def generate(self, hub, cost_obs, time_range="30d"):
        insights = []

        # Analyze security-related costs
        insights.append(
            Insight(
                title="Unnecessary Public IPs Detected",
                description="15 EC2 instances have public IPs but no inbound traffic...",
                priority=InsightPriority.MEDIUM,
                category=InsightCategory.SECURITY,
                impact="Medium - Security risk + unnecessary costs",
                recommendation="Remove public IPs, use NAT gateway instead",
                metadata={"instance_count": 15, "monthly_savings": 450},
                confidence=0.92,
            )
        )

        return insights

# Register with engine
engine.register_generator("security_lead", SecurityLeadInsightGenerator())

# Use it
insights = engine.generate_insights("security_lead")
```

## Testing

```bash
# Run all insight system tests
pytest tests/insights/ -v

# Run specific test suites
pytest tests/insights/test_insight_engine.py -v
pytest tests/insights/test_personas.py -v
pytest tests/insights/test_delivery.py -v

# Run with coverage
pytest tests/insights/ --cov=src/openfinops/insights --cov-report=html
```

## Integration with Existing Features

### With ObservabilityHub

```python
# Insights can use real observability data
hub = ObservabilityHub()

# Register clusters and services
hub.register_cluster("prod-cluster", nodes=50, region="us-west-2")

# Collect metrics
hub.collect_system_metrics(SystemMetrics(...))

# Generate insights based on real data
insights = engine.generate_insights("engineer", time_range="7d")
```

### With CostObservatory

```python
# Insights can use real cost data
cost_obs = CostObservatory()

# Add cost entries
cost_obs.add_cost_entry(CostEntry(...))

# Create budgets
cost_obs.create_budget(Budget(...))

# Generate budget-aware insights
insights = engine.generate_insights("cfo", time_range="30d")
```

### With Dashboards

```python
from openfinops.dashboard import CFODashboard

# Dashboards can display insights
dashboard = CFODashboard(hub=hub, cost_obs=cost_obs, insight_engine=engine)

# Get insights for display
insights = engine.generate_insights("cfo", min_priority=InsightPriority.MEDIUM)
```

## API Reference

### InsightEngine

```python
class InsightEngine:
    def __init__(hub, cost_obs):
        """Initialize with observability components."""

    def register_generator(persona: str, generator: InsightGenerator):
        """Register a custom persona generator."""

    def generate_insights(
        persona: str,
        time_range: str = "30d",
        min_priority: Optional[InsightPriority] = None,
        categories: Optional[List[InsightCategory]] = None
    ) -> List[Insight]:
        """Generate filtered insights for a persona."""
```

### InsightDeliveryEngine

```python
class InsightDeliveryEngine:
    def register_channel_handler(channel: DeliveryChannel, handler: Callable):
        """Register a notification channel handler."""

    def configure_persona_preferences(preferences: PersonaNotificationPreferences):
        """Configure notification preferences for a persona."""

    def deliver_insight(
        insight: Insight,
        persona: str,
        recipient: str,
        force: bool = False
    ) -> List[DeliveryReceipt]:
        """Deliver an insight through configured channels."""

    def deliver_batch(
        insights: List[Insight],
        persona: str,
        recipient: str
    ) -> List[DeliveryReceipt]:
        """Deliver a batch of insights."""

    def get_delivery_stats(
        persona: Optional[str] = None,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Get delivery statistics."""
```

## Roadmap

Future enhancements planned for the insights system:

1. **ML-Based Insights** (Feature #3) - ML-driven anomaly detection for smarter insights
2. **Workflow Integration** - Jira, ServiceNow, PagerDuty incident creation
3. **Insight Feedback Loop** - Users can rate insights to improve relevance
4. **Historical Tracking** - Track insight accuracy over time
5. **Custom Templates** - User-defined insight templates
6. **Multi-Language Support** - Insights in multiple languages

## Support

- **Documentation**: `/docs/INSIGHTS_SYSTEM.md`
- **Examples**: `/examples/insights/`
- **Tests**: `/tests/insights/`
- **Issues**: https://github.com/openfinops/openfinops/issues

## License

Apache 2.0 - See LICENSE file for details.

## Contributors

OpenFinOps Contributors - See CONTRIBUTORS.md
