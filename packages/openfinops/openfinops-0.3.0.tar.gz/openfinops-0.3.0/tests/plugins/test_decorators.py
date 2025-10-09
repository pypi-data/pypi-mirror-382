"""Tests for plugin decorators."""

import pytest
import time
from openfinops.plugins import (
    hook,
    requires_config,
    retry,
    cache_result,
    measure_time,
    PluginBase,
    PluginMetadata,
    PluginType,
)


class DecoratorTestPlugin(PluginBase):
    """Plugin for testing decorators."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="decorator-test",
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.TELEMETRY,
        )

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    @requires_config("api_key", "endpoint")
    def method_with_required_config(self):
        return "success"

    @retry(max_attempts=3, delay_seconds=0.01)
    def method_with_retry(self, should_fail=True):
        if should_fail:
            raise ValueError("Intentional failure")
        return "success"

    @cache_result(ttl_seconds=1)
    def expensive_method(self, value):
        return value * 2


def test_hook_decorator():
    """Test hook decorator."""
    called = []

    @hook("test_event")
    def test_handler(value):
        called.append(value)
        return value + 1

    # Verify hook attributes
    assert hasattr(test_handler, '_is_hook')
    assert test_handler._is_hook
    assert test_handler._event_name == "test_event"

    # Call hook
    result = test_handler(5)
    assert result == 6
    assert called == [5]


def test_requires_config_success():
    """Test requires_config decorator with valid config."""
    plugin = DecoratorTestPlugin(config={"api_key": "secret", "endpoint": "https://api.example.com"})

    result = plugin.method_with_required_config()
    assert result == "success"


def test_requires_config_missing():
    """Test requires_config decorator with missing config."""
    plugin = DecoratorTestPlugin(config={"api_key": "secret"})  # Missing 'endpoint'

    with pytest.raises(ValueError, match="Missing required configuration"):
        plugin.method_with_required_config()


def test_retry_decorator_success():
    """Test retry decorator eventual success."""
    plugin = DecoratorTestPlugin()

    result = plugin.method_with_retry(should_fail=False)
    assert result == "success"


def test_retry_decorator_failure():
    """Test retry decorator all attempts fail."""
    plugin = DecoratorTestPlugin()

    with pytest.raises(ValueError, match="Intentional failure"):
        plugin.method_with_retry(should_fail=True)


def test_cache_result_decorator():
    """Test cache_result decorator."""
    plugin = DecoratorTestPlugin()

    # First call - should execute
    result1 = plugin.expensive_method(5)
    assert result1 == 10

    # Second call - should use cache
    result2 = plugin.expensive_method(5)
    assert result2 == 10

    # Wait for cache to expire
    time.sleep(1.1)

    # Third call - should execute again (cache expired)
    result3 = plugin.expensive_method(5)
    assert result3 == 10


def test_measure_time_decorator():
    """Test measure_time decorator."""
    @measure_time(log_level="INFO")
    def slow_function():
        time.sleep(0.1)
        return "done"

    result = slow_function()
    assert result == "done"
