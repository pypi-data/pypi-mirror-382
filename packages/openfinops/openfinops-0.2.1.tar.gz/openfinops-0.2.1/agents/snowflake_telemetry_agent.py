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
Snowflake Telemetry Agent for OpenFinOps
=========================================

Collects cost and usage metrics from Snowflake including:
- Warehouse credit consumption
- Storage costs (database, stage, failsafe)
- Data transfer costs
- Query execution metrics
- Compute vs storage cost breakdown
- User and role-level cost attribution
- Automatic scaling metrics

Features:
- Real-time credit consumption tracking
- Warehouse efficiency analysis
- Storage growth monitoring
- Query cost optimization insights
- Cost allocation by department/team

Requirements:
    pip install snowflake-connector-python requests

Usage:
    python snowflake_telemetry_agent.py \\
        --openfinops-endpoint http://localhost:8080 \\
        --snowflake-account your_account \\
        --snowflake-user your_user \\
        --snowflake-password your_password \\
        --snowflake-warehouse your_warehouse
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

# Try to import Snowflake connector
try:
    import snowflake.connector
    from snowflake.connector import DictCursor
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    print("Warning: snowflake-connector-python not installed. Install with: pip install snowflake-connector-python")


class SnowflakeCostCalculator:
    """Calculate costs from Snowflake credit consumption"""

    # Credit pricing (adjust based on your Snowflake edition and region)
    # These are approximate on-demand prices
    CREDIT_PRICES = {
        'standard': 2.00,      # Standard Edition: $2 per credit
        'enterprise': 3.00,    # Enterprise Edition: $3 per credit
        'business_critical': 4.00,  # Business Critical: $4 per credit
    }

    # Storage pricing per TB per month
    STORAGE_PRICE_PER_TB = {
        'on_demand': 40.00,    # $40 per TB per month
        'capacity': 23.00,     # $23 per TB per month (with capacity commitment)
    }

    # Data transfer pricing per TB
    DATA_TRANSFER_PRICE_PER_TB = {
        'same_region': 0.00,   # Free within same cloud region
        'cross_region': 2.00,  # $2 per TB across regions
        'external': 9.00,      # $9 per TB external transfer
    }

    @classmethod
    def calculate_warehouse_cost(cls, credits_used: float, edition: str = 'enterprise') -> float:
        """Calculate warehouse compute cost from credits"""
        credit_price = cls.CREDIT_PRICES.get(edition, 3.00)
        return credits_used * credit_price

    @classmethod
    def calculate_storage_cost(cls, storage_tb: float, pricing_model: str = 'on_demand',
                              days: int = 30) -> float:
        """Calculate storage cost"""
        monthly_price = cls.STORAGE_PRICE_PER_TB.get(pricing_model, 40.00)
        daily_price = monthly_price / 30
        return storage_tb * daily_price * days

    @classmethod
    def calculate_transfer_cost(cls, transfer_tb: float, transfer_type: str = 'cross_region') -> float:
        """Calculate data transfer cost"""
        price_per_tb = cls.DATA_TRANSFER_PRICE_PER_TB.get(transfer_type, 2.00)
        return transfer_tb * price_per_tb


