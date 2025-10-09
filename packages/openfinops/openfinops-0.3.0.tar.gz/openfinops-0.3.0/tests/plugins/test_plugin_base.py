"""Tests for plugin base classes."""

import pytest
from openfinops.plugins import (
    PluginBase,
    PluginMetadata,
    PluginType,
    PluginState,
)


class MockPlugin(PluginBase):
    """Mock plugin for testing."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="mock-plugin",
            version="1.0.0",
            author="Test Author",
            description="Test plugin",
            plugin_type=PluginType.TELEMETRY,
        )

    def initialize(self) -> None:
        self.state = PluginState.READY

    def shutdown(self) -> None:
        self.state = PluginState.SHUTDOWN


def test_plugin_metadata():
    """Test plugin metadata creation."""
    metadata = PluginMetadata(
        name="test-plugin",
        version="1.0.0",
        author="Test",
        description="Test",
        plugin_type=PluginType.TELEMETRY,
    )

    assert metadata.name == "test-plugin"
    assert metadata.version == "1.0.0"
    assert metadata.plugin_type == PluginType.TELEMETRY


def test_plugin_metadata_validation():
    """Test metadata validation."""
    with pytest.raises(ValueError):
        PluginMetadata(
            name="",  # Empty name should fail
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.TELEMETRY,
        )


def test_plugin_initialization():
    """Test plugin initialization."""
    plugin = MockPlugin(config={"key": "value"})

    assert plugin.state == PluginState.UNINITIALIZED
    assert plugin.config == {"key": "value"}

    plugin.initialize()

    assert plugin.state == PluginState.READY
    assert plugin.is_ready


def test_plugin_config_access():
    """Test configuration access."""
    plugin = MockPlugin(config={"api_key": "secret", "timeout": 30})

    assert plugin.get_config_value("api_key") == "secret"
    assert plugin.get_config_value("timeout") == 30
    assert plugin.get_config_value("missing", default="default") == "default"


def test_plugin_required_config():
    """Test required configuration validation."""
    plugin = MockPlugin(config={"key": "value"})

    # Should work
    value = plugin.get_config_value("key", required=True)
    assert value == "value"

    # Should raise error
    with pytest.raises(ValueError):
        plugin.get_config_value("missing_key", required=True)


def test_plugin_health_check():
    """Test health check."""
    plugin = MockPlugin()
    plugin.initialize()

    health = plugin.health_check()

    assert health["plugin"] == "mock-plugin"
    assert health["version"] == "1.0.0"
    assert health["state"] == "ready"
    assert health["healthy"] is True


def test_plugin_error_state():
    """Test error state handling."""
    plugin = MockPlugin()

    plugin.set_error("Something went wrong")

    assert plugin.state == PluginState.ERROR
    assert plugin.error_message == "Something went wrong"
    assert not plugin.is_ready


def test_plugin_hooks():
    """Test hook registration and triggering."""
    plugin = MockPlugin()

    results = []

    def hook_handler(value):
        results.append(value)
        return value * 2

    plugin.register_hook("test_event", hook_handler)

    hook_results = plugin.trigger_hook("test_event", 5)

    assert results == [5]
    assert hook_results == [10]
