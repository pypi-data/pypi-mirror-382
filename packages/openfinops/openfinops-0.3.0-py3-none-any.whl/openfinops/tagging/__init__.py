"""
Auto-Tagging and Cost Attribution System
=========================================

Automated resource tagging, virtual tagging, and tag-based cost attribution.

This module provides:
- Automated resource tagging based on patterns
- Virtual tagging (tag inference from naming conventions, patterns)
- Tag policy enforcement
- Tag-based cost attribution
- Tag recommendations

Example:
    >>> from openfinops.tagging import TaggingEngine, TagPolicy
    >>>
    >>> engine = TaggingEngine()
    >>>
    >>> # Define tag policy
    >>> policy = TagPolicy(
    ...     name="production_tags",
    ...     required_tags=["environment", "team", "cost_center"],
    ...     tag_patterns={"environment": r"^(prod|staging|dev)$"}
    ... )
    >>> engine.add_policy(policy)
    >>>
    >>> # Auto-tag resources
    >>> resource = {"id": "i-12345", "name": "prod-web-server-1"}
    >>> tags = engine.auto_tag(resource)
    >>> print(tags)  # {'environment': 'prod', 'service': 'web'}
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from .tagging_engine import TaggingEngine, TagSuggestion
from .virtual_tagger import VirtualTagger, VirtualTag
from .tag_policy import TagPolicy, TagPolicyViolation, PolicySeverity, PolicyEnforcer
from .cost_attribution import TagBasedAttribution, AttributionResult

__all__ = [
    # Core tagging
    "TaggingEngine",
    "TagSuggestion",
    # Virtual tagging
    "VirtualTagger",
    "VirtualTag",
    # Policy enforcement
    "TagPolicy",
    "TagPolicyViolation",
    "PolicySeverity",
    "PolicyEnforcer",
    # Cost attribution
    "TagBasedAttribution",
    "AttributionResult",
]
