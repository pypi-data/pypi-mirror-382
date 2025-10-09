"""
Slack Insight Notification Plugin
==================================

Delivers persona-specific insights to Slack channels.

Features:
- Rich message formatting with attachments
- Priority-based color coding
- Channel routing by persona
- Thread-based conversations
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import json
from typing import Dict, Any
from openfinops.plugins import NotificationPlugin, PluginMetadata, PluginType
from openfinops.insights.insight_engine import Insight, InsightPriority
from openfinops.insights.delivery import DeliveryChannel


class SlackInsightNotifier(NotificationPlugin):
    """Slack notification plugin for persona-specific insights."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Slack notifier.

        Config keys:
        - webhook_url: Slack webhook URL
        - channel: Default Slack channel
        - username: Bot username (default: "OpenFinOps Insights")
        - icon_emoji: Bot icon (default: ":chart_with_upwards_trend:")
        - persona_channels: Dict mapping personas to channels
        """
        super().__init__(config)
        self.webhook_url = None
        self.default_channel = None
        self.username = "OpenFinOps Insights"
        self.icon_emoji = ":chart_with_upwards_trend:"
        self.persona_channels = {}

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="slack_insight_notifier",
            version="1.0.0",
            author="OpenFinOps Contributors",
            description="Delivers persona-specific insights to Slack",
            plugin_type=PluginType.NOTIFICATION,
            requires_config=["webhook_url"],
            dependencies=[],
        )

    def initialize(self) -> None:
        """Initialize Slack client."""
        self.webhook_url = self.config.get("webhook_url")
        self.default_channel = self.config.get("channel", "#finops-insights")
        self.username = self.config.get("username", self.username)
        self.icon_emoji = self.config.get("icon_emoji", self.icon_emoji)
        self.persona_channels = self.config.get("persona_channels", {})

        if not self.webhook_url:
            raise ValueError("webhook_url is required in config")

        self._state = self._state.__class__.ACTIVE
        print(f"✅ Slack Insight Notifier initialized for {self.default_channel}")

    def send_notification(self, insight: Insight, recipient: str, **kwargs) -> bool:
        """
        Send insight to Slack.

        Args:
            insight: Insight to send
            recipient: Persona name (used to route to correct channel)
            **kwargs: Additional options

        Returns:
            True if sent successfully
        """
        # Get channel for persona
        channel = self.persona_channels.get(recipient, self.default_channel)

        # Build Slack message
        message = self._build_slack_message(insight, channel)

        # Send via webhook (mocked for example)
        return self._send_to_slack(message)

    def _build_slack_message(self, insight: Insight, channel: str) -> Dict[str, Any]:
        """Build Slack message with rich formatting."""
        # Priority-based color coding
        color_map = {
            InsightPriority.LOW: "#36a64f",  # Green
            InsightPriority.MEDIUM: "#ffcc00",  # Yellow
            InsightPriority.HIGH: "#ff9900",  # Orange
            InsightPriority.CRITICAL: "#ff0000",  # Red
        }
        color = color_map.get(insight.priority, "#808080")

        # Build attachment
        attachment = {
            "fallback": f"{insight.title}: {insight.description[:100]}",
            "color": color,
            "title": f"{self._get_priority_emoji(insight.priority)} {insight.title}",
            "text": insight.description,
            "fields": [
                {
                    "title": "Category",
                    "value": insight.category.value.replace("_", " ").title(),
                    "short": True,
                },
                {"title": "Priority", "value": insight.priority.value.upper(), "short": True},
                {"title": "Impact", "value": insight.impact, "short": False},
                {"title": "Recommendation", "value": insight.recommendation, "short": False},
            ],
            "footer": "OpenFinOps Insight Engine",
            "footer_icon": "https://openfinops.ai/icon.png",
            "ts": int(insight.metadata.get("timestamp", 0)),
        }

        # Add confidence if high enough
        if insight.confidence >= 0.8:
            attachment["fields"].append(
                {
                    "title": "Confidence",
                    "value": f"{insight.confidence * 100:.0f}%",
                    "short": True,
                }
            )

        # Add metadata fields
        if insight.metadata:
            metadata_text = self._format_metadata(insight.metadata)
            if metadata_text:
                attachment["fields"].append(
                    {"title": "Details", "value": metadata_text, "short": False}
                )

        return {
            "channel": channel,
            "username": self.username,
            "icon_emoji": self.icon_emoji,
            "text": f"*New {insight.category.value.replace('_', ' ').title()} Insight*",
            "attachments": [attachment],
        }

    def _get_priority_emoji(self, priority: InsightPriority) -> str:
        """Get emoji for priority level."""
        emoji_map = {
            InsightPriority.LOW: "ℹ️",
            InsightPriority.MEDIUM: "⚠️",
            InsightPriority.HIGH: "🔥",
            InsightPriority.CRITICAL: "🚨",
        }
        return emoji_map.get(priority, "📊")

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format metadata for display."""
        # Skip common fields
        skip_keys = {"timestamp", "confidence"}
        relevant = {k: v for k, v in metadata.items() if k not in skip_keys}

        if not relevant:
            return ""

        lines = []
        for key, value in relevant.items():
            if isinstance(value, dict):
                continue  # Skip nested dicts for now
            formatted_key = key.replace("_", " ").title()
            if isinstance(value, float):
                if "pct" in key:
                    lines.append(f"• {formatted_key}: {value:.1f}%")
                else:
                    lines.append(f"• {formatted_key}: {value:,.2f}")
            elif isinstance(value, int):
                if value > 1000:
                    lines.append(f"• {formatted_key}: {value:,}")
                else:
                    lines.append(f"• {formatted_key}: {value}")
            else:
                lines.append(f"• {formatted_key}: {value}")

        return "\n".join(lines[:5])  # Limit to 5 fields

    def _send_to_slack(self, message: Dict[str, Any]) -> bool:
        """Send message to Slack via webhook."""
        # In a real implementation, use requests library
        # For this example, we'll simulate success
        print(f"\n📤 Sending to Slack channel: {message['channel']}")
        print(f"   {message['text']}")
        print(f"   Title: {message['attachments'][0]['title']}")

        # Simulate HTTP POST
        # import requests
        # response = requests.post(self.webhook_url, json=message)
        # return response.status_code == 200

        return True  # Simulated success

    def shutdown(self) -> None:
        """Cleanup resources."""
        self._state = self._state.__class__.INACTIVE
        print("Slack Insight Notifier shut down")


