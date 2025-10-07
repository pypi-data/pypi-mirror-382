#!/usr/bin/env python3
"""
Vizly Web Dashboard Demo - Interactive Frontend
"""

import time
import numpy as np
import threading
from datetime import datetime, timedelta

try:
    import vizly as px
    from vizly.web import VizlyServer, DashboardComponent, InteractiveChart
    from vizly.core.streaming import DataStream, RandomDataSource
    print("✓ Vizly web components imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Vizly web components: {e}")
    print("Install web dependencies with: pip install tornado plotly")
    exit(1)


def create_sample_dashboard():
    """Create a comprehensive dashboard with multiple charts."""
    print("🎨 Creating interactive dashboard...")

    # Create dashboard
    dashboard = DashboardComponent(title="Vizly Analytics Dashboard")
    dashboard.set_layout("grid", columns=2)

    # Chart 1: Real-time line chart
    chart1 = InteractiveChart()
    chart1.config.title = "Real-Time Sensor Data"
    chart1.config.width = 600
    chart1.config.height = 400

    # Generate time series data
    time_points = np.linspace(0, 24, 100)  # 24 hours
    sensor1_data = 20 + 5 * np.sin(time_points) + np.random.normal(0, 1, 100)
    sensor2_data = 22 + 3 * np.cos(time_points * 1.5) + np.random.normal(0, 0.8, 100)

    chart1.add_line_series(time_points, sensor1_data, name="Temperature", color="red")
    chart1.add_line_series(time_points, sensor2_data, name="Humidity", color="blue")
    chart1.set_layout_options(
        xaxis_title="Time (hours)",
        yaxis_title="Value",
        legend=dict(x=0.1, y=0.9)
    )

    # Chart 2: Financial candlestick
    chart2 = InteractiveChart()
    chart2.config.title = "Stock Price Analysis"
    chart2.config.width = 600
    chart2.config.height = 400

    # Generate sample OHLC data
    dates = [datetime.now() - timedelta(days=x) for x in range(30, 0, -1)]
    prices = 100 + np.cumsum(np.random.normal(0, 2, 30))

    opens = prices + np.random.normal(0, 1, 30)
    highs = np.maximum(opens, prices) + np.abs(np.random.normal(0, 1, 30))
    lows = np.minimum(opens, prices) - np.abs(np.random.normal(0, 1, 30))
    closes = prices

    # For demo, we'll create a simple line chart (candlestick requires more complex setup)
    chart2.add_line_series(list(range(30)), closes, name="Close Price", color="green")
    chart2.set_layout_options(
        xaxis_title="Days",
        yaxis_title="Price ($)",
    )

    # Chart 3: 3D Surface
    chart3 = InteractiveChart()
    chart3.config.title = "3D Surface Visualization"
    chart3.config.width = 600
    chart3.config.height = 500

    # Generate 3D surface data
    x = np.linspace(-2, 2, 20)
    y = np.linspace(-2, 2, 20)
    X, Y = np.meshgrid(x, y)
    Z = np.sin(np.sqrt(X**2 + Y**2)) * np.exp(-0.3 * np.sqrt(X**2 + Y**2))

    chart3.add_surface_series(X, Y, Z, name="Mathematical Surface", colorscale="viridis")

    # Chart 4: Bar chart with performance metrics
    chart4 = InteractiveChart()
    chart4.config.title = "Performance Metrics"
    chart4.config.width = 600
    chart4.config.height = 400

    metrics = ["Rendering", "Memory", "CPU", "Network", "Storage"]
    values = [95, 78, 65, 88, 92]
    colors = ["green" if v > 80 else "orange" if v > 60 else "red" for v in values]

    chart4.add_bar_series(metrics, values, name="Performance %", color="steelblue")
    chart4.set_layout_options(
        xaxis_title="Component",
        yaxis_title="Performance (%)",
        yaxis_range=[0, 100]
    )

    # Add charts to dashboard
    dashboard.add_chart(chart1)
    dashboard.add_chart(chart2)
    dashboard.add_chart(chart3)
    dashboard.add_chart(chart4)

    print(f"✓ Dashboard created with {len(dashboard.charts)} interactive charts")
    return dashboard


def setup_real_time_data(server):
    """Set up real-time data streaming."""
    print("📡 Setting up real-time data streaming...")

    try:
        # Create data stream
        data_stream = DataStream()

        # Add random data source
        random_source = RandomDataSource(frequency=2.0)  # 2 Hz
        data_stream.add_source("live_sensor", random_source, ["timestamp", "value", "temperature"])

        # Add to server
        server.add_data_stream("sensor_data", data_stream)

        # Start streaming
        data_stream.start_streaming()
        print("✓ Real-time data streaming active")

        return data_stream
    except Exception as e:
        print(f"⚠️  Real-time streaming setup failed: {e}")
        return None


