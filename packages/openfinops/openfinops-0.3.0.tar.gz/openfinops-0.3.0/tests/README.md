# OpenFinOps Test Suite

Comprehensive test suite for OpenFinOps platform using pytest.

## Quick Start

```bash
# Install test dependencies
pip install -e ".[dev]"
# or
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src/openfinops --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m visualization # Visualization tests only
```

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── test_observability_hub.py  # ObservabilityHub tests
├── test_llm_observability.py  # LLM observability tests
├── test_vizlychart.py         # VizlyChart library tests
└── test_dashboards.py         # Dashboard component tests
```

## Test Categories

### Unit Tests (`-m unit`)
Fast, isolated tests for individual components:
- Core observability platform
- LLM metrics collection
- VizlyChart rendering
- Dashboard initialization

### Integration Tests (`-m integration`)
Tests that verify component interactions:
- Multi-cluster monitoring
- End-to-end metric collection
- Dashboard data flow

### Visualization Tests (`-m visualization`)
Chart and visualization rendering tests:
- 2D charts (line, scatter, bar)
- 3D visualizations (surface, scatter)
- Styling and theming

### Cloud Tests (`-m cloud`)
Tests requiring cloud provider credentials (skipped by default):
- AWS telemetry agents
- Azure telemetry agents
- GCP telemetry agents

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_observability_hub.py
```

### Run Specific Test Function
```bash
pytest tests/test_observability_hub.py::TestObservabilityHub::test_initialization
```

### Run Tests in Parallel
```bash
pytest -n auto  # Uses all CPU cores
pytest -n 4     # Uses 4 workers
```

### Run with Coverage Report
```bash
# Terminal report
pytest --cov=src/openfinops --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=src/openfinops --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=src/openfinops --cov-report=xml
```

### Filter by Test Markers
```bash
pytest -m unit                    # Run unit tests
pytest -m "unit and visualization" # Run unit visualization tests
pytest -m "not slow"              # Skip slow tests
pytest -m "not cloud"             # Skip cloud provider tests
```

## Coverage Requirements

- **Minimum Coverage**: 80%
- **Target Coverage**: 90%+

Current coverage by module:
- `observability/`: Target 90%
- `vizlychart/`: Target 85%
- `dashboard/`: Target 85%
- `agents/`: Target 70% (requires cloud SDKs)

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Using Fixtures
```python
def test_with_observability_hub(observability_hub):
    """Use shared fixture from conftest.py"""
    observability_hub.register_cluster("test", ["node1"])
    assert "test" in observability_hub.clusters
```

### Parametric Tests
```python
@pytest.mark.parametrize("model_type", [
    ModelType.FOUNDATION_MODEL,
    ModelType.FINE_TUNED,
])
def test_model_types(llm_observability_hub, model_type):
    """Test multiple model types"""
    # Test logic here
```

### Marking Tests
```python
@pytest.mark.unit
@pytest.mark.slow
def test_expensive_operation():
    """Mark tests with appropriate markers"""
    # Test logic
```

## Continuous Integration

Tests run automatically on:
- **Push to main/develop**: Full test suite
- **Pull requests**: Full test suite + code quality checks
- **Scheduled**: Nightly full test suite with cloud tests

### GitHub Actions Workflow
- Python versions: 3.8, 3.9, 3.10, 3.11, 3.12
- Coverage uploaded to Codecov
- Test artifacts saved for 30 days

## Debugging Failed Tests

### Run with Debug Output
```bash
pytest -vv --tb=long
```

### Run with Print Statements
```bash
pytest -s  # Show print() output
```

### Run Last Failed Tests
```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

### Drop into Debugger on Failure
```bash
pytest --pdb
```

## Test Fixtures

### Available Fixtures (from conftest.py)
- `observability_hub` - ObservabilityHub instance
- `llm_observability_hub` - LLMObservabilityHub instance
- `cost_observatory` - CostObservatory instance
- `sample_llm_metrics` - Sample LLM training metrics
- `sample_cluster_config` - Sample cluster configuration
- `sample_cost_data` - Sample cost tracking data

### Creating Custom Fixtures
```python
# In your test file
@pytest.fixture
def custom_setup():
    # Setup code
    yield resource
    # Teardown code
```

## Performance Testing

```bash
# Time each test
pytest --durations=10

# Profile test execution
pytest --profile

# Benchmark tests
pytest --benchmark-only
```

## Mocking Cloud Services

For cloud provider tests without credentials:

```python
@pytest.mark.cloud
def test_aws_agent(mocker):
    """Test AWS agent with mocked boto3"""
    mock_boto = mocker.patch('boto3.client')
    # Test logic with mocked AWS
```

## Contributing Tests

When adding new features:
1. Write tests first (TDD)
2. Ensure >80% coverage for new code
3. Add appropriate markers
4. Update this README if adding new test categories

## Troubleshooting

### Common Issues

**ModuleNotFoundError**
```bash
pip install -e .  # Install package in development mode
```

**Coverage report not generated**
```bash
pip install pytest-cov coverage
```

**Parallel tests failing**
```bash
pytest -n 0  # Disable parallel execution
```

**Cloud tests failing**
```bash
pytest -m "not cloud"  # Skip cloud tests
```

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [OpenFinOps Contributing Guide](../CONTRIBUTING.md)
