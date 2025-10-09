"""
Persistence Configuration Examples for OpenFinOps
=================================================

Examples of how to configure different storage backends for telemetry data persistence.
"""

from openfinops.observability import ObservabilityHub, CostObservatory
from openfinops.observability.persistence import PersistenceConfig, StorageBackend
import time


# Example 1: In-Memory Only (Default - No Persistence)
# ====================================================
# Fastest performance, but data is lost on restart
# Suitable for: development, testing, ephemeral workloads

def example_in_memory():
    """In-memory storage (default behavior)"""
    hub = ObservabilityHub()  # No persistence config = in-memory only
    cost_obs = CostObservatory()

    print("Using in-memory storage (no persistence)")
    # Data will be lost when process stops


# Example 2: SQLite Backend (File-Based Persistence)
# ==================================================
# Simple file-based storage, good for small/medium deployments
# Suitable for: single-server deployments, development, small teams

def example_sqlite():
    """SQLite persistence for local storage"""
    config = PersistenceConfig(
        backend=StorageBackend.SQLITE,
        connection_string="sqlite:///openfinops_telemetry.db",
        retention_days=90,  # Keep 90 days of historical data
        batch_size=100,  # Batch writes for performance
        batch_interval_seconds=60.0,  # Flush every minute
    )

    hub = ObservabilityHub(persistence_config=config)
    cost_obs = CostObservatory(persistence_config=config)

    print("Using SQLite backend: openfinops_telemetry.db")
    print("Retention: 90 days")

    # All metrics are now persisted to SQLite database
    # Can query historical data even after restart
    return hub, cost_obs


# Example 3: PostgreSQL Backend (Production Database)
# ===================================================
# Production-grade relational database
# Suitable for: multi-server deployments, teams, production workloads

def example_postgresql():
    """PostgreSQL persistence for production use"""
    config = PersistenceConfig(
        backend=StorageBackend.POSTGRESQL,
        connection_string="postgresql://user:password@localhost:5432/openfinops",
        retention_days=365,  # Keep 1 year of data
        batch_size=500,
        batch_interval_seconds=30.0,
    )

    hub = ObservabilityHub(persistence_config=config)
    cost_obs = CostObservatory(persistence_config=config)

    print("Using PostgreSQL backend")
    print("Retention: 365 days")

    return hub, cost_obs


# Example 4: TimescaleDB Backend (Time-Series Optimized)
# ======================================================
# Optimized for time-series data with automatic compression
# Suitable for: high-volume telemetry, long retention periods, analytics

def example_timescaledb():
    """TimescaleDB for optimized time-series storage"""
    config = PersistenceConfig(
        backend=StorageBackend.TIMESCALEDB,
        connection_string="postgresql://user:password@localhost:5432/openfinops",
        retention_days=730,  # Keep 2 years of data
        batch_size=1000,
        batch_interval_seconds=30.0,
        enable_compression=True,  # Automatic compression after 7 days
    )

    hub = ObservabilityHub(persistence_config=config)
    cost_obs = CostObservatory(persistence_config=config)

    print("Using TimescaleDB backend with compression")
    print("Retention: 730 days (2 years)")

    return hub, cost_obs


# Example 5: Querying Historical Data
# ===================================

def example_historical_queries():
    """Query historical data from persistence layer"""
    config = PersistenceConfig(
        backend=StorageBackend.SQLITE,
        connection_string="sqlite:///openfinops_telemetry.db",
        retention_days=90
    )

    hub = ObservabilityHub(persistence_config=config)
    cost_obs = CostObservatory(persistence_config=config)

    # Query system metrics from last 7 days
    seven_days_ago = time.time() - (7 * 24 * 3600)
    metrics = hub.query_historical_metrics(
        start_time=seven_days_ago,
        cluster_id="production-cluster",
        limit=10000
    )
    print(f"Retrieved {len(metrics)} historical metrics")

    # Query cost data from last 30 days for compute resources
    thirty_days_ago = time.time() - (30 * 24 * 3600)
    costs = cost_obs.query_historical_costs(
        start_time=thirty_days_ago,
        category="compute",
        limit=5000
    )
    print(f"Retrieved {len(costs)} cost entries")

    # Calculate total cost over period
    total_cost = sum(entry.get('amount', 0) for entry in costs)
    print(f"Total compute cost (30 days): ${total_cost:.2f}")

    return metrics, costs


# Example 6: Data Retention and Cleanup
# =====================================

