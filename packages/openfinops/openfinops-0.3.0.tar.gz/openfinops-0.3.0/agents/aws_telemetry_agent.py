#!/usr/bin/env python3
# Copyright (c) 2025 Infinidatum
# Author: Duraimurugan Rajamanickam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
AWS Telemetry Agent for OpenFinOps
================================

Collects comprehensive telemetry data from AWS infrastructure and sends to
your local OpenFinOps platform. Includes EC2, EKS, Lambda, RDS, S3 monitoring.

Usage:
    python aws_telemetry_agent.py --server http://your-office-ip:8080
    python aws_telemetry_agent.py --config aws_agent_config.yaml
"""

import boto3
import json
import time
import requests
import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import socket
import psutil
import uuid
import yaml


class AWSCredentialsManager:
    """Manage AWS credentials and regions"""

    def __init__(self, profile_name: str = None, region: str = None):
        self.profile_name = profile_name
        self.region = region or 'us-east-1'
        self._session = None

    def get_session(self):
        """Get boto3 session with proper credentials"""
        if not self._session:
            if self.profile_name:
                self._session = boto3.Session(
                    profile_name=self.profile_name,
                    region_name=self.region
                )
            else:
                self._session = boto3.Session(region_name=self.region)
        return self._session

    def get_client(self, service_name: str):
        """Get AWS service client"""
        return self.get_session().client(service_name)


class AWSResourceCollector:
    """Collect data from various AWS services"""

    def __init__(self, credentials_manager: AWSCredentialsManager):
        self.creds = credentials_manager
        self.logger = logging.getLogger(__name__)

    def collect_ec2_data(self) -> Dict[str, Any]:
        """Collect EC2 instance data"""
        try:
            ec2 = self.creds.get_client('ec2')
            cloudwatch = self.creds.get_client('cloudwatch')

            # Get all running instances
            response = ec2.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
            )

            instances = []
            total_cost = 0.0

            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']

                    # Get CPU utilization from CloudWatch
                    cpu_stats = cloudwatch.get_metric_statistics(
                        Namespace='AWS/EC2',
                        MetricName='CPUUtilization',
                        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                        StartTime=datetime.utcnow() - timedelta(minutes=10),
                        EndTime=datetime.utcnow(),
                        Period=300,
                        Statistics=['Average']
                    )

                    cpu_usage = 0.0
                    if cpu_stats['Datapoints']:
                        cpu_usage = cpu_stats['Datapoints'][-1]['Average']

                    # Estimate cost (simplified pricing)
                    hourly_cost = self._get_ec2_hourly_cost(instance_type)
                    total_cost += hourly_cost

                    # Get tags for cost attribution
                    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}

                    instances.append({
                        'instance_id': instance_id,
                        'instance_type': instance_type,
                        'state': instance['State']['Name'],
                        'availability_zone': instance['Placement']['AvailabilityZone'],
                        'cpu_usage': cpu_usage,
                        'hourly_cost': hourly_cost,
                        'tags': tags,
                        'launch_time': instance['LaunchTime'].isoformat(),
                        'private_ip': instance.get('PrivateIpAddress'),
                        'public_ip': instance.get('PublicIpAddress')
                    })

            return {
                'service': 'ec2',
                'instances': instances,
                'total_instances': len(instances),
                'total_hourly_cost': total_cost,
                'collection_time': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error collecting EC2 data: {e}")
            return {'service': 'ec2', 'error': str(e)}

    def collect_eks_data(self) -> Dict[str, Any]:
        """Collect EKS cluster data"""
        try:
            eks = self.creds.get_client('eks')
            ec2 = self.creds.get_client('ec2')

            # List all EKS clusters
            clusters_response = eks.list_clusters()
            clusters = []
            total_cost = 0.0

            for cluster_name in clusters_response['clusters']:
                # Get cluster details
                cluster_info = eks.describe_cluster(name=cluster_name)['cluster']

                # Get node groups
                nodegroups_response = eks.list_nodegroups(clusterName=cluster_name)
                nodegroups = []

                for ng_name in nodegroups_response['nodegroups']:
                    ng_info = eks.describe_nodegroup(
                        clusterName=cluster_name,
                        nodegroupName=ng_name
                    )['nodegroup']

                    # Calculate nodegroup cost
                    instance_types = ng_info.get('instanceTypes', [])
                    desired_capacity = ng_info.get('scalingConfig', {}).get('desiredSize', 0)

                    ng_cost = 0.0
                    if instance_types and desired_capacity:
                        instance_cost = self._get_ec2_hourly_cost(instance_types[0])
                        ng_cost = instance_cost * desired_capacity

                    total_cost += ng_cost

                    nodegroups.append({
                        'nodegroup_name': ng_name,
                        'instance_types': instance_types,
                        'desired_capacity': desired_capacity,
                        'max_size': ng_info.get('scalingConfig', {}).get('maxSize', 0),
                        'min_size': ng_info.get('scalingConfig', {}).get('minSize', 0),
                        'hourly_cost': ng_cost,
                        'status': ng_info.get('status'),
                        'version': ng_info.get('version')
                    })

                clusters.append({
                    'cluster_name': cluster_name,
                    'status': cluster_info.get('status'),
                    'version': cluster_info.get('version'),
                    'platform_version': cluster_info.get('platformVersion'),
                    'endpoint': cluster_info.get('endpoint'),
                    'nodegroups': nodegroups,
                    'created_at': cluster_info.get('createdAt').isoformat() if cluster_info.get('createdAt') else None
                })

            return {
                'service': 'eks',
                'clusters': clusters,
                'total_clusters': len(clusters),
                'total_hourly_cost': total_cost,
                'collection_time': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error collecting EKS data: {e}")
            return {'service': 'eks', 'error': str(e)}

    def collect_lambda_data(self) -> Dict[str, Any]:
        """Collect Lambda function data"""
        try:
            lambda_client = self.creds.get_client('lambda')
            cloudwatch = self.creds.get_client('cloudwatch')

            # List all functions
            functions_response = lambda_client.list_functions()
            functions = []
            total_invocations = 0
            total_cost = 0.0

            for func in functions_response['Functions']:
                func_name = func['FunctionName']

                # Get invocation metrics
                invocations_stats = cloudwatch.get_metric_statistics(
                    Namespace='AWS/Lambda',
                    MetricName='Invocations',
                    Dimensions=[{'Name': 'FunctionName', 'Value': func_name}],
                    StartTime=datetime.utcnow() - timedelta(hours=1),
                    EndTime=datetime.utcnow(),
                    Period=3600,
                    Statistics=['Sum']
                )

                invocations = 0
                if invocations_stats['Datapoints']:
                    invocations = int(invocations_stats['Datapoints'][-1]['Sum'])

                # Get duration metrics
                duration_stats = cloudwatch.get_metric_statistics(
                    Namespace='AWS/Lambda',
                    MetricName='Duration',
                    Dimensions=[{'Name': 'FunctionName', 'Value': func_name}],
                    StartTime=datetime.utcnow() - timedelta(hours=1),
                    EndTime=datetime.utcnow(),
                    Period=3600,
                    Statistics=['Average']
                )

                avg_duration = 0.0
                if duration_stats['Datapoints']:
                    avg_duration = duration_stats['Datapoints'][-1]['Average']

                # Calculate cost (simplified)
                memory_mb = func.get('MemorySize', 128)
                cost = self._calculate_lambda_cost(invocations, avg_duration, memory_mb)
                total_cost += cost
                total_invocations += invocations

                functions.append({
                    'function_name': func_name,
                    'runtime': func.get('Runtime'),
                    'memory_size': memory_mb,
                    'timeout': func.get('Timeout'),
                    'invocations_last_hour': invocations,
                    'avg_duration_ms': avg_duration,
                    'estimated_hourly_cost': cost,
                    'last_modified': func.get('LastModified'),
                    'code_size': func.get('CodeSize', 0)
                })

            return {
                'service': 'lambda',
                'functions': functions,
                'total_functions': len(functions),
                'total_invocations_last_hour': total_invocations,
                'total_hourly_cost': total_cost,
                'collection_time': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error collecting Lambda data: {e}")
            return {'service': 'lambda', 'error': str(e)}

    def collect_rds_data(self) -> Dict[str, Any]:
        """Collect RDS database data"""
        try:
            rds = self.creds.get_client('rds')
            cloudwatch = self.creds.get_client('cloudwatch')

            # Get all DB instances
            response = rds.describe_db_instances()
            databases = []
            total_cost = 0.0

            for db in response['DBInstances']:
                db_identifier = db['DBInstanceIdentifier']

                # Get CPU utilization
                cpu_stats = cloudwatch.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                    StartTime=datetime.utcnow() - timedelta(minutes=10),
                    EndTime=datetime.utcnow(),
                    Period=300,
                    Statistics=['Average']
                )

                cpu_usage = 0.0
                if cpu_stats['Datapoints']:
                    cpu_usage = cpu_stats['Datapoints'][-1]['Average']

                # Get connection count
                connections_stats = cloudwatch.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName='DatabaseConnections',
                    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_identifier}],
                    StartTime=datetime.utcnow() - timedelta(minutes=10),
                    EndTime=datetime.utcnow(),
                    Period=300,
                    Statistics=['Average']
                )

                connections = 0
                if connections_stats['Datapoints']:
                    connections = int(connections_stats['Datapoints'][-1]['Average'])

                # Estimate cost
                db_class = db.get('DBInstanceClass', '')
                hourly_cost = self._get_rds_hourly_cost(db_class)
                total_cost += hourly_cost

                databases.append({
                    'db_identifier': db_identifier,
                    'db_instance_class': db_class,
                    'engine': db.get('Engine'),
                    'engine_version': db.get('EngineVersion'),
                    'status': db.get('DBInstanceStatus'),
                    'allocated_storage': db.get('AllocatedStorage'),
                    'cpu_usage': cpu_usage,
                    'connections': connections,
                    'hourly_cost': hourly_cost,
                    'availability_zone': db.get('AvailabilityZone'),
                    'backup_retention_period': db.get('BackupRetentionPeriod'),
                    'multi_az': db.get('MultiAZ', False)
                })

            return {
                'service': 'rds',
                'databases': databases,
                'total_databases': len(databases),
                'total_hourly_cost': total_cost,
                'collection_time': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error collecting RDS data: {e}")
            return {'service': 'rds', 'error': str(e)}

    def collect_s3_data(self) -> Dict[str, Any]:
        """Collect S3 bucket data"""
        try:
            s3 = self.creds.get_client('s3')
            cloudwatch = self.creds.get_client('cloudwatch')

            # List all buckets
            buckets_response = s3.list_buckets()
            buckets = []
            total_cost = 0.0

            for bucket in buckets_response['Buckets']:
                bucket_name = bucket['Name']

                try:
                    # Get bucket size from CloudWatch
                    size_stats = cloudwatch.get_metric_statistics(
                        Namespace='AWS/S3',
                        MetricName='BucketSizeBytes',
                        Dimensions=[
                            {'Name': 'BucketName', 'Value': bucket_name},
                            {'Name': 'StorageType', 'Value': 'StandardStorage'}
                        ],
                        StartTime=datetime.utcnow() - timedelta(days=2),
                        EndTime=datetime.utcnow(),
                        Period=86400,
                        Statistics=['Average']
                    )

                    size_bytes = 0
                    if size_stats['Datapoints']:
                        size_bytes = int(size_stats['Datapoints'][-1]['Average'])

                    size_gb = size_bytes / (1024**3)

                    # Get object count
                    objects_stats = cloudwatch.get_metric_statistics(
                        Namespace='AWS/S3',
                        MetricName='NumberOfObjects',
                        Dimensions=[
                            {'Name': 'BucketName', 'Value': bucket_name},
                            {'Name': 'StorageType', 'Value': 'AllStorageTypes'}
                        ],
                        StartTime=datetime.utcnow() - timedelta(days=2),
                        EndTime=datetime.utcnow(),
                        Period=86400,
                        Statistics=['Average']
                    )

                    object_count = 0
                    if objects_stats['Datapoints']:
                        object_count = int(objects_stats['Datapoints'][-1]['Average'])

                    # Calculate monthly cost (S3 standard pricing)
                    monthly_cost = size_gb * 0.023  # $0.023 per GB
                    total_cost += monthly_cost / 30 / 24  # Convert to hourly

                    buckets.append({
                        'bucket_name': bucket_name,
                        'size_bytes': size_bytes,
                        'size_gb': round(size_gb, 2),
                        'object_count': object_count,
                        'monthly_cost': round(monthly_cost, 2),
                        'created_date': bucket['CreationDate'].isoformat()
                    })

                except Exception as e:
                    # Handle buckets without metrics or permission issues
                    buckets.append({
                        'bucket_name': bucket_name,
                        'size_bytes': 0,
                        'size_gb': 0,
                        'object_count': 0,
                        'monthly_cost': 0,
                        'created_date': bucket['CreationDate'].isoformat(),
                        'error': str(e)
                    })

            return {
                'service': 's3',
                'buckets': buckets,
                'total_buckets': len(buckets),
                'total_hourly_cost': total_cost,
                'collection_time': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error collecting S3 data: {e}")
            return {'service': 's3', 'error': str(e)}

    def _get_ec2_hourly_cost(self, instance_type: str) -> float:
        """Get estimated hourly cost for EC2 instance type"""
        # Simplified pricing (US East 1, On-Demand)
        pricing = {
            't2.micro': 0.0116, 't2.small': 0.023, 't2.medium': 0.0464,
            't3.micro': 0.0104, 't3.small': 0.0208, 't3.medium': 0.0416,
            'm5.large': 0.096, 'm5.xlarge': 0.192, 'm5.2xlarge': 0.384,
            'c5.large': 0.085, 'c5.xlarge': 0.17, 'c5.2xlarge': 0.34,
            'r5.large': 0.126, 'r5.xlarge': 0.252, 'r5.2xlarge': 0.504
        }
        return pricing.get(instance_type, 0.1)  # Default estimate

    def _get_rds_hourly_cost(self, db_class: str) -> float:
        """Get estimated hourly cost for RDS instance class"""
        pricing = {
            'db.t3.micro': 0.017, 'db.t3.small': 0.034, 'db.t3.medium': 0.068,
            'db.m5.large': 0.192, 'db.m5.xlarge': 0.384, 'db.m5.2xlarge': 0.768,
            'db.r5.large': 0.24, 'db.r5.xlarge': 0.48, 'db.r5.2xlarge': 0.96
        }
        return pricing.get(db_class, 0.1)

    def _calculate_lambda_cost(self, invocations: int, avg_duration_ms: float, memory_mb: int) -> float:
        """Calculate Lambda cost based on invocations and duration"""
        # AWS Lambda pricing
        request_cost = invocations * 0.0000002  # $0.20 per 1M requests

        # Duration cost
        gb_seconds = (memory_mb / 1024) * (avg_duration_ms / 1000) * invocations
        duration_cost = gb_seconds * 0.0000166667  # $0.0000166667 per GB-second

        return request_cost + duration_cost


class AWSTelemetryAgent:
    """Main AWS telemetry agent"""

    def __init__(self, server_url: str = None, agent_id: str = None, region: str = None,
                 openfinops_endpoint: str = None, aws_region: str = None):
        # Support both old and new parameter names
        self.server_url = (openfinops_endpoint or server_url or 'http://localhost:8080').rstrip('/')
        self.openfinops_endpoint = self.server_url  # Alias for compatibility
        self.region = aws_region or region or 'us-east-1'
        self.agent_id = agent_id or f"aws-agent-{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
        self.logger = logging.getLogger(__name__)

        # Initialize AWS components
        self.creds_manager = AWSCredentialsManager(region=self.region)
        self.collector = AWSResourceCollector(self.creds_manager)

        # Agent metadata
        self.hostname = socket.gethostname()
        self.start_time = time.time()

    def register_agent(self) -> bool:
        """Register agent with OpenFinOps platform"""
        try:
            registration_data = {
                "agent_id": self.agent_id,
                "hostname": self.hostname,
                "cloud_provider": "aws",
                "region": self.region,
                "agent_type": "aws_telemetry",
                "agent_version": "1.0.0",
                "config": {
                    "services": ["ec2", "eks", "lambda", "rds", "s3"],
                    "collection_interval": 300,
                    "cost_tracking": True
                }
            }

            response = requests.post(
                f"{self.server_url}/api/v1/agents/register",
                json=registration_data,
                timeout=30
            )

            if response.status_code == 200:
                self.logger.info(f"Agent {self.agent_id} registered successfully")
                return True
            else:
                self.logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error registering agent: {e}")
            return False

    def collect_telemetry_data(self) -> Dict[str, Any]:
        """Collect comprehensive telemetry data from AWS"""
        self.logger.info("Collecting AWS telemetry data...")

        # Collect data from all services
        telemetry_data = {
            "agent_id": self.agent_id,
            "timestamp": time.time(),
            "hostname": self.hostname,
            "cloud_provider": "aws",
            "region": self.region,
            "uptime_seconds": time.time() - self.start_time,
            "services": {},
            "summary": {}
        }

        # Collect EC2 data
        ec2_data = self.collector.collect_ec2_data()
        telemetry_data["services"]["ec2"] = ec2_data

        # Collect EKS data
        eks_data = self.collector.collect_eks_data()
        telemetry_data["services"]["eks"] = eks_data

        # Collect Lambda data
        lambda_data = self.collector.collect_lambda_data()
        telemetry_data["services"]["lambda"] = lambda_data

        # Collect RDS data
        rds_data = self.collector.collect_rds_data()
        telemetry_data["services"]["rds"] = rds_data

        # Collect S3 data
        s3_data = self.collector.collect_s3_data()
        telemetry_data["services"]["s3"] = s3_data

        # Calculate summary
        total_hourly_cost = (
            ec2_data.get('total_hourly_cost', 0) +
            eks_data.get('total_hourly_cost', 0) +
            lambda_data.get('total_hourly_cost', 0) +
            rds_data.get('total_hourly_cost', 0) +
            s3_data.get('total_hourly_cost', 0)
        )

        telemetry_data["summary"] = {
            "total_hourly_cost": round(total_hourly_cost, 4),
            "daily_cost_estimate": round(total_hourly_cost * 24, 2),
            "monthly_cost_estimate": round(total_hourly_cost * 24 * 30, 2),
            "total_ec2_instances": ec2_data.get('total_instances', 0),
            "total_eks_clusters": eks_data.get('total_clusters', 0),
            "total_lambda_functions": lambda_data.get('total_functions', 0),
            "total_rds_databases": rds_data.get('total_databases', 0),
            "total_s3_buckets": s3_data.get('total_buckets', 0)
        }

        return telemetry_data

    def send_telemetry_data(self, data: Dict[str, Any]) -> bool:
        """Send telemetry data to OpenFinOps platform"""
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/telemetry/ingest",
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                self.logger.info("Telemetry data sent successfully")
                return True
            else:
                self.logger.error(f"Failed to send telemetry: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending telemetry data: {e}")
            return False

    def collect_ec2_metrics(self) -> Dict[str, Any]:
        """Collect EC2 metrics (test-compatible method)."""
        return self.collector.collect_ec2_data()

    def push_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Push metrics to OpenFinOps platform (alias for send_telemetry_data)."""
        return self.send_telemetry_data(metrics)

    def run_once(self) -> bool:
        """Run one cycle of telemetry collection and transmission"""
        try:
            # Collect data
            telemetry_data = self.collect_telemetry_data()

            # Send to platform
            success = self.send_telemetry_data(telemetry_data)

            if success:
                cost = telemetry_data["summary"]["total_hourly_cost"]
                instances = telemetry_data["summary"]["total_ec2_instances"]
                self.logger.info(f"✅ Sent AWS telemetry - ${cost:.2f}/hr, {instances} instances")

            return success

        except Exception as e:
            self.logger.error(f"Error in telemetry cycle: {e}")
            return False

    def run_continuous(self, interval_seconds: int = 300):
        """Run continuous telemetry collection"""
        self.logger.info(f"Starting AWS telemetry agent (interval: {interval_seconds}s)")

        # Register agent
        if not self.register_agent():
            self.logger.error("Failed to register agent. Exiting.")
            return

        # Main collection loop
        try:
            while True:
                success = self.run_once()
                if not success:
                    self.logger.warning("Telemetry collection failed, will retry...")

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            self.logger.info("Agent stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error in agent: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AWS Telemetry Agent for OpenFinOps")
    parser.add_argument("--server", required=True,
                       help="OpenFinOps server URL (e.g., http://your-office-ip:8080)")
    parser.add_argument("--agent-id",
                       help="Custom agent ID (default: auto-generated)")
    parser.add_argument("--region", default="us-east-1",
                       help="AWS region (default: us-east-1)")
    parser.add_argument("--interval", type=int, default=300,
                       help="Collection interval in seconds (default: 300)")
    parser.add_argument("--once", action="store_true",
                       help="Run once and exit")
    parser.add_argument("--config",
                       help="Configuration file (YAML)")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load config file if provided
    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
            args.server = config.get('server', args.server)
            args.region = config.get('region', args.region)
            args.interval = config.get('interval', args.interval)

    # Create and run agent
    agent = AWSTelemetryAgent(
        server_url=args.server,
        agent_id=args.agent_id,
        region=args.region
    )

    if args.once:
        # Run once and exit
        success = agent.run_once()
        exit(0 if success else 1)
    else:
        # Run continuously
        agent.run_continuous(args.interval)


if __name__ == "__main__":
    main()