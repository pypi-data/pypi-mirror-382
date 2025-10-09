"""
Plugin Decorators
=================

Decorators for convenient plugin development.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from functools import wraps
from typing import Callable, Any, List
import logging

from .base import PluginType

logger = logging.getLogger(__name__)


def plugin(plugin_type: PluginType, auto_register: bool = True):
    """
    Decorator to mark a class as a plugin.

    Args:
        plugin_type: Type of plugin
        auto_register: If True, automatically register with global registry

    Example:
        >>> from openfinops.plugins import plugin, PluginType
        >>>
        >>> @plugin(PluginType.TELEMETRY)
        >>> class MyTelemetryPlugin(TelemetryPlugin):
        ...     pass
    """
    def decorator(cls):
        cls._plugin_type = plugin_type
        cls._auto_register = auto_register

        # Auto-register if requested
        if auto_register:
            try:
                from .registry import registry
                registry.register(cls)
            except Exception as e:
                logger.warning(f"Failed to auto-register plugin {cls.__name__}: {e}")

        return cls
    return decorator


def hook(event_name: str):
    """
    Decorator to register a function as a hook.

    Hooks are called when specific events occur in the OpenFinOps system.

    Args:
        event_name: Name of the event to hook into

    Available hooks:
        - pre_collect_metrics: Before metric collection
        - post_collect_metrics: After metric collection
        - cost_entry_received: When a cost entry is added
        - budget_threshold_exceeded: When budget is exceeded
        - recommendation_generated: When recommendation is created
        - dashboard_render: Before dashboard renders
        - alert_triggered: When alert is triggered

    Example:
        >>> from openfinops.plugins import hook
        >>>
        >>> @hook("cost_entry_received")
        >>> def on_cost_entry(entry):
        ...     # Modify or enrich the cost entry
        ...     entry.tags["processed"] = "true"
        ...     return entry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Executing hook: {event_name}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Hook {event_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error in hook {event_name}: {e}")
                raise

        # Mark as hook
        wrapper._is_hook = True
        wrapper._event_name = event_name
        wrapper._original_func = func

        return wrapper
    return decorator


def requires_config(*required_keys: str):
    """
    Decorator to validate required configuration keys.

    Args:
        *required_keys: Configuration keys that must be present

    Raises:
        ValueError: If required keys are missing

    Example:
        >>> from openfinops.plugins import requires_config
        >>>
        >>> class MyPlugin(PluginBase):
        ...     @requires_config("api_key", "endpoint")
        ...     def initialize(self):
        ...         # api_key and endpoint are guaranteed to exist
        ...         self.client = Client(
        ...             api_key=self.config["api_key"],
        ...             endpoint=self.config["endpoint"]
        ...         )
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            missing = [key for key in required_keys if key not in self.config]
            if missing:
                raise ValueError(
                    f"Missing required configuration keys: {', '.join(missing)}"
                )
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def retry(max_attempts: int = 3, delay_seconds: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry a function on failure.

    Args:
        max_attempts: Maximum number of attempts
        delay_seconds: Initial delay between retries
        backoff: Backoff multiplier for delay

    Example:
        >>> from openfinops.plugins import retry
        >>>
        >>> class MyPlugin(PluginBase):
        ...     @retry(max_attempts=3, delay_seconds=1.0)
        ...     def fetch_data(self):
        ...         # This will retry up to 3 times on failure
        ...         return self.api.get_data()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time

            last_exception = None
            current_delay = delay_seconds

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt}/{max_attempts} failed for "
                            f"{func.__name__}: {e}. Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}"
                        )

            raise last_exception

        return wrapper
    return decorator


def cache_result(ttl_seconds: int = 300):
    """
    Decorator to cache function results.

    Args:
        ttl_seconds: Time-to-live for cached results in seconds

    Example:
        >>> from openfinops.plugins import cache_result
        >>>
        >>> class MyPlugin(PluginBase):
        ...     @cache_result(ttl_seconds=600)
        ...     def get_expensive_data(self):
        ...         # Result will be cached for 10 minutes
        ...         return expensive_computation()
    """
    def decorator(func: Callable) -> Callable:
        import time

        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from args and kwargs
            cache_key = str((args, tuple(sorted(kwargs.items()))))

            # Check if cached and not expired
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            logger.debug(f"Cached result for {func.__name__}")

            return result

        # Add cache management methods
        wrapper.clear_cache = lambda: cache.clear()
        wrapper.cache_info = lambda: {
            "size": len(cache),
            "ttl_seconds": ttl_seconds,
        }

        return wrapper
    return decorator


def rate_limit(calls: int = 10, period_seconds: int = 60):
    """
    Decorator to rate limit function calls.

    Args:
        calls: Number of allowed calls
        period_seconds: Time period in seconds

    Raises:
        RuntimeError: If rate limit exceeded

    Example:
        >>> from openfinops.plugins import rate_limit
        >>>
        >>> class MyPlugin(PluginBase):
        ...     @rate_limit(calls=100, period_seconds=3600)
        ...     def api_call(self):
        ...         # Limited to 100 calls per hour
        ...         return self.api.fetch()
    """
    def decorator(func: Callable) -> Callable:
        import time
        from collections import deque

        call_times = deque(maxlen=calls)

        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()

            # Remove old calls outside the period
            while call_times and current_time - call_times[0] > period_seconds:
                call_times.popleft()

            # Check rate limit
            if len(call_times) >= calls:
                wait_time = period_seconds - (current_time - call_times[0])
                raise RuntimeError(
                    f"Rate limit exceeded: {calls} calls per {period_seconds}s. "
                    f"Wait {wait_time:.1f}s"
                )

            # Record call and execute
            call_times.append(current_time)
            return func(*args, **kwargs)

        return wrapper
    return decorator


def measure_time(log_level: str = "DEBUG"):
    """
    Decorator to measure and log function execution time.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Example:
        >>> from openfinops.plugins import measure_time
        >>>
        >>> class MyPlugin(PluginBase):
        ...     @measure_time(log_level="INFO")
        ...     def slow_operation(self):
        ...         # Execution time will be logged
        ...         time.sleep(5)
    """
    def decorator(func: Callable) -> Callable:
        import time

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time

                log_func = getattr(logger, log_level.lower(), logger.debug)
                log_func(f"{func.__name__} completed in {elapsed:.3f}s")

                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{func.__name__} failed after {elapsed:.3f}s: {e}")
                raise

        return wrapper
    return decorator


# Export all decorators
__all__ = [
    "plugin",
    "hook",
    "requires_config",
    "retry",
    "cache_result",
    "rate_limit",
    "measure_time",
]
