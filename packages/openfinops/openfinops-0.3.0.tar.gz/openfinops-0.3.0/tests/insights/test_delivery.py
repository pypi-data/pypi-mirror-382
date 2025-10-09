"""
Tests for Insight Delivery System
==================================

Test notification routing, batching, and delivery tracking.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

import pytest
import time
from openfinops.insights.delivery import (
    InsightDeliveryEngine,
    DeliveryChannel,
    DeliveryStatus,
    ChannelConfig,
    PersonaNotificationPreferences,
    DeliveryReceipt,
)
from openfinops.insights.insight_engine import Insight, InsightPriority, InsightCategory


@pytest.fixture
def delivery_engine():
    """Create InsightDeliveryEngine instance."""
    return InsightDeliveryEngine()


@pytest.fixture
def sample_insight():
    """Create a sample insight."""
    return Insight(
        title="Test Insight",
        description="Test description",
        priority=InsightPriority.HIGH,
        category=InsightCategory.COST_OPTIMIZATION,
        impact="High impact",
        recommendation="Test recommendation",
        metadata={"key": "value"},
        confidence=0.9,
    )


@pytest.fixture
def mock_channel_handler():
    """Create a mock channel handler."""

    def handler(insight, config):
        return True  # Always succeed

    return handler


class TestDeliveryEngine:
    """Test InsightDeliveryEngine."""

    def test_register_channel_handler(self, delivery_engine, mock_channel_handler):
        """Test registering a channel handler."""
        delivery_engine.register_channel_handler(DeliveryChannel.SLACK, mock_channel_handler)

        assert DeliveryChannel.SLACK in delivery_engine._channel_handlers
        assert delivery_engine._channel_handlers[DeliveryChannel.SLACK] == mock_channel_handler

    def test_configure_persona_preferences(self, delivery_engine):
        """Test configuring persona preferences."""
        preferences = PersonaNotificationPreferences(
            persona="cfo",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.EMAIL, priority_threshold=InsightPriority.MEDIUM
                )
            ],
        )

        delivery_engine.configure_persona_preferences(preferences)

        assert "cfo" in delivery_engine._preferences
        assert delivery_engine._preferences["cfo"] == preferences

    def test_deliver_insight_success(self, delivery_engine, sample_insight, mock_channel_handler):
        """Test successful insight delivery."""
        # Setup
        delivery_engine.register_channel_handler(DeliveryChannel.SLACK, mock_channel_handler)
        preferences = PersonaNotificationPreferences(
            persona="cfo",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.SLACK, priority_threshold=InsightPriority.LOW
                )
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        # Deliver
        receipts = delivery_engine.deliver_insight(sample_insight, "cfo", "user@example.com")

        assert len(receipts) == 1
        assert receipts[0].status == DeliveryStatus.SENT
        assert receipts[0].channel == DeliveryChannel.SLACK

    def test_deliver_insight_no_preferences(
        self, delivery_engine, sample_insight, mock_channel_handler
    ):
        """Test delivery with no persona preferences."""
        delivery_engine.register_channel_handler(DeliveryChannel.SLACK, mock_channel_handler)

        receipts = delivery_engine.deliver_insight(sample_insight, "unknown", "user@example.com")

        assert len(receipts) == 0

    def test_priority_threshold_filtering(
        self, delivery_engine, sample_insight, mock_channel_handler
    ):
        """Test filtering by priority threshold."""
        delivery_engine.register_channel_handler(DeliveryChannel.SLACK, mock_channel_handler)

        # Set threshold to CRITICAL (higher than insight priority)
        preferences = PersonaNotificationPreferences(
            persona="cfo",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.SLACK, priority_threshold=InsightPriority.CRITICAL
                )
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        receipts = delivery_engine.deliver_insight(sample_insight, "cfo", "user@example.com")

        # Should be empty because insight priority is HIGH, threshold is CRITICAL
        assert len(receipts) == 0

    def test_batching_low_priority_insights(
        self, delivery_engine, sample_insight, mock_channel_handler
    ):
        """Test that low priority insights are batched."""
        delivery_engine.register_channel_handler(DeliveryChannel.EMAIL, mock_channel_handler)

        preferences = PersonaNotificationPreferences(
            persona="finance",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.EMAIL,
                    priority_threshold=InsightPriority.LOW,
                    batch_size=5,
                )
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        # Create low priority insight
        low_priority_insight = Insight(
            title="Low Priority",
            description="Test",
            priority=InsightPriority.LOW,
            category=InsightCategory.EFFICIENCY,
            impact="Low",
            recommendation="Test",
        )

        receipts = delivery_engine.deliver_insight(
            low_priority_insight, "finance", "user@example.com"
        )

        assert len(receipts) == 1
        assert receipts[0].status == DeliveryStatus.BATCHED

    def test_critical_insights_not_batched(
        self, delivery_engine, mock_channel_handler
    ):
        """Test that critical insights are never batched."""
        delivery_engine.register_channel_handler(DeliveryChannel.EMAIL, mock_channel_handler)

        preferences = PersonaNotificationPreferences(
            persona="engineer",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.EMAIL,
                    priority_threshold=InsightPriority.LOW,
                    batch_size=10,  # Batching enabled
                )
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        # Critical insight
        critical_insight = Insight(
            title="Critical Issue",
            description="Urgent",
            priority=InsightPriority.CRITICAL,
            category=InsightCategory.ANOMALY,
            impact="Critical",
            recommendation="Act now",
        )

        receipts = delivery_engine.deliver_insight(
            critical_insight, "engineer", "user@example.com"
        )

        assert len(receipts) == 1
        assert receipts[0].status == DeliveryStatus.SENT  # Not batched

    def test_deliver_batch(self, delivery_engine, sample_insight, mock_channel_handler):
        """Test batch delivery."""
        delivery_engine.register_channel_handler(DeliveryChannel.EMAIL, mock_channel_handler)

        preferences = PersonaNotificationPreferences(
            persona="cfo",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.EMAIL, priority_threshold=InsightPriority.LOW
                )
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        # Create batch of insights
        insights = [sample_insight] * 3

        receipts = delivery_engine.deliver_batch(insights, "cfo", "user@example.com")

        assert len(receipts) == 1
        assert receipts[0].status == DeliveryStatus.SENT
        assert receipts[0].metadata["batch_size"] == 3

    def test_multiple_channels(self, delivery_engine, sample_insight, mock_channel_handler):
        """Test delivery through multiple channels."""
        delivery_engine.register_channel_handler(DeliveryChannel.SLACK, mock_channel_handler)
        delivery_engine.register_channel_handler(DeliveryChannel.EMAIL, mock_channel_handler)

        preferences = PersonaNotificationPreferences(
            persona="cfo",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.SLACK, priority_threshold=InsightPriority.LOW
                ),
                ChannelConfig(
                    channel=DeliveryChannel.EMAIL, priority_threshold=InsightPriority.LOW
                ),
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        receipts = delivery_engine.deliver_insight(sample_insight, "cfo", "user@example.com")

        assert len(receipts) == 2
        channels = [r.channel for r in receipts]
        assert DeliveryChannel.SLACK in channels
        assert DeliveryChannel.EMAIL in channels

    def test_disabled_channel_not_used(
        self, delivery_engine, sample_insight, mock_channel_handler
    ):
        """Test that disabled channels are not used."""
        delivery_engine.register_channel_handler(DeliveryChannel.SLACK, mock_channel_handler)

        preferences = PersonaNotificationPreferences(
            persona="cfo",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.SLACK,
                    enabled=False,  # Disabled
                    priority_threshold=InsightPriority.LOW,
                )
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        receipts = delivery_engine.deliver_insight(sample_insight, "cfo", "user@example.com")

        assert len(receipts) == 0

    def test_failed_delivery(self, delivery_engine, sample_insight):
        """Test handling of failed delivery."""

        def failing_handler(insight, config):
            raise Exception("Delivery failed")

        delivery_engine.register_channel_handler(DeliveryChannel.SLACK, failing_handler)

        preferences = PersonaNotificationPreferences(
            persona="cfo",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.SLACK, priority_threshold=InsightPriority.LOW
                )
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        receipts = delivery_engine.deliver_insight(sample_insight, "cfo", "user@example.com")

        assert len(receipts) == 1
        assert receipts[0].status == DeliveryStatus.FAILED
        assert "Delivery failed" in receipts[0].error_message

    def test_delivery_stats(self, delivery_engine, sample_insight, mock_channel_handler):
        """Test delivery statistics."""
        delivery_engine.register_channel_handler(DeliveryChannel.SLACK, mock_channel_handler)

        preferences = PersonaNotificationPreferences(
            persona="cfo",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.SLACK, priority_threshold=InsightPriority.LOW
                )
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        # Deliver multiple insights
        for _ in range(3):
            delivery_engine.deliver_insight(sample_insight, "cfo", "user@example.com")

        stats = delivery_engine.get_delivery_stats()

        assert stats["total_deliveries"] == 3
        assert stats["by_status"]["sent"] == 3
        assert stats["by_channel"]["slack"] == 3
        assert stats["success_rate"] == 1.0

    def test_force_immediate_delivery(self, delivery_engine, mock_channel_handler):
        """Test forcing immediate delivery bypasses batching."""
        delivery_engine.register_channel_handler(DeliveryChannel.EMAIL, mock_channel_handler)

        preferences = PersonaNotificationPreferences(
            persona="finance",
            channels=[
                ChannelConfig(
                    channel=DeliveryChannel.EMAIL,
                    priority_threshold=InsightPriority.LOW,
                    batch_size=10,
                )
            ],
        )
        delivery_engine.configure_persona_preferences(preferences)

        low_priority_insight = Insight(
            title="Low Priority",
            description="Test",
            priority=InsightPriority.LOW,
            category=InsightCategory.EFFICIENCY,
            impact="Low",
            recommendation="Test",
        )

        # Force delivery
        receipts = delivery_engine.deliver_insight(
            low_priority_insight, "finance", "user@example.com", force=True
        )

        assert len(receipts) == 1
        assert receipts[0].status == DeliveryStatus.SENT  # Not batched


class TestChannelConfig:
    """Test ChannelConfig dataclass."""

    def test_default_config(self):
        """Test default channel configuration."""
        config = ChannelConfig(channel=DeliveryChannel.SLACK)

        assert config.enabled is True
        assert config.priority_threshold == InsightPriority.LOW
        assert config.batch_size == 10
        assert config.batch_interval_seconds == 3600
        assert config.rate_limit_per_hour == 100

    def test_custom_config(self):
        """Test custom configuration."""
        config = ChannelConfig(
            channel=DeliveryChannel.EMAIL,
            enabled=False,
            priority_threshold=InsightPriority.HIGH,
            batch_size=5,
            batch_interval_seconds=1800,
            rate_limit_per_hour=50,
            config={"key": "value"},
        )

        assert config.enabled is False
        assert config.priority_threshold == InsightPriority.HIGH
        assert config.batch_size == 5
        assert config.config["key"] == "value"


class TestPersonaNotificationPreferences:
    """Test PersonaNotificationPreferences."""

    def test_default_preferences(self):
        """Test default preferences."""
        prefs = PersonaNotificationPreferences(
            persona="cfo", channels=[ChannelConfig(channel=DeliveryChannel.EMAIL)]
        )

        assert prefs.quiet_hours_start is None
        assert prefs.quiet_hours_end is None
        assert prefs.timezone == "UTC"

    def test_with_quiet_hours(self):
        """Test quiet hours configuration."""
        prefs = PersonaNotificationPreferences(
            persona="cfo",
            channels=[ChannelConfig(channel=DeliveryChannel.EMAIL)],
            quiet_hours_start=22,  # 10 PM
            quiet_hours_end=7,  # 7 AM
            timezone="America/New_York",
        )

        assert prefs.quiet_hours_start == 22
        assert prefs.quiet_hours_end == 7
        assert prefs.timezone == "America/New_York"


class TestDeliveryReceipt:
    """Test DeliveryReceipt dataclass."""

    def test_receipt_creation(self):
        """Test creating a delivery receipt."""
        receipt = DeliveryReceipt(
            insight_id="insight-123",
            channel=DeliveryChannel.SLACK,
            status=DeliveryStatus.SENT,
            timestamp=time.time(),
            recipient="user@example.com",
        )

        assert receipt.insight_id == "insight-123"
        assert receipt.channel == DeliveryChannel.SLACK
        assert receipt.status == DeliveryStatus.SENT
        assert receipt.error_message is None

    def test_failed_receipt(self):
        """Test failed delivery receipt."""
        receipt = DeliveryReceipt(
            insight_id="insight-456",
            channel=DeliveryChannel.EMAIL,
            status=DeliveryStatus.FAILED,
            timestamp=time.time(),
            recipient="user@example.com",
            error_message="SMTP connection failed",
        )

        assert receipt.status == DeliveryStatus.FAILED
        assert receipt.error_message == "SMTP connection failed"
