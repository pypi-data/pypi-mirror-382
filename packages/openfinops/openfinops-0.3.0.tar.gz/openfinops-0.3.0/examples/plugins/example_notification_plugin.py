"""
Example Notification Plugin
============================

Example of a Slack notification plugin.
"""

from typing import Dict, Any

from openfinops.plugins import NotificationPlugin, PluginMetadata, PluginType


class SlackNotificationPlugin(NotificationPlugin):
    """
    Send notifications to Slack.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="slack-notifications",
            version="1.0.0",
            author="OpenFinOps Contributors",
            description="Send notifications to Slack",
            plugin_type=PluginType.NOTIFICATION,
            dependencies=["slack-sdk>=3.0.0"],
            config_schema={
                "webhook_url": {"type": "string", "required": True},
                "channel": {"type": "string", "required": False},
                "username": {"type": "string", "required": False},
            },
            homepage="https://github.com/openfinops/openfinops-plugin-slack",
            tags=["slack", "notification", "alerts"],
        )

    def initialize(self) -> None:
        """Initialize Slack client."""
        self.webhook_url = self.get_config_value("webhook_url", required=True)
        self.channel = self.get_config_value("channel", default="#finops-alerts")
        self.username = self.get_config_value("username", default="OpenFinOps Bot")

        # In production:
        # from slack_sdk.webhook import WebhookClient
        # self.client = WebhookClient(self.webhook_url)

        print(f"✓ Initialized Slack plugin for channel: {self.channel}")

    def send_notification(
        self,
        message: str,
        priority: str = "normal",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Send notification to Slack.

        Args:
            message: Message to send
            priority: Priority level
            metadata: Additional metadata

        Returns:
            True if sent successfully
        """
        if not self.is_ready:
            raise RuntimeError("Plugin not initialized")

        # Map priority to emoji
        emoji_map = {
            "low": "ℹ️",
            "normal": "📊",
            "high": "⚠️",
            "critical": "🚨",
        }
        emoji = emoji_map.get(priority, "📊")

        # Format message
        formatted_message = f"{emoji} *{priority.upper()}*\n{message}"

        if metadata:
            formatted_message += "\n\n*Details:*\n"
            for key, value in metadata.items():
                formatted_message += f"• {key}: {value}\n"

        # In production, actually send to Slack:
        # response = self.client.send(text=formatted_message)
        # return response.status_code == 200

        # For this example:
        print(f"\n📤 Sending to Slack ({self.channel}):")
        print(f"   {formatted_message}")

        return True

    def shutdown(self) -> None:
        """Cleanup."""
        print("✓ Shut down Slack plugin")


# Example usage
if __name__ == "__main__":
    from openfinops.plugins import registry

    # Register and load
    registry.register(SlackNotificationPlugin)
    plugin = registry.load_plugin(
        "slack-notifications",
        config={
            "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            "channel": "#cost-alerts",
        }
    )

    # Send notification
    plugin.send_notification(
        message="AWS costs increased by 25% in the last hour",
        priority="high",
        metadata={
            "service": "EC2",
            "region": "us-west-2",
            "current_cost": "$450/hour",
            "baseline": "$360/hour",
        }
    )

    # Cleanup
    registry.unload_plugin("slack-notifications")
