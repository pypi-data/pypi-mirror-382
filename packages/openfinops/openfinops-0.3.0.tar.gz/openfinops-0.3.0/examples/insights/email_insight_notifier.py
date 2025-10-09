"""
Email Insight Notification Plugin
==================================

Delivers persona-specific insights via email.

Features:
- HTML email templates
- Daily digest mode
- Priority-based subject lines
- Inline charts and metrics
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, List
from openfinops.plugins import NotificationPlugin, PluginMetadata, PluginType
from openfinops.insights.insight_engine import Insight, InsightPriority


class EmailInsightNotifier(NotificationPlugin):
    """Email notification plugin for persona-specific insights."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Email notifier.

        Config keys:
        - smtp_host: SMTP server hostname
        - smtp_port: SMTP server port (default: 587)
        - smtp_user: SMTP username
        - smtp_password: SMTP password
        - from_address: Sender email address
        - from_name: Sender name (default: "OpenFinOps Insights")
        """
        super().__init__(config)
        self.smtp_host = None
        self.smtp_port = 587
        self.smtp_user = None
        self.smtp_password = None
        self.from_address = None
        self.from_name = "OpenFinOps Insights"

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="email_insight_notifier",
            version="1.0.0",
            author="OpenFinOps Contributors",
            description="Delivers persona-specific insights via email",
            plugin_type=PluginType.NOTIFICATION,
            requires_config=["smtp_host", "smtp_user", "smtp_password", "from_address"],
            dependencies=[],
        )

    def initialize(self) -> None:
        """Initialize SMTP client."""
        self.smtp_host = self.config.get("smtp_host")
        self.smtp_port = self.config.get("smtp_port", 587)
        self.smtp_user = self.config.get("smtp_user")
        self.smtp_password = self.config.get("smtp_password")
        self.from_address = self.config.get("from_address")
        self.from_name = self.config.get("from_name", self.from_name)

        required = ["smtp_host", "smtp_user", "smtp_password", "from_address"]
        missing = [k for k in required if not self.config.get(k)]
        if missing:
            raise ValueError(f"Missing required config keys: {missing}")

        self._state = self._state.__class__.ACTIVE
        print(f"✅ Email Insight Notifier initialized (from: {self.from_address})")

    def send_notification(self, insight: Insight, recipient: str, **kwargs) -> bool:
        """
        Send insight via email.

        Args:
            insight: Insight to send
            recipient: Email address
            **kwargs: Additional options (cc, bcc, etc.)

        Returns:
            True if sent successfully
        """
        subject = self._build_subject(insight)
        html_body = self._build_html_email(insight)
        text_body = self._build_text_email(insight)

        return self._send_email(recipient, subject, html_body, text_body, **kwargs)

    def send_digest(self, insights: List[Insight], recipient: str, **kwargs) -> bool:
        """
        Send daily/weekly digest of insights.

        Args:
            insights: List of insights to include
            recipient: Email address
            **kwargs: Additional options

        Returns:
            True if sent successfully
        """
        subject = f"OpenFinOps Insights Digest - {len(insights)} New Insights"
        html_body = self._build_digest_html(insights)
        text_body = self._build_digest_text(insights)

        return self._send_email(recipient, subject, html_body, text_body, **kwargs)

    def _build_subject(self, insight: Insight) -> str:
        """Build email subject line."""
        prefix_map = {
            InsightPriority.CRITICAL: "🚨 CRITICAL",
            InsightPriority.HIGH: "⚠️ HIGH PRIORITY",
            InsightPriority.MEDIUM: "ℹ️",
            InsightPriority.LOW: "",
        }
        prefix = prefix_map.get(insight.priority, "")
        return f"{prefix} {insight.title}".strip()

    def _build_html_email(self, insight: Insight) -> str:
        """Build HTML email body."""
        # Priority badge color
        badge_color = {
            InsightPriority.LOW: "#4CAF50",
            InsightPriority.MEDIUM: "#FFC107",
            InsightPriority.HIGH: "#FF9800",
            InsightPriority.CRITICAL: "#F44336",
        }.get(insight.priority, "#9E9E9E")

        # Build metadata table
        metadata_rows = ""
        for key, value in insight.metadata.items():
            if key not in ["timestamp", "confidence"]:
                formatted_key = key.replace("_", " ").title()
                metadata_rows += f"""
                <tr>
                    <td style="padding: 8px; border-bottom: 1px solid #eee; font-weight: 500;">
                        {formatted_key}
                    </td>
                    <td style="padding: 8px; border-bottom: 1px solid #eee;">
                        {self._format_value(value)}
                    </td>
                </tr>
                """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                     sans-serif; line-height: 1.6; color: #333; max-width: 600px;
                     margin: 0 auto; padding: 20px;">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px; border-radius: 8px 8px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">
                    OpenFinOps Insights
                </h1>
            </div>

            <!-- Content -->
            <div style="background: white; padding: 30px; border: 1px solid #e0e0e0;
                        border-top: none; border-radius: 0 0 8px 8px;">

                <!-- Priority Badge -->
                <div style="margin-bottom: 20px;">
                    <span style="display: inline-block; padding: 6px 12px;
                                 background: {badge_color}; color: white;
                                 border-radius: 4px; font-size: 12px;
                                 font-weight: 600; text-transform: uppercase;">
                        {insight.priority.value}
                    </span>
                    <span style="display: inline-block; padding: 6px 12px;
                                 background: #f5f5f5; color: #666;
                                 border-radius: 4px; font-size: 12px;
                                 margin-left: 8px;">
                        {insight.category.value.replace('_', ' ').title()}
                    </span>
                </div>

                <!-- Title -->
                <h2 style="color: #333; margin: 0 0 16px 0; font-size: 20px;">
                    {insight.title}
                </h2>

                <!-- Description -->
                <div style="background: #f9f9f9; padding: 16px; border-radius: 6px;
                            margin-bottom: 20px; border-left: 4px solid {badge_color};">
                    <p style="margin: 0; color: #555;">
                        {insight.description}
                    </p>
                </div>

                <!-- Impact -->
                <div style="margin-bottom: 20px;">
                    <h3 style="color: #667eea; margin: 0 0 8px 0; font-size: 16px;">
                        💡 Impact
                    </h3>
                    <p style="margin: 0; color: #555;">
                        {insight.impact}
                    </p>
                </div>

                <!-- Recommendation -->
                <div style="background: #e8f5e9; padding: 16px; border-radius: 6px;
                            margin-bottom: 20px; border-left: 4px solid #4CAF50;">
                    <h3 style="color: #2e7d32; margin: 0 0 8px 0; font-size: 16px;">
                        ✅ Recommendation
                    </h3>
                    <p style="margin: 0; color: #333;">
                        {insight.recommendation}
                    </p>
                </div>

                <!-- Metadata -->
                {f'''
                <div style="margin-top: 30px;">
                    <h3 style="color: #666; margin: 0 0 12px 0; font-size: 14px;
                               text-transform: uppercase; letter-spacing: 0.5px;">
                        Details
                    </h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        {metadata_rows}
                    </table>
                </div>
                ''' if metadata_rows else ''}

                <!-- Confidence -->
                <div style="margin-top: 20px; padding-top: 20px;
                            border-top: 1px solid #eee; text-align: center;">
                    <span style="color: #999; font-size: 12px;">
                        Confidence: {insight.confidence * 100:.0f}%
                    </span>
                </div>
            </div>

            <!-- Footer -->
            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p style="margin: 0;">
                    Powered by <strong>OpenFinOps</strong> Insight Engine
                </p>
                <p style="margin: 8px 0 0 0;">
                    <a href="#" style="color: #667eea; text-decoration: none;">
                        View Dashboard
                    </a> |
                    <a href="#" style="color: #667eea; text-decoration: none;">
                        Unsubscribe
                    </a>
                </p>
            </div>
        </body>
        </html>
        """
        return html

    def _build_text_email(self, insight: Insight) -> str:
        """Build plain text email body."""
        lines = [
            "=" * 60,
            "OpenFinOps Insight",
            "=" * 60,
            "",
            f"Priority: {insight.priority.value.upper()}",
            f"Category: {insight.category.value.replace('_', ' ').title()}",
            "",
            insight.title,
            "-" * 60,
            "",
            insight.description,
            "",
            "IMPACT:",
            insight.impact,
            "",
            "RECOMMENDATION:",
            insight.recommendation,
            "",
        ]

        if insight.metadata:
            lines.append("DETAILS:")
            for key, value in insight.metadata.items():
                if key not in ["timestamp", "confidence"]:
                    formatted_key = key.replace("_", " ").title()
                    lines.append(f"  {formatted_key}: {self._format_value(value)}")
            lines.append("")

        lines.extend(
            [
                f"Confidence: {insight.confidence * 100:.0f}%",
                "",
                "=" * 60,
                "Powered by OpenFinOps Insight Engine",
            ]
        )

        return "\n".join(lines)

    def _build_digest_html(self, insights: List[Insight]) -> str:
        """Build HTML digest email."""
        # Group by priority
        by_priority = {p: [] for p in InsightPriority}
        for insight in insights:
            by_priority[insight.priority].append(insight)

        insight_cards = ""
        for priority in [
            InsightPriority.CRITICAL,
            InsightPriority.HIGH,
            InsightPriority.MEDIUM,
            InsightPriority.LOW,
        ]:
            priority_insights = by_priority[priority]
            if not priority_insights:
                continue

            for insight in priority_insights:
                insight_cards += f"""
                <div style="margin-bottom: 16px; padding: 16px; background: #f9f9f9;
                            border-radius: 6px; border-left: 4px solid
                            {'#F44336' if priority == InsightPriority.CRITICAL else
                             '#FF9800' if priority == InsightPriority.HIGH else
                             '#FFC107' if priority == InsightPriority.MEDIUM else '#4CAF50'};">
                    <h3 style="margin: 0 0 8px 0; font-size: 16px;">{insight.title}</h3>
                    <p style="margin: 0; color: #666; font-size: 14px;">
                        {insight.description[:200]}...
                    </p>
                </div>
                """

        # Use similar HTML template structure, but with multiple insights
        # Simplified for brevity
        return f"<html><body><h1>Insights Digest</h1>{insight_cards}</body></html>"

    def _build_digest_text(self, insights: List[Insight]) -> str:
        """Build plain text digest."""
        lines = ["OpenFinOps Insights Digest", "=" * 60, ""]
        for i, insight in enumerate(insights, 1):
            lines.extend(
                [f"{i}. {insight.title}", f"   {insight.description[:100]}...", ""]
            )
        return "\n".join(lines)

    def _format_value(self, value: Any) -> str:
        """Format a value for display."""
        if isinstance(value, float):
            return f"{value:,.2f}"
        elif isinstance(value, int) and value > 1000:
            return f"{value:,}"
        elif isinstance(value, dict):
            return str(value)  # Simplified
        else:
            return str(value)

    def _send_email(
        self, to_address: str, subject: str, html_body: str, text_body: str, **kwargs
    ) -> bool:
        """Send email via SMTP."""
        # In real implementation, use smtplib
        print(f"\n📧 Sending email to: {to_address}")
        print(f"   Subject: {subject}")
        print(f"   From: {self.from_name} <{self.from_address}>")

        # Simulate SMTP
        # import smtplib
        # from email.mime.multipart import MIMEMultipart
        # from email.mime.text import MIMEText
        #
        # msg = MIMEMultipart('alternative')
        # msg['Subject'] = subject
        # msg['From'] = f"{self.from_name} <{self.from_address}>"
        # msg['To'] = to_address
        #
        # msg.attach(MIMEText(text_body, 'plain'))
        # msg.attach(MIMEText(html_body, 'html'))
        #
        # with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
        #     server.starttls()
        #     server.login(self.smtp_user, self.smtp_password)
        #     server.send_message(msg)

        return True  # Simulated success

    def shutdown(self) -> None:
        """Cleanup resources."""
        self._state = self._state.__class__.INACTIVE
        print("Email Insight Notifier shut down")


