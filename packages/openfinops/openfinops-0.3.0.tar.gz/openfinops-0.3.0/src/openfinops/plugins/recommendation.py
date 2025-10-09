"""Recommendation Plugin Base Class"""

from abc import abstractmethod
from typing import List
from dataclasses import dataclass
from .base import PluginBase


@dataclass
class Recommendation:
    """Optimization recommendation."""
    resource_id: str
    recommendation_type: str
    current_state: str
    recommended_state: str
    annual_savings: float
    confidence: float
    implementation_effort: str
    description: str


class RecommendationPlugin(PluginBase):
    """
    Base class for optimization recommendation plugins.

    Recommendation plugins analyze infrastructure and suggest optimizations.
    """

    @abstractmethod
    def generate_recommendations(self, **kwargs) -> List[Recommendation]:
        """
        Generate optimization recommendations.

        Returns:
            List of Recommendation objects
        """
        pass
