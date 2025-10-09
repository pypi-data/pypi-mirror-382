"""
Unit tests for ObservabilityHub core functionality.
"""

import pytest
import time
from openfinops import ObservabilityHub


@pytest.mark.unit
class TestObservabilityHub:
    """Test suite for ObservabilityHub."""

    def test_initialization(self, observability_hub):
        """Test ObservabilityHub initialization."""
        assert observability_hub is not None
        assert hasattr(observability_hub, 'clusters')
        assert hasattr(observability_hub, 'system_metrics')
        assert hasattr(observability_hub, 'service_metrics')

    def test_register_cluster(self, observability_hub, sample_cluster_config):
        """Test cluster registration."""
        cluster_id = sample_cluster_config['cluster_name']
        nodes = sample_cluster_config['nodes']

        observability_hub.register_cluster(
            cluster_id=cluster_id,
            nodes=nodes
        )

        # Verify cluster is registered
        assert cluster_id in observability_hub.clusters
        assert observability_hub.clusters[cluster_id]['nodes'] == nodes

    def test_collect_system_metrics(self, observability_hub):
        """Test system metrics collection."""
        from openfinops.observability.observability_hub import SystemMetrics

        # Create system metrics
        metrics = SystemMetrics(
            timestamp=time.time(),
            cpu_usage=75.5,
            memory_usage=80.0,
            disk_usage=60.0,
            network_io={'in': 1000, 'out': 800},
            active_connections=50,
            error_count=2,
            warning_count=5
        )

        observability_hub.collect_system_metrics(metrics)

        # Verify metrics are stored
        assert len(observability_hub.system_metrics) > 0

    def test_get_cluster_health_summary(self, observability_hub, sample_cluster_config):
        """Test cluster health summary retrieval."""
        cluster_name = sample_cluster_config['cluster_name']
        nodes = sample_cluster_config['nodes']

        # Register cluster
        observability_hub.register_cluster(cluster_name, nodes)

        # Get health summary
        summary = observability_hub.get_cluster_health_summary()

        assert summary is not None
        assert isinstance(summary, (dict, list))

    def test_service_registration(self, observability_hub, sample_cluster_config):
        """Test service registration."""
        cluster_id = sample_cluster_config['cluster_name']
        nodes = sample_cluster_config['nodes']

        # Register cluster first
        observability_hub.register_cluster(cluster_id, nodes)

        # Register service
        observability_hub.register_service(
            service_name="api-service",
            cluster_id=cluster_id,
            dependencies=["database", "cache"]
        )

        # Verify service is registered
        assert "api-service" in observability_hub.services
        assert observability_hub.services["api-service"]["cluster_id"] == cluster_id

    def test_multiple_clusters(self, observability_hub):
        """Test managing multiple clusters."""
        clusters = [
            {"id": "cluster-1", "nodes": ["n1-1", "n1-2"]},
            {"id": "cluster-2", "nodes": ["n2-1", "n2-2", "n2-3"]},
            {"id": "cluster-3", "nodes": ["n3-1"]},
        ]

        for cluster in clusters:
            observability_hub.register_cluster(
                cluster_id=cluster['id'],
                nodes=cluster['nodes']
            )

        # Verify all clusters are registered
        assert len(observability_hub.clusters) >= len(clusters)
        for cluster in clusters:
            assert cluster['id'] in observability_hub.clusters
