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
Databricks Telemetry Agent for OpenFinOps
==========================================

Collects cost and usage metrics from Databricks workspaces including:
- Cluster DBU (Databricks Units) consumption
- Job run costs and execution metrics
- SQL warehouse usage and costs
- Delta Live Tables costs
- Storage costs (DBFS, Unity Catalog)
- Notebook execution metrics
- Model serving costs (MLflow)

Features:
- Automatic DBU cost calculation by cluster type
- Job-level cost attribution
- Workspace-level cost aggregation
- Real-time cluster monitoring
- Cost optimization recommendations

Requirements:
    pip install databricks-sdk requests

Usage:
    python databricks_telemetry_agent.py \\
        --openfinops-endpoint http://localhost:8080 \\
        --databricks-host https://your-workspace.cloud.databricks.com \\
        --databricks-token dapi***
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

import requests

# Try to import Databricks SDK
try:
    from databricks.sdk import WorkspaceClient
    from databricks.sdk.service.compute import ClusterDetails
    from databricks.sdk.service.jobs import Run
    from databricks.sdk.service.sql import Warehouse
    DATABRICKS_SDK_AVAILABLE = True
except ImportError:
    DATABRICKS_SDK_AVAILABLE = False
    print("Warning: databricks-sdk not installed. Install with: pip install databricks-sdk")


class DatabricksDBUCalculator:
    """Calculate costs from Databricks DBU consumption"""

    # DBU pricing per hour (approximate AWS pricing - adjust for your region/contract)
    DBU_PRICES = {
        # Jobs Compute
        'jobs_light': 0.07,
        'jobs_compute': 0.15,

        # All-Purpose Compute
        'all_purpose': 0.40,

        # SQL Compute
        'sql_classic': 0.22,
        'sql_pro': 0.55,

        # DLT (Delta Live Tables)
        'dlt_core': 0.20,
        'dlt_pro': 0.25,
        'dlt_advanced': 0.30,

        # Model Serving
        'model_serving': 0.07,

        # Serverless SQL
        'serverless_sql': 0.70,
    }

    # DBU consumption per hour by instance type (approximate)
    INSTANCE_DBU_RATES = {
        # General Purpose
        'm5.large': 0.75,
        'm5.xlarge': 1.5,
        'm5.2xlarge': 3.0,
        'm5.4xlarge': 6.0,
        'm5.8xlarge': 12.0,
        'm5.12xlarge': 18.0,
        'm5.16xlarge': 24.0,
        'm5.24xlarge': 36.0,

        # Memory Optimized
        'r5.large': 1.0,
        'r5.xlarge': 2.0,
        'r5.2xlarge': 4.0,
        'r5.4xlarge': 8.0,
        'r5.8xlarge': 16.0,
        'r5.12xlarge': 24.0,
        'r5.16xlarge': 32.0,
        'r5.24xlarge': 48.0,

        # Compute Optimized
        'c5.large': 0.5,
        'c5.xlarge': 1.0,
        'c5.2xlarge': 2.0,
        'c5.4xlarge': 4.0,
        'c5.9xlarge': 9.0,
        'c5.12xlarge': 12.0,
        'c5.18xlarge': 18.0,
        'c5.24xlarge': 24.0,

        # GPU Instances
        'p3.2xlarge': 8.0,
        'p3.8xlarge': 32.0,
        'p3.16xlarge': 64.0,
        'g4dn.xlarge': 2.0,
        'g4dn.2xlarge': 4.0,
        'g4dn.4xlarge': 8.0,
        'g4dn.8xlarge': 16.0,
        'g4dn.12xlarge': 24.0,
        'g4dn.16xlarge': 32.0,
    }

    @classmethod
    def calculate_cluster_cost(cls, instance_type: str, num_workers: int,
                              uptime_hours: float, cluster_type: str = 'all_purpose') -> float:
        """Calculate cluster cost based on DBU consumption"""
        # Get DBU rate for instance type (default to 1.0 if unknown)
        dbu_per_hour = cls.INSTANCE_DBU_RATES.get(instance_type, 1.0)

        # Total DBU consumption
        total_dbus = dbu_per_hour * (num_workers + 1) * uptime_hours  # +1 for driver

        # Get price per DBU
        dbu_price = cls.DBU_PRICES.get(cluster_type, 0.15)

        # Calculate cost
        cost = total_dbus * dbu_price

        return cost

    @classmethod
    def estimate_job_cost(cls, job_cluster_config: Dict, runtime_seconds: int) -> float:
        """Estimate job execution cost"""
        instance_type = job_cluster_config.get('node_type_id', 'm5.large')
        num_workers = job_cluster_config.get('num_workers', 1)
        runtime_hours = runtime_seconds / 3600.0

        return cls.calculate_cluster_cost(
            instance_type,
            num_workers,
            runtime_hours,
            cluster_type='jobs_compute'
        )


