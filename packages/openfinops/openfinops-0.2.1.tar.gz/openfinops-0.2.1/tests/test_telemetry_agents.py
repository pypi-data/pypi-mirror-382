"""
Tests for cloud telemetry agents with mocked cloud services.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add agents directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))


@pytest.mark.unit
@pytest.mark.cloud
class TestAWSTelemetryAgent:
    """Tests for AWS telemetry agent with mocked boto3."""

    @patch('boto3.client')
    def test_aws_agent_initialization(self, mock_boto_client):
        """Test AWS agent initializes with mocked boto3."""
        from aws_telemetry_agent import AWSTelemetryAgent

        mock_boto_client.return_value = MagicMock()

        agent = AWSTelemetryAgent(
            openfinops_endpoint='http://localhost:8080',
            aws_region='us-east-1'
        )

        assert agent is not None
        assert agent.openfinops_endpoint == 'http://localhost:8080'
        assert agent.region == 'us-east-1'

    @patch('boto3.Session')
    def test_ec2_metrics_collection(self, mock_session_class):
        """Test EC2 metrics collection with mocked responses."""
        from aws_telemetry_agent import AWSTelemetryAgent

        # Mock EC2 client
        mock_ec2 = MagicMock()
        mock_ec2.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-1234567890abcdef0',
                            'InstanceType': 'p3.8xlarge',
                            'State': {'Name': 'running'},
                            'Placement': {'AvailabilityZone': 'us-east-1a'},
                            'LaunchTime': MagicMock(isoformat=lambda: '2024-01-01T00:00:00Z'),
                            'Tags': [{'Key': 'Name', 'Value': 'gpu-instance-1'}]
                        }
                    ]
                }
            ]
        }

        mock_cloudwatch = MagicMock()
        mock_cloudwatch.get_metric_statistics.return_value = {'Datapoints': []}

        # Mock session that returns appropriate clients
        mock_session = MagicMock()
        def get_client(service_name):
            if service_name == 'ec2':
                return mock_ec2
            elif service_name == 'cloudwatch':
                return mock_cloudwatch
            return MagicMock()

        mock_session.client = get_client
        mock_session_class.return_value = mock_session

        agent = AWSTelemetryAgent(
            openfinops_endpoint='http://localhost:8080',
            aws_region='us-east-1'
        )

        # Test metrics collection
        metrics = agent.collect_ec2_metrics()

        assert metrics is not None
        assert 'instances' in metrics or 'service' in metrics
        mock_ec2.describe_instances.assert_called_once()

    @patch('boto3.Session')
    @patch('requests.post')
    def test_metrics_push_to_openfinops(self, mock_post, mock_session_class):
        """Test pushing metrics to OpenFinOps endpoint."""
        from aws_telemetry_agent import AWSTelemetryAgent

        mock_session_class.return_value = MagicMock()
        mock_post.return_value = Mock(status_code=200)

        agent = AWSTelemetryAgent(
            openfinops_endpoint='http://localhost:8080',
            aws_region='us-east-1'
        )

        # Mock metrics data
        metrics = {
            'timestamp': '2024-10-03T00:00:00Z',
            'region': 'us-east-1',
            'ec2_instances': 5,
            'total_cost': 1234.56
        }

        # Push metrics
        agent.push_metrics(metrics)

        # Verify POST request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'http://localhost:8080' in call_args[0][0]


@pytest.mark.unit
@pytest.mark.cloud
class TestAzureTelemetryAgent:
    """Tests for Azure telemetry agent with mocked Azure SDK."""

    @patch('azure.identity.DefaultAzureCredential')
    @patch('azure.mgmt.compute.ComputeManagementClient')
    def test_azure_agent_initialization(self, mock_compute_client, mock_credential):
        """Test Azure agent initializes with mocked SDK."""
        from azure_telemetry_agent import AzureTelemetryAgent

        mock_credential.return_value = MagicMock()
        mock_compute_client.return_value = MagicMock()

        agent = AzureTelemetryAgent(
            openfinops_endpoint='http://localhost:8080',
            subscription_id='test-sub-id'
        )

        assert agent is not None
        assert agent.openfinops_endpoint == 'http://localhost:8080'

    @patch('azure.identity.DefaultAzureCredential')
    @patch('azure.mgmt.compute.ComputeManagementClient')
    def test_vm_metrics_collection(self, mock_compute_client, mock_credential):
        """Test Azure VM metrics collection."""
        from azure_telemetry_agent import AzureTelemetryAgent

        # Mock VM list
        mock_vm = MagicMock()
        mock_vm.name = 'gpu-vm-1'
        mock_vm.hardware_profile.vm_size = 'Standard_NC6s_v3'
        mock_vm.provisioning_state = 'Succeeded'

        # Setup proper mock structure
        mock_compute = MagicMock()
        mock_vms = MagicMock()
        mock_vms.list_all.return_value = [mock_vm]
        mock_compute.virtual_machines = mock_vms

        mock_credential.return_value = MagicMock()
        mock_compute_client.return_value = mock_compute

        agent = AzureTelemetryAgent(
            openfinops_endpoint='http://localhost:8080',
            subscription_id='test-sub-id'
        )

        # Collect metrics
        metrics = agent.collect_vm_metrics()

        # Just verify metrics were collected
        assert metrics is not None
        assert isinstance(metrics, dict)


@pytest.mark.unit
@pytest.mark.cloud
class TestGCPTelemetryAgent:
    """Tests for GCP telemetry agent with mocked Google Cloud SDK."""

    @patch('google.auth.default')
    @patch('google.cloud.compute_v1.InstancesClient')
    @patch('google.cloud.container_v1.ClusterManagerClient')
    @patch('google.cloud.functions_v1.CloudFunctionsServiceClient')
    @patch('google.cloud.storage.Client')
    @patch('google.cloud.monitoring_v3.MetricServiceClient')
    def test_gcp_agent_initialization(self, mock_monitoring, mock_storage, mock_functions,
                                      mock_container, mock_compute, mock_auth):
        """Test GCP agent initializes with mocked SDK."""
        from gcp_telemetry_agent import GCPTelemetryAgent

        # Mock authentication
        mock_creds = MagicMock()
        mock_auth.return_value = (mock_creds, 'test-project')

        # Mock all clients
        mock_compute.return_value = MagicMock()
        mock_container.return_value = MagicMock()
        mock_functions.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        mock_monitoring.return_value = MagicMock()

        agent = GCPTelemetryAgent(
            openfinops_endpoint='http://localhost:8080',
            project_id='test-project'
        )

        assert agent is not None
        assert agent.openfinops_endpoint == 'http://localhost:8080'
        assert agent.project_id == 'test-project'

    @patch('google.auth.default')
    @patch('google.cloud.compute_v1.InstancesClient')
    @patch('google.cloud.container_v1.ClusterManagerClient')
    @patch('google.cloud.functions_v1.CloudFunctionsServiceClient')
    @patch('google.cloud.storage.Client')
    @patch('google.cloud.monitoring_v3.MetricServiceClient')
    def test_compute_metrics_collection(self, mock_monitoring, mock_storage, mock_functions,
                                       mock_container, mock_compute, mock_auth):
        """Test GCP Compute Engine metrics collection."""
        from gcp_telemetry_agent import GCPTelemetryAgent

        # Mock authentication
        mock_creds = MagicMock()
        mock_auth.return_value = (mock_creds, 'test-project')

        # Mock instance
        mock_instance = MagicMock()
        mock_instance.name = 'gpu-instance-1'
        mock_instance.machine_type = 'n1-standard-8'
        mock_instance.status = 'RUNNING'

        # Mock aggregated list response
        mock_compute_instance = MagicMock()
        mock_compute_instance.aggregated_list.return_value = MagicMock(
            items={'zones/us-central1-a': MagicMock(instances=[mock_instance])}
        )
        mock_compute.return_value = mock_compute_instance

        # Mock other clients
        mock_container.return_value = MagicMock()
        mock_functions.return_value = MagicMock()
        mock_storage.return_value = MagicMock()
        mock_monitoring.return_value = MagicMock()

        agent = GCPTelemetryAgent(
            openfinops_endpoint='http://localhost:8080',
            project_id='test-project'
        )

        # Collect metrics
        metrics = agent.collect_compute_metrics()

        assert metrics is not None


@pytest.mark.unit
class TestGenericTelemetryAgent:
    """Tests for generic telemetry agent."""

    def test_generic_agent_initialization(self):
        """Test generic agent initialization."""
        from generic_telemetry_agent import GenericTelemetryAgent

        agent = GenericTelemetryAgent(
            openfinops_endpoint='http://localhost:8080'
        )

        assert agent is not None
        assert agent.openfinops_endpoint == 'http://localhost:8080'

    @patch('requests.post')
    def test_custom_metric_collection(self, mock_post):
        """Test custom metric collection and push."""
        from generic_telemetry_agent import GenericTelemetryAgent

        mock_post.return_value = Mock(status_code=200)

        agent = GenericTelemetryAgent(
            openfinops_endpoint='http://localhost:8080'
        )

        # Register custom metric collector
        def custom_collector():
            return {
                'cpu_usage': 75.0,
                'memory_usage': 80.0,
                'custom_metric': 42
            }

        agent.register_metric_collector('custom', custom_collector)

        # Collect and push metrics
        metrics = agent.collect_metrics()
        assert 'custom' in metrics

        agent.push_metrics(metrics)
        mock_post.assert_called_once()

    def test_metric_aggregation(self):
        """Test metric aggregation across sources."""
        from generic_telemetry_agent import GenericTelemetryAgent

        agent = GenericTelemetryAgent(
            openfinops_endpoint='http://localhost:8080'
        )

        # Register multiple collectors
        agent.register_metric_collector('source1', lambda: {'value': 10})
        agent.register_metric_collector('source2', lambda: {'value': 20})

        # Collect all metrics
        all_metrics = agent.collect_metrics()

        assert 'source1' in all_metrics
        assert 'source2' in all_metrics


@pytest.mark.integration
@pytest.mark.cloud
class TestTelemetryAgentIntegration:
    """Integration tests for telemetry agents."""

    @patch('boto3.Session')
    @patch('requests.post')
    def test_aws_to_openfinops_workflow(self, mock_post, mock_session_class):
        """Test complete AWS to OpenFinOps workflow."""
        from aws_telemetry_agent import AWSTelemetryAgent

        # Mock AWS responses
        mock_ec2 = MagicMock()
        mock_ec2.describe_instances.return_value = {
            'Reservations': [
                {
                    'Instances': [
                        {
                            'InstanceId': 'i-test',
                            'InstanceType': 't2.micro',
                            'State': {'Name': 'running'},
                            'Placement': {'AvailabilityZone': 'us-east-1a'},
                            'LaunchTime': MagicMock(isoformat=lambda: '2024-01-01T00:00:00Z'),
                            'Tags': []
                        }
                    ]
                }
            ]
        }

        mock_cloudwatch = MagicMock()
        mock_cloudwatch.get_metric_statistics.return_value = {'Datapoints': []}

        mock_session = MagicMock()
        def get_client(service_name):
            if service_name == 'ec2':
                return mock_ec2
            elif service_name == 'cloudwatch':
                return mock_cloudwatch
            return MagicMock()

        mock_session.client = get_client
        mock_session_class.return_value = mock_session
        mock_post.return_value = Mock(status_code=200)

        # Create agent
        agent = AWSTelemetryAgent(
            openfinops_endpoint='http://localhost:8080',
            aws_region='us-east-1'
        )

        # Collect and push metrics
        metrics = agent.collect_ec2_metrics()
        agent.push_metrics(metrics)

        # Verify workflow
        mock_ec2.describe_instances.assert_called()
        mock_post.assert_called()

    @patch('requests.post')
    def test_multi_agent_coordination(self, mock_post):
        """Test coordinating multiple telemetry agents."""
        from generic_telemetry_agent import GenericTelemetryAgent

        mock_post.return_value = Mock(status_code=200)

        # Create multiple agents for different sources
        agents = [
            GenericTelemetryAgent('http://localhost:8080'),
            GenericTelemetryAgent('http://localhost:8080'),
        ]

        # Each agent collects and pushes metrics
        for i, agent in enumerate(agents):
            agent.register_metric_collector(
                f'source_{i}',
                lambda idx=i: {'agent_id': idx, 'value': idx * 10}
            )

            metrics = agent.collect_metrics()
            agent.push_metrics(metrics)

        # Verify all agents pushed metrics
        assert mock_post.call_count == len(agents)
