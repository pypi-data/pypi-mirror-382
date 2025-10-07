"""
Database Management CLI for OpenFinOps
======================================

Command-line utility for managing persistence layer databases.
"""

import click
import sys
import time
from typing import Optional

try:
    from openfinops.observability.persistence import (
        PersistenceConfig,
        StorageBackend,
        create_persistence_backend
    )
    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False
    print("Error: Persistence module not available")
    sys.exit(1)


@click.group()
def database():
    """Database management commands for OpenFinOps telemetry storage."""
    pass


@database.command()
@click.option('--backend', type=click.Choice(['sqlite', 'postgresql', 'timescaledb']),
              default='sqlite', help='Storage backend type')
@click.option('--connection-string', help='Database connection string')
@click.option('--retention-days', default=90, help='Data retention period in days')
def init(backend: str, connection_string: Optional[str], retention_days: int):
    """Initialize database schema for telemetry storage."""
    click.echo(f"Initializing {backend} database...")

    backend_map = {
        'sqlite': StorageBackend.SQLITE,
        'postgresql': StorageBackend.POSTGRESQL,
        'timescaledb': StorageBackend.TIMESCALEDB,
    }

    config = PersistenceConfig(
        backend=backend_map[backend],
        connection_string=connection_string,
        retention_days=retention_days
    )

    try:
        persistence = create_persistence_backend(config)
        click.echo("✓ Database schema initialized successfully")
        click.echo(f"  Backend: {backend}")
        click.echo(f"  Connection: {config.connection_string}")
        click.echo(f"  Retention: {retention_days} days")
        persistence.close()
    except Exception as e:
        click.echo(f"✗ Failed to initialize database: {e}", err=True)
        sys.exit(1)


@database.command()
@click.option('--backend', type=click.Choice(['sqlite', 'postgresql', 'timescaledb']),
              required=True, help='Storage backend type')
@click.option('--connection-string', required=True, help='Database connection string')
def test_connection(backend: str, connection_string: str):
    """Test database connection."""
    click.echo(f"Testing {backend} connection...")

    backend_map = {
        'sqlite': StorageBackend.SQLITE,
        'postgresql': StorageBackend.POSTGRESQL,
        'timescaledb': StorageBackend.TIMESCALEDB,
    }

    config = PersistenceConfig(
        backend=backend_map[backend],
        connection_string=connection_string
    )

    try:
        persistence = create_persistence_backend(config)
        click.echo("✓ Connection successful")
        persistence.close()
    except Exception as e:
        click.echo(f"✗ Connection failed: {e}", err=True)
        sys.exit(1)


@database.command()
@click.option('--backend', type=click.Choice(['sqlite', 'postgresql', 'timescaledb']),
              required=True, help='Storage backend type')
@click.option('--connection-string', required=True, help='Database connection string')
@click.option('--retention-days', required=True, type=int, help='Data retention period')
def cleanup(backend: str, connection_string: str, retention_days: int):
    """Remove data older than retention period."""
    click.echo(f"Cleaning up data older than {retention_days} days...")

    backend_map = {
        'sqlite': StorageBackend.SQLITE,
        'postgresql': StorageBackend.POSTGRESQL,
        'timescaledb': StorageBackend.TIMESCALEDB,
    }

    config = PersistenceConfig(
        backend=backend_map[backend],
        connection_string=connection_string,
        retention_days=retention_days
    )

    try:
        persistence = create_persistence_backend(config)
        persistence.cleanup_old_data()
        click.echo("✓ Cleanup completed successfully")
        persistence.close()
    except Exception as e:
        click.echo(f"✗ Cleanup failed: {e}", err=True)
        sys.exit(1)


@database.command()
@click.option('--backend', type=click.Choice(['sqlite', 'postgresql', 'timescaledb']),
              required=True, help='Storage backend type')
@click.option('--connection-string', required=True, help='Database connection string')
def stats(backend: str, connection_string: str):
    """Show database statistics."""
    click.echo("Fetching database statistics...")

    backend_map = {
        'sqlite': StorageBackend.SQLITE,
        'postgresql': StorageBackend.POSTGRESQL,
        'timescaledb': StorageBackend.TIMESCALEDB,
    }

    config = PersistenceConfig(
        backend=backend_map[backend],
        connection_string=connection_string
    )

    try:
        persistence = create_persistence_backend(config)

        # Query metrics count
        all_metrics = persistence.query_system_metrics(limit=1000000)
        all_costs = persistence.query_cost_entries(limit=1000000)

        # Calculate time range
        if all_metrics:
            oldest_metric = min(m['timestamp'] for m in all_metrics)
            newest_metric = max(m['timestamp'] for m in all_metrics)
            days_of_data = (newest_metric - oldest_metric) / (24 * 3600)
        else:
            oldest_metric = newest_metric = days_of_data = 0

        click.echo("\n" + "=" * 50)
        click.echo("Database Statistics")
        click.echo("=" * 50)
        click.echo(f"Backend: {backend}")
        click.echo(f"Connection: {connection_string}")
        click.echo(f"\nData Counts:")
        click.echo(f"  System Metrics: {len(all_metrics):,}")
        click.echo(f"  Cost Entries: {len(all_costs):,}")
        if days_of_data > 0:
            click.echo(f"\nTime Range:")
            click.echo(f"  Oldest: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(oldest_metric))}")
            click.echo(f"  Newest: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(newest_metric))}")
            click.echo(f"  Days of Data: {days_of_data:.1f}")
        click.echo("=" * 50)

        persistence.close()
    except Exception as e:
        click.echo(f"✗ Failed to fetch statistics: {e}", err=True)
        sys.exit(1)


