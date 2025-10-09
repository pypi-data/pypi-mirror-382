# OpenFinOps v0.2.1 Release Notes

**Release Date:** October 6, 2025
**PyPI:** https://pypi.org/project/openfinops/0.2.1/

## 🚀 What's New

### Major Feature: Telemetry Data Persistence Layer

OpenFinOps now supports multiple database backends for persistent telemetry data storage, enabling historical analysis and long-term data retention!

#### **4 Storage Backend Options:**

1. **In-Memory (Default)** - Fast, no persistence
2. **SQLite** - File-based, single-server deployments
3. **PostgreSQL** - Production-grade relational database
4. **TimescaleDB** - Time-series optimized with 90%+ compression

### Key Capabilities

✅ **Pluggable Storage** - Easy backend switching
✅ **Automatic Schema Management** - No manual setup required
✅ **Batch Processing** - High-performance batch inserts
✅ **Query Historical Data** - New APIs for historical analysis
✅ **Data Retention** - Configurable retention policies
✅ **100% Backward Compatible** - No breaking changes

## 📦 Installation

```bash
# Basic installation
pip install openfinops

# With PostgreSQL support
pip install openfinops[postgres]

# With all features
pip install openfinops[all]

# Upgrade from previous version
pip install --upgrade openfinops
```

## 🎯 Quick Start

### Default (In-Memory)

```python
from openfinops.observability import ObservabilityHub, CostObservatory

# No config needed - works like before
hub = ObservabilityHub()
cost_obs = CostObservatory()
```

### SQLite Persistence

```python
from openfinops.observability import ObservabilityHub, CostObservatory
from openfinops.observability.persistence import PersistenceConfig, StorageBackend

config = PersistenceConfig(
    backend=StorageBackend.SQLITE,
    connection_string="sqlite:///openfinops.db",
    retention_days=90
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)
```

### PostgreSQL/TimescaleDB

```python
config = PersistenceConfig(
    backend=StorageBackend.TIMESCALEDB,
    connection_string="postgresql://user:pass@localhost:5432/openfinops",
    retention_days=365,
    enable_compression=True
)

hub = ObservabilityHub(persistence_config=config)
cost_obs = CostObservatory(persistence_config=config)
```

## 🔍 Query Historical Data

```python
import time

# Query system metrics from last 7 days
seven_days_ago = time.time() - (7 * 24 * 3600)
metrics = hub.query_historical_metrics(
    start_time=seven_days_ago,
    cluster_id="production",
    limit=10000
)

# Query cost data from last 30 days
thirty_days_ago = time.time() - (30 * 24 * 3600)
costs = cost_obs.query_historical_costs(
    start_time=thirty_days_ago,
    category="compute",
    limit=10000
)

# Calculate total cost
total = sum(entry['amount'] for entry in costs)
print(f"Total cost: ${total:.2f}")
```

## 🛠️ Database CLI Tools

New command-line utilities for database management:

```bash
# Initialize database
openfinops database init --backend sqlite --connection-string "sqlite:///openfinops.db"

# Test connection
openfinops database test-connection --backend postgresql \
  --connection-string "postgresql://localhost/openfinops"

# View statistics
openfinops database stats --backend sqlite \
  --connection-string "sqlite:///openfinops.db"

# Query recent data
openfinops database query --backend sqlite \
  --connection-string "sqlite:///openfinops.db" --days 7

# Cleanup old data
openfinops database cleanup --backend postgresql \
  --connection-string "postgresql://localhost/openfinops" \
  --retention-days 90

# Show examples
openfinops database examples
```

## 📊 Performance Characteristics

| Backend | Write Speed | Query Speed | Concurrency | Scalability | Storage |
|---------|-------------|-------------|-------------|-------------|---------|
| In-Memory | ⚡ Fastest | ⚡ Fastest | ⚠️ Limited | ❌ Single | RAM only |
| SQLite | ✅ Fast | ✅ Fast | ⚠️ Single writer | ⚠️ Single server | ✅ Good |
| PostgreSQL | ✅ Fast | ✅ Fast | ✅ Excellent | ✅ Clustered | ✅ Good |
| TimescaleDB | ✅ Fast | ⚡ Fastest* | ✅ Excellent | ✅ Clustered | ⚡ Excellent** |

