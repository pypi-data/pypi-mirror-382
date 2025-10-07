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
Vizly Command Line Interface
Provides command-line tools for Vizly demonstration and utilities.
"""

import argparse
import sys
import os
import subprocess


def demo_command():
    """Run Vizly demonstration."""
    print("🚀 Vizly Demonstration")
    print("=" * 30)

    try:
        import vizly
        import numpy as np

        # Check dependencies
        print("Checking dependencies...")
        if not vizly.check_dependencies():
            return 1

        print("Creating demonstration charts...")

        # Basic line chart
        x = np.linspace(0, 2 * np.pi, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)

        chart = vizly.LineChart()
        chart.plot(x, y1, color="blue", linewidth=2, label="sin(x)")
        chart.plot(x, y2, color="red", linewidth=2, label="cos(x)")
        chart.set_title("Vizly Demo - Pure Python Trigonometric Functions")
        chart.set_labels("X", "Y")
        chart.add_legend()
        chart.add_grid(alpha=0.3)
        chart.save("vizly_demo_trig.png")

        # Scatter plot
        np.random.seed(42)
        x_scatter = np.random.randn(200)
        y_scatter = np.random.randn(200)
        colors = x_scatter + y_scatter

        scatter_chart = vizly.ScatterChart()
        scatter_chart.plot(
            x_scatter, y_scatter, c=colors, s=50, alpha=0.7, cmap="viridis"
        )
        scatter_chart.set_title("Vizly Demo - Scatter Plot")
        scatter_chart.set_labels("X Values", "Y Values")
        scatter_chart.add_colorbar(label="Color Scale")
        scatter_chart.save("vizly_demo_scatter.png")

        # 3D Surface
        x_3d = np.linspace(-2, 2, 30)
        y_3d = np.linspace(-2, 2, 30)
        X, Y = np.meshgrid(x_3d, y_3d)
        Z = np.sin(X) * np.cos(Y)

        surface_chart = vizly.SurfaceChart()
        surface_chart.plot_surface(X, Y, Z, cmap="coolwarm", alpha=0.8)
        surface_chart.set_title("Vizly Demo - 3D Surface")
        surface_chart.save("vizly_demo_3d.png")

        print("\n✅ Demo completed successfully!")
        print("Generated files:")
        print("  📈 vizly_demo_trig.png")
        print("  📊 vizly_demo_scatter.png")
        print("  🌄 vizly_demo_3d.png")
        print("\n🎉 Vizly is working correctly!")

        return 0

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install Vizly: pip install vizly")
        return 1
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1


def gallery_command():
    """Launch Vizly gallery."""
    print("🎨 Launching Vizly Gallery...")

    try:
        # Try to find gallery script
        gallery_paths = [
            "examples/web_start.py",
            "vizly/examples/web_start.py",
            os.path.join(
                os.path.dirname(__file__), "..", "..", "examples", "web_start.py"
            ),
        ]

        gallery_script = None
        for path in gallery_paths:
            if os.path.exists(path):
                gallery_script = path
                break

        if gallery_script:
            print(f"Starting gallery from: {gallery_script}")
            subprocess.run([sys.executable, gallery_script])
        else:
            print("❌ Gallery script not found")
            print(
                "Please run from Vizly repository directory or install complete package"
            )
            return 1

        return 0

    except Exception as e:
        print(f"❌ Gallery launch failed: {e}")
        return 1


def server_command():
    """Start Vizly web server."""
    print("🌐 Starting Vizly Web Server...")

    try:
        import vizly.web

        server = vizly.web.VizlyServer()
        server.start(port=8888)
        return 0

    except ImportError:
        print("❌ Web components not available")
        print("Install with web support: pip install vizly[web]")
        return 1
    except Exception as e:
        print(f"❌ Server start failed: {e}")
        return 1


def info_command():
    """Show Vizly information."""
    print("📊 Vizly Information")
    print("=" * 30)

    try:
        import vizly

        info = vizly.get_info()

        print(f"Version: {info['version']}")
        print(f"Description: {info['description']}")
        print(f"Author: {info['author']}")
        print(f"License: {info['license']}")
        print(f"Python Requirements: {info['python_requires']}")
        print(f"Dependencies: {', '.join(info['dependencies'])}")

        print(f"\nFeatures ({len(info['features'])}):")
        for feature in info["features"]:
            print(f"  ✓ {feature}")

        print(f"\nChart Types ({len(info['chart_types'])}):")
        for chart_type in info["chart_types"]:
            print(f"  📊 {chart_type}")

        # Check if installed correctly
        print("\nInstallation Check:")
        if vizly.check_dependencies():
            print("  ✅ All dependencies satisfied")
        else:
            print("  ❌ Missing dependencies")

        return 0

    except Exception as e:
        print(f"❌ Info command failed: {e}")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Vizly Command Line Interface", prog="vizly"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run Vizly demonstration")
    demo_parser.set_defaults(func=demo_command)

    # Gallery command
    gallery_parser = subparsers.add_parser("gallery", help="Launch interactive gallery")
    gallery_parser.set_defaults(func=gallery_command)

    # Server command
    server_parser = subparsers.add_parser("server", help="Start web server")
    server_parser.add_argument(
        "--port", type=int, default=8888, help="Port number (default: 8888)"
    )
    server_parser.set_defaults(func=server_command)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show Vizly information")
    info_parser.set_defaults(func=info_command)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    try:
        return args.func()
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