class SnowflakeTelemetryAgent:
    """Snowflake telemetry collection agent"""

    def __init__(self, openfinops_endpoint: str, snowflake_account: str,
                 snowflake_user: str, snowflake_password: str,
                 snowflake_warehouse: str, snowflake_database: str = 'SNOWFLAKE',
                 snowflake_role: str = 'ACCOUNTADMIN',
                 edition: str = 'enterprise'):
        self.openfinops_endpoint = openfinops_endpoint.rstrip('/')
        self.snowflake_account = snowflake_account
        self.snowflake_user = snowflake_user
        self.snowflake_password = snowflake_password
        self.snowflake_warehouse = snowflake_warehouse
        self.snowflake_database = snowflake_database
        self.snowflake_role = snowflake_role
        self.edition = edition

        # Agent identification
        self.agent_id = f"snowflake-{snowflake_account}-{int(time.time())}"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('SnowflakeTelemetryAgent')

        # Check Snowflake connector
        if not SNOWFLAKE_AVAILABLE:
            raise ImportError("snowflake-connector-python is required. Install with: pip install snowflake-connector-python")

        # Initialize connection
        self.connection = None
        self._connect()

        # State tracking
        self.registered = False
        self.start_time = time.time()

        # Cost calculator
        self.cost_calculator = SnowflakeCostCalculator()

    def _connect(self):
        """Establish connection to Snowflake"""
        try:
            self.connection = snowflake.connector.connect(
                user=self.snowflake_user,
                password=self.snowflake_password,
                account=self.snowflake_account,
                warehouse=self.snowflake_warehouse,
                database=self.snowflake_database,
                role=self.snowflake_role,
                schema='ACCOUNT_USAGE'
            )
            self.logger.info(f"Connected to Snowflake account: {self.snowflake_account}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Snowflake: {e}")
            raise

    def _execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute query and return results as list of dictionaries"""
        try:
            cursor = self.connection.cursor(DictCursor)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Exception as e:
            self.logger.error(f"Query execution error: {e}")
            return []

    def register_agent(self) -> bool:
        """Register agent with OpenFinOps platform"""
        try:
            registration_data = {
                "agent_id": self.agent_id,
                "agent_type": "snowflake_telemetry",
                "account_name": self.snowflake_account,
                "edition": self.edition,
                "capabilities": [
                    "warehouse_monitoring",
                    "credit_tracking",
                    "storage_monitoring",
                    "query_analytics",
                    "cost_attribution"
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

    def collect_warehouse_metrics(self, hours_lookback: int = 24) -> Dict[str, Any]:
        """Collect warehouse credit consumption metrics"""
        try:
            query = f"""
            SELECT
                WAREHOUSE_NAME,
                SUM(CREDITS_USED) AS TOTAL_CREDITS,
                SUM(CREDITS_USED_COMPUTE) AS COMPUTE_CREDITS,
                SUM(CREDITS_USED_CLOUD_SERVICES) AS CLOUD_SERVICE_CREDITS,
                COUNT(DISTINCT DATE_TRUNC('hour', START_TIME)) AS ACTIVE_HOURS,
                AVG(CREDITS_USED) AS AVG_CREDITS_PER_QUERY
            FROM WAREHOUSE_METERING_HISTORY
            WHERE START_TIME >= DATEADD(hour, -{hours_lookback}, CURRENT_TIMESTAMP())
            GROUP BY WAREHOUSE_NAME
            ORDER BY TOTAL_CREDITS DESC
            """

            results = self._execute_query(query)

            warehouse_metrics = []
            total_credits = 0.0
            total_cost = 0.0

            for row in results:
                warehouse_name = row['WAREHOUSE_NAME']
                credits_used = float(row['TOTAL_CREDITS'] or 0)
                compute_credits = float(row['COMPUTE_CREDITS'] or 0)
                cloud_service_credits = float(row['CLOUD_SERVICE_CREDITS'] or 0)

                # Calculate cost
                cost = self.cost_calculator.calculate_warehouse_cost(credits_used, self.edition)
                total_credits += credits_used
                total_cost += cost

                warehouse_metrics.append({
                    "warehouse_name": warehouse_name,
                    "total_credits_used": round(credits_used, 4),
                    "compute_credits": round(compute_credits, 4),
                    "cloud_service_credits": round(cloud_service_credits, 4),
                    "active_hours": int(row['ACTIVE_HOURS'] or 0),
                    "avg_credits_per_query": round(float(row['AVG_CREDITS_PER_QUERY'] or 0), 4),
                    "estimated_cost_usd": round(cost, 2)
                })

            return {
                "timestamp": time.time(),
                "lookback_hours": hours_lookback,
                "total_warehouses": len(warehouse_metrics),
                "total_credits_used": round(total_credits, 4),
                "total_estimated_cost_usd": round(total_cost, 2),
                "warehouses": warehouse_metrics
            }

        except Exception as e:
            self.logger.error(f"Error collecting warehouse metrics: {e}")
            return {"error": str(e)}

    def collect_storage_metrics(self) -> Dict[str, Any]:
        """Collect storage usage metrics"""
        try:
            query = """
            SELECT
                DATABASE_NAME,
                USAGE_DATE,
                AVERAGE_DATABASE_BYTES / POWER(1024, 4) AS DATABASE_TB,
                AVERAGE_FAILSAFE_BYTES / POWER(1024, 4) AS FAILSAFE_TB,
                (AVERAGE_DATABASE_BYTES + AVERAGE_FAILSAFE_BYTES) / POWER(1024, 4) AS TOTAL_TB
            FROM DATABASE_STORAGE_USAGE_HISTORY
            WHERE USAGE_DATE >= DATEADD(day, -7, CURRENT_DATE())
            ORDER BY USAGE_DATE DESC, DATABASE_NAME
            """

            results = self._execute_query(query)

            # Group by database
            storage_by_db = defaultdict(list)
            for row in results:
                db_name = row['DATABASE_NAME']
                storage_by_db[db_name].append({
                    "date": row['USAGE_DATE'].isoformat() if hasattr(row['USAGE_DATE'], 'isoformat') else str(row['USAGE_DATE']),
                    "database_tb": round(float(row['DATABASE_TB'] or 0), 6),
                    "failsafe_tb": round(float(row['FAILSAFE_TB'] or 0), 6),
                    "total_tb": round(float(row['TOTAL_TB'] or 0), 6)
                })

            # Calculate current total and cost
            total_storage_tb = 0.0
            storage_summary = []

            for db_name, records in storage_by_db.items():
                if records:
                    latest = records[0]
                    total_tb = latest['total_tb']
                    total_storage_tb += total_tb

                    # Calculate monthly cost
                    cost = self.cost_calculator.calculate_storage_cost(total_tb, 'on_demand', days=30)

                    storage_summary.append({
                        "database_name": db_name,
                        "current_storage_tb": round(total_tb, 6),
                        "database_tb": latest['database_tb'],
                        "failsafe_tb": latest['failsafe_tb'],
                        "estimated_monthly_cost_usd": round(cost, 2),
                        "trend": records[:7]  # Last 7 days
                    })

            total_storage_cost = self.cost_calculator.calculate_storage_cost(
                total_storage_tb, 'on_demand', days=30
            )

            return {
                "timestamp": time.time(),
                "total_storage_tb": round(total_storage_tb, 6),
                "estimated_monthly_cost_usd": round(total_storage_cost, 2),
                "databases": storage_summary
            }

        except Exception as e:
            self.logger.error(f"Error collecting storage metrics: {e}")
            return {"error": str(e)}

    def collect_query_metrics(self, hours_lookback: int = 24) -> Dict[str, Any]:
        """Collect query execution metrics"""
        try:
            query = f"""
            SELECT
                WAREHOUSE_NAME,
                USER_NAME,
                QUERY_TYPE,
                COUNT(*) AS QUERY_COUNT,
                AVG(EXECUTION_TIME) / 1000 AS AVG_EXECUTION_SECONDS,
                SUM(EXECUTION_TIME) / 1000 AS TOTAL_EXECUTION_SECONDS,
                AVG(BYTES_SCANNED) / POWER(1024, 3) AS AVG_GB_SCANNED,
                SUM(BYTES_SCANNED) / POWER(1024, 3) AS TOTAL_GB_SCANNED
            FROM QUERY_HISTORY
            WHERE START_TIME >= DATEADD(hour, -{hours_lookback}, CURRENT_TIMESTAMP())
                AND EXECUTION_STATUS = 'SUCCESS'
            GROUP BY WAREHOUSE_NAME, USER_NAME, QUERY_TYPE
            ORDER BY QUERY_COUNT DESC
            LIMIT 100
            """

            results = self._execute_query(query)

            query_metrics = []
            total_queries = 0
            total_execution_time = 0.0

            for row in results:
                query_count = int(row['QUERY_COUNT'] or 0)
                total_queries += query_count
                total_execution_time += float(row['TOTAL_EXECUTION_SECONDS'] or 0)

                query_metrics.append({
                    "warehouse_name": row['WAREHOUSE_NAME'],
                    "user_name": row['USER_NAME'],
                    "query_type": row['QUERY_TYPE'],
                    "query_count": query_count,
                    "avg_execution_seconds": round(float(row['AVG_EXECUTION_SECONDS'] or 0), 2),
                    "total_execution_seconds": round(float(row['TOTAL_EXECUTION_SECONDS'] or 0), 2),
                    "avg_gb_scanned": round(float(row['AVG_GB_SCANNED'] or 0), 4),
                    "total_gb_scanned": round(float(row['TOTAL_GB_SCANNED'] or 0), 4)
                })

            return {
                "timestamp": time.time(),
                "lookback_hours": hours_lookback,
                "total_queries": total_queries,
                "total_execution_seconds": round(total_execution_time, 2),
                "top_query_patterns": query_metrics[:20]
            }

        except Exception as e:
            self.logger.error(f"Error collecting query metrics: {e}")
            return {"error": str(e)}

    def collect_user_cost_attribution(self, hours_lookback: int = 24) -> Dict[str, Any]:
        """Collect cost attribution by user"""
        try:
            # Get credits by user
            query = f"""
            SELECT
                qh.USER_NAME,
                wmh.WAREHOUSE_NAME,
                SUM(wmh.CREDITS_USED) AS TOTAL_CREDITS,
                COUNT(DISTINCT qh.QUERY_ID) AS QUERY_COUNT
            FROM QUERY_HISTORY qh
            JOIN WAREHOUSE_METERING_HISTORY wmh
                ON qh.WAREHOUSE_NAME = wmh.WAREHOUSE_NAME
                AND DATE_TRUNC('hour', qh.START_TIME) = DATE_TRUNC('hour', wmh.START_TIME)
            WHERE qh.START_TIME >= DATEADD(hour, -{hours_lookback}, CURRENT_TIMESTAMP())
            GROUP BY qh.USER_NAME, wmh.WAREHOUSE_NAME
            ORDER BY TOTAL_CREDITS DESC
            LIMIT 50
            """

            results = self._execute_query(query)

            user_costs = []
            total_cost = 0.0

            for row in results:
                credits = float(row['TOTAL_CREDITS'] or 0)
                cost = self.cost_calculator.calculate_warehouse_cost(credits, self.edition)
                total_cost += cost

                user_costs.append({
                    "user_name": row['USER_NAME'],
                    "warehouse_name": row['WAREHOUSE_NAME'],
                    "credits_used": round(credits, 4),
                    "query_count": int(row['QUERY_COUNT'] or 0),
                    "estimated_cost_usd": round(cost, 2)
                })

            return {
                "timestamp": time.time(),
                "lookback_hours": hours_lookback,
                "total_estimated_cost_usd": round(total_cost, 2),
                "user_attributions": user_costs
            }

        except Exception as e:
            self.logger.error(f"Error collecting user cost attribution: {e}")
            return {"error": str(e)}

    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all Snowflake metrics"""
        try:
            # Collect from all sources
            warehouse_metrics = self.collect_warehouse_metrics(hours_lookback=24)
            storage_metrics = self.collect_storage_metrics()
            query_metrics = self.collect_query_metrics(hours_lookback=24)
            user_attribution = self.collect_user_cost_attribution(hours_lookback=24)

            # Calculate totals
            compute_cost = warehouse_metrics.get('total_estimated_cost_usd', 0)
            storage_cost = storage_metrics.get('estimated_monthly_cost_usd', 0)
            daily_storage_cost = storage_cost / 30  # Convert monthly to daily

            total_cost = compute_cost + daily_storage_cost

            return {
                "timestamp": time.time(),
                "agent_id": self.agent_id,
                "account_name": self.snowflake_account,
                "edition": self.edition,
                "metrics": {
                    "warehouses": warehouse_metrics,
                    "storage": storage_metrics,
                    "queries": query_metrics,
                    "user_attribution": user_attribution
                },
                "summary": {
                    "total_daily_cost_usd": round(total_cost, 2),
                    "compute_cost_24h_usd": round(compute_cost, 2),
                    "storage_daily_cost_usd": round(daily_storage_cost, 2),
                    "total_credits_24h": warehouse_metrics.get('total_credits_used', 0),
                    "total_storage_tb": storage_metrics.get('total_storage_tb', 0),
                    "total_queries_24h": query_metrics.get('total_queries', 0)
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
                    f"Telemetry sent - Daily cost: ${summary.get('total_daily_cost_usd', 0):.2f}, "
                    f"Credits: {summary.get('total_credits_24h', 0):.2f}, "
                    f"Storage: {summary.get('total_storage_tb', 0):.4f} TB"
                )
                return True
            else:
                self.logger.error(f"Failed to send telemetry: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending telemetry data: {e}")
            return False

    def run_continuous(self, interval_seconds: int = 300):
        """Run continuous telemetry collection"""
        self.logger.info(f"Starting Snowflake Telemetry Agent for account: {self.snowflake_account}")
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
        finally:
            if self.connection:
                self.connection.close()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Snowflake Telemetry Agent for OpenFinOps",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--openfinops-endpoint",
        required=True,
        help="OpenFinOps platform endpoint (e.g., http://localhost:8080)"
    )

    parser.add_argument(
        "--snowflake-account",
        required=True,
        help="Snowflake account identifier (e.g., xy12345.us-east-1)"
    )

    parser.add_argument(
        "--snowflake-user",
        help="Snowflake username (or set SNOWFLAKE_USER env var)"
    )

    parser.add_argument(
        "--snowflake-password",
        help="Snowflake password (or set SNOWFLAKE_PASSWORD env var)"
    )

    parser.add_argument(
        "--snowflake-warehouse",
        default="COMPUTE_WH",
        help="Snowflake warehouse name (default: COMPUTE_WH)"
    )

    parser.add_argument(
        "--snowflake-role",
        default="ACCOUNTADMIN",
        help="Snowflake role (default: ACCOUNTADMIN)"
    )

    parser.add_argument(
        "--edition",
        choices=['standard', 'enterprise', 'business_critical'],
        default='enterprise',
        help="Snowflake edition for cost calculation (default: enterprise)"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Collection interval in seconds (default: 300)"
    )

    args = parser.parse_args()

    # Get credentials from args or environment
    user = args.snowflake_user or os.environ.get('SNOWFLAKE_USER')
    password = args.snowflake_password or os.environ.get('SNOWFLAKE_PASSWORD')

    if not user:
        parser.error("--snowflake-user is required or set SNOWFLAKE_USER environment variable")
    if not password:
        parser.error("--snowflake-password is required or set SNOWFLAKE_PASSWORD environment variable")

    # Create and start agent
    agent = SnowflakeTelemetryAgent(
        openfinops_endpoint=args.openfinops_endpoint,
        snowflake_account=args.snowflake_account,
        snowflake_user=user,
        snowflake_password=password,
        snowflake_warehouse=args.snowflake_warehouse,
        snowflake_role=args.snowflake_role,
        edition=args.edition
    )

    try:
        agent.run_continuous(interval_seconds=args.interval)
    except KeyboardInterrupt:
        print("\nSnowflake Telemetry Agent stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Agent failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
