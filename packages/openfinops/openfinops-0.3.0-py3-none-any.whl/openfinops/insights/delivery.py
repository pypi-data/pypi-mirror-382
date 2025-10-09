"""
Insight Delivery System
=======================

Routes and delivers persona-specific insights through various notification channels.

Features:
- Multi-channel delivery (Slack, Email, Teams, PagerDuty, etc.)
- Priority-based routing
- Batching and scheduling
- Delivery tracking
- Channel preferences per persona
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import logging
from collections import defaultdict

from .insight_engine import Insight, InsightPriority

logger = logging.getLogger(__name__)


class DeliveryChannel(Enum):
    """Supported notification channels."""

    SLACK = "slack"
    EMAIL = "email"
    TEAMS = "teams"
    PAGERDUTY = "pagerduty"
    WEBHOOK = "webhook"
    SMS = "sms"
    IN_APP = "in_app"


class DeliveryStatus(Enum):
    """Delivery status tracking."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SCHEDULED = "scheduled"
    BATCHED = "batched"


@dataclass
class DeliveryReceipt:
    """Receipt for insight delivery."""

    insight_id: str
    channel: DeliveryChannel
    status: DeliveryStatus
    timestamp: float
    recipient: str
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChannelConfig:
    """Configuration for a notification channel."""

    channel: DeliveryChannel
    enabled: bool = True
    priority_threshold: InsightPriority = InsightPriority.LOW
    batch_size: int = 10
    batch_interval_seconds: int = 3600  # 1 hour
    rate_limit_per_hour: int = 100
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonaNotificationPreferences:
    """Notification preferences for a persona."""

    persona: str
    channels: List[ChannelConfig]
    quiet_hours_start: Optional[int] = None  # Hour in 24h format
    quiet_hours_end: Optional[int] = None
    timezone: str = "UTC"


