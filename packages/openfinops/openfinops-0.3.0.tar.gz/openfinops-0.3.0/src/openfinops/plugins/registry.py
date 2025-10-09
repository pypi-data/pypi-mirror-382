"""
Plugin Registry
===============

Central registry for plugin discovery, registration, and management.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, List, Type, Optional, Any
import importlib
import pkgutil
import logging
import sys
from pathlib import Path

from .base import PluginBase, PluginMetadata, PluginType, PluginState

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Central registry for all plugins.

    The registry maintains a catalog of available plugins and their instances.
    It provides methods for:
    - Registering plugin classes
    - Loading and unloading plugin instances
    - Discovering plugins from packages
    - Querying available plugins

    Example:
        >>> from openfinops.plugins import registry
        >>>
        >>> # List all registered plugins
        >>> plugins = registry.list_plugins()
        >>>
        >>> # Load a plugin
        >>> plugin = registry.load_plugin("aws-telemetry", config={
        ...     "region": "us-west-2"
        ... })
        >>>
        >>> # Use the plugin
        >>> data = plugin.collect_telemetry()
        >>>
        >>> # Unload when done
        >>> registry.unload_plugin("aws-telemetry")
    """

    def __init__(self):
        """Initialize the plugin registry."""
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        self._plugin_instances: Dict[str, PluginBase] = {}
        self._discovery_paths: List[str] = []

    def register(
        self,
        plugin_class: Type[PluginBase],
        replace: bool = False
    ) -> None:
        """
        Register a plugin class.

        Args:
            plugin_class: Plugin class to register
            replace: If True, replace existing plugin with same name

        Raises:
            ValueError: If plugin already registered and replace=False
            TypeError: If plugin_class is not a subclass of PluginBase
        """
        if not issubclass(plugin_class, PluginBase):
            raise TypeError(
                f"{plugin_class.__name__} must be a subclass of PluginBase"
            )

        # Get metadata to validate and get name
        try:
            temp_instance = plugin_class()
            metadata = temp_instance.metadata
            plugin_name = metadata.name
        except Exception as e:
            raise ValueError(
                f"Failed to get metadata from {plugin_class.__name__}: {e}"
            )

        if plugin_name in self._plugin_classes and not replace:
            logger.warning(
                f"Plugin '{plugin_name}' already registered. "
                f"Use replace=True to overwrite."
            )
            return

        self._plugin_classes[plugin_name] = plugin_class
        logger.info(
            f"Registered plugin: {plugin_name} v{metadata.version} "
            f"(type: {metadata.plugin_type.value})"
        )

    def unregister(self, plugin_name: str) -> None:
        """
        Unregister a plugin class.

        Args:
            plugin_name: Name of plugin to unregister

        Raises:
            ValueError: If plugin is currently loaded
        """
        if plugin_name in self._plugin_instances:
            raise ValueError(
                f"Cannot unregister plugin '{plugin_name}' while it is loaded. "
                f"Unload it first."
            )

        if plugin_name in self._plugin_classes:
            del self._plugin_classes[plugin_name]
            logger.info(f"Unregistered plugin: {plugin_name}")

    def load_plugin(
        self,
        plugin_name: str,
        config: Optional[Dict[str, Any]] = None,
        auto_initialize: bool = True
    ) -> PluginBase:
        """
        Load and initialize a plugin.

        Args:
            plugin_name: Name of plugin to load
            config: Plugin configuration dictionary
            auto_initialize: If True, automatically call initialize()

        Returns:
            Loaded plugin instance

        Raises:
            ValueError: If plugin not found or already loaded
            RuntimeError: If plugin initialization fails
        """
        if plugin_name not in self._plugin_classes:
            raise ValueError(
                f"Plugin '{plugin_name}' not found in registry. "
                f"Available plugins: {list(self._plugin_classes.keys())}"
            )

        if plugin_name in self._plugin_instances:
            logger.warning(f"Plugin '{plugin_name}' already loaded")
            return self._plugin_instances[plugin_name]

        plugin_class = self._plugin_classes[plugin_name]

        try:
            # Create instance
            plugin = plugin_class(config=config)
            plugin.state = PluginState.INITIALIZING

            # Validate configuration
            if not plugin.validate_config():
                raise ValueError(f"Invalid configuration for plugin '{plugin_name}'")

            # Initialize if requested
            if auto_initialize:
                plugin.initialize()
                plugin.state = PluginState.READY
                import time
                plugin._initialized_at = time.time()

            self._plugin_instances[plugin_name] = plugin
            logger.info(f"Loaded plugin: {plugin_name}")

            return plugin

        except Exception as e:
            logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            raise RuntimeError(f"Plugin initialization failed: {e}")

    def unload_plugin(self, plugin_name: str) -> None:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of plugin to unload

        Raises:
            ValueError: If plugin not currently loaded
        """
        if plugin_name not in self._plugin_instances:
            raise ValueError(f"Plugin '{plugin_name}' is not loaded")

        plugin = self._plugin_instances[plugin_name]

        try:
            plugin.shutdown()
            plugin.state = PluginState.SHUTDOWN
        except Exception as e:
            logger.error(f"Error during plugin shutdown: {e}")

        del self._plugin_instances[plugin_name]
        logger.info(f"Unloaded plugin: {plugin_name}")

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """
        Get a loaded plugin instance.

        Args:
            plugin_name: Name of plugin

        Returns:
            Plugin instance if loaded, None otherwise
        """
        return self._plugin_instances.get(plugin_name)

    def list_plugins(
        self,
        plugin_type: Optional[PluginType] = None,
        loaded_only: bool = False,
        tags: Optional[List[str]] = None
    ) -> List[PluginMetadata]:
        """
        List available plugins.

        Args:
            plugin_type: Filter by plugin type
            loaded_only: If True, only show loaded plugins
            tags: Filter by tags (any tag match)

        Returns:
            List of plugin metadata
        """
        plugins_dict = (
            self._plugin_instances if loaded_only else self._plugin_classes
        )

        results = []
        for name, plugin_obj in plugins_dict.items():
            # Get metadata
            if loaded_only:
                metadata = plugin_obj.metadata
            else:
                # Create temporary instance to get metadata
                try:
                    temp = plugin_obj()
                    metadata = temp.metadata
                except Exception as e:
                    logger.warning(f"Failed to get metadata for {name}: {e}")
                    continue

            # Apply filters
            if plugin_type and metadata.plugin_type != plugin_type:
                continue

            if tags and not any(tag in metadata.tags for tag in tags):
                continue

            results.append(metadata)

        return results

    def discover_plugins(
        self,
        package_name: str = "openfinops_plugins",
        auto_register: bool = True
    ) -> List[str]:
        """
        Auto-discover plugins from a package.

        Searches for plugin classes in the specified package and optionally
        registers them automatically.

        Args:
            package_name: Package name to search for plugins
            auto_register: If True, automatically register discovered plugins

        Returns:
            List of discovered plugin names
        """
        discovered = []

        try:
            package = importlib.import_module(package_name)
        except ImportError:
            logger.debug(f"Plugin package '{package_name}' not found")
            return discovered

        # Iterate through modules in package
        if hasattr(package, '__path__'):
            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                full_module_name = f"{package_name}.{module_name}"

                try:
                    module = importlib.import_module(full_module_name)

                    # Look for plugin classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)

                        # Check if it's a plugin class
                        if (isinstance(attr, type) and
                            issubclass(attr, PluginBase) and
                            attr != PluginBase and
                            not attr.__name__.endswith('Plugin')):  # Exclude base classes

                            if auto_register:
                                self.register(attr)

                            discovered.append(attr_name)
                            logger.debug(f"Discovered plugin: {attr_name}")

                except Exception as e:
                    logger.error(
                        f"Failed to load plugin module '{full_module_name}': {e}"
                    )

        return discovered

    def discover_from_path(self, path: str) -> List[str]:
        """
        Discover plugins from a filesystem path.

        Args:
            path: Path to search for plugins

        Returns:
            List of discovered plugin names
        """
        discovered = []
        plugin_path = Path(path)

        if not plugin_path.exists():
            logger.warning(f"Plugin path does not exist: {path}")
            return discovered

        # Add path to sys.path if not already there
        path_str = str(plugin_path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)
            self._discovery_paths.append(path_str)

        # Search for Python files
        for py_file in plugin_path.glob("**/*.py"):
            if py_file.stem.startswith("_"):
                continue

            # Try to import and discover plugins
            try:
                module_name = py_file.stem
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Look for plugin classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            issubclass(attr, PluginBase) and
                            attr != PluginBase):

                            self.register(attr)
                            discovered.append(attr_name)

            except Exception as e:
                logger.error(f"Failed to load plugin from {py_file}: {e}")

        return discovered

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with registry statistics
        """
        stats = {
            "total_registered": len(self._plugin_classes),
            "total_loaded": len(self._plugin_instances),
            "by_type": {},
            "by_state": {},
        }

        # Count by type
        for metadata in self.list_plugins():
            type_name = metadata.plugin_type.value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1

        # Count by state (loaded plugins only)
        for plugin in self._plugin_instances.values():
            state_name = plugin.state.value
            stats["by_state"][state_name] = stats["by_state"].get(state_name, 0) + 1

        return stats

    def reload_plugin(
        self,
        plugin_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> PluginBase:
        """
        Reload a plugin (unload and load again).

        Args:
            plugin_name: Name of plugin to reload
            config: New configuration (optional)

        Returns:
            Reloaded plugin instance
        """
        # Get current config if none provided
        if config is None and plugin_name in self._plugin_instances:
            config = self._plugin_instances[plugin_name].config

        # Unload if loaded
        if plugin_name in self._plugin_instances:
            self.unload_plugin(plugin_name)

        # Load again
        return self.load_plugin(plugin_name, config=config)

    def unload_all(self) -> None:
        """Unload all loaded plugins."""
        plugin_names = list(self._plugin_instances.keys())
        for plugin_name in plugin_names:
            try:
                self.unload_plugin(plugin_name)
            except Exception as e:
                logger.error(f"Error unloading plugin {plugin_name}: {e}")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<PluginRegistry "
            f"registered={len(self._plugin_classes)} "
            f"loaded={len(self._plugin_instances)}>"
        )


# Global plugin registry instance
registry = PluginRegistry()