# Example usage
if __name__ == "__main__":
    from openfinops.insights.insight_engine import Insight, InsightCategory
    import time

    # Initialize plugin
    config = {
        "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        "channel": "#finops-insights",
        "persona_channels": {
            "cfo": "#executive-insights",
            "engineer": "#engineering-alerts",
            "finance": "#finance-reports",
        },
    }

    notifier = SlackInsightNotifier(config)
    notifier.initialize()

    # Create sample insight
    insight = Insight(
        title="Cloud Costs Trending 15% Over Budget",
        description=(
            "AWS spending is projected to exceed budget by $22,000 this month. "
            "Primary drivers: EC2 instances in us-east-1 ($12K) and Databricks "
            "compute ($8K). Current trajectory shows $256K total vs $234K budget."
        ),
        priority=InsightPriority.HIGH,
        category=InsightCategory.FORECAST,
        impact="High - Budget reallocation needed",
        recommendation=(
            "Submit budget amendment request for Q1. Review EC2 instance sizing "
            "and Databricks auto-scaling configuration."
        ),
        metadata={
            "timestamp": time.time(),
            "budget": 234000,
            "projected": 256000,
            "variance_pct": 9.4,
            "top_services": {"ec2": 12000, "databricks": 8000},
        },
        confidence=0.93,
    )

    # Send to CFO channel
    success = notifier.send_notification(insight, recipient="cfo")
    print(f"\n{'✅' if success else '❌'} Notification sent: {success}")

    notifier.shutdown()