class InsightDeliveryEngine:
    """
    Central engine for delivering insights to personas.

    Handles routing, batching, scheduling, and delivery tracking.
    """

    # Priority ordering for comparison
    PRIORITY_ORDER = {
        InsightPriority.LOW: 0,
        InsightPriority.MEDIUM: 1,
        InsightPriority.HIGH: 2,
        InsightPriority.CRITICAL: 3,
    }

    def __init__(self):
        """Initialize the delivery engine."""
        self._channel_handlers: Dict[DeliveryChannel, Callable] = {}
        self._preferences: Dict[str, PersonaNotificationPreferences] = {}
        self._delivery_history: List[DeliveryReceipt] = []
        self._pending_batches: Dict[str, List[Insight]] = defaultdict(list)
        self._last_batch_sent: Dict[str, float] = {}
        self._hourly_counts: Dict[str, int] = defaultdict(int)

    def register_channel_handler(
        self, channel: DeliveryChannel, handler: Callable[[Insight, Dict[str, Any]], bool]
    ) -> None:
        """
        Register a notification channel handler.

        Args:
            channel: The notification channel type
            handler: Callable that sends the notification
                     Returns True if successful, False otherwise
        """
        self._channel_handlers[channel] = handler
        logger.info(f"Registered handler for channel: {channel.value}")

    def configure_persona_preferences(
        self, preferences: PersonaNotificationPreferences
    ) -> None:
        """
        Configure notification preferences for a persona.

        Args:
            preferences: PersonaNotificationPreferences configuration
        """
        self._preferences[preferences.persona] = preferences
        logger.info(f"Configured preferences for persona: {preferences.persona}")

    def deliver_insight(
        self, insight: Insight, persona: str, recipient: str, force: bool = False
    ) -> List[DeliveryReceipt]:
        """
        Deliver an insight to a persona through configured channels.

        Args:
            insight: The insight to deliver
            persona: Target persona
            recipient: Recipient identifier (email, user ID, etc.)
            force: Force immediate delivery, bypass batching

        Returns:
            List of delivery receipts
        """
        receipts = []

        # Get persona preferences
        preferences = self._preferences.get(persona)
        if not preferences:
            logger.warning(f"No preferences configured for persona: {persona}")
            return receipts

        # Check quiet hours
        if not force and self._is_quiet_hours(preferences):
            logger.info(f"Skipping delivery during quiet hours for {persona}")
            # Schedule for later
            for channel_config in preferences.channels:
                receipts.append(
                    DeliveryReceipt(
                        insight_id=id(insight),
                        channel=channel_config.channel,
                        status=DeliveryStatus.SCHEDULED,
                        timestamp=time.time(),
                        recipient=recipient,
                        metadata={"reason": "quiet_hours"},
                    )
                )
            return receipts

        # Deliver through each configured channel
        for channel_config in preferences.channels:
            if not channel_config.enabled:
                continue

            # Check priority threshold
            insight_level = self.PRIORITY_ORDER[insight.priority]
            threshold_level = self.PRIORITY_ORDER[channel_config.priority_threshold]
            if insight_level < threshold_level:
                logger.debug(
                    f"Insight priority {insight.priority} below threshold "
                    f"{channel_config.priority_threshold} for {channel_config.channel}"
                )
                continue

            # Check rate limits
            if self._is_rate_limited(channel_config, persona):
                logger.warning(
                    f"Rate limit exceeded for {channel_config.channel} / {persona}"
                )
                receipts.append(
                    DeliveryReceipt(
                        insight_id=id(insight),
                        channel=channel_config.channel,
                        status=DeliveryStatus.FAILED,
                        timestamp=time.time(),
                        recipient=recipient,
                        error_message="Rate limit exceeded",
                    )
                )
                continue

            # Handle batching
            if not force and self._should_batch(insight, channel_config):
                batch_key = f"{persona}:{channel_config.channel.value}"
                self._pending_batches[batch_key].append(insight)
                receipts.append(
                    DeliveryReceipt(
                        insight_id=id(insight),
                        channel=channel_config.channel,
                        status=DeliveryStatus.BATCHED,
                        timestamp=time.time(),
                        recipient=recipient,
                        metadata={"batch_size": len(self._pending_batches[batch_key])},
                    )
                )
                continue

            # Send immediately
            receipt = self._send_insight(
                insight, channel_config.channel, recipient, channel_config.config
            )
            receipts.append(receipt)

        self._delivery_history.extend(receipts)
        return receipts

    def deliver_batch(
        self, insights: List[Insight], persona: str, recipient: str
    ) -> List[DeliveryReceipt]:
        """
        Deliver a batch of insights.

        Args:
            insights: List of insights to deliver
            persona: Target persona
            recipient: Recipient identifier

        Returns:
            List of delivery receipts
        """
        receipts = []

        preferences = self._preferences.get(persona)
        if not preferences:
            return receipts

        for channel_config in preferences.channels:
            if not channel_config.enabled:
                continue

            # Filter by priority
            threshold_level = self.PRIORITY_ORDER[channel_config.priority_threshold]
            filtered_insights = [
                i
                for i in insights
                if self.PRIORITY_ORDER[i.priority] >= threshold_level
            ]

            if not filtered_insights:
                continue

            # Send batch
            receipt = self._send_batch(
                filtered_insights, channel_config.channel, recipient, channel_config.config
            )
            receipts.append(receipt)

        self._delivery_history.extend(receipts)
        return receipts

    def process_pending_batches(self) -> List[DeliveryReceipt]:
        """
        Process all pending batches that are ready to send.

        Returns:
            List of delivery receipts
        """
        receipts = []
        current_time = time.time()

        for batch_key, insights in list(self._pending_batches.items()):
            persona, channel_str = batch_key.split(":")
            channel = DeliveryChannel(channel_str)

            preferences = self._preferences.get(persona)
            if not preferences:
                continue

            channel_config = next(
                (c for c in preferences.channels if c.channel == channel), None
            )
            if not channel_config:
                continue

            # Check if batch is ready
            last_sent = self._last_batch_sent.get(batch_key, 0)
            time_since_last = current_time - last_sent
            batch_size = len(insights)

            if (
                batch_size >= channel_config.batch_size
                or time_since_last >= channel_config.batch_interval_seconds
            ):
                # Send batch
                # For now, use first insight's recipient (in production, use proper tracking)
                receipt = self._send_batch(
                    insights,
                    channel,
                    f"batch_{persona}",  # Placeholder
                    channel_config.config,
                )
                receipts.append(receipt)

                # Clear batch
                self._pending_batches[batch_key] = []
                self._last_batch_sent[batch_key] = current_time

        return receipts

    def get_delivery_stats(
        self, persona: Optional[str] = None, time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get delivery statistics.

        Args:
            persona: Filter by persona (optional)
            time_window_hours: Time window for statistics

        Returns:
            Dictionary with delivery statistics
        """
        cutoff_time = time.time() - (time_window_hours * 3600)

        # Filter receipts
        receipts = [r for r in self._delivery_history if r.timestamp >= cutoff_time]

        if persona:
            # This is simplified - in production, track persona with receipt
            pass

        stats = {
            "total_deliveries": len(receipts),
            "by_status": defaultdict(int),
            "by_channel": defaultdict(int),
            "success_rate": 0.0,
            "failed_deliveries": [],
        }

        for receipt in receipts:
            stats["by_status"][receipt.status.value] += 1
            stats["by_channel"][receipt.channel.value] += 1

            if receipt.status == DeliveryStatus.FAILED:
                stats["failed_deliveries"].append(
                    {
                        "insight_id": receipt.insight_id,
                        "channel": receipt.channel.value,
                        "error": receipt.error_message,
                        "timestamp": receipt.timestamp,
                    }
                )

        # Calculate success rate
        sent = stats["by_status"].get("sent", 0)
        failed = stats["by_status"].get("failed", 0)
        total = sent + failed
        if total > 0:
            stats["success_rate"] = sent / total

        return dict(stats)

    def _send_insight(
        self, insight: Insight, channel: DeliveryChannel, recipient: str, config: Dict[str, Any]
    ) -> DeliveryReceipt:
        """Send a single insight through a channel."""
        handler = self._channel_handlers.get(channel)
        if not handler:
            return DeliveryReceipt(
                insight_id=id(insight),
                channel=channel,
                status=DeliveryStatus.FAILED,
                timestamp=time.time(),
                recipient=recipient,
                error_message=f"No handler registered for {channel.value}",
            )

        try:
            success = handler(insight, config)
            status = DeliveryStatus.SENT if success else DeliveryStatus.FAILED

            # Update rate limit counter
            self._increment_rate_counter(channel, recipient)

            return DeliveryReceipt(
                insight_id=id(insight),
                channel=channel,
                status=status,
                timestamp=time.time(),
                recipient=recipient,
            )
        except Exception as e:
            logger.exception(f"Failed to send insight via {channel.value}")
            return DeliveryReceipt(
                insight_id=id(insight),
                channel=channel,
                status=DeliveryStatus.FAILED,
                timestamp=time.time(),
                recipient=recipient,
                error_message=str(e),
            )

    def _send_batch(
        self,
        insights: List[Insight],
        channel: DeliveryChannel,
        recipient: str,
        config: Dict[str, Any],
    ) -> DeliveryReceipt:
        """Send a batch of insights."""
        # For batch sending, we'd modify the handler to accept a list
        # For now, send individually and return aggregate receipt
        batch_id = f"batch_{int(time.time())}"

        success_count = 0
        for insight in insights:
            receipt = self._send_insight(insight, channel, recipient, config)
            if receipt.status == DeliveryStatus.SENT:
                success_count += 1

        return DeliveryReceipt(
            insight_id=batch_id,
            channel=channel,
            status=DeliveryStatus.SENT if success_count > 0 else DeliveryStatus.FAILED,
            timestamp=time.time(),
            recipient=recipient,
            metadata={
                "batch_size": len(insights),
                "success_count": success_count,
                "failed_count": len(insights) - success_count,
            },
        )

    def _is_quiet_hours(self, preferences: PersonaNotificationPreferences) -> bool:
        """Check if current time is within quiet hours."""
        if preferences.quiet_hours_start is None or preferences.quiet_hours_end is None:
            return False

        # Simplified - in production, use proper timezone handling
        from datetime import datetime

        current_hour = datetime.now().hour

        start = preferences.quiet_hours_start
        end = preferences.quiet_hours_end

        if start < end:
            return start <= current_hour < end
        else:  # Crosses midnight
            return current_hour >= start or current_hour < end

    def _should_batch(self, insight: Insight, channel_config: ChannelConfig) -> bool:
        """Determine if insight should be batched."""
        # Critical and HIGH priority insights are never batched
        if insight.priority in (InsightPriority.CRITICAL, InsightPriority.HIGH):
            return False

        # Check if batching is enabled
        return channel_config.batch_size > 1

    def _is_rate_limited(self, channel_config: ChannelConfig, persona: str) -> bool:
        """Check if channel is rate limited."""
        rate_key = f"{channel_config.channel.value}:{persona}"
        current_count = self._hourly_counts.get(rate_key, 0)
        return current_count >= channel_config.rate_limit_per_hour

    def _increment_rate_counter(self, channel: DeliveryChannel, recipient: str) -> None:
        """Increment rate limit counter."""
        # Simplified - in production, use sliding window
        rate_key = f"{channel.value}:{recipient}"
        self._hourly_counts[rate_key] += 1