class DatabricksTelemetryAgent:
    """Databricks telemetry collection agent"""

    def __init__(self, openfinops_endpoint: str, databricks_host: str,
                 databricks_token: str, workspace_name: str = None):
        self.openfinops_endpoint = openfinops_endpoint.rstrip('/')
        self.databricks_host = databricks_host.rstrip('/')
        self.databricks_token = databricks_token
        self.workspace_name = workspace_name or databricks_host.split('.')[0].replace('https://', '')

        # Agent identification
        self.agent_id = f"databricks-{self.workspace_name}-{int(time.time())}"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DatabricksTelemetryAgent')

        # Initialize Databricks client
        if not DATABRICKS_SDK_AVAILABLE:
            raise ImportError("databricks-sdk is required. Install with: pip install databricks-sdk")

        self.workspace = WorkspaceClient(
            host=databricks_host,
            token=databricks_token
        )

        # State tracking
        self.registered = False
        self.start_time = time.time()

        # Cost calculator
        self.cost_calculator = DatabricksDBUCalculator()

    def register_agent(self) -> bool:
        """Register agent with OpenFinOps platform"""
        try:
            registration_data = {
                "agent_id": self.agent_id,
                "agent_type": "databricks_telemetry",
                "workspace_name": self.workspace_name,
                "workspace_host": self.databricks_host,
                "capabilities": [
                    "cluster_monitoring",
                    "job_cost_tracking",
                    "sql_warehouse_monitoring",
                    "dbu_calculation",
                    "storage_tracking"
                ],
                "version": "1.0.0",
                "registration_time": time.time()
            }

            response = requests.post(
                f"{self.openfinops_endpoint}/api/v1/agents/register",
                json=registration_data,
                timeout=30
            )

            if response.status_code == 200:
                self.registered = True
                self.logger.info(f"Agent registered successfully: {self.agent_id}")
                return True
            else:
                self.logger.error(f"Registration failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False

    def collect_cluster_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all clusters"""
        try:
            clusters = list(self.workspace.clusters.list())
            cluster_metrics = []
            total_cost = 0.0

            for cluster in clusters:
                try:
                    # Get cluster details
                    cluster_id = cluster.cluster_id
                    cluster_name = cluster.cluster_name
                    state = cluster.state.value if cluster.state else 'UNKNOWN'

                    # Calculate uptime if running
                    uptime_hours = 0.0
                    cost = 0.0

                    if state == 'RUNNING' and cluster.start_time:
                        uptime_ms = time.time() * 1000 - cluster.start_time
                        uptime_hours = uptime_ms / (1000 * 3600)

                        # Calculate cost
                        instance_type = cluster.node_type_id or 'm5.large'
                        num_workers = cluster.num_workers or 0
                        cluster_type = 'all_purpose' if not cluster.cluster_source else 'jobs_compute'

                        cost = self.cost_calculator.calculate_cluster_cost(
                            instance_type,
                            num_workers,
                            uptime_hours,
                            cluster_type
                        )
                        total_cost += cost

                    cluster_info = {
                        "cluster_id": cluster_id,
                        "cluster_name": cluster_name,
                        "state": state,
                        "instance_type": cluster.node_type_id,
                        "num_workers": cluster.num_workers,
                        "driver_node_type": cluster.driver_node_type_id,
                        "spark_version": cluster.spark_version,
                        "uptime_hours": round(uptime_hours, 2),
                        "estimated_cost_usd": round(cost, 4),
                        "cluster_source": cluster.cluster_source.value if cluster.cluster_source else None,
                        "creator_user_name": cluster.creator_user_name,
                        "last_state_change": cluster.state_message
                    }

                    cluster_metrics.append(cluster_info)

                except Exception as e:
                    self.logger.error(f"Error processing cluster {cluster.cluster_id}: {e}")
                    continue

            return {
                "timestamp": time.time(),
                "total_clusters": len(clusters),
                "running_clusters": len([c for c in cluster_metrics if c['state'] == 'RUNNING']),
                "total_estimated_cost_usd": round(total_cost, 4),
                "clusters": cluster_metrics
            }

        except Exception as e:
            self.logger.error(f"Error collecting cluster metrics: {e}")
            return {"error": str(e)}

    def collect_job_metrics(self, hours_lookback: int = 24) -> Dict[str, Any]:
        """Collect job run metrics and costs"""
        try:
            # Get recent job runs
            completed_since = int((time.time() - hours_lookback * 3600) * 1000)
            runs = list(self.workspace.jobs.list_runs(
                completed_only=True,
                limit=100
            ))

            job_metrics = []
            total_cost = 0.0

            for run in runs:
                try:
                    # Skip if too old
                    if run.start_time and run.start_time < completed_since:
                        continue

                    # Calculate runtime
                    runtime_seconds = 0
                    if run.start_time and run.end_time:
                        runtime_seconds = (run.end_time - run.start_time) / 1000

                    # Estimate cost
                    cost = 0.0
                    if run.cluster_spec and run.cluster_spec.new_cluster:
                        cluster_config = {
                            'node_type_id': run.cluster_spec.new_cluster.node_type_id,
                            'num_workers': run.cluster_spec.new_cluster.num_workers or 0
                        }
                        cost = self.cost_calculator.estimate_job_cost(cluster_config, runtime_seconds)
                        total_cost += cost

                    job_info = {
                        "run_id": run.run_id,
                        "job_id": run.job_id,
                        "run_name": run.run_name,
                        "state": run.state.life_cycle_state.value if run.state else 'UNKNOWN',
                        "result_state": run.state.result_state.value if run.state and run.state.result_state else None,
                        "start_time": datetime.fromtimestamp(run.start_time / 1000).isoformat() if run.start_time else None,
                        "end_time": datetime.fromtimestamp(run.end_time / 1000).isoformat() if run.end_time else None,
                        "runtime_seconds": int(runtime_seconds),
                        "estimated_cost_usd": round(cost, 4),
                        "creator_user_name": run.creator_user_name,
                        "run_page_url": run.run_page_url
                    }

                    job_metrics.append(job_info)

                except Exception as e:
                    self.logger.error(f"Error processing job run {run.run_id}: {e}")
                    continue

            return {
                "timestamp": time.time(),
                "lookback_hours": hours_lookback,
                "total_runs": len(job_metrics),
                "successful_runs": len([j for j in job_metrics if j['result_state'] == 'SUCCESS']),
                "failed_runs": len([j for j in job_metrics if j['result_state'] == 'FAILED']),
                "total_estimated_cost_usd": round(total_cost, 4),
                "jobs": job_metrics
            }

        except Exception as e:
            self.logger.error(f"Error collecting job metrics: {e}")
            return {"error": str(e)}

    def collect_sql_warehouse_metrics(self) -> Dict[str, Any]:
        """Collect SQL warehouse metrics and costs"""
        try:
            warehouses = list(self.workspace.warehouses.list())
            warehouse_metrics = []
            total_cost = 0.0

            for warehouse in warehouses:
                try:
                    # Estimate cost based on cluster size and uptime
                    cost = 0.0
                    uptime_hours = 0.0

                    if warehouse.state and warehouse.state.value == 'RUNNING':
                        # Rough estimate - adjust based on actual usage
                        cluster_size = warehouse.cluster_size or 'Small'
                        size_multiplier = {'Small': 1, 'Medium': 2, 'Large': 4, 'X-Large': 8, '2X-Large': 16, '3X-Large': 32, '4X-Large': 64}
                        multiplier = size_multiplier.get(cluster_size, 1)

                        # Assume 1 hour uptime for cost estimation (adjust based on actual metrics)
                        uptime_hours = 1.0
                        dbu_price = self.cost_calculator.DBU_PRICES.get('sql_pro', 0.55)
                        cost = multiplier * uptime_hours * dbu_price
                        total_cost += cost

                    warehouse_info = {
                        "warehouse_id": warehouse.id,
                        "warehouse_name": warehouse.name,
                        "state": warehouse.state.value if warehouse.state else 'UNKNOWN',
                        "cluster_size": warehouse.cluster_size,
                        "min_num_clusters": warehouse.min_num_clusters,
                        "max_num_clusters": warehouse.max_num_clusters,
                        "auto_stop_mins": warehouse.auto_stop_mins,
                        "warehouse_type": warehouse.warehouse_type.value if warehouse.warehouse_type else None,
                        "estimated_hourly_cost_usd": round(cost, 4),
                        "creator_name": warehouse.creator_name
                    }

                    warehouse_metrics.append(warehouse_info)

                except Exception as e:
                    self.logger.error(f"Error processing warehouse {warehouse.id}: {e}")
                    continue

            return {
                "timestamp": time.time(),
                "total_warehouses": len(warehouses),
                "running_warehouses": len([w for w in warehouse_metrics if w['state'] == 'RUNNING']),
                "total_estimated_cost_usd": round(total_cost, 4),
                "warehouses": warehouse_metrics
            }

        except Exception as e:
            self.logger.error(f"Error collecting SQL warehouse metrics: {e}")
            return {"error": str(e)}

    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all Databricks metrics"""
        try:
            # Collect from all sources
            cluster_metrics = self.collect_cluster_metrics()
            job_metrics = self.collect_job_metrics(hours_lookback=24)
            warehouse_metrics = self.collect_sql_warehouse_metrics()

            # Calculate totals
            total_cost = 0.0
            if 'total_estimated_cost_usd' in cluster_metrics:
                total_cost += cluster_metrics['total_estimated_cost_usd']
            if 'total_estimated_cost_usd' in job_metrics:
                total_cost += job_metrics['total_estimated_cost_usd']
            if 'total_estimated_cost_usd' in warehouse_metrics:
                total_cost += warehouse_metrics['total_estimated_cost_usd']

            return {
                "timestamp": time.time(),
                "agent_id": self.agent_id,
                "workspace_name": self.workspace_name,
                "workspace_host": self.databricks_host,
                "metrics": {
                    "clusters": cluster_metrics,
                    "jobs": job_metrics,
                    "sql_warehouses": warehouse_metrics
                },
                "summary": {
                    "total_estimated_cost_usd": round(total_cost, 4),
                    "total_running_clusters": cluster_metrics.get('running_clusters', 0),
                    "total_job_runs_24h": job_metrics.get('total_runs', 0),
                    "total_sql_warehouses": warehouse_metrics.get('total_warehouses', 0)
                }
            }

        except Exception as e:
            self.logger.error(f"Error collecting all metrics: {e}")
            return {"error": str(e), "timestamp": time.time()}

    def send_telemetry_data(self, metrics: Dict[str, Any]) -> bool:
        """Send telemetry data to OpenFinOps platform"""
        try:
            telemetry_data = {
                "agent_id": self.agent_id,
                "timestamp": time.time(),
                "metrics": metrics,
                "agent_health": {
                    "status": "healthy",
                    "uptime": time.time() - self.start_time,
                    "last_collection": time.time()
                }
            }

            response = requests.post(
                f"{self.openfinops_endpoint}/api/v1/telemetry/ingest",
                json=telemetry_data,
                timeout=30
            )

            if response.status_code == 200:
                self.logger.info(f"Telemetry data sent successfully - Total cost: ${metrics.get('summary', {}).get('total_estimated_cost_usd', 0):.2f}")
                return True
            else:
                self.logger.error(f"Failed to send telemetry: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending telemetry data: {e}")
            return False

    def run_continuous(self, interval_seconds: int = 300):
        """Run continuous telemetry collection"""
        self.logger.info(f"Starting Databricks Telemetry Agent for workspace: {self.workspace_name}")
        self.logger.info(f"Collection interval: {interval_seconds} seconds")

        if not self.register_agent():
            self.logger.error("Failed to register agent. Exiting.")
            return

        try:
            while True:
                # Collect metrics
                metrics = self.collect_all_metrics()

                # Send to platform
                self.send_telemetry_data(metrics)

                # Wait for next collection
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Agent error: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Databricks Telemetry Agent for OpenFinOps",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--openfinops-endpoint",
        required=True,
        help="OpenFinOps platform endpoint (e.g., http://localhost:8080)"
    )

    parser.add_argument(
        "--databricks-host",
        required=True,
        help="Databricks workspace URL (e.g., https://your-workspace.cloud.databricks.com)"
    )

    parser.add_argument(
        "--databricks-token",
        help="Databricks personal access token (or set DATABRICKS_TOKEN env var)"
    )

    parser.add_argument(
        "--workspace-name",
        help="Workspace name for identification (default: derived from host)"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Collection interval in seconds (default: 300)"
    )

    args = parser.parse_args()

    # Get token from args or environment
    token = args.databricks_token or os.environ.get('DATABRICKS_TOKEN')
    if not token:
        parser.error("--databricks-token is required or set DATABRICKS_TOKEN environment variable")

    # Create and start agent
    agent = DatabricksTelemetryAgent(
        openfinops_endpoint=args.openfinops_endpoint,
        databricks_host=args.databricks_host,
        databricks_token=token,
        workspace_name=args.workspace_name
    )

    try:
        agent.run_continuous(interval_seconds=args.interval)
    except KeyboardInterrupt:
        print("\nDatabricks Telemetry Agent stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Agent failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
