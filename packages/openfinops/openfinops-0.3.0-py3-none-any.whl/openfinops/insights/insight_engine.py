"""
Insight Engine
==============

Core engine for generating persona-specific insights.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class InsightPriority(Enum):
    """Insight priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InsightCategory(Enum):
    """Insight categories."""
    COST_OPTIMIZATION = "cost_optimization"
    EFFICIENCY = "efficiency"
    BUDGET = "budget"
    ANOMALY = "anomaly"
    FORECAST = "forecast"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    RECOMMENDATION = "recommendation"


@dataclass
class Insight:
    """
    A single insight.

    Attributes:
        title: Brief title of the insight
        description: Detailed description
        priority: Priority level
        category: Insight category
        impact: Estimated impact (financial, operational, etc.)
        recommendation: Actionable recommendation
        metadata: Additional context
        confidence: Confidence score (0.0-1.0)
    """
    title: str
    description: str
    priority: InsightPriority
    category: InsightCategory
    impact: str
    recommendation: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def __post_init__(self):
        """Validate insight data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


class InsightGenerator(ABC):
    """Base class for persona-specific insight generators."""

    @abstractmethod
    def generate(
        self,
        hub: Any,
        cost_obs: Any,
        time_range: str = "30d"
    ) -> List[Insight]:
        """
        Generate insights for this persona.

        Args:
            hub: ObservabilityHub instance
            cost_obs: CostObservatory instance
            time_range: Time range for analysis

        Returns:
            List of Insight objects
        """
        pass


class InsightEngine:
    """
    Central engine for generating persona-specific insights.

    Example:
        >>> engine = InsightEngine(hub=hub, cost_obs=cost_obs)
        >>> insights = engine.generate_insights(persona="cfo", time_range="30d")
    """

    def __init__(self, hub: Any = None, cost_obs: Any = None):
        """
        Initialize insight engine.

        Args:
            hub: ObservabilityHub instance
            cost_obs: CostObservatory instance
        """
        self.hub = hub
        self.cost_obs = cost_obs
        self._generators: Dict[str, InsightGenerator] = {}

        # Register default generators
        self._register_default_generators()

    def _register_default_generators(self):
        """Register default persona insight generators."""
        try:
            from .personas.cfo import CFOInsightGenerator
            from .personas.engineer import EngineerInsightGenerator
            from .personas.finance import FinanceInsightGenerator
            from .personas.business_lead import BusinessLeadInsightGenerator

            self.register_generator("cfo", CFOInsightGenerator())
            self.register_generator("engineer", EngineerInsightGenerator())
            self.register_generator("finance", FinanceInsightGenerator())
            self.register_generator("business_lead", BusinessLeadInsightGenerator())

            logger.info("Registered default insight generators")
        except Exception as e:
            logger.warning(f"Failed to register some default generators: {e}")

    def register_generator(self, persona: str, generator: InsightGenerator):
        """
        Register an insight generator for a persona.

        Args:
            persona: Persona identifier
            generator: InsightGenerator instance
        """
        self._generators[persona] = generator
        logger.debug(f"Registered insight generator for persona: {persona}")

    def generate_insights(
        self,
        persona: str,
        time_range: str = "30d",
        min_priority: Optional[InsightPriority] = None,
        categories: Optional[List[InsightCategory]] = None
    ) -> List[Insight]:
        """
        Generate insights for a specific persona.

        Args:
            persona: Persona identifier (cfo, engineer, finance, business_lead)
            time_range: Time range for analysis (e.g., "7d", "30d", "90d")
            min_priority: Minimum priority level to include
            categories: Filter by specific categories

        Returns:
            List of Insight objects (empty list if persona not found)
        """
        if persona not in self._generators:
            logger.warning(
                f"No generator found for persona '{persona}'. "
                f"Available: {list(self._generators.keys())}"
            )
            return []

        generator = self._generators[persona]

        # Generate insights
        insights = generator.generate(
            hub=self.hub,
            cost_obs=self.cost_obs,
            time_range=time_range
        )

        # Apply filters
        filtered_insights = insights

        if min_priority:
            priority_order = {
                InsightPriority.LOW: 0,
                InsightPriority.MEDIUM: 1,
                InsightPriority.HIGH: 2,
                InsightPriority.CRITICAL: 3,
            }
            min_level = priority_order[min_priority]
            filtered_insights = [
                i for i in filtered_insights
                if priority_order[i.priority] >= min_level
            ]

        if categories:
            filtered_insights = [
                i for i in filtered_insights
                if i.category in categories
            ]

        # Sort by priority (critical first)
        priority_order = {
            InsightPriority.CRITICAL: 0,
            InsightPriority.HIGH: 1,
            InsightPriority.MEDIUM: 2,
            InsightPriority.LOW: 3,
        }
        filtered_insights.sort(key=lambda x: priority_order[x.priority])

        logger.info(
            f"Generated {len(filtered_insights)} insights for persona '{persona}'"
        )

        return filtered_insights

    def get_insight_summary(self, insights: List[Insight]) -> Dict[str, Any]:
        """
        Get summary statistics for a list of insights.

        Args:
            insights: List of Insight objects

        Returns:
            Summary dictionary
        """
        summary = {
            "total_count": len(insights),
            "by_priority": {},
            "by_category": {},
            "critical_count": 0,
        }

        for insight in insights:
            # Count by priority
            priority = insight.priority.value
            summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1

            # Count by category
            category = insight.category.value
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1

            # Count critical
            if insight.priority == InsightPriority.CRITICAL:
                summary["critical_count"] += 1

        return summary

    def list_personas(self) -> List[str]:
        """Get list of available personas."""
        return list(self._generators.keys())
