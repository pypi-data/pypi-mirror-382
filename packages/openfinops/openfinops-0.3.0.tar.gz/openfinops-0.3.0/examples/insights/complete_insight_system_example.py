"""
Complete Insight System Example
================================

End-to-end demonstration of the persona-specific insights system.

This example shows:
1. Generating insights for different personas
2. Configuring notification delivery
3. Routing insights to appropriate channels
4. Tracking delivery status

"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from openfinops.insights import (
    InsightEngine,
    InsightDeliveryEngine,
    DeliveryChannel,
    ChannelConfig,
    PersonaNotificationPreferences,
    InsightPriority,
    InsightCategory,
)
from openfinops.observability import ObservabilityHub, CostObservatory
import time


def setup_insight_system():
    """Set up the complete insight system."""
    print("=" * 80)
    print("OPENFINOPS PERSONA-SPECIFIC INSIGHTS SYSTEM")
    print("=" * 80)
    print()

    # Step 1: Initialize observability components
    print("📊 Step 1: Initializing observability components...")
    hub = ObservabilityHub()
    cost_obs = CostObservatory()
    print("✅ ObservabilityHub and CostObservatory initialized\n")

    # Step 2: Initialize insight engine
    print("🧠 Step 2: Initializing insight engine...")
    engine = InsightEngine(hub=hub, cost_obs=cost_obs)
    print(f"✅ Insight engine initialized with {len(engine._generators)} personas:")
    for persona in engine._generators.keys():
        print(f"   - {persona}")
    print()

    # Step 3: Initialize delivery engine
    print("📨 Step 3: Initializing delivery engine...")
    delivery = InsightDeliveryEngine()
    print("✅ Delivery engine initialized\n")

    return engine, delivery, hub, cost_obs


def configure_notification_channels(delivery):
    """Configure notification channels and handlers."""
    print("🔧 Step 4: Configuring notification channels...")

    # Mock Slack handler
    def slack_handler(insight, config):
        channel = config.get("channel", "#general")
        print(f"   📤 Sent to Slack {channel}: {insight.title}")
        return True

    # Mock Email handler
    def email_handler(insight, config):
        print(f"   📧 Sent email: {insight.title}")
        return True

    # Mock Teams handler
    def teams_handler(insight, config):
        print(f"   💬 Sent to Teams: {insight.title}")
        return True

    # Register handlers
    delivery.register_channel_handler(DeliveryChannel.SLACK, slack_handler)
    delivery.register_channel_handler(DeliveryChannel.EMAIL, email_handler)
    delivery.register_channel_handler(DeliveryChannel.TEAMS, teams_handler)

    print("✅ Registered 3 notification channels: Slack, Email, Teams\n")


def configure_persona_preferences(delivery):
    """Configure notification preferences for each persona."""
    print("👤 Step 5: Configuring persona notification preferences...")

    # CFO preferences - Email for all, Slack for high priority
    cfo_prefs = PersonaNotificationPreferences(
        persona="cfo",
        channels=[
            ChannelConfig(
                channel=DeliveryChannel.EMAIL,
                priority_threshold=InsightPriority.LOW,
                batch_size=5,  # Batch low/medium priority emails
                batch_interval_seconds=3600,
            ),
            ChannelConfig(
                channel=DeliveryChannel.SLACK,
                priority_threshold=InsightPriority.HIGH,  # Only high/critical to Slack
                config={"channel": "#executive-alerts"},
            ),
        ],
        quiet_hours_start=22,  # 10 PM
        quiet_hours_end=7,  # 7 AM
    )
    delivery.configure_persona_preferences(cfo_prefs)
    print("✅ Configured CFO: Email (batched) + Slack (high priority)")

    # Engineer preferences - Slack for everything urgent
    engineer_prefs = PersonaNotificationPreferences(
        persona="engineer",
        channels=[
            ChannelConfig(
                channel=DeliveryChannel.SLACK,
                priority_threshold=InsightPriority.MEDIUM,
                config={"channel": "#ops-alerts"},
            ),
            ChannelConfig(
                channel=DeliveryChannel.EMAIL,
                priority_threshold=InsightPriority.LOW,
                batch_size=10,
            ),
        ],
    )
    delivery.configure_persona_preferences(engineer_prefs)
    print("✅ Configured Engineer: Slack (medium+) + Email (batched)")

    # Finance preferences - Email for reports, Teams for critical
    finance_prefs = PersonaNotificationPreferences(
        persona="finance",
        channels=[
            ChannelConfig(
                channel=DeliveryChannel.EMAIL,
                priority_threshold=InsightPriority.LOW,
                batch_size=5,
            ),
            ChannelConfig(
                channel=DeliveryChannel.TEAMS,
                priority_threshold=InsightPriority.HIGH,
                config={"channel": "Finance Team"},
            ),
        ],
    )
    delivery.configure_persona_preferences(finance_prefs)
    print("✅ Configured Finance: Email (batched) + Teams (high priority)")

    # Business Lead preferences - Slack for strategic insights
    business_prefs = PersonaNotificationPreferences(
        persona="business_lead",
        channels=[
            ChannelConfig(
                channel=DeliveryChannel.SLACK,
                priority_threshold=InsightPriority.MEDIUM,
                config={"channel": "#leadership"},
            ),
        ],
    )
    delivery.configure_persona_preferences(business_prefs)
    print("✅ Configured Business Lead: Slack (medium+)\n")


def generate_and_deliver_insights(engine, delivery, persona, recipient):
    """Generate insights for a persona and deliver them."""
    print(f"\n{'=' * 80}")
    print(f"GENERATING INSIGHTS FOR: {persona.upper()}")
    print(f"{'=' * 80}\n")

    # Generate insights
    print(f"🔍 Generating {persona} insights...")
    insights = engine.generate_insights(persona=persona, time_range="30d")
    print(f"✅ Generated {len(insights)} insights:\n")

    # Display insights
    for i, insight in enumerate(insights, 1):
        priority_emoji = {
            InsightPriority.LOW: "ℹ️",
            InsightPriority.MEDIUM: "⚠️",
            InsightPriority.HIGH: "🔥",
            InsightPriority.CRITICAL: "🚨",
        }[insight.priority]

        print(f"   {i}. {priority_emoji} {insight.title}")
        print(f"      Priority: {insight.priority.value.upper()}")
        print(f"      Category: {insight.category.value.replace('_', ' ').title()}")
        print(f"      Description: {insight.description[:100]}...")
        print()

    # Deliver insights
    print(f"📨 Delivering insights to {persona}...")
    for insight in insights:
        receipts = delivery.deliver_insight(insight, persona, recipient)

        if receipts:
            for receipt in receipts:
                status_emoji = {
                    "sent": "✅",
                    "batched": "📦",
                    "scheduled": "⏰",
                    "failed": "❌",
                }[receipt.status.value]
                print(
                    f"   {status_emoji} {receipt.channel.value.upper()}: {receipt.status.value}"
                )
        else:
            print("   ⚠️  No channels configured for delivery")

    print(f"\n✅ Completed delivery for {persona}")


def demonstrate_filtering(engine):
    """Demonstrate insight filtering capabilities."""
    print(f"\n{'=' * 80}")
    print("FILTERING CAPABILITIES")
    print(f"{'=' * 80}\n")

    # Filter by priority
    print("🔍 Example 1: CFO insights with HIGH priority or above")
    high_priority = engine.generate_insights(
        persona="cfo", min_priority=InsightPriority.HIGH
    )
    print(f"   Found {len(high_priority)} high-priority insights\n")

    # Filter by category
    print("🔍 Example 2: Engineer insights in COST_OPTIMIZATION category")
    cost_optimization = engine.generate_insights(
        persona="engineer", categories=[InsightCategory.COST_OPTIMIZATION]
    )
    print(f"   Found {len(cost_optimization)} cost optimization insights\n")

    # Combined filter
    print("🔍 Example 3: Finance FORECAST insights with MEDIUM priority or above")
    forecast_insights = engine.generate_insights(
        persona="finance",
        min_priority=InsightPriority.MEDIUM,
        categories=[InsightCategory.FORECAST],
    )
    print(f"   Found {len(forecast_insights)} matching insights\n")


def show_delivery_stats(delivery):
    """Show delivery statistics."""
    print(f"\n{'=' * 80}")
    print("DELIVERY STATISTICS")
    print(f"{'=' * 80}\n")

    stats = delivery.get_delivery_stats(time_window_hours=24)

    print(f"📊 Last 24 hours:")
    print(f"   Total deliveries: {stats['total_deliveries']}")
    print(f"   Success rate: {stats['success_rate'] * 100:.1f}%\n")

    print(f"📈 By Status:")
    for status, count in stats["by_status"].items():
        print(f"   {status}: {count}")
    print()

    print(f"📢 By Channel:")
    for channel, count in stats["by_channel"].items():
        print(f"   {channel}: {count}")
    print()

    if stats["failed_deliveries"]:
        print(f"❌ Failed Deliveries: {len(stats['failed_deliveries'])}")
        for failure in stats["failed_deliveries"]:
            print(f"   - {failure['channel']}: {failure['error']}")
    else:
        print("✅ No failed deliveries")


def main():
    """Run the complete insight system demonstration."""
    # Setup
    engine, delivery, hub, cost_obs = setup_insight_system()
    configure_notification_channels(delivery)
    configure_persona_preferences(delivery)

    # Generate and deliver insights for each persona
    personas = [
        ("cfo", "cfo@company.com"),
        ("engineer", "devops@company.com"),
        ("finance", "finance@company.com"),
        ("business_lead", "leadership@company.com"),
    ]

    for persona, recipient in personas:
        generate_and_deliver_insights(engine, delivery, persona, recipient)
        time.sleep(0.5)  # Small delay for readability

    # Demonstrate filtering
    demonstrate_filtering(engine)

    # Show statistics
    show_delivery_stats(delivery)

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}\n")
    print("✅ Successfully demonstrated:")
    print("   1. Insight generation for 4 personas")
    print("   2. Multi-channel notification delivery")
    print("   3. Priority-based routing")
    print("   4. Batching for low-priority insights")
    print("   5. Filtering by priority and category")
    print("   6. Delivery tracking and statistics")
    print()
    print("🎉 Persona-Specific Insights System is fully operational!\n")
    print(f"{'=' * 80}\n")


if __name__ == "__main__":
    main()
