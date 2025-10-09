# Telemetry Data Persistence

OpenFinOps supports multiple storage backends for telemetry data persistence, enabling historical analysis and long-term data retention.

## Overview

By default, OpenFinOps stores telemetry data **in-memory only**. This is fast but data is lost on restart. For production deployments and historical analysis, you can configure a persistent storage backend.

## Storage Backends

### 1. In-Memory (Default)

**Pros:**
- Fastest performance
- No dependencies
- Zero configuration

**Cons:**
- Data lost on restart
- Limited by RAM
- No historical analysis beyond buffer limits

**Use Cases:**
- Development and testing
- Ephemeral workloads
- Short-term monitoring

**Configuration:**
```python
from openfinops.observability import ObservabilityHub, CostObservatory

# No configuration needed - default behavior
hub = ObservabilityHub()
cost_obs = CostObservatory()
```

### 2. SQLite

**Pros:**
- Simple file-based storage
- No server required
- Easy backup (just copy the file)
- Good query performance

**Cons:**
- Single-writer limitations
- Not suitable for high concurrency
- Limited to single server

**Use Cases:**
- Single-server deployments
- Small teams
- Development with persistence
- Embedded deployments

**Configuration:**
```python
from openfinops.observability import ObservabilityHub, CostObservatory
from openfinops.observability.persistence import PersistenceConfig, StorageBackend

config = PersistenceConfig(
    backend=StorageBackend.SQLITE,
    connection_string="sqlite:///openfinops_telemetry.db",
    retention_days=90,
    batch_size=100,
    batch_interval_seconds=60.0
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)
```

### 3. PostgreSQL

**Pros:**
- Production-grade reliability
- Multi-writer support
- Rich query capabilities
- ACID compliance
- Connection pooling

**Cons:**
- Requires PostgreSQL server
- More complex setup
- Higher resource usage

**Use Cases:**
- Multi-server deployments
- Production workloads
- Team environments
- When you already use PostgreSQL

**Configuration:**
```python
config = PersistenceConfig(
    backend=StorageBackend.POSTGRESQL,
    connection_string="postgresql://user:password@localhost:5432/openfinops",
    retention_days=365,
    batch_size=500,
    batch_interval_seconds=30.0
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)
```

**PostgreSQL Setup:**
```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Create database
sudo -u postgres createdb openfinops

# Create user
sudo -u postgres createuser openfinops_user

# Grant privileges
sudo -u postgres psql
postgres=# GRANT ALL PRIVILEGES ON DATABASE openfinops TO openfinops_user;
```

### 4. TimescaleDB (Recommended for Production)

**Pros:**
- Optimized for time-series data
- Automatic compression (saves 90%+ storage)
- Excellent query performance for time-based queries
- Built on PostgreSQL (compatible)
- Hypertables for partitioning

**Cons:**
- Requires TimescaleDB extension
- Slightly more complex setup

**Use Cases:**
- High-volume telemetry
- Long retention periods (1+ years)
- Analytics and reporting
- Production deployments

**Configuration:**
```python
config = PersistenceConfig(
    backend=StorageBackend.TIMESCALEDB,
    connection_string="postgresql://user:password@localhost:5432/openfinops",
    retention_days=730,  # 2 years
    batch_size=1000,
    batch_interval_seconds=30.0,
    enable_compression=True
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)
```

**TimescaleDB Setup:**
```bash
# Install TimescaleDB (Ubuntu/Debian)
sudo add-apt-repository ppa:timescale/timescaledb-ppa
sudo apt-get update
sudo apt-get install timescaledb-postgresql-14

# Initialize TimescaleDB
sudo timescaledb-tune

# Enable extension in database
sudo -u postgres psql -d openfinops
openfinops=# CREATE EXTENSION IF NOT EXISTS timescaledb;
```

## Configuration Options

### PersistenceConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `backend` | StorageBackend | IN_MEMORY | Storage backend to use |
| `connection_string` | str | Auto | Database connection string |
| `retention_days` | int | 90 | How long to keep historical data |
| `batch_size` | int | 100 | Number of entries to batch before writing |
| `batch_interval_seconds` | float | 60.0 | Max time to wait before flushing batch |
| `enable_compression` | bool | False | Enable compression (TimescaleDB only) |
| `max_memory_entries` | int | 10000 | Max entries to keep in memory |

### Connection String Formats

**SQLite:**
```python
"sqlite:///openfinops.db"  # Relative path
"sqlite:////var/lib/openfinops/data.db"  # Absolute path
```

**PostgreSQL / TimescaleDB:**
```python
"postgresql://localhost/openfinops"
"postgresql://user:pass@localhost:5432/openfinops"
"postgresql://user:pass@host:5432/db?sslmode=require"
```

## Querying Historical Data

### System Metrics