@database.command()
@click.option('--backend', type=click.Choice(['sqlite', 'postgresql', 'timescaledb']),
              required=True, help='Storage backend type')
@click.option('--connection-string', required=True, help='Database connection string')
@click.option('--table', type=click.Choice(['system_metrics', 'cost_entries', 'all']),
              default='all', help='Table to query')
@click.option('--days', default=7, help='Number of days to query')
@click.option('--limit', default=100, help='Maximum results to show')
def query(backend: str, connection_string: str, table: str, days: int, limit: int):
    """Query recent data from database."""
    click.echo(f"Querying {table} from last {days} days...")

    backend_map = {
        'sqlite': StorageBackend.SQLITE,
        'postgresql': StorageBackend.POSTGRESQL,
        'timescaledb': StorageBackend.TIMESCALEDB,
    }

    config = PersistenceConfig(
        backend=backend_map[backend],
        connection_string=connection_string
    )

    try:
        persistence = create_persistence_backend(config)
        start_time = time.time() - (days * 24 * 3600)

        if table in ['system_metrics', 'all']:
            metrics = persistence.query_system_metrics(
                start_time=start_time,
                limit=limit
            )
            click.echo(f"\n--- System Metrics ({len(metrics)} results) ---")
            for m in metrics[:10]:  # Show first 10
                click.echo(f"  {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(m.get('timestamp', 0)))} "
                          f"| Cluster: {m.get('cluster_id', 'N/A')} "
                          f"| Node: {m.get('node_id', 'N/A')} "
                          f"| CPU: {m.get('cpu_usage', 0):.1f}% "
                          f"| Mem: {m.get('memory_usage', 0):.1f}%")

        if table in ['cost_entries', 'all']:
            costs = persistence.query_cost_entries(
                start_time=start_time,
                limit=limit
            )
            click.echo(f"\n--- Cost Entries ({len(costs)} results) ---")
            total_cost = 0
            for c in costs[:10]:  # Show first 10
                amount = c.get('amount', 0)
                total_cost += amount
                click.echo(f"  {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(c.get('timestamp', 0)))} "
                          f"| Category: {c.get('category', 'N/A')} "
                          f"| Resource: {c.get('resource_id', 'N/A')} "
                          f"| Cost: ${amount:.2f}")
            if costs:
                click.echo(f"\nTotal Cost (shown): ${total_cost:.2f}")

        persistence.close()
    except Exception as e:
        click.echo(f"✗ Query failed: {e}", err=True)
        sys.exit(1)


@database.command()
def examples():
    """Show example commands for common operations."""
    examples_text = """
Example Commands:
=================

1. Initialize SQLite Database:
   openfinops database init --backend sqlite --connection-string "sqlite:///openfinops.db"

2. Initialize PostgreSQL Database:
   openfinops database init --backend postgresql \\
     --connection-string "postgresql://user:pass@localhost:5432/openfinops"

3. Initialize TimescaleDB with 1 year retention:
   openfinops database init --backend timescaledb \\
     --connection-string "postgresql://user:pass@localhost:5432/openfinops" \\
     --retention-days 365

4. Test PostgreSQL Connection:
   openfinops database test-connection --backend postgresql \\
     --connection-string "postgresql://user:pass@localhost:5432/openfinops"

5. View Database Statistics:
   openfinops database stats --backend sqlite \\
     --connection-string "sqlite:///openfinops.db"

6. Query Last 7 Days of Data:
   openfinops database query --backend sqlite \\
     --connection-string "sqlite:///openfinops.db" \\
     --days 7 --limit 100

7. Cleanup Old Data (keep last 90 days):
   openfinops database cleanup --backend postgresql \\
     --connection-string "postgresql://user:pass@localhost/openfinops" \\
     --retention-days 90

Environment Variables:
======================

Set these to avoid repeating connection strings:

export OPENFINOPS_BACKEND=postgresql
export OPENFINOPS_DB_URL=postgresql://user:pass@localhost:5432/openfinops
export OPENFINOPS_RETENTION_DAYS=90

Then use in your Python code:

    import os
    from openfinops.observability.persistence import PersistenceConfig, StorageBackend

    config = PersistenceConfig(
        backend=StorageBackend.POSTGRESQL,
        connection_string=os.getenv('OPENFINOPS_DB_URL'),
        retention_days=int(os.getenv('OPENFINOPS_RETENTION_DAYS', 90))
    )
"""
    click.echo(examples_text)


if __name__ == '__main__':
    database()
