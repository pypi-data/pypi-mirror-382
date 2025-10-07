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
Generic Telemetry Agent for OpenFinOps
====================================

Universal telemetry collection agent that can be customized for any infrastructure.
Provides a flexible framework for collecting metrics from custom systems, on-premise infrastructure,
or any environment not covered by the specific cloud agents.

This agent can be extended and configured to collect metrics from:
- Custom applications and services
- On-premise infrastructure (servers, databases, networks)
- Docker containers and orchestration platforms
- Monitoring tools (Prometheus, Grafana, etc.)
- Network devices (switches, routers, firewalls)
- IoT devices and edge computing platforms

Features:
- Flexible metric collection framework
- Plugin-based architecture for easy extension
- Custom metric definitions and collection intervals
- Event tracking and alerting
- Health monitoring and self-healing
- Configurable data pipelines

Usage:
    python generic_telemetry_agent.py --openfinops-endpoint http://localhost:8080 --config config.json
"""

import os
import sys
import time
import json
import yaml
import logging
import argparse
import threading
import subprocess
import importlib.util
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from collections import deque, defaultdict
from abc import ABC, abstractmethod

import requests
import psutil


class MetricCollector(ABC):
    """Abstract base class for metric collectors"""

    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Collect metrics and return as dictionary"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return collector name"""
        pass

    def is_healthy(self) -> bool:
        """Check if collector is healthy"""
        return True


class SystemMetricsCollector(MetricCollector):
    """System metrics collector using psutil"""

    def get_name(self) -> str:
        return "system_metrics"

    def collect(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()

            # Network metrics
            network_io = psutil.net_io_counters()

            # Process metrics
            process_count = len(psutil.pids())

            # Load average (Unix only)
            load_avg = None
            try:
                load_avg = os.getloadavg()
            except (OSError, AttributeError):
                pass

            return {
                "timestamp": time.time(),
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": {
                        "current": cpu_freq.current if cpu_freq else None,
                        "min": cpu_freq.min if cpu_freq else None,
                        "max": cpu_freq.max if cpu_freq else None
                    }
                },
                "memory": {
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_bytes": memory.used,
                    "usage_percent": memory.percent,
                    "swap_total": swap.total,
                    "swap_used": swap.used,
                    "swap_percent": swap.percent
                },
                "disk": {
                    "total_bytes": disk_usage.total,
                    "used_bytes": disk_usage.used,
                    "free_bytes": disk_usage.free,
                    "usage_percent": (disk_usage.used / disk_usage.total) * 100,
                    "io": {
                        "read_bytes": disk_io.read_bytes if disk_io else 0,
                        "write_bytes": disk_io.write_bytes if disk_io else 0,
                        "read_count": disk_io.read_count if disk_io else 0,
                        "write_count": disk_io.write_count if disk_io else 0
                    }
                },
                "network": {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_recv": network_io.packets_recv,
                    "errors_in": network_io.errin,
                    "errors_out": network_io.errout,
                    "drops_in": network_io.dropin,
                    "drops_out": network_io.dropout
                },
                "processes": {
                    "count": process_count
                },
                "load_average": load_avg
            }

        except Exception as e:
            return {"error": str(e)}


