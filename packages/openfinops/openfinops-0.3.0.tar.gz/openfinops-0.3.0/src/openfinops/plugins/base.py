"""
Base Plugin Classes
===================

Core abstract base classes for the OpenFinOps plugin system.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import logging
import time

logger = logging.getLogger(__name__)


class PluginType(Enum):
    """Types of plugins supported by OpenFinOps."""

    TELEMETRY = "telemetry"           # Custom data collectors
    ATTRIBUTION = "attribution"        # Custom cost attribution logic
    RECOMMENDATION = "recommendation"  # Custom optimization rules
    DASHBOARD = "dashboard"           # Custom dashboard widgets
    INTEGRATION = "integration"       # External tool integrations
    NOTIFICATION = "notification"     # Custom notification channels
    POLICY = "policy"                 # Custom policy rules


class PluginState(Enum):
    """Plugin lifecycle states."""

    UNINITIALIZED = "uninitialized"  # Plugin class loaded but not initialized
    INITIALIZING = "initializing"     # Initialization in progress
    READY = "ready"                   # Initialized and ready to use
    ERROR = "error"                   # Error during initialization or operation
    SHUTDOWN = "shutdown"             # Plugin has been shut down


@dataclass
class PluginMetadata:
    """
    Plugin metadata information.

    Attributes:
        name: Unique plugin name (e.g., "aws-telemetry")
        version: Plugin version (semantic versioning recommended)
        author: Plugin author name or organization
        description: Brief description of plugin functionality
        plugin_type: Type of plugin (see PluginType enum)
        dependencies: List of required Python packages
        config_schema: JSON schema for configuration validation
        homepage: Plugin homepage or repository URL
        license: License identifier (e.g., "Apache-2.0")
        tags: Tags for categorization and discovery
    """

    name: str
    version: str
    author: str
    description: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    homepage: Optional[str] = None
    license: str = "Apache-2.0"
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate metadata after initialization."""
        if not self.name:
            raise ValueError("Plugin name is required")
        if not self.version:
            raise ValueError("Plugin version is required")
        if not isinstance(self.plugin_type, PluginType):
            raise TypeError("plugin_type must be a PluginType enum")


class PluginBase(ABC):
    """
    Abstract base class for all OpenFinOps plugins.

    All plugins must inherit from this class and implement the required methods.

    Example:
        >>> class MyPlugin(PluginBase):
        ...     @property
        ...     def metadata(self) -> PluginMetadata:
        ...         return PluginMetadata(
        ...             name="my-plugin",
        ...             version="1.0.0",
        ...             author="Me",
        ...             description="My custom plugin",
        ...             plugin_type=PluginType.TELEMETRY,
        ...         )
        ...
        ...     def initialize(self) -> None:
        ...         # Initialize resources
        ...         self._initialized = True
        ...
        ...     def shutdown(self) -> None:
        ...         # Cleanup resources
        ...         self._initialized = False
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the plugin.

        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self._state = PluginState.UNINITIALIZED
        self._error_message: Optional[str] = None
        self._initialized_at: Optional[float] = None
        self._hooks: Dict[str, List[Callable]] = {}

        logger.debug(f"Plugin {self.metadata.name} created")

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """
        Return plugin metadata.

        Returns:
            PluginMetadata instance with plugin information
        """
        pass

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the plugin.

        This method is called when the plugin is loaded. Use it to:
        - Validate configuration
        - Connect to external services
        - Load resources
        - Prepare the plugin for use

        Raises:
            ValueError: If configuration is invalid
            RuntimeError: If initialization fails
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Cleanup when plugin is unloaded.

        This method is called when the plugin is being unloaded. Use it to:
        - Close connections
        - Release resources
        - Save state if needed
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate plugin configuration.

        Override this method to implement custom configuration validation.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.metadata.config_schema:
            return True

        # Basic validation against config_schema
        # In production, use jsonschema library for full validation
        required_keys = [
            key for key, spec in self.metadata.config_schema.items()
            if spec.get("required", False)
        ]

        missing = [key for key in required_keys if key not in self.config]
        if missing:
            logger.error(f"Missing required configuration keys: {missing}")
            return False

        return True

    def get_config_value(
        self,
        key: str,
        default: Any = None,
        required: bool = False
    ) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found
            required: If True, raise ValueError if key not found

        Returns:
            Configuration value

        Raises:
            ValueError: If key is required but not found
        """
        if required and key not in self.config:
            raise ValueError(f"Required configuration key '{key}' not found")

        return self.config.get(key, default)

    def register_hook(self, event: str, handler: Callable) -> None:
        """
        Register a hook handler.

        Args:
            event: Event name
            handler: Callable to handle the event
        """
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(handler)
        logger.debug(f"Registered hook '{event}' for plugin {self.metadata.name}")

    def trigger_hook(self, event: str, *args, **kwargs) -> List[Any]:
        """
        Trigger all handlers for an event.

        Args:
            event: Event name
            *args: Positional arguments for handlers
            **kwargs: Keyword arguments for handlers

        Returns:
            List of results from all handlers
        """
        if event not in self._hooks:
            return []

        results = []
        for handler in self._hooks[event]:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in hook handler for '{event}': {e}")

        return results

    @property
    def state(self) -> PluginState:
        """Get current plugin state."""
        return self._state

    @state.setter
    def state(self, value: PluginState) -> None:
        """Set plugin state."""
        old_state = self._state
        self._state = value
        logger.debug(f"Plugin {self.metadata.name} state: {old_state} -> {value}")

    @property
    def is_ready(self) -> bool:
        """Check if plugin is ready to use."""
        return self._state == PluginState.READY

    @property
    def error_message(self) -> Optional[str]:
        """Get error message if plugin is in error state."""
        return self._error_message

    def set_error(self, message: str) -> None:
        """
        Set plugin to error state.

        Args:
            message: Error message
        """
        self._error_message = message
        self.state = PluginState.ERROR
        logger.error(f"Plugin {self.metadata.name} error: {message}")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.

        Override this method to implement custom health checks.

        Returns:
            Health check result dictionary
        """
        return {
            "plugin": self.metadata.name,
            "version": self.metadata.version,
            "state": self.state.value,
            "healthy": self.state == PluginState.READY,
            "error": self._error_message,
            "uptime_seconds": (
                time.time() - self._initialized_at
                if self._initialized_at
                else None
            ),
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.metadata.name}' "
            f"version='{self.metadata.version}' "
            f"state='{self.state.value}'>"
        )

    def __str__(self) -> str:
        """Human-readable string."""
        return f"{self.metadata.name} v{self.metadata.version} ({self.state.value})"
