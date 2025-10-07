"""
Unit tests for LLMObservabilityHub.
"""

import pytest
import time
from openfinops import LLMObservabilityHub
from openfinops.observability.llm_observability import (
    LLMTrainingMetrics, RAGPipelineMetrics, LLMTrainingStage,
    RAGStage, ModelType
)


@pytest.mark.unit
class TestLLMObservabilityHub:
    """Test suite for LLMObservabilityHub."""

    def test_initialization(self, llm_observability_hub):
        """Test LLMObservabilityHub initialization."""
        assert llm_observability_hub is not None
        assert hasattr(llm_observability_hub, 'llm_training_metrics')
        assert hasattr(llm_observability_hub, 'rag_pipeline_metrics')
        assert hasattr(llm_observability_hub, 'active_training_runs')

    def test_collect_llm_training_metrics(self, llm_observability_hub, sample_llm_metrics):
        """Test collecting LLM training metrics."""
        initial_count = len(llm_observability_hub.llm_training_metrics)

        llm_observability_hub.collect_llm_training_metrics(sample_llm_metrics)

        # Verify metrics are collected
        assert len(llm_observability_hub.llm_training_metrics) == initial_count + 1
        assert sample_llm_metrics.run_id in llm_observability_hub.active_training_runs

    def test_collect_multiple_epochs(self, llm_observability_hub):
        """Test collecting metrics for multiple training epochs."""
        run_id = "multi-epoch-test"

        for epoch in range(1, 4):
            metrics = LLMTrainingMetrics(
                run_id=run_id,
                model_name="test-model",
                model_type=ModelType.FINE_TUNED,
                stage=LLMTrainingStage.FINE_TUNING,
                timestamp=time.time(),
                epoch=epoch,
                step=100 * epoch,
                global_step=100 * epoch,
                total_steps=1000,
                progress_percent=epoch * 10.0,
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

            llm_observability_hub.collect_llm_training_metrics(metrics)

        # Verify all epochs collected
        assert len(llm_observability_hub.llm_training_metrics) >= 3
        assert run_id in llm_observability_hub.active_training_runs

    def test_training_loss_tracking(self, llm_observability_hub):
        """Test that training loss is properly tracked across epochs."""
        run_id = "loss-tracking-test"
        losses = [1.0, 0.5, 0.25, 0.125]

        for i, loss in enumerate(losses):
            metrics = LLMTrainingMetrics(
                run_id=run_id,
                model_name="test-model",
                model_type=ModelType.FINE_TUNED,
                stage=LLMTrainingStage.FINE_TUNING,
                timestamp=time.time(),
                epoch=i + 1,
                step=(i + 1) * 100,
                global_step=(i + 1) * 100,
                total_steps=1000,
                progress_percent=(i + 1) * 25.0,
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

            llm_observability_hub.collect_llm_training_metrics(metrics)

        # Verify latest metrics reflect last loss
        latest = llm_observability_hub.active_training_runs[run_id]
        assert latest.train_loss == losses[-1]
        assert latest.epoch == len(losses)

    def test_gpu_memory_tracking(self, llm_observability_hub, sample_llm_metrics):
        """Test GPU memory usage tracking."""
        llm_observability_hub.collect_llm_training_metrics(sample_llm_metrics)

        latest = llm_observability_hub.active_training_runs[sample_llm_metrics.run_id]
        assert latest.gpu_memory_allocated > 0
        assert latest.gpu_utilization > 0

    @pytest.mark.parametrize("model_type", [
        ModelType.FOUNDATION_MODEL,
        ModelType.FINE_TUNED,
        ModelType.ADAPTER,
        ModelType.EMBEDDING_MODEL,
    ])
    def test_different_model_types(self, llm_observability_hub, model_type):
        """Test tracking different model types."""
        metrics = LLMTrainingMetrics(
            run_id=f"test-{model_type.value}",
            model_name=f"model-{model_type.value}",
            model_type=model_type,
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

        llm_observability_hub.collect_llm_training_metrics(metrics)

        assert metrics.run_id in llm_observability_hub.active_training_runs
        assert llm_observability_hub.active_training_runs[metrics.run_id].model_type == model_type
