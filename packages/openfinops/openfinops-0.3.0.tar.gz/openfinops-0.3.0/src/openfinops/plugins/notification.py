"""Notification Plugin Base Class"""

from abc import abstractmethod
from typing import Dict, Any
from .base import PluginBase


class NotificationPlugin(PluginBase):
    """
    Base class for notification channel plugins.

    Notification plugins send alerts and messages through various channels.
    """

    @abstractmethod
    def send_notification(
        self,
        message: str,
        priority: str = "normal",
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Send a notification.

        Args:
            message: Message to send
            priority: Priority level (low, normal, high, critical)
            metadata: Additional metadata

        Returns:
            True if sent successfully, False otherwise
        """
        pass
