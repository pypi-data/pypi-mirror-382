"""Tests for plugin registry."""

import pytest
from openfinops.plugins import (
    PluginBase,
    PluginMetadata,
    PluginType,
    PluginState,
    PluginRegistry,
)


class TestPlugin(PluginBase):
    """Test plugin class."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            author="Test",
            description="Test plugin",
            plugin_type=PluginType.TELEMETRY,
        )

    def initialize(self) -> None:
        self.state = PluginState.READY
        self.initialized = True

    def shutdown(self) -> None:
        self.state = PluginState.SHUTDOWN
        self.initialized = False


@pytest.fixture
def registry():
    """Create a fresh registry for each test."""
    return PluginRegistry()


def test_register_plugin(registry):
    """Test plugin registration."""
    registry.register(TestPlugin)

    plugins = registry.list_plugins()
    assert len(plugins) == 1
    assert plugins[0].name == "test-plugin"


def test_register_duplicate_plugin(registry):
    """Test registering duplicate plugin."""
    registry.register(TestPlugin)
    registry.register(TestPlugin)  # Should log warning but not fail

    plugins = registry.list_plugins()
    assert len(plugins) == 1


def test_load_plugin(registry):
    """Test loading a plugin."""
    registry.register(TestPlugin)

    plugin = registry.load_plugin("test-plugin", config={"key": "value"})

    assert plugin is not None
    assert plugin.state == PluginState.READY
    assert plugin.config == {"key": "value"}
    assert plugin.initialized


def test_load_nonexistent_plugin(registry):
    """Test loading non-existent plugin."""
    with pytest.raises(ValueError, match="not found in registry"):
        registry.load_plugin("nonexistent-plugin")


def test_unload_plugin(registry):
    """Test unloading a plugin."""
    registry.register(TestPlugin)
    plugin = registry.load_plugin("test-plugin")

    assert plugin.initialized

    registry.unload_plugin("test-plugin")

    assert plugin.state == PluginState.SHUTDOWN
    assert not plugin.initialized


def test_get_plugin(registry):
    """Test getting a loaded plugin."""
    registry.register(TestPlugin)
    loaded = registry.load_plugin("test-plugin")

    retrieved = registry.get_plugin("test-plugin")

    assert retrieved is loaded
    assert retrieved.state == PluginState.READY


def test_list_plugins_by_type(registry):
    """Test listing plugins filtered by type."""
    registry.register(TestPlugin)

    telemetry_plugins = registry.list_plugins(plugin_type=PluginType.TELEMETRY)
    assert len(telemetry_plugins) == 1

    dashboard_plugins = registry.list_plugins(plugin_type=PluginType.DASHBOARD)
    assert len(dashboard_plugins) == 0


def test_list_loaded_plugins(registry):
    """Test listing only loaded plugins."""
    registry.register(TestPlugin)

    # Before loading
    plugins = registry.list_plugins(loaded_only=True)
    assert len(plugins) == 0

    # After loading
    registry.load_plugin("test-plugin")
    plugins = registry.list_plugins(loaded_only=True)
    assert len(plugins) == 1


def test_reload_plugin(registry):
    """Test reloading a plugin."""
    registry.register(TestPlugin)

    plugin1 = registry.load_plugin("test-plugin", config={"key": "value1"})
    assert plugin1.config == {"key": "value1"}

    plugin2 = registry.reload_plugin("test-plugin", config={"key": "value2"})
    assert plugin2.config == {"key": "value2"}
    assert plugin1 is not plugin2


def test_unload_all(registry):
    """Test unloading all plugins."""
    registry.register(TestPlugin)
    registry.load_plugin("test-plugin")

    loaded = registry.list_plugins(loaded_only=True)
    assert len(loaded) == 1

    registry.unload_all()

    loaded = registry.list_plugins(loaded_only=True)
    assert len(loaded) == 0


def test_get_statistics(registry):
    """Test getting registry statistics."""
    registry.register(TestPlugin)
    registry.load_plugin("test-plugin")

    stats = registry.get_statistics()

    assert stats["total_registered"] == 1
    assert stats["total_loaded"] == 1
    assert "telemetry" in stats["by_type"]
    assert "ready" in stats["by_state"]
