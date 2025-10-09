"""Attribution Plugin Base Class"""

from abc import abstractmethod
from typing import List, Dict, Any
from .base import PluginBase
from openfinops.observability.cost_observatory import CostEntry


class AttributionPlugin(PluginBase):
    """
    Base class for cost attribution plugins.

    Attribution plugins implement custom logic for splitting and
    attributing costs to different entities.
    """

    @abstractmethod
    def attribute_cost(
        self,
        cost_entry: CostEntry,
        context: Dict[str, Any]
    ) -> List[CostEntry]:
        """
        Attribute cost to entities.

        Args:
            cost_entry: The cost entry to attribute
            context: Additional context for attribution

        Returns:
            List of attributed cost entries
        """
        pass
