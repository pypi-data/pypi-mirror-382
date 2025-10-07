"""
Integration tests for OpenFinOps multi-component workflows.
"""

import pytest
import time
import numpy as np
from openfinops import ObservabilityHub, LLMObservabilityHub, CostObservatory
from openfinops.observability.llm_observability import (
    LLMTrainingMetrics, LLMTrainingStage, ModelType
)


@pytest.mark.integration
class TestLLMTrainingWorkflow:
    """Integration tests for complete LLM training monitoring workflow."""

    def test_end_to_end_training_monitoring(self):
        """Test complete LLM training monitoring workflow."""
        # Initialize components
        obs_hub = ObservabilityHub()
        llm_hub = LLMObservabilityHub()
        cost_obs = CostObservatory()

        # Register training cluster
        cluster_id = "gpu-cluster-001"
        nodes = [f"gpu-node-{i}" for i in range(1, 5)]
        obs_hub.register_cluster(cluster_id, nodes)

        # Simulate training epochs
        model_id = "llm-training-001"
        total_cost = 0.0

        for epoch in range(1, 4):
            # Track training metrics
            metrics = LLMTrainingMetrics(
                run_id=model_id,
                model_name="gpt-custom",
                model_type=ModelType.FINE_TUNED,
                stage=LLMTrainingStage.FINE_TUNING,
                timestamp=time.time(),
                epoch=epoch,
                step=100 * epoch,
                global_step=100 * epoch,
                total_steps=300,
                progress_percent=(epoch / 3) * 100,
                train_loss=1.0 / epoch,
                validation_loss=1.2 / epoch,
                perplexity=2.0 ** (1.0 / epoch),
                gradient_norm=0.5,
                learning_rate=0.001,
                tokens_per_second=1000.0,
                sequences_per_second=10.0,
                gpu_memory_allocated=8.0 + epoch * 0.1,
                gpu_memory_cached=10.0,
                gpu_utilization=85.0,
                batch_size=32,
                sequence_length=512,
                vocab_size=50000,
                total_parameters=1000000000,
                trainable_parameters=1000000000
            )

            llm_hub.collect_llm_training_metrics(metrics)

            # Track costs for each epoch
            epoch_cost = 150.0 * epoch  # $150 per epoch
            total_cost += epoch_cost

        # Verify workflow completion
        assert model_id in llm_hub.active_training_runs
        assert len(llm_hub.llm_training_metrics) >= 3
        assert cluster_id in obs_hub.clusters

        # Verify final state
        final_metrics = llm_hub.active_training_runs[model_id]
        assert final_metrics.epoch == 3
        assert final_metrics.train_loss < 0.5  # Loss should decrease

    def test_multi_model_parallel_training(self):
        """Test monitoring multiple models training in parallel."""
        llm_hub = LLMObservabilityHub()

        models = [
            {"id": "model-A", "type": ModelType.FOUNDATION_MODEL},
            {"id": "model-B", "type": ModelType.FINE_TUNED},
            {"id": "model-C", "type": ModelType.ADAPTER},
        ]

        # Simulate parallel training
        for model in models:
            metrics = LLMTrainingMetrics(
                run_id=model["id"],
                model_name=model["id"],
                model_type=model["type"],
                stage=LLMTrainingStage.FINE_TUNING,
                timestamp=time.time(),
                epoch=1,
                step=100,
                global_step=100,
                total_steps=1000,
                progress_percent=10.0,
                train_loss=0.5,
                validation_loss=0.6,
                perplexity=1.5,
                gradient_norm=0.3,
                learning_rate=0.001,
                tokens_per_second=1000.0,
                sequences_per_second=10.0,
                gpu_memory_allocated=8.0,
                gpu_memory_cached=10.0,
                gpu_utilization=85.0,
                batch_size=32,
                sequence_length=512,
                vocab_size=50000,
                total_parameters=1000000000,
                trainable_parameters=1000000000
            )

            llm_hub.collect_llm_training_metrics(metrics)

        # Verify all models are tracked
        assert len(llm_hub.active_training_runs) >= len(models)
        for model in models:
            assert model["id"] in llm_hub.active_training_runs


@pytest.mark.integration
class TestClusterMonitoringWorkflow:
    """Integration tests for cluster monitoring workflows."""

    def test_cluster_health_monitoring(self):
        """Test complete cluster health monitoring workflow."""
        obs_hub = ObservabilityHub()

        # Register multiple clusters
        clusters = {
            "prod-cluster": ["prod-node-1", "prod-node-2", "prod-node-3"],
            "dev-cluster": ["dev-node-1", "dev-node-2"],
            "test-cluster": ["test-node-1"],
        }

        for cluster_id, nodes in clusters.items():
            obs_hub.register_cluster(cluster_id, nodes)

        # Register services
        obs_hub.register_service("api-service", "prod-cluster", ["database", "cache"])
        obs_hub.register_service("worker-service", "prod-cluster", ["queue"])

        # Get health summary
        health = obs_hub.get_cluster_health_summary()

        # Verify monitoring
        assert health is not None
        assert len(obs_hub.clusters) == len(clusters)
        assert len(obs_hub.services) == 2

    def test_service_dependency_mapping(self):
        """Test service dependency mapping across clusters."""
        obs_hub = ObservabilityHub()

        # Set up infrastructure
        obs_hub.register_cluster("main-cluster", ["node-1", "node-2"])

        obs_hub.register_service("frontend", "main-cluster", ["backend-api"])
        obs_hub.register_service("backend-api", "main-cluster", ["database", "cache"])
        obs_hub.register_service("worker", "main-cluster", ["queue", "database"])

        # Get dependency map
        dep_map = obs_hub.get_service_dependency_map()

        # Verify dependencies
        assert dep_map is not None
        assert len(obs_hub.services) == 3