class DockerMetricsCollector(MetricCollector):
    """Docker container metrics collector"""

    def get_name(self) -> str:
        return "docker_metrics"

    def collect(self) -> Dict[str, Any]:
        """Collect Docker container metrics"""
        try:
            # Check if Docker is available
            result = subprocess.run(['docker', 'ps', '--format', 'json'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return {"error": "Docker not available"}

            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    container = json.loads(line)
                    # Get detailed stats
                    stats_result = subprocess.run(
                        ['docker', 'stats', '--no-stream', '--format', 'json', container['ID'][:12]],
                        capture_output=True, text=True, timeout=5
                    )

                    if stats_result.returncode == 0:
                        stats = json.loads(stats_result.stdout.strip())
                        container.update(stats)

                    containers.append(container)

            return {
                "timestamp": time.time(),
                "containers": containers,
                "total_containers": len(containers),
                "running_containers": len([c for c in containers if c.get('State') == 'running'])
            }

        except Exception as e:
            return {"error": str(e)}


class ProcessMetricsCollector(MetricCollector):
    """Process-specific metrics collector"""

    def __init__(self, process_names: List[str] = None):
        self.process_names = process_names or []

    def get_name(self) -> str:
        return "process_metrics"

    def collect(self) -> Dict[str, Any]:
        """Collect process-specific metrics"""
        try:
            processes = []

            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status']):
                try:
                    if not self.process_names or proc.info['name'] in self.process_names:
                        proc_info = {
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu_percent": proc.info['cpu_percent'],
                            "memory_rss": proc.info['memory_info'].rss,
                            "memory_vms": proc.info['memory_info'].vms,
                            "status": proc.info['status']
                        }
                        processes.append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            return {
                "timestamp": time.time(),
                "processes": processes,
                "monitored_process_names": self.process_names,
                "total_monitored": len(processes)
            }

        except Exception as e:
            return {"error": str(e)}


class CustomCommandCollector(MetricCollector):
    """Custom command-based metrics collector"""

    def __init__(self, commands: Dict[str, str]):
        self.commands = commands

    def get_name(self) -> str:
        return "custom_commands"

    def collect(self) -> Dict[str, Any]:
        """Execute custom commands and collect output"""
        try:
            results = {}

            for name, command in self.commands.items():
                try:
                    result = subprocess.run(
                        command.split(),
                        capture_output=True,
                        text=True,
                        timeout=30
                    )

                    results[name] = {
                        "return_code": result.returncode,
                        "stdout": result.stdout.strip(),
                        "stderr": result.stderr.strip(),
                        "success": result.returncode == 0
                    }
                except subprocess.TimeoutExpired:
                    results[name] = {"error": "Command timeout"}
                except Exception as e:
                    results[name] = {"error": str(e)}

            return {
                "timestamp": time.time(),
                "command_results": results
            }

        except Exception as e:
            return {"error": str(e)}


class GenericTelemetryAgent:
    """Generic telemetry collection agent for any infrastructure"""

    def __init__(self, openfinops_endpoint: str, config_file: str = None):
        self.openfinops_endpoint = openfinops_endpoint.rstrip('/')
        self.config_file = config_file
        self.agent_id = f"generic-telemetry-{os.uname().nodename}-{int(time.time())}"

        # Setup logging first (needed by _load_config)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('GenericTelemetryAgent')

        # Load configuration
        self.config = self._load_config()

        # Update log level from config
        log_level = self.config.get('log_level', 'INFO')
        self.logger.setLevel(getattr(logging, log_level))

        # Initialize collectors
        self.collectors: List[MetricCollector] = []
        self._initialize_collectors()

        # Metrics storage
        self.metrics_buffer = deque(maxlen=1000)
        self.events_buffer = deque(maxlen=500)

        # Configuration
        self.collection_interval = self.config.get('collection_interval', 60)
        self.health_check_interval = self.config.get('health_check_interval', 300)

        # State tracking
        self.running = False
        self.registered = False
        self.start_time = time.time()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "agent_type": "generic_telemetry",
            "hostname": os.uname().nodename,
            "environment": "on-premise",
            "capabilities": ["system_monitoring"],
            "collection_interval": 60,
            "health_check_interval": 300,
            "log_level": "INFO",
            "collectors": {
                "system_metrics": {"enabled": True},
                "docker_metrics": {"enabled": False},
                "process_metrics": {
                    "enabled": False,
                    "process_names": []
                },
                "custom_commands": {
                    "enabled": False,
                    "commands": {}
                }
            }
        }

        if not self.config_file or not os.path.exists(self.config_file):
            self.logger.info("Using default configuration")
            return default_config

        try:
            with open(self.config_file, 'r') as f:
                if self.config_file.endswith('.json'):
                    config = json.load(f)
                elif self.config_file.endswith(('.yml', '.yaml')):
                    config = yaml.safe_load(f)
                else:
                    self.logger.warning("Unknown config format, using defaults")
                    return default_config

            # Merge with defaults
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value

            return config

        except Exception as e:
            self.logger.error(f"Error loading config: {e}, using defaults")
            return default_config

    def _initialize_collectors(self):
        """Initialize metric collectors based on configuration"""
        collectors_config = self.config.get('collectors', {})

        # System metrics collector
        if collectors_config.get('system_metrics', {}).get('enabled', True):
            self.collectors.append(SystemMetricsCollector())
            self.logger.info("Enabled system metrics collector")

        # Docker metrics collector
        if collectors_config.get('docker_metrics', {}).get('enabled', False):
            self.collectors.append(DockerMetricsCollector())
            self.logger.info("Enabled Docker metrics collector")

        # Process metrics collector
        process_config = collectors_config.get('process_metrics', {})
        if process_config.get('enabled', False):
            process_names = process_config.get('process_names', [])
            self.collectors.append(ProcessMetricsCollector(process_names))
            self.logger.info(f"Enabled process metrics collector for: {process_names}")

        # Custom commands collector
        commands_config = collectors_config.get('custom_commands', {})
        if commands_config.get('enabled', False):
            commands = commands_config.get('commands', {})
            if commands:
                self.collectors.append(CustomCommandCollector(commands))
                self.logger.info(f"Enabled custom commands collector: {list(commands.keys())}")

        # Load custom collectors from plugins
        self._load_custom_collectors()

    def _load_custom_collectors(self):
        """Load custom collectors from plugins directory"""
        plugins_dir = self.config.get('plugins_directory', 'plugins')
        if not os.path.exists(plugins_dir):
            return

        try:
            for plugin_file in os.listdir(plugins_dir):
                if plugin_file.endswith('.py') and not plugin_file.startswith('_'):
                    plugin_path = os.path.join(plugins_dir, plugin_file)
                    spec = importlib.util.spec_from_file_location(
                        plugin_file[:-3], plugin_path
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Look for collector classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and
                            issubclass(attr, MetricCollector) and
                            attr != MetricCollector):
                            try:
                                collector = attr()
                                self.collectors.append(collector)
                                self.logger.info(f"Loaded custom collector: {collector.get_name()}")
                            except Exception as e:
                                self.logger.error(f"Error loading collector {attr_name}: {e}")

        except Exception as e:
            self.logger.error(f"Error loading custom collectors: {e}")

    def register_metric_collector(self, name: str, collector_func: Callable[[], Dict[str, Any]]):
        """Register a custom metric collector function.

        Args:
            name: Name for the collector
            collector_func: Function that returns metrics as a dictionary
        """
        class FunctionBasedCollector(MetricCollector):
            def __init__(self, collector_name: str, func: Callable[[], Dict[str, Any]]):
                self.collector_name = collector_name
                self.func = func

            def get_name(self) -> str:
                return self.collector_name

            def collect(self) -> Dict[str, Any]:
                return self.func()

        collector = FunctionBasedCollector(name, collector_func)
        self.collectors.append(collector)
        self.logger.info(f"Registered custom collector: {name}")

    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all collectors.

        Returns a simplified dictionary with collector names as keys.
        For full telemetry data, use collect_all_metrics().
        """
        all_metrics = self.collect_all_metrics()
        # Return just the collectors portion for simplified API
        return all_metrics.get('collectors', {})

    def push_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Push metrics to OpenFinOps platform (alias for send_telemetry_data)."""
        return self.send_telemetry_data(metrics)

    def register_agent(self) -> bool:
        """Register agent with OpenFinOps platform"""
        try:
            registration_data = {
                "agent_id": self.agent_id,
                "agent_type": self.config.get('agent_type', 'generic_telemetry'),
                "hostname": self.config.get('hostname', os.uname().nodename),
                "environment": self.config.get('environment', 'on-premise'),
                "capabilities": self.config.get('capabilities', ['system_monitoring']),
                "collectors": [collector.get_name() for collector in self.collectors],
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

    def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect metrics from all configured collectors"""
        try:
            all_metrics = {
                "timestamp": time.time(),
                "agent_id": self.agent_id,
                "hostname": self.config.get('hostname'),
                "environment": self.config.get('environment'),
                "collectors": {}
            }

            # Collect from each collector
            for collector in self.collectors:
                try:
                    collector_name = collector.get_name()
                    self.logger.debug(f"Collecting from {collector_name}")

                    metrics = collector.collect()
                    all_metrics["collectors"][collector_name] = {
                        "data": metrics,
                        "healthy": collector.is_healthy(),
                        "collection_time": time.time()
                    }

                except Exception as e:
                    self.logger.error(f"Error collecting from {collector.get_name()}: {e}")
                    all_metrics["collectors"][collector.get_name()] = {
                        "error": str(e),
                        "healthy": False,
                        "collection_time": time.time()
                    }

            # Generate summary
            all_metrics["summary"] = self._generate_metrics_summary(all_metrics)

            return all_metrics

        except Exception as e:
            self.logger.error(f"Error collecting all metrics: {e}")
            return {"error": str(e), "timestamp": time.time()}

    def _generate_metrics_summary(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of collected metrics"""
        summary = {
            "collectors_count": len(self.collectors),
            "healthy_collectors": 0,
            "total_metrics": 0,
            "health_status": "healthy"
        }

        collectors_data = metrics.get("collectors", {})
        for collector_name, collector_data in collectors_data.items():
            if collector_data.get("healthy", False):
                summary["healthy_collectors"] += 1

            if "data" in collector_data and isinstance(collector_data["data"], dict):
                summary["total_metrics"] += len(collector_data["data"])

        # Overall health assessment
        if summary["healthy_collectors"] < len(self.collectors) * 0.8:
            summary["health_status"] = "warning"
        elif summary["healthy_collectors"] == 0:
            summary["health_status"] = "critical"

        # Add system-specific summary if available
        system_data = collectors_data.get("system_metrics", {}).get("data", {})
        if "cpu" in system_data:
            summary["cpu_usage"] = system_data["cpu"].get("usage_percent", 0)
        if "memory" in system_data:
            summary["memory_usage"] = system_data["memory"].get("usage_percent", 0)
        if "disk" in system_data:
            summary["disk_usage"] = system_data["disk"].get("usage_percent", 0)

        return summary

    def send_telemetry_data(self, metrics: Dict[str, Any]) -> bool:
        """Send telemetry data to OpenFinOps platform"""
        try:
            telemetry_data = {
                "agent_id": self.agent_id,
                "timestamp": time.time(),
                "metrics": metrics,
                "events": list(self.events_buffer),
                "agent_health": {
                    "status": "healthy",
                    "uptime": time.time() - self.start_time,
                    "last_collection": time.time(),
                    "metrics_count": len(self.metrics_buffer),
                    "collectors_count": len(self.collectors)
                }
            }

            response = requests.post(
                f"{self.openfinops_endpoint}/api/v1/telemetry/ingest",
                json=telemetry_data,
                timeout=30
            )

            if response.status_code == 200:
                self.logger.info("Telemetry data sent successfully")
                # Clear buffers after successful send
                self.events_buffer.clear()
                return True
            else:
                self.logger.error(f"Failed to send telemetry: {response.status_code}")
                return False

        except Exception as e:
            self.logger.error(f"Error sending telemetry data: {e}")
            return False

    def health_check(self) -> bool:
        """Perform health check with OpenFinOps platform"""
        try:
            response = requests.get(
                f"{self.openfinops_endpoint}/health",
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def run_collection_cycle(self):
        """Run a single collection cycle"""
        try:
            # Collect all metrics
            metrics = self.collect_all_metrics()

            # Store in buffer
            self.metrics_buffer.append(metrics)

            # Send to platform
            self.send_telemetry_data(metrics)

            # Log summary
            summary = metrics.get("summary", {})
            self.logger.info(
                f"Collection complete - Collectors: {summary.get('collectors_count', 0)}, "
                f"Healthy: {summary.get('healthy_collectors', 0)}, "
                f"Status: {summary.get('health_status', 'unknown')}"
            )

        except Exception as e:
            self.logger.error(f"Collection cycle error: {e}")
            # Add error event
            self.events_buffer.append({
                "type": "collection_error",
                "timestamp": time.time(),
                "error": str(e)
            })

    def start(self):
        """Start the telemetry agent"""
        self.logger.info(f"Starting Generic Telemetry Agent: {self.agent_id}")
        self.logger.info(f"Collectors: {[c.get_name() for c in self.collectors]}")
        self.start_time = time.time()

        # Register with platform
        if not self.register_agent():
            self.logger.error("Failed to register agent. Exiting.")
            return

        self.running = True
        last_health_check = 0

        try:
            while self.running:
                current_time = time.time()

                # Run collection cycle
                self.run_collection_cycle()

                # Periodic health check
                if current_time - last_health_check > self.health_check_interval:
                    if not self.health_check():
                        self.logger.warning("Health check failed")
                    last_health_check = current_time

                # Wait for next collection
                time.sleep(self.collection_interval)

        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal")
        except Exception as e:
            self.logger.error(f"Agent error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the telemetry agent"""
        self.running = False
        self.logger.info("Generic Telemetry Agent stopped")

    def create_sample_config(self, output_file: str):
        """Create a sample configuration file"""
        sample_config = {
            "agent_type": "generic_telemetry",
            "hostname": os.uname().nodename,
            "environment": "on-premise",
            "capabilities": [
                "system_monitoring",
                "process_monitoring",
                "docker_monitoring",
                "custom_commands"
            ],
            "collection_interval": 60,
            "health_check_interval": 300,
            "log_level": "INFO",
            "plugins_directory": "plugins",
            "collectors": {
                "system_metrics": {
                    "enabled": True,
                    "description": "Collects CPU, memory, disk, and network metrics"
                },
                "docker_metrics": {
                    "enabled": False,
                    "description": "Collects Docker container metrics"
                },
                "process_metrics": {
                    "enabled": False,
                    "process_names": ["nginx", "apache2", "mysql", "postgres"],
                    "description": "Monitors specific processes"
                },
                "custom_commands": {
                    "enabled": False,
                    "commands": {
                        "disk_check": "df -h",
                        "service_status": "systemctl status nginx",
                        "network_connections": "netstat -an | wc -l"
                    },
                    "description": "Executes custom commands for metrics"
                }
            }
        }

        try:
            with open(output_file, 'w') as f:
                if output_file.endswith('.json'):
                    json.dump(sample_config, f, indent=2)
                else:
                    yaml.dump(sample_config, f, default_flow_style=False)

            print(f"Sample configuration created: {output_file}")

        except Exception as e:
            print(f"Error creating sample config: {e}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generic Telemetry Agent for OpenFinOps",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generic_telemetry_agent.py --openfinops-endpoint http://localhost:8080
  python generic_telemetry_agent.py --openfinops-endpoint http://localhost:8080 --config config.yml
  python generic_telemetry_agent.py --create-config config.yml
        """
    )

    parser.add_argument(
        "--openfinops-endpoint",
        help="OpenFinOps platform endpoint (e.g., http://localhost:8080)"
    )

    parser.add_argument(
        "--config",
        help="Configuration file (JSON or YAML format)"
    )

    parser.add_argument(
        "--create-config",
        metavar="FILE",
        help="Create sample configuration file and exit"
    )

    parser.add_argument(
        "--log-level",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="Log level (default: INFO)"
    )

    args = parser.parse_args()

    # Create sample config and exit
    if args.create_config:
        agent = GenericTelemetryAgent("http://localhost:8080")
        agent.create_sample_config(args.create_config)
        return

    # Validate required arguments
    if not args.openfinops_endpoint:
        parser.error("--openfinops-endpoint is required")

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Create and start agent
    agent = GenericTelemetryAgent(
        openfinops_endpoint=args.openfinops_endpoint,
        config_file=args.config
    )

    try:
        agent.start()
    except KeyboardInterrupt:
        print("\nGeneric Telemetry Agent stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Agent failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()