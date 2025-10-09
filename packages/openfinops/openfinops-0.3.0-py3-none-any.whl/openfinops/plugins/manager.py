"""
Plugin Manager
==============

High-level plugin management with lifecycle control.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, List, Optional, Any
import logging

from .base import PluginBase, PluginType, PluginState
from .registry import registry

logger = logging.getLogger(__name__)


class PluginManager:
    """
    High-level plugin lifecycle manager.

    Provides convenient methods for managing multiple plugins and their lifecycle.

    Example:
        >>> from openfinops.plugins import PluginManager
        >>>
        >>> manager = PluginManager()
        >>>
        >>> # Load plugins from config
        >>> manager.load_from_config({
        ...     "aws-telemetry": {"region": "us-west-2"},
        ...     "slack-notifications": {"webhook_url": "https://..."},
        ... })
        >>>
        >>> # Get plugin
        >>> aws_plugin = manager.get("aws-telemetry")
        >>>
        >>> # Unload all
        >>> manager.shutdown()
    """

    def __init__(self, auto_discover: bool = True):
        """
        Initialize plugin manager.

        Args:
            auto_discover: If True, automatically discover plugins on startup
        """
        self._registry = registry

        if auto_discover:
            self.discover_plugins()

    def discover_plugins(
        self,
        packages: Optional[List[str]] = None
    ) -> Dict[str, int]:
        """
        Discover plugins from packages.

        Args:
            packages: List of package names to search (default: ["openfinops_plugins"])

        Returns:
            Dictionary with package names and number of discovered plugins
        """
        if packages is None:
            packages = ["openfinops_plugins"]

        discovered = {}
        for package in packages:
            plugins = self._registry.discover_plugins(package)
            discovered[package] = len(plugins)
            if plugins:
                logger.info(
                    f"Discovered {len(plugins)} plugin(s) from '{package}': "
                    f"{', '.join(plugins)}"
                )

        return discovered

    def load(
        self,
        plugin_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> PluginBase:
        """
        Load a plugin.

        Args:
            plugin_name: Name of plugin to load
            config: Plugin configuration

        Returns:
            Loaded plugin instance
        """
        return self._registry.load_plugin(plugin_name, config=config)

    def unload(self, plugin_name: str) -> None:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload
        """
        self._registry.unload_plugin(plugin_name)

    def get(self, plugin_name: str) -> Optional[PluginBase]:
        """
        Get a loaded plugin.

        Args:
            plugin_name: Name of plugin

        Returns:
            Plugin instance if loaded, None otherwise
        """
        return self._registry.get_plugin(plugin_name)

    def load_from_config(self, config: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Load multiple plugins from configuration.

        Args:
            config: Dictionary mapping plugin names to their configurations

        Returns:
            List of successfully loaded plugin names

        Example:
            >>> manager.load_from_config({
            ...     "aws-telemetry": {
            ...         "region": "us-west-2",
            ...         "interval": 300
            ...     },
            ...     "slack-notifications": {
            ...         "webhook_url": "https://hooks.slack.com/..."
            ...     }
            ... })
        """
        loaded = []

        for plugin_name, plugin_config in config.items():
            try:
                self.load(plugin_name, config=plugin_config)
                loaded.append(plugin_name)
                logger.info(f"Loaded plugin from config: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to load plugin '{plugin_name}': {e}")

        return loaded

    def get_by_type(self, plugin_type: PluginType) -> List[PluginBase]:
        """
        Get all loaded plugins of a specific type.

        Args:
            plugin_type: Type of plugins to get

        Returns:
            List of plugin instances
        """
        plugins = []
        for metadata in self._registry.list_plugins(
            plugin_type=plugin_type,
            loaded_only=True
        ):
            plugin = self._registry.get_plugin(metadata.name)
            if plugin:
                plugins.append(plugin)

        return plugins

    def health_check(self) -> Dict[str, Dict[str, Any]]:
        """
        Perform health check on all loaded plugins.

        Returns:
            Dictionary mapping plugin names to health check results
        """
        results = {}

        for metadata in self._registry.list_plugins(loaded_only=True):
            plugin = self._registry.get_plugin(metadata.name)
            if plugin:
                results[metadata.name] = plugin.health_check()

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about loaded plugins.

        Returns:
            Statistics dictionary
        """
        return self._registry.get_statistics()

    def reload(self, plugin_name: str) -> PluginBase:
        """
        Reload a plugin.

        Args:
            plugin_name: Name of plugin to reload

        Returns:
            Reloaded plugin instance
        """
        return self._registry.reload_plugin(plugin_name)

    def reload_all(self) -> List[str]:
        """
        Reload all loaded plugins.

        Returns:
            List of successfully reloaded plugin names
        """
        reloaded = []
        plugin_names = [
            metadata.name
            for metadata in self._registry.list_plugins(loaded_only=True)
        ]

        for plugin_name in plugin_names:
            try:
                self.reload(plugin_name)
                reloaded.append(plugin_name)
                logger.info(f"Reloaded plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"Failed to reload plugin '{plugin_name}': {e}")

        return reloaded

    def shutdown(self) -> None:
        """Shutdown all loaded plugins."""
        self._registry.unload_all()
        logger.info("Plugin manager shut down")

    def list_available(
        self,
        plugin_type: Optional[PluginType] = None
    ) -> List[str]:
        """
        List available plugins.

        Args:
            plugin_type: Filter by plugin type

        Returns:
            List of plugin names
        """
        return [
            metadata.name
            for metadata in self._registry.list_plugins(plugin_type=plugin_type)
        ]

    def list_loaded(self, plugin_type: Optional[PluginType] = None) -> List[str]:
        """
        List loaded plugins.

        Args:
            plugin_type: Filter by plugin type

        Returns:
            List of loaded plugin names
        """
        return [
            metadata.name
            for metadata in self._registry.list_plugins(
                plugin_type=plugin_type,
                loaded_only=True
            )
        ]

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_statistics()
        return (
            f"<PluginManager "
            f"registered={stats['total_registered']} "
            f"loaded={stats['total_loaded']}>"
        )
