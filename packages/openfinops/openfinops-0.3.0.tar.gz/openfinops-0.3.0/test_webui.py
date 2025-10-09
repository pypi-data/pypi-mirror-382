#!/usr/bin/env python3
"""
Test script for OpenFinOps Web UI Server
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from openfinops.webui import start_server

if __name__ == '__main__':
    print("🚀 Starting OpenFinOps Web UI Server...")
    print("   Host: 127.0.0.1")
    print("   Port: 8080")
    print()
    print("📊 Available Dashboards:")
    print("   • Overview:        http://127.0.0.1:8080/")
    print("   • CFO Executive:   http://127.0.0.1:8080/dashboard/cfo")
    print("   • COO Operational: http://127.0.0.1:8080/dashboard/coo")
    print("   • Infrastructure:  http://127.0.0.1:8080/dashboard/infrastructure")
    print()
    print("Press Ctrl+C to stop\n")

    start_server(host='127.0.0.1', port=8080, debug=True)