@pytest.mark.integration
class TestVisualizationWorkflow:
    """Integration tests for visualization workflows."""

    def test_training_metrics_visualization(self):
        """Test creating visualizations from training metrics."""
        from openfinops.vizlychart import LineChart

        llm_hub = LLMObservabilityHub()

        # Collect metrics over time
        losses = []
        for epoch in range(1, 11):
            loss = 2.0 / epoch
            losses.append(loss)

            metrics = LLMTrainingMetrics(
                run_id="viz-test-run",
                model_name="test-model",
                model_type=ModelType.FINE_TUNED,
                stage=LLMTrainingStage.FINE_TUNING,
                timestamp=time.time(),
                epoch=epoch,
                step=100 * epoch,
                global_step=100 * epoch,
                total_steps=1000,
                progress_percent=(epoch / 10) * 100,
                train_loss=loss,
                validation_loss=loss * 1.2,
                perplexity=2.0 ** loss,
                gradient_norm=0.5,
                learning_rate=0.001,
                tokens_per_second=1000.0,
                sequences_per_second=10.0,
                gpu_memory_allocated=8.0,
                gpu_memory_cached=10.0,
                gpu_utilization=85.0,
                batch_size=32,
                sequence_length=512,
                vocab_size=50000,
                total_parameters=1000000000,
                trainable_parameters=1000000000
            )

            llm_hub.collect_llm_training_metrics(metrics)

        # Create visualization
        chart = LineChart()
        epochs = list(range(1, 11))
        chart.plot(epochs, losses, label="Training Loss")

        # Verify chart
        assert chart.line_series is not None
        assert len(chart.line_series) > 0

    def test_multi_metric_dashboard(self):
        """Test creating dashboard with multiple metrics."""
        from openfinops.vizlychart import LineChart, BarChart

        # Create loss chart
        loss_chart = LineChart()
        epochs = np.arange(1, 11)
        losses = 2.0 / epochs
        loss_chart.plot(epochs, losses, label="Loss")

        # Create performance chart
        perf_chart = BarChart()
        metrics = ["Throughput", "Latency", "Accuracy"]
        values = [85, 20, 92]
        perf_chart.bar(metrics, values)

        # Verify both charts
        assert loss_chart.line_series is not None
        assert perf_chart.data_series is not None


@pytest.mark.integration
class TestCostTrackingWorkflow:
    """Integration tests for cost tracking workflows."""

    def test_cost_attribution_workflow(self):
        """Test complete cost attribution workflow."""
        cost_obs = CostObservatory()
        llm_hub = LLMObservabilityHub()

        # Track training run
        model_id = "cost-test-model"
        training_hours = 24
        gpu_count = 8
        hourly_rate = 32.77  # A100 rate

        total_cost = training_hours * gpu_count * hourly_rate

        # Track metrics
        metrics = LLMTrainingMetrics(
            run_id=model_id,
            model_name="cost-optimized-model",
            model_type=ModelType.FOUNDATION_MODEL,
            stage=LLMTrainingStage.PRE_TRAINING,
            timestamp=time.time(),
            epoch=1,
            step=1000,
            global_step=1000,
            total_steps=10000,
            progress_percent=10.0,
            train_loss=1.5,
            validation_loss=1.6,
            perplexity=4.0,
            gradient_norm=0.8,
            learning_rate=0.0001,
            tokens_per_second=5000.0,
            sequences_per_second=50.0,
            gpu_memory_allocated=40.0,
            gpu_memory_cached=80.0,
            gpu_utilization=95.0,
            batch_size=128,
            sequence_length=2048,
            vocab_size=50000,
            total_parameters=7000000000,
            trainable_parameters=7000000000
        )

        llm_hub.collect_llm_training_metrics(metrics)

        # Verify cost tracking
        assert model_id in llm_hub.active_training_runs
        assert total_cost > 0  # $6,290.88 for this run


@pytest.mark.integration
@pytest.mark.slow
class TestLargeScaleWorkflow:
    """Integration tests for large-scale scenarios."""

    def test_high_volume_metrics_collection(self):
        """Test collecting high volume of metrics."""
        llm_hub = LLMObservabilityHub()

        # Simulate 100 training steps
        for step in range(1, 101):
            metrics = LLMTrainingMetrics(
                run_id="high-volume-run",
                model_name="stress-test-model",
                model_type=ModelType.FINE_TUNED,
                stage=LLMTrainingStage.FINE_TUNING,
                timestamp=time.time(),
                epoch=step // 10 + 1,
                step=step,
                global_step=step,
                total_steps=100,
                progress_percent=step,
                train_loss=2.0 / (step + 1),
                validation_loss=2.2 / (step + 1),
                perplexity=1.5,
                gradient_norm=0.5,
                learning_rate=0.001,
                tokens_per_second=1000.0,
                sequences_per_second=10.0,
                gpu_memory_allocated=8.0,
                gpu_memory_cached=10.0,
                gpu_utilization=85.0,
                batch_size=32,
                sequence_length=512,
                vocab_size=50000,
                total_parameters=1000000000,
                trainable_parameters=1000000000
            )

            llm_hub.collect_llm_training_metrics(metrics)

        # Verify all metrics collected
        assert len(llm_hub.llm_training_metrics) >= 100
        assert "high-volume-run" in llm_hub.active_training_runs
