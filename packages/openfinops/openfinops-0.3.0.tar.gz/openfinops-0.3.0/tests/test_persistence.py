"""
Tests for Persistence Layer
============================

Tests for telemetry data persistence backends.
"""

import pytest
import time
import tempfile
import os
from dataclasses import asdict

from openfinops.observability import ObservabilityHub, CostObservatory
from openfinops.observability.persistence import (
    PersistenceConfig,
    StorageBackend,
    create_persistence_backend,
    InMemoryBackend,
    SQLiteBackend
)
from openfinops.observability.observability_hub import SystemMetrics, SystemHealth
from openfinops.observability.cost_observatory import CostEntry, CostCategory


class TestInMemoryBackend:
    """Test in-memory storage backend"""

    def test_in_memory_storage(self):
        """Test in-memory storage"""
        config = PersistenceConfig(
            backend=StorageBackend.IN_MEMORY,
            max_memory_entries=100
        )
        backend = create_persistence_backend(config)

        assert isinstance(backend, InMemoryBackend)

        # Store system metric
        metric = {
            'timestamp': time.time(),
            'cluster_id': 'test-cluster',
            'node_id': 'test-node',
            'cpu_usage': 75.5,
            'memory_usage': 68.2,
            'disk_usage': 50.0
        }
        backend.store_system_metric(metric)

        # Query it back
        results = backend.query_system_metrics(cluster_id='test-cluster')
        assert len(results) == 1
        assert results[0]['cpu_usage'] == 75.5

    def test_in_memory_cost_storage(self):
        """Test cost entry storage in memory"""
        config = PersistenceConfig(backend=StorageBackend.IN_MEMORY)
        backend = create_persistence_backend(config)

        # Store cost entry
        cost = {
            'entry_id': 'test-001',
            'timestamp': time.time(),
            'resource_id': 'i-12345',
            'category': 'compute',
            'amount': 125.50
        }
        backend.store_cost_entry(cost)

        # Query it back
        results = backend.query_cost_entries(resource_id='i-12345')
        assert len(results) == 1
        assert results[0]['amount'] == 125.50

    def test_in_memory_query_filters(self):
        """Test query filtering"""
        config = PersistenceConfig(backend=StorageBackend.IN_MEMORY)
        backend = create_persistence_backend(config)

        # Store multiple metrics
        now = time.time()
        for i in range(10):
            metric = {
                'timestamp': now - (i * 3600),  # 1 hour apart
                'cluster_id': 'cluster-1' if i < 5 else 'cluster-2',
                'node_id': f'node-{i}',
                'cpu_usage': 50.0 + i,
                'memory_usage': 60.0,
                'disk_usage': 40.0
            }
            backend.store_system_metric(metric)

        # Query by cluster
        cluster1_metrics = backend.query_system_metrics(cluster_id='cluster-1')
        assert len(cluster1_metrics) == 5

        # Query by time range
        six_hours_ago = now - (5.5 * 3600)  # Between 5 and 6 hours
        recent_metrics = backend.query_system_metrics(start_time=six_hours_ago)
        assert len(recent_metrics) <= 6