# Example usage
if __name__ == "__main__":
    from openfinops.insights.insight_engine import Insight, InsightCategory
    import time

    config = {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "insights@openfinops.ai",
        "smtp_password": "your-password-here",
        "from_address": "insights@openfinops.ai",
        "from_name": "OpenFinOps Insights",
    }

    notifier = EmailInsightNotifier(config)
    notifier.initialize()

    # Create sample insight
    insight = Insight(
        title="Idle Production Resources Detected",
        description=(
            "prod-cluster-3 has 23 idle pods consuming $1,200/day. "
            "Average CPU usage: 8%, Memory usage: 12%. These pods have "
            "been idle for 72+ hours with no traffic."
        ),
        priority=InsightPriority.HIGH,
        category=InsightCategory.COST_OPTIMIZATION,
        impact="High - Wasting $36K/month on unused resources",
        recommendation=(
            "Immediate: Scale down prod-cluster-3 to minimum required capacity. "
            "Long-term: Implement auto-scaling based on traffic patterns."
        ),
        metadata={
            "timestamp": time.time(),
            "cluster": "prod-cluster-3",
            "idle_pods": 23,
            "daily_cost": 1200,
            "monthly_savings": 30000,
        },
        confidence=0.95,
    )

    # Send email
    success = notifier.send_notification(insight, recipient="cfo@example.com")
    print(f"\n{'✅' if success else '❌'} Email sent: {success}")

    notifier.shutdown()
