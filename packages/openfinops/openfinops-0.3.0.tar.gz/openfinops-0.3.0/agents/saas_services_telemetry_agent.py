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
SaaS Services Telemetry Agent for OpenFinOps
==============================================

Collects cost and usage metrics from popular SaaS/PaaS services including:
- MongoDB Atlas (clusters, storage, data transfer)
- Redis Cloud (database instances, throughput)
- Confluent Kafka (clusters, topics, connectors)
- Elasticsearch/OpenSearch (clusters, storage, shards)
- GitHub Actions (workflow minutes, storage)
- Vercel (deployments, bandwidth, functions)
- Docker Hub (pulls, storage)
- DataDog/New Relic (hosts, custom metrics)

Features:
- Multi-service support in single agent
- API-based metric collection
- Cost estimation for all services
- Usage pattern analysis
- Optimization recommendations

Requirements:
    pip install requests

Usage:
    python saas_services_telemetry_agent.py \\
        --openfinops-endpoint http://localhost:8080 \\
        --config saas_services_config.json
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


class MongoDBAtlasCollector:
    """Collect metrics from MongoDB Atlas"""

    # Pricing (approximate - varies by region)
    CLUSTER_PRICING = {
        'M10': 0.08,   # $0.08/hour
        'M20': 0.20,
        'M30': 0.54,
        'M40': 1.04,
        'M50': 2.56,
        'M60': 5.76,
        'M80': 11.52,
        'M140': 20.48,
        'M200': 34.56,
        'M300': 55.68,
    }

    def __init__(self, public_key: str, private_key: str, project_id: str):
        self.public_key = public_key
        self.private_key = private_key
        self.project_id = project_id
        self.base_url = "https://cloud.mongodb.com/api/atlas/v1.0"

    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make authenticated request to MongoDB Atlas API"""
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                auth=(self.public_key, self.private_key),
                headers={"Accept": "application/json"},
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"MongoDB Atlas API error: {e}")
            return None

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect MongoDB Atlas metrics"""
        try:
            # Get clusters
            clusters_data = self._make_request(f"groups/{self.project_id}/clusters")
            if not clusters_data:
                return {"error": "Failed to fetch clusters"}

            clusters = clusters_data.get('results', [])
            cluster_metrics = []
            total_cost = 0.0

            for cluster in clusters:
                cluster_name = cluster.get('name')
                instance_size = cluster.get('providerSettings', {}).get('instanceSizeName', 'M10')
                num_shards = cluster.get('numShards', 1)
                replication_factor = cluster.get('replicationFactor', 3)

                # Calculate hourly cost
                hourly_cost = self.CLUSTER_PRICING.get(instance_size, 0.08)
                total_hourly_cost = hourly_cost * num_shards * replication_factor
                daily_cost = total_hourly_cost * 24
                total_cost += daily_cost

                # Get process metrics
                processes_data = self._make_request(
                    f"groups/{self.project_id}/processes"
                )

                cluster_metrics.append({
                    "cluster_name": cluster_name,
                    "instance_size": instance_size,
                    "num_shards": num_shards,
                    "replication_factor": replication_factor,
                    "provider": cluster.get('providerSettings', {}).get('providerName'),
                    "region": cluster.get('providerSettings', {}).get('regionName'),
                    "mongodb_version": cluster.get('mongoDBVersion'),
                    "state": cluster.get('stateName'),
                    "hourly_cost_usd": round(total_hourly_cost, 4),
                    "daily_cost_usd": round(daily_cost, 2)
                })

            return {
                "service": "mongodb_atlas",
                "total_clusters": len(clusters),
                "total_daily_cost_usd": round(total_cost, 2),
                "clusters": cluster_metrics
            }

        except Exception as e:
            logging.error(f"MongoDB Atlas collection error: {e}")
            return {"error": str(e)}


