"""
Pytest configuration and shared fixtures for OpenFinOps tests.
"""

import pytest
import time
from datetime import datetime
from typing import Dict, Any


@pytest.fixture
def sample_llm_metrics():
    """Sample LLM training metrics for testing."""
    from openfinops.observability.llm_observability import (
        LLMTrainingMetrics, LLMTrainingStage, ModelType
    )

    return LLMTrainingMetrics(
        run_id="test-run-001",
        model_name="test-model",
        model_type=ModelType.FINE_TUNED,
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


@pytest.fixture
def observability_hub():
    """ObservabilityHub instance for testing."""
    from openfinops import ObservabilityHub
    return ObservabilityHub()


@pytest.fixture
def llm_observability_hub():
    """LLMObservabilityHub instance for testing."""
    from openfinops import LLMObservabilityHub
    return LLMObservabilityHub()


@pytest.fixture
def cost_observatory():
    """CostObservatory instance for testing."""
    from openfinops import CostObservatory
    return CostObservatory()


@pytest.fixture
def sample_cluster_config():
    """Sample cluster configuration."""
    return {
        "cluster_name": "test-cluster",
        "nodes": ["node-1", "node-2", "node-3"],
        "gpu_type": "A100",
        "num_gpus": 8
    }


@pytest.fixture
def sample_cost_data():
    """Sample cost tracking data."""
    return {
        "provider": "aws",
        "service": "sagemaker",
        "cost": 1234.56,
        "currency": "USD",
        "timestamp": datetime.now().isoformat(),
        "tags": {
            "team": "ml-research",
            "project": "llm-training"
        }
    }


@pytest.fixture(autouse=True)
def setup_test_users():
    """Automatically create test users for all tests."""
    from openfinops.dashboard.iam_system import get_iam_manager

    iam = get_iam_manager()

    # Create test CFO user
    if "test-cfo-001" not in iam.users:
        iam.create_user({
            "user_id": "test-cfo-001",
            "username": "test_cfo",
            "email": "cfo@test.com",
            "full_name": "Test CFO",
            "department": "Finance",
            "roles": ["cfo"],  # Lowercase role name
            "password": "test123"
        })

    # Create test COO user
    if "test-coo-001" not in iam.users:
        iam.create_user({
            "user_id": "test-coo-001",
            "username": "test_coo",
            "email": "coo@test.com",
            "full_name": "Test COO",
            "department": "Operations",
            "roles": ["coo"],  # Lowercase role name
            "password": "test123"
        })

    # Create test Infrastructure Leader user
    if "test-infra-001" not in iam.users:
        iam.create_user({
            "user_id": "test-infra-001",
            "username": "test_infra",
            "email": "infra@test.com",
            "full_name": "Test Infrastructure Leader",
            "department": "Engineering",
            "roles": ["infrastructure_leader"],  # Lowercase role name
            "password": "test123"
        })

    # Create test Finance Analyst user
    if "test-analyst-001" not in iam.users:
        iam.create_user({
            "user_id": "test-analyst-001",
            "username": "test_analyst",
            "email": "analyst@test.com",
            "full_name": "Test Finance Analyst",
            "department": "Finance",
            "roles": ["finance_analyst"],  # Lowercase role name
            "password": "test123"
        })

    yield

    # Cleanup after tests (optional - comment out if you want to keep users between test runs)
    # for user_id in ["test-cfo-001", "test-coo-001", "test-infra-001", "test-analyst-001"]:
    #     if user_id in iam.users:
    #         del iam.users[user_id]