def create_status_page():
    """Create a simple status page for monitoring."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vizly Server Status</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
            .status.online { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .status.warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
            .metric { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }
            .logo { text-align: center; margin-bottom: 30px; }
            .logo h1 { color: #2c3e50; margin: 0; font-size: 2.5em; }
            .logo p { color: #7f8c8d; margin: 5px 0 0 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <h1>🚀 Vizly Server</h1>
                <p>High-Performance Visualization Platform</p>
            </div>

            <div class="status online">
                <strong>✓ Server Status: ONLINE</strong><br>
                Vizly web server is running and ready to serve interactive dashboards.
            </div>

            <h3>📊 Server Metrics</h3>
            <div class="metric"><span>Server Port:</span><span>8888</span></div>
            <div class="metric"><span>Active Connections:</span><span id="connections">0</span></div>
            <div class="metric"><span>Uptime:</span><span id="uptime">Just started</span></div>
            <div class="metric"><span>Charts Served:</span><span>4</span></div>
            <div class="metric"><span>Real-time Streams:</span><span>1 active</span></div>

            <h3>🎯 Available Dashboards</h3>
            <div style="margin: 20px 0;">
                <a href="/dashboard" style="display: inline-block; background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin-right: 10px;">📈 Main Dashboard</a>
                <a href="/api/components" style="display: inline-block; background: #95a5a6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">🔧 API Status</a>
            </div>

            <div class="status warning">
                <strong>⚡ Performance Mode: CPU</strong><br>
                For GPU acceleration, install: <code>pip install plotx[gpu]</code>
            </div>

            <p style="text-align: center; color: #7f8c8d; margin-top: 30px;">
                <em>Vizly: Where Performance Meets Beauty</em>
            </p>
        </div>

        <script>
            // Simple uptime counter
            let startTime = Date.now();
            setInterval(() => {
                let uptime = Math.floor((Date.now() - startTime) / 1000);
                let minutes = Math.floor(uptime / 60);
                let seconds = uptime % 60;
                document.getElementById('uptime').textContent = `${minutes}m ${seconds}s`;
            }, 1000);

            // Simulate connection counter
            setInterval(() => {
                let connections = Math.floor(Math.random() * 5) + 1;
                document.getElementById('connections').textContent = connections;
            }, 3000);
        </script>
    </body>
    </html>
    """


def run_web_server():
    """Run the Vizly web server with dashboard."""
    print("🌐 Starting Vizly Web Server...")
    print("=" * 50)

    try:
        # Check if tornado is available
        import tornado.web
        import tornado.ioloop

        # Create server
        server = VizlyServer(port=8888, debug=True)

        # Create and add dashboard
        dashboard = create_sample_dashboard()
        dashboard_id = server.add_component(dashboard)

        # Set up real-time data
        data_stream = setup_real_time_data(server)

        print(f"✓ Vizly server configured")
        print(f"✓ Dashboard ID: {dashboard_id}")
        print(f"✓ Real-time streaming: {'Active' if data_stream else 'Disabled'}")

        # Add custom status page handler
        status_html = create_status_page()

        class StatusHandler(tornado.web.RequestHandler):
            def get(self):
                self.write(status_html)

        # Override the server's create_application to add status page
        original_create_app = server.create_application
        def create_application_with_status():
            app = original_create_app()
            app.add_handlers(r".*", [(r"/status", StatusHandler)])
            return app
        server.create_application = create_application_with_status

        print("\n🎯 Server URLs:")
        print("=" * 30)
        print(f"📊 Main Dashboard:  http://localhost:8888/dashboard/{dashboard_id}")
        print(f"📈 Server Status:   http://localhost:8888/status")
        print(f"🔧 API Endpoints:   http://localhost:8888/api/components")
        print(f"🌐 WebSocket:       ws://localhost:8888/ws")

        print(f"\n🚀 Starting server...")
        print("=" * 50)
        print("Press Ctrl+C to stop the server")
        print("=" * 50)

        # Start server in a way that allows graceful shutdown
        def start_server():
            server.start(blocking=True)

        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        # Keep main thread alive and handle keyboard interrupt
        try:
            while server_thread.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down Vizly server...")
            server.stop()
            if data_stream:
                data_stream.stop_streaming()
            print("✓ Server stopped gracefully")

    except ImportError:
        print("❌ Tornado not available for web server")
        print("Install with: pip install tornado")
        return False

    except Exception as e:
        print(f"❌ Failed to start web server: {e}")
        return False

    return True


def main():
    """Main entry point for web dashboard demo."""
    print("Vizly Web Dashboard Demo")
    print("🌐" + "=" * 48 + "🌐")

    success = run_web_server()

    if success:
        print("\n✅ Web dashboard demo completed successfully!")
    else:
        print("\n⚠️  Web dashboard demo encountered issues")
        print("   Try installing: pip install tornado plotly")


if __name__ == "__main__":
    main()