```python
import time

# Query last 7 days
seven_days_ago = time.time() - (7 * 24 * 3600)
metrics = hub.query_historical_metrics(
    start_time=seven_days_ago,
    cluster_id="production",
    limit=10000
)

# Query specific node
metrics = hub.query_historical_metrics(
    start_time=seven_days_ago,
    cluster_id="production",
    node_id="node-1",
    limit=5000
)
```

### Cost Data

```python
# Query last 30 days of compute costs
thirty_days_ago = time.time() - (30 * 24 * 3600)
costs = cost_obs.query_historical_costs(
    start_time=thirty_days_ago,
    category="compute",
    limit=10000
)

# Calculate total cost
total = sum(entry['amount'] for entry in costs)
print(f"Total cost: ${total:.2f}")

# Query by resource
costs = cost_obs.query_historical_costs(
    resource_id="i-1234567890abcdef0",
    limit=1000
)
```

## Data Retention and Cleanup

Data older than `retention_days` is automatically deleted:

```python
# Manual cleanup (runs automatically in background)
hub.cleanup_old_data()
cost_obs.cleanup_old_data()
```

## Performance Considerations

### Batch Configuration

Higher batch sizes reduce write overhead but increase latency:

```python
# Low latency (writes every 10 seconds)
config = PersistenceConfig(
    batch_size=50,
    batch_interval_seconds=10.0
)

# High throughput (larger batches)
config = PersistenceConfig(
    batch_size=1000,
    batch_interval_seconds=60.0
)
```

### Memory vs Persistence

The system maintains a dual-layer approach:
1. **In-memory buffer**: Fast access to recent data
2. **Persistent storage**: Historical analysis

```python
# Recent data (fast, from memory)
summary = hub.get_cluster_health_summary()

# Historical data (from database)
historical = hub.query_historical_metrics(
    start_time=thirty_days_ago
)
```

## Environment-Based Configuration

```bash
# .env file
OPENFINOPS_BACKEND=timescaledb
OPENFINOPS_DB_URL=postgresql://user:pass@localhost:5432/openfinops
OPENFINOPS_RETENTION_DAYS=365
```

```python
import os
from openfinops.observability.persistence import PersistenceConfig, StorageBackend

backend_map = {
    "sqlite": StorageBackend.SQLITE,
    "postgresql": StorageBackend.POSTGRESQL,
    "timescaledb": StorageBackend.TIMESCALEDB,
}

backend = os.getenv("OPENFINOPS_BACKEND", "in_memory")
if backend != "in_memory":
    config = PersistenceConfig(
        backend=backend_map[backend],
        connection_string=os.getenv("OPENFINOPS_DB_URL"),
        retention_days=int(os.getenv("OPENFINOPS_RETENTION_DAYS", "90"))
    )
    hub = ObservabilityHub(persistence_config=config)
else:
    hub = ObservabilityHub()  # In-memory only
```

## Proper Shutdown

Always close connections cleanly:

```python
try:
    # Your application logic
    pass
finally:
    hub.close()
    cost_obs.close()
```

## Migration Between Backends

To migrate data between backends:

1. **Export from old backend:**
```python
# Query all data
old_metrics = old_hub.query_historical_metrics(limit=1000000)
old_costs = old_cost_obs.query_historical_costs(limit=1000000)
```

2. **Import to new backend:**
```python
# Create new hub with different backend
new_hub = ObservabilityHub(persistence_config=new_config)

# Re-insert data
for metric in old_metrics:
    # Convert back to dataclass and insert
    pass
```

## Troubleshooting

### PostgreSQL Connection Errors

```python
# Test connection
import psycopg2
try:
    conn = psycopg2.connect("postgresql://user:pass@localhost/openfinops")
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
```

### SQLite Lock Errors

SQLite doesn't handle high concurrency well. Use PostgreSQL/TimescaleDB for multi-process deployments.

### Slow Queries

For TimescaleDB, ensure hypertables are created:
```sql
SELECT create_hypertable('system_metrics', 'timestamp');
SELECT create_hypertable('cost_entries', 'timestamp');
```

## Best Practices

1. **Use TimescaleDB for production** with high data volumes
2. **Configure appropriate retention** - balance storage vs historical needs
3. **Monitor database size** - implement cleanup strategies
4. **Use connection pooling** for PostgreSQL/TimescaleDB
5. **Regular backups** - especially for SQLite deployments
6. **Index optimization** - create indexes for frequently queried fields
7. **Compression** - enable for TimescaleDB to save 90%+ storage

## Schema Management

The persistence layer automatically creates tables on initialization. No manual schema setup required.

For advanced users, schemas are in:
- `src/openfinops/observability/persistence.py`

## Dependencies

- **SQLite**: No additional dependencies (built into Python)
- **PostgreSQL**: `pip install psycopg2-binary`
- **TimescaleDB**: `pip install psycopg2-binary` + TimescaleDB server