class TestSQLiteBackend:
    """Test SQLite storage backend"""

    def test_sqlite_initialization(self):
        """Test SQLite database initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            config = PersistenceConfig(
                backend=StorageBackend.SQLITE,
                connection_string=f"sqlite:///{db_path}"
            )
            backend = create_persistence_backend(config)

            assert isinstance(backend, SQLiteBackend)
            assert os.path.exists(db_path)

            backend.close()

    def test_sqlite_persistence(self):
        """Test data persists across backend instances"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            config = PersistenceConfig(
                backend=StorageBackend.SQLITE,
                connection_string=f"sqlite:///{db_path}"
            )

            # Store data with first backend instance
            backend1 = create_persistence_backend(config)
            metric = {
                'timestamp': time.time(),
                'cluster_id': 'test-cluster',
                'node_id': 'test-node',
                'cpu_usage': 85.0,
                'memory_usage': 70.0,
                'disk_usage': 60.0
            }
            backend1.store_system_metric(metric)
            backend1.flush_buffer()
            backend1.close()

            # Retrieve with second backend instance
            backend2 = create_persistence_backend(config)
            results = backend2.query_system_metrics(cluster_id='test-cluster')
            assert len(results) == 1
            assert results[0]['cpu_usage'] == 85.0
            backend2.close()

    def test_sqlite_batch_insertion(self):
        """Test batch insertion performance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            config = PersistenceConfig(
                backend=StorageBackend.SQLITE,
                connection_string=f"sqlite:///{db_path}",
                batch_size=10
            )
            backend = create_persistence_backend(config)

            # Store metrics
            now = time.time()
            for i in range(25):
                metric = {
                    'timestamp': now + i,
                    'cluster_id': 'test-cluster',
                    'node_id': f'node-{i % 5}',
                    'cpu_usage': 50.0 + i,
                    'memory_usage': 60.0,
                    'disk_usage': 40.0
                }
                backend.store_system_metric(metric)

            # Force flush
            backend.flush_buffer()

            # Query all
            results = backend.query_system_metrics(limit=100)
            assert len(results) == 25

            backend.close()

    def test_sqlite_cost_entries(self):
        """Test cost entry storage in SQLite"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            config = PersistenceConfig(
                backend=StorageBackend.SQLITE,
                connection_string=f"sqlite:///{db_path}"
            )
            backend = create_persistence_backend(config)

            # Store cost entries
            now = time.time()
            for i in range(5):
                cost = {
                    'entry_id': f'cost-{i}',
                    'timestamp': now + i,
                    'resource_id': f'resource-{i}',
                    'category': 'compute',
                    'amount': 100.0 + i
                }
                backend.store_cost_entry(cost)

            backend.flush_buffer()

            # Query by category
            results = backend.query_cost_entries(category='compute')
            assert len(results) == 5

            # Query by resource
            results = backend.query_cost_entries(resource_id='resource-2')
            assert len(results) == 1
            assert results[0]['amount'] == 102.0

            backend.close()

    def test_sqlite_cleanup(self):
        """Test data cleanup"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            config = PersistenceConfig(
                backend=StorageBackend.SQLITE,
                connection_string=f"sqlite:///{db_path}",
                retention_days=7
            )
            backend = create_persistence_backend(config)

            # Store old and new data
            now = time.time()
            old_time = now - (10 * 24 * 3600)  # 10 days ago

            # Old metric
            backend.store_system_metric({
                'timestamp': old_time,
                'cluster_id': 'old-cluster',
                'node_id': 'old-node',
                'cpu_usage': 50.0,
                'memory_usage': 60.0,
                'disk_usage': 40.0
            })

            # New metric
            backend.store_system_metric({
                'timestamp': now,
                'cluster_id': 'new-cluster',
                'node_id': 'new-node',
                'cpu_usage': 75.0,
                'memory_usage': 80.0,
                'disk_usage': 50.0
            })

            backend.flush_buffer()

            # Verify both exist
            all_metrics = backend.query_system_metrics(limit=100)
            assert len(all_metrics) == 2

            # Cleanup old data
            backend.cleanup_old_data()

            # Verify only new data remains
            remaining = backend.query_system_metrics(limit=100)
            assert len(remaining) == 1
            assert remaining[0]['cluster_id'] == 'new-cluster'

            backend.close()


class TestObservabilityHubIntegration:
    """Test ObservabilityHub with persistence"""

    def test_hub_with_sqlite_persistence(self):
        """Test ObservabilityHub with SQLite persistence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            config = PersistenceConfig(
                backend=StorageBackend.SQLITE,
                connection_string=f"sqlite:///{db_path}"
            )

            hub = ObservabilityHub(persistence_config=config)

            # Collect metrics
            metric = SystemMetrics(
                timestamp=time.time(),
                cpu_usage=75.5,
                memory_usage=68.2,
                disk_usage=50.0,
                cluster_id='test-cluster',
                node_id='test-node',
                health_status=SystemHealth.HEALTHY
            )
            hub.collect_system_metrics(metric)

            # Force flush
            if hub.persistence_backend:
                hub.persistence_backend.flush_buffer()

            # Query historical data
            results = hub.query_historical_metrics(cluster_id='test-cluster')
            assert len(results) >= 1

            hub.close()

    def test_hub_without_persistence(self):
        """Test ObservabilityHub defaults to in-memory"""
        hub = ObservabilityHub()  # No config = in-memory

        metric = SystemMetrics(
            timestamp=time.time(),
            cpu_usage=85.0,
            memory_usage=70.0,
            disk_usage=60.0,
            cluster_id='test-cluster',
            node_id='test-node'
        )
        hub.collect_system_metrics(metric)

        # Query should work (from in-memory)
        results = hub.query_historical_metrics(cluster_id='test-cluster')
        assert len(results) == 1


class TestCostObservatoryIntegration:
    """Test CostObservatory with persistence"""

    def test_cost_obs_with_sqlite_persistence(self):
        """Test CostObservatory with SQLite persistence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'test.db')
            config = PersistenceConfig(
                backend=StorageBackend.SQLITE,
                connection_string=f"sqlite:///{db_path}"
            )

            cost_obs = CostObservatory(persistence_config=config)

            # Add cost entry
            entry = CostEntry(
                entry_id='test-001',
                timestamp=time.time(),
                resource_id='i-12345',
                category=CostCategory.COMPUTE,
                amount=125.50
            )
            cost_obs.add_cost_entry(entry)

            # Force flush
            if cost_obs.persistence_backend:
                cost_obs.persistence_backend.flush_buffer()

            # Query historical costs
            results = cost_obs.query_historical_costs(resource_id='i-12345')
            assert len(results) >= 1
            assert results[0]['amount'] == 125.50

            cost_obs.close()

    def test_cost_obs_without_persistence(self):
        """Test CostObservatory defaults to in-memory"""
        cost_obs = CostObservatory()  # No config = in-memory

        entry = CostEntry(
            entry_id='test-002',
            timestamp=time.time(),
            resource_id='i-67890',
            category=CostCategory.STORAGE,
            amount=50.25
        )
        cost_obs.add_cost_entry(entry)

        # Query should work (from in-memory)
        results = cost_obs.query_historical_costs(resource_id='i-67890')
        assert len(results) == 1


@pytest.mark.skipif(
    not os.getenv('TEST_POSTGRESQL'),
    reason="PostgreSQL tests require TEST_POSTGRESQL env var"
)
class TestPostgreSQLBackend:
    """Test PostgreSQL backend (requires PostgreSQL server)"""

    def test_postgresql_connection(self):
        """Test PostgreSQL connection"""
        connection_string = os.getenv('POSTGRESQL_URL',
                                     'postgresql://localhost/openfinops_test')
        config = PersistenceConfig(
            backend=StorageBackend.POSTGRESQL,
            connection_string=connection_string
        )

        backend = create_persistence_backend(config)
        # If we get here, connection worked
        backend.close()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
