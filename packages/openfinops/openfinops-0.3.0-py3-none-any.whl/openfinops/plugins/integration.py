"""Integration Plugin Base Class"""

from abc import abstractmethod
from typing import Any, Dict
from .base import PluginBase


class IntegrationPlugin(PluginBase):
    """
    Base class for external integration plugins.

    Integration plugins connect OpenFinOps with external tools and services.
    """

    @abstractmethod
    def send_data(self, data: Dict[str, Any]) -> bool:
        """
        Send data to external service.

        Args:
            data: Data to send

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def receive_data(self) -> Dict[str, Any]:
        """
        Receive data from external service.

        Returns:
            Received data
        """
        pass
