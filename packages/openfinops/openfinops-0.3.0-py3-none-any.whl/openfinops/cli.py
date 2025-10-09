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
OpenFinOps Command Line Interface
==================================

Provides command-line tools for OpenFinOps operations.
"""

import argparse
import sys


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OpenFinOps - AI/ML Cost Observability Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="OpenFinOps 0.1.5"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Server command
    server_parser = subparsers.add_parser("server", help="Start the OpenFinOps server")
    server_parser.add_argument("--port", type=int, default=8080, help="Port to run on")
    server_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")

    # Dashboard command
    dashboard_parser = subparsers.add_parser("dashboard", help="Launch the dashboard")
    dashboard_parser.add_argument("--port", type=int, default=8080, help="Port to run on")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize OpenFinOps configuration")
    init_parser.add_argument("--config", default="config.yaml", help="Config file path")

    args = parser.parse_args()

    if args.command == "server":
        server_command(args)
    elif args.command == "dashboard":
        dashboard_command(args)
    elif args.command == "init":
        init_command(args)
    else:
        parser.print_help()


def server_command(args=None):
    """Start the OpenFinOps server."""
    print("🚀 Starting OpenFinOps Web UI Server...")
    host = args.host if args else '127.0.0.1'
    port = args.port if args else 8080

    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print("\n   Dashboard will be available at:")
    print(f"   http://{host}:{port}\n")

    try:
        from openfinops.webui import start_server

        if start_server is None:
            raise ImportError("Web UI module not available")

        print("✅ OpenFinOps Web UI loaded successfully")
        print()
        print("📊 Available Dashboards:")
        print(f"   • Overview Dashboard:     http://{host}:{port}/")
        print(f"   • CFO Executive:          http://{host}:{port}/dashboard/cfo")
        print(f"   • COO Operational:        http://{host}:{port}/dashboard/coo")
        print(f"   • Infrastructure Leader:  http://{host}:{port}/dashboard/infrastructure")
        print()
        print("🔄 Real-time Updates: Enabled (WebSocket)")
        print("📈 Live Charts: Enabled (Chart.js)")
        print()
        print("Press Ctrl+C to stop the server\n")
        print("-" * 60)

        # Start the server
        start_server(host=host, port=port, debug=False)

    except ImportError as e:
        print(f"⚠️  Error: Web UI dependencies not available")
        print(f"   {str(e)}")
        print()
        print("   Please install web UI dependencies:")
        print("   pip install flask flask-socketio flask-cors")
        print()
        print("   Or install with all dependencies:")
        print("   pip install openfinops[all]")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()


def dashboard_command(args=None):
    """Launch the dashboard."""
    # Reuse server_command since they both launch the same Web UI
    if args is None:
        # Create a simple args object
        class Args:
            port = 8080
            host = '127.0.0.1'
        args = Args()

    server_command(args)


def init_command(args):
    """Initialize OpenFinOps configuration."""
    print("🔧 Initializing OpenFinOps...")
    print(f"   Config file: {args.config}")

    # TODO: Implement config initialization
    print("⚠️  Configuration initialization coming soon!")
    print("   This will create a default configuration file")


if __name__ == "__main__":
    main()
