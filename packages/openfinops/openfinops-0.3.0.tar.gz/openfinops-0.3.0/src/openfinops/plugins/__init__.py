"""
OpenFinOps Plugin System
========================

A powerful plugin architecture for extending OpenFinOps functionality.

This module provides the core plugin infrastructure including:
- Plugin base classes for different plugin types
- Plugin registry for discovery and management
- Hook system for interception points
- Decorators for easy plugin development

Plugin Types:
-------------
- TelemetryPlugin: Custom data collectors
- AttributionPlugin: Custom cost attribution logic
- RecommendationPlugin: Custom optimization rules
- DashboardPlugin: Custom dashboard widgets
- IntegrationPlugin: External tool integrations
- NotificationPlugin: Custom notification channels
- PolicyPlugin: Custom policy rules

Example:
--------
    >>> from openfinops.plugins import registry, TelemetryPlugin
    >>>
    >>> # Register and load a plugin
    >>> plugin = registry.load_plugin("my-plugin", config={
    ...     "api_key": "secret"
    ... })
    >>>
    >>> # Use the plugin
    >>> data = plugin.collect_telemetry()

For detailed documentation, see:
https://github.com/openfinops/openfinops/blob/main/docs/PLUGIN_ARCHITECTURE.md
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from .base import (
    PluginBase,
    PluginMetadata,
    PluginType,
    PluginState,
)
from .registry import PluginRegistry, registry
from .decorators import plugin, hook, requires_config
from .manager import PluginManager
from .telemetry import TelemetryPlugin
from .attribution import AttributionPlugin
from .recommendation import RecommendationPlugin
from .dashboard import DashboardPlugin
from .integration import IntegrationPlugin
from .notification import NotificationPlugin
from .policy import PolicyPlugin

__all__ = [
    # Core classes
    "PluginBase",
    "PluginMetadata",
    "PluginType",
    "PluginState",

    # Registry
    "PluginRegistry",
    "registry",

    # Decorators
    "plugin",
    "hook",
    "requires_config",

    # Manager
    "PluginManager",

    # Plugin types
    "TelemetryPlugin",
    "AttributionPlugin",
    "RecommendationPlugin",
    "DashboardPlugin",
    "IntegrationPlugin",
    "NotificationPlugin",
    "PolicyPlugin",
]

__version__ = "0.3.0"