\* For time-series queries
\*\* With compression enabled (90%+ reduction)

## 📚 Documentation

- **Complete Guide:** `docs/PERSISTENCE.md`
- **Examples:** `examples/persistence_config_examples.py`
- **Implementation Details:** `PERSISTENCE_IMPLEMENTATION.md`
- **API Reference:** Integrated into existing docs

## 🧪 Testing

All tests pass (12 tests for persistence layer):

```bash
# Run persistence tests
pytest tests/test_persistence.py -v

# Run all tests
pytest
```

## 🔧 Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `backend` | StorageBackend | IN_MEMORY | Storage backend |
| `connection_string` | str | Auto | Database connection |
| `retention_days` | int | 90 | Data retention period |
| `batch_size` | int | 100 | Batch size for writes |
| `batch_interval_seconds` | float | 60.0 | Max flush interval |
| `enable_compression` | bool | False | Enable compression (TimescaleDB) |
| `max_memory_entries` | int | 10000 | In-memory buffer size |

## 🎨 Use Cases

### Development & Testing
```python
hub = ObservabilityHub()  # In-memory, no persistence
```

### Small Deployments
```python
config = PersistenceConfig(
    backend=StorageBackend.SQLITE,
    retention_days=90
)
```

### Production Workloads
```python
config = PersistenceConfig(
    backend=StorageBackend.POSTGRESQL,
    retention_days=365
)
```

### High-Volume Analytics
```python
config = PersistenceConfig(
    backend=StorageBackend.TIMESCALEDB,
    retention_days=730,
    enable_compression=True
)
```

## 🔄 Migration Path

Switching backends is simple:

1. Update configuration
2. Restart application
3. New data flows to new backend

For historical data migration:

```python
# Export from old
old_metrics = old_hub.query_historical_metrics(limit=1000000)

# Import to new
for metric in old_metrics:
    new_hub.collect_system_metrics(SystemMetrics(**metric))
```

## 📦 Files Added

### New Files
- `src/openfinops/observability/persistence.py` - Persistence layer (900+ lines)
- `src/openfinops/cli/database.py` - Database CLI tools
- `examples/persistence_config_examples.py` - 10 detailed examples
- `docs/PERSISTENCE.md` - Complete documentation
- `tests/test_persistence.py` - Comprehensive test suite
- `PERSISTENCE_IMPLEMENTATION.md` - Implementation guide

### Modified Files
- `src/openfinops/observability/observability_hub.py` - Added persistence support
- `src/openfinops/observability/cost_observatory.py` - Added persistence support
- `pyproject.toml` - Version bump to 0.2.1
- `src/openfinops/__init__.py` - Version update

## 🐛 Bug Fixes

- None in this release (new feature only)

## ⚠️ Breaking Changes

**None!** This release is 100% backward compatible. Existing code continues to work without any changes.

## 🔮 What's Next (v0.3.0)

Planned features for next release:
- InfluxDB backend support
- Data export utilities
- Advanced query APIs
- Dashboard for historical analysis
- Performance metrics dashboard

## 👥 Contributors

- Duraimurugan Rajamanickam (@infinidatum)

## 📝 License

Apache License 2.0

## 🔗 Links

- **PyPI:** https://pypi.org/project/openfinops/0.2.1/
- **GitHub:** https://github.com/openfinops/openfinops
- **Documentation:** https://openfinops.readthedocs.io/
- **Issues:** https://github.com/openfinops/openfinops/issues

## 🙏 Feedback

We'd love to hear from you! Please:
- ⭐ Star the repo if you find it useful
- 🐛 Report issues on GitHub
- 💡 Suggest features via GitHub Issues
- 📖 Improve docs with PRs

---

**Install now:** `pip install --upgrade openfinops`

**Try it:** Check out `examples/persistence_config_examples.py` for quick start examples!
