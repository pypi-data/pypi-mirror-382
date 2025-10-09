"""Telemetry Plugin Base Class"""

from abc import abstractmethod
from typing import List
from .base import PluginBase, PluginType
from openfinops.observability.cost_observatory import CostEntry


class TelemetryPlugin(PluginBase):
    """
    Base class for telemetry collection plugins.

    Telemetry plugins collect cost and usage data from various sources.
    """

    @abstractmethod
    def collect_telemetry(self) -> List[CostEntry]:
        """
        Collect telemetry data.

        Returns:
            List of CostEntry objects
        """
        pass

    def get_collection_interval(self) -> int:
        """Get recommended collection interval in seconds."""
        return self.get_config_value("collection_interval", default=300)
