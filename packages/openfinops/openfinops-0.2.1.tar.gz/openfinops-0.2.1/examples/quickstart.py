#!/usr/bin/env python3
"""
OpenFinOps Quick Start Example
================================

This example demonstrates basic usage of OpenFinOps for AI/ML cost monitoring.
"""

import sys
import os
import time

# Add parent directory to path for local development
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openfinops import ObservabilityHub, LLMObservabilityHub


def main():
    """Quick start example."""
    print("=" * 60)
    print("OpenFinOps Quick Start")
    print("=" * 60)
    print()

    # Initialize observability hub
    print("1. Initializing ObservabilityHub...")
    hub = ObservabilityHub()
    print("   ✓ ObservabilityHub initialized")
    print()

    # Initialize LLM observability
    print("2. Initializing LLMObservabilityHub...")
    llm_hub = LLMObservabilityHub()
    print("   ✓ LLMObservabilityHub initialized")
    print()

    # Collect LLM training metrics
    print("3. Collecting LLM training metrics...")
    from openfinops.observability.llm_observability import (
        LLMTrainingMetrics, LLMTrainingStage, ModelType
    )

    for epoch in range(1, 4):
        metrics = LLMTrainingMetrics(
            run_id="demo-run-001",
            model_name="demo-llm",
            model_type=ModelType.FINE_TUNED,
            stage=LLMTrainingStage.FINE_TUNING,
            timestamp=time.time(),
            epoch=epoch,
            step=100 * epoch,
            global_step=100 * epoch,
            total_steps=1000,
            progress_percent=epoch * 33.3,
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
        print(f"   ✓ Epoch {epoch} metrics collected (loss: {metrics.train_loss:.3f})")
    print()

    # Get cluster health summary
    print("4. Getting cluster health summary...")
    try:
        summary = hub.get_cluster_health_summary()
        print(f"   ✓ Health summary retrieved")
        print(f"   Clusters monitored: {len(summary) if summary else 0}")
    except Exception as e:
        print(f"   ⚠ Could not get summary: {e}")
    print()

    print("=" * 60)
    print("Quick Start Complete!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("- Check out other examples in the examples/ directory")
    print("- Read the documentation in docs/")
    print("- Start the dashboard: openfinops-dashboard")
    print()


if __name__ == "__main__":
    main()