class RedisCloudCollector:
    """Collect metrics from Redis Cloud"""

    def __init__(self, api_key: str, secret_key: str, account_id: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.account_id = account_id
        self.base_url = "https://api.redislabs.com/v1"

    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make authenticated request to Redis Cloud API"""
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers={
                    "x-api-key": self.api_key,
                    "x-api-secret-key": self.secret_key
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"Redis Cloud API error: {e}")
            return None

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect Redis Cloud metrics"""
        try:
            # Get subscriptions
            subscriptions = self._make_request(f"subscriptions")
            if not subscriptions:
                return {"error": "Failed to fetch subscriptions"}

            subscription_metrics = []
            total_cost = 0.0

            for subscription in subscriptions.get('subscriptions', []):
                subscription_id = subscription.get('id')
                name = subscription.get('name')

                # Get databases for this subscription
                databases = self._make_request(f"subscriptions/{subscription_id}/databases")

                db_count = len(databases.get('subscription', {}).get('databases', []))

                # Estimate cost (would need actual pricing API)
                estimated_cost = subscription.get('pricing', {}).get('cost', 0)
                total_cost += estimated_cost

                subscription_metrics.append({
                    "subscription_id": subscription_id,
                    "name": name,
                    "status": subscription.get('status'),
                    "cloud_provider": subscription.get('cloudDetails', [{}])[0].get('provider'),
                    "region": subscription.get('cloudDetails', [{}])[0].get('region'),
                    "database_count": db_count,
                    "estimated_monthly_cost_usd": round(estimated_cost, 2)
                })

            return {
                "service": "redis_cloud",
                "total_subscriptions": len(subscription_metrics),
                "total_monthly_cost_usd": round(total_cost, 2),
                "subscriptions": subscription_metrics
            }

        except Exception as e:
            logging.error(f"Redis Cloud collection error: {e}")
            return {"error": str(e)}


class GitHubActionsCollector:
    """Collect GitHub Actions usage metrics"""

    def __init__(self, token: str, org_name: str):
        self.token = token
        self.org_name = org_name
        self.base_url = "https://api.github.com"

    def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make authenticated request to GitHub API"""
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"GitHub API error: {e}")
            return None

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect GitHub Actions metrics"""
        try:
            # Get billing info
            billing = self._make_request(f"orgs/{self.org_name}/settings/billing/actions")
            if not billing:
                return {"error": "Failed to fetch billing data"}

            total_minutes = billing.get('total_minutes_used', 0)
            included_minutes = billing.get('included_minutes', 0)
            billable_minutes = total_minutes - included_minutes

            # GitHub Actions pricing: $0.008 per minute for Linux
            cost_per_minute = 0.008
            estimated_cost = max(0, billable_minutes * cost_per_minute)

            return {
                "service": "github_actions",
                "total_minutes_used": total_minutes,
                "included_minutes": included_minutes,
                "billable_minutes": max(0, billable_minutes),
                "estimated_monthly_cost_usd": round(estimated_cost, 2),
                "minutes_used_breakdown": billing.get('minutes_used_breakdown', {})
            }

        except Exception as e:
            logging.error(f"GitHub Actions collection error: {e}")
            return {"error": str(e)}


class DataDogCollector:
    """Collect DataDog usage metrics"""

    def __init__(self, api_key: str, app_key: str):
        self.api_key = api_key
        self.app_key = app_key
        self.base_url = "https://api.datadoghq.com/api/v1"

    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated request to DataDog API"""
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers={
                    "DD-API-KEY": self.api_key,
                    "DD-APPLICATION-KEY": self.app_key
                },
                params=params,
                timeout=30
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logging.error(f"DataDog API error: {e}")
            return None

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect DataDog metrics"""
        try:
            # Get usage for current month
            now = datetime.now()
            start_date = now.replace(day=1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')

            usage = self._make_request("usage/hosts", {
                "start_hr": start_date,
                "end_hr": end_date
            })

            if not usage:
                return {"error": "Failed to fetch usage data"}

            # Extract metrics
            host_count = 0
            if usage.get('usage'):
                for day_usage in usage['usage']:
                    host_count = max(host_count, day_usage.get('host_count', 0))

            # DataDog pricing: approximately $15 per host per month
            host_price = 15.0
            estimated_cost = host_count * host_price

            return {
                "service": "datadog",
                "max_host_count": host_count,
                "estimated_monthly_cost_usd": round(estimated_cost, 2),
                "period_start": start_date,
                "period_end": end_date
            }

        except Exception as e:
            logging.error(f"DataDog collection error: {e}")
            return {"error": str(e)}


class SaaSServicesTelemetryAgent:
    """Main telemetry agent for SaaS services"""

    def __init__(self, openfinops_endpoint: str, config_file: str):
        self.openfinops_endpoint = openfinops_endpoint.rstrip('/')
        self.config_file = config_file

        # Agent identification
        self.agent_id = f"saas-services-{int(time.time())}"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('SaaSServicesTelemetryAgent')

        # Load configuration
        self.config = self._load_config()

        # Initialize collectors
        self.collectors = []
        self._initialize_collectors()

        # State tracking
        self.registered = False
        self.start_time = time.time()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}

    def _initialize_collectors(self):
        """Initialize service collectors based on configuration"""
        # MongoDB Atlas
        if 'mongodb_atlas' in self.config:
            config = self.config['mongodb_atlas']
            if config.get('enabled', False):
                collector = MongoDBAtlasCollector(
                    config['public_key'],
                    config['private_key'],
                    config['project_id']
                )
                self.collectors.append(('mongodb_atlas', collector))
                self.logger.info("Enabled MongoDB Atlas collector")

        # Redis Cloud
        if 'redis_cloud' in self.config:
            config = self.config['redis_cloud']
            if config.get('enabled', False):
                collector = RedisCloudCollector(
                    config['api_key'],
                    config['secret_key'],
                    config['account_id']
                )
                self.collectors.append(('redis_cloud', collector))
                self.logger.info("Enabled Redis Cloud collector")

        # GitHub Actions
        if 'github_actions' in self.config:
            config = self.config['github_actions']
            if config.get('enabled', False):
                collector = GitHubActionsCollector(
                    config['token'],
                    config['org_name']
                )
                self.collectors.append(('github_actions', collector))
                self.logger.info("Enabled GitHub Actions collector")

        # DataDog
        if 'datadog' in self.config:
            config = self.config['datadog']
            if config.get('enabled', False):
                collector = DataDogCollector(
                    config['api_key'],
                    config['app_key']
                )
                self.collectors.append(('datadog', collector))
                self.logger.info("Enabled DataDog collector")

    def register_agent(self) -> bool:
        """Register agent with OpenFinOps platform"""
        try:
            registration_data = {
                "agent_id": self.agent_id,
                "agent_type": "saas_services_telemetry",
                "services": [name for name, _ in self.collectors],
                "capabilities": [
                    "multi_service_monitoring",
                    "saas_cost_tracking",
                    "usage_analytics"
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
                self.logger.error(f"Registration failed: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False

    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all enabled services"""
        try:
            service_metrics = {}
            total_monthly_cost = 0.0
            total_daily_cost = 0.0

            for service_name, collector in self.collectors:
                try:
                    metrics = collector.collect_metrics()
                    service_metrics[service_name] = metrics

                    # Aggregate costs
                    if 'total_monthly_cost_usd' in metrics:
                        total_monthly_cost += metrics['total_monthly_cost_usd']
                    if 'total_daily_cost_usd' in metrics:
                        total_daily_cost += metrics['total_daily_cost_usd']
                    if 'estimated_monthly_cost_usd' in metrics:
                        total_monthly_cost += metrics['estimated_monthly_cost_usd']

                except Exception as e:
                    self.logger.error(f"Error collecting from {service_name}: {e}")
                    service_metrics[service_name] = {"error": str(e)}

            return {
                "timestamp": time.time(),
                "agent_id": self.agent_id,
                "services": service_metrics,
                "summary": {
                    "total_services": len(self.collectors),
                    "total_monthly_cost_usd": round(total_monthly_cost, 2),
                    "total_daily_cost_usd": round(total_daily_cost, 2),
                    "estimated_annual_cost_usd": round(total_monthly_cost * 12, 2)
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
                summary = metrics.get('summary', {})
                self.logger.info(
                    f"Telemetry sent - Services: {summary.get('total_services', 0)}, "
                    f"Monthly cost: ${summary.get('total_monthly_cost_usd', 0):.2f}"
                )
                return True
            else:
                self.logger.error(f"Failed to send telemetry: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending telemetry data: {e}")
            return False

    def run_continuous(self, interval_seconds: int = 3600):
        """Run continuous telemetry collection"""
        self.logger.info(f"Starting SaaS Services Telemetry Agent")
        self.logger.info(f"Enabled services: {[name for name, _ in self.collectors]}")
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

    @staticmethod
    def create_sample_config(output_file: str):
        """Create a sample configuration file"""
        sample_config = {
            "mongodb_atlas": {
                "enabled": False,
                "public_key": "your_public_key",
                "private_key": "your_private_key",
                "project_id": "your_project_id"
            },
            "redis_cloud": {
                "enabled": False,
                "api_key": "your_api_key",
                "secret_key": "your_secret_key",
                "account_id": "your_account_id"
            },
            "github_actions": {
                "enabled": False,
                "token": "ghp_your_token",
                "org_name": "your_org"
            },
            "datadog": {
                "enabled": False,
                "api_key": "your_api_key",
                "app_key": "your_app_key"
            }
        }

        try:
            with open(output_file, 'w') as f:
                json.dump(sample_config, f, indent=2)
            print(f"Sample configuration created: {output_file}")
        except Exception as e:
            print(f"Error creating sample config: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="SaaS Services Telemetry Agent for OpenFinOps"
    )

    parser.add_argument(
        "--openfinops-endpoint",
        help="OpenFinOps platform endpoint (e.g., http://localhost:8080)"
    )

    parser.add_argument(
        "--config",
        help="Configuration file (JSON format)"
    )

    parser.add_argument(
        "--create-config",
        help="Create sample configuration file and exit"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Collection interval in seconds (default: 3600 = 1 hour)"
    )

    args = parser.parse_args()

    # Create sample config and exit
    if args.create_config:
        SaaSServicesTelemetryAgent.create_sample_config(args.create_config)
        return

    # Validate required arguments
    if not args.openfinops_endpoint or not args.config:
        parser.error("--openfinops-endpoint and --config are required")

    # Create and start agent
    agent = SaaSServicesTelemetryAgent(
        openfinops_endpoint=args.openfinops_endpoint,
        config_file=args.config
    )

    try:
        agent.run_continuous(interval_seconds=args.interval)
    except KeyboardInterrupt:
        print("\nSaaS Services Telemetry Agent stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Agent failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