def example_data_cleanup():
    """Automatic cleanup of old data"""
    config = PersistenceConfig(
        backend=StorageBackend.POSTGRESQL,
        connection_string="postgresql://user:password@localhost:5432/openfinops",
        retention_days=90  # Automatically delete data older than 90 days
    )

    hub = ObservabilityHub(persistence_config=config)
    cost_obs = CostObservatory(persistence_config=config)

    # Manual cleanup (usually runs automatically)
    hub.cleanup_old_data()
    cost_obs.cleanup_old_data()

    print("Cleaned up data older than 90 days")


# Example 7: Hybrid Approach (Fast Recent + Historical)
# =====================================================

def example_hybrid_usage():
    """Use in-memory for recent data, persistence for historical analysis"""
    config = PersistenceConfig(
        backend=StorageBackend.TIMESCALEDB,
        connection_string="postgresql://user:password@localhost:5432/openfinops",
        retention_days=365,
        max_memory_entries=10000  # Keep last 10k entries in memory
    )

    hub = ObservabilityHub(persistence_config=config)
    cost_obs = CostObservatory(persistence_config=config)

    # Recent data (fast access from memory)
    recent_summary = hub.get_cluster_health_summary()
    print("Recent cluster health:", recent_summary)

    # Historical analysis (from database)
    thirty_days_ago = time.time() - (30 * 24 * 3600)
    historical_metrics = hub.query_historical_metrics(
        start_time=thirty_days_ago,
        limit=100000
    )
    print(f"Historical data points: {len(historical_metrics)}")


# Example 8: Connection String Formats
# ====================================

def example_connection_strings():
    """Examples of different connection string formats"""

    # SQLite (local file)
    sqlite_configs = [
        "sqlite:///openfinops.db",  # In current directory
        "sqlite:////var/lib/openfinops/data.db",  # Absolute path
        "sqlite:///data/telemetry.db",  # Relative path
    ]

    # PostgreSQL
    postgres_configs = [
        "postgresql://localhost/openfinops",
        "postgresql://user:pass@localhost:5432/openfinops",
        "postgresql://user:pass@db.example.com:5432/openfinops?sslmode=require",
    ]

    # TimescaleDB (same as PostgreSQL)
    timescale_configs = [
        "postgresql://localhost/openfinops",
        "postgresql://user:pass@timescaledb.example.com:5432/openfinops",
    ]

    print("SQLite connection strings:", sqlite_configs)
    print("PostgreSQL connection strings:", postgres_configs)
    print("TimescaleDB connection strings:", timescale_configs)


# Example 9: Environment-Based Configuration
# ==========================================

def example_environment_config():
    """Configure persistence based on environment variables"""
    import os

    backend_type = os.getenv("OPENFINOPS_BACKEND", "in_memory")
    connection_string = os.getenv("OPENFINOPS_DB_URL")
    retention_days = int(os.getenv("OPENFINOPS_RETENTION_DAYS", "90"))

    if backend_type == "sqlite":
        config = PersistenceConfig(
            backend=StorageBackend.SQLITE,
            connection_string=connection_string or "sqlite:///openfinops.db",
            retention_days=retention_days
        )
    elif backend_type == "postgresql":
        config = PersistenceConfig(
            backend=StorageBackend.POSTGRESQL,
            connection_string=connection_string,
            retention_days=retention_days
        )
    elif backend_type == "timescaledb":
        config = PersistenceConfig(
            backend=StorageBackend.TIMESCALEDB,
            connection_string=connection_string,
            retention_days=retention_days
        )
    else:
        config = None  # In-memory only

    hub = ObservabilityHub(persistence_config=config)
    print(f"Configured with backend: {backend_type}")
    return hub


# Example 10: Cleanup on Application Shutdown
# ===========================================

def example_proper_shutdown():
    """Properly close persistence connections on shutdown"""
    config = PersistenceConfig(
        backend=StorageBackend.POSTGRESQL,
        connection_string="postgresql://localhost/openfinops"
    )

    hub = ObservabilityHub(persistence_config=config)
    cost_obs = CostObservatory(persistence_config=config)

    try:
        # Your application logic here
        pass
    finally:
        # Always close connections properly
        hub.close()
        cost_obs.close()
        print("Persistence connections closed")


if __name__ == "__main__":
    print("=" * 60)
    print("OpenFinOps Persistence Configuration Examples")
    print("=" * 60)

    print("\n1. In-Memory (Default)")
    example_in_memory()

    print("\n2. SQLite Backend")
    example_sqlite()

    print("\n3. Connection String Examples")
    example_connection_strings()

    print("\n4. Environment-Based Configuration")
    example_environment_config()

    print("\nFor more examples, see the function definitions above.")
