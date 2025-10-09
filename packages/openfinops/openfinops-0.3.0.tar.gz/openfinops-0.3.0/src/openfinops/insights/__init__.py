"""
Persona-Specific Insights System
=================================

Intelligent insight generation tailored to different organizational roles.

This module provides:
- Context-aware insight generation
- Role-based insights (CFO, Engineer, Finance, Business Lead)
- Intelligent prioritization
- Actionable recommendations

Example:
    >>> from openfinops.insights import InsightEngine
    >>> from openfinops.observability import ObservabilityHub, CostObservatory
    >>>
    >>> hub = ObservabilityHub()
    >>> cost_obs = CostObservatory()
    >>> engine = InsightEngine(hub=hub, cost_obs=cost_obs)
    >>>
    >>> # Generate CFO insights
    >>> insights = engine.generate_insights(persona="cfo", time_range="30d")
    >>> for insight in insights:
    ...     print(f"{insight.title}: {insight.description}")
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from .insight_engine import InsightEngine, Insight, InsightPriority, InsightCategory
from .personas.cfo import CFOInsightGenerator
from .personas.engineer import EngineerInsightGenerator
from .personas.finance import FinanceInsightGenerator
from .personas.business_lead import BusinessLeadInsightGenerator
from .delivery import (
    InsightDeliveryEngine,
    DeliveryChannel,
    DeliveryStatus,
    ChannelConfig,
    PersonaNotificationPreferences,
    DeliveryReceipt,
)

__all__ = [
    # Core insight engine
    "InsightEngine",
    "Insight",
    "InsightPriority",
    "InsightCategory",
    # Persona generators
    "CFOInsightGenerator",
    "EngineerInsightGenerator",
    "FinanceInsightGenerator",
    "BusinessLeadInsightGenerator",
    # Delivery system
    "InsightDeliveryEngine",
    "DeliveryChannel",
    "DeliveryStatus",
    "ChannelConfig",
    "PersonaNotificationPreferences",
    "DeliveryReceipt",
]
