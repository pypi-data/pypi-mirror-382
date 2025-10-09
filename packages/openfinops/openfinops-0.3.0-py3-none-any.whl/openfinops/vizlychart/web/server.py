"""Web server and WebSocket handlers for real-time Vizly applications."""

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



from __future__ import annotations

import json
import logging
import threading
import time
from typing import Any, Dict, Optional, Set

try:
    import tornado.web
    import tornado.websocket
    import tornado.ioloop

    HAS_TORNADO = True
except ImportError:
    HAS_TORNADO = False

from .components import BaseWebComponent, InteractionEvent
from ..core.streaming import DataStream


logger = logging.getLogger(__name__)


class WebSocketHandler(tornado.websocket.WebSocketHandler if HAS_TORNADO else object):
    """WebSocket handler for real-time chart updates."""

    # Class-level storage for all connected clients
    clients: Set[WebSocketHandler] = set()
    subscriptions: Dict[str, Set[WebSocketHandler]] = {}

    def __init__(self, *args, **kwargs):
        if not HAS_TORNADO:
            raise ImportError("Tornado is required for WebSocket functionality")
        super().__init__(*args, **kwargs)
        self.client_id = None
        self.subscribed_charts: Set[str] = set()

    def open(self) -> None:
        """Handle new WebSocket connection."""
        self.client_id = f"client_{int(time.time() * 1000)}"
        WebSocketHandler.clients.add(self)
        logger.info(f"WebSocket client connected: {self.client_id}")

        # Send welcome message
        self.write_message(
            {
                "type": "connection",
                "client_id": self.client_id,
                "message": "Connected to Vizly server",
            }
        )

    def on_message(self, message: str) -> None:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "subscribe":
                self._handle_subscribe(data)
            elif message_type == "unsubscribe":
                self._handle_unsubscribe(data)
            elif message_type == "interaction":
                self._handle_interaction(data)
            elif message_type == "data_request":
                self._handle_data_request(data)
            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from {self.client_id}")
        except Exception as e:
            logger.error(f"Error handling message from {self.client_id}: {e}")

    def on_close(self) -> None:
        """Handle WebSocket connection close."""
        # Remove from all subscriptions
        for chart_id in self.subscribed_charts:
            if chart_id in WebSocketHandler.subscriptions:
                WebSocketHandler.subscriptions[chart_id].discard(self)

        WebSocketHandler.clients.discard(self)
        logger.info(f"WebSocket client disconnected: {self.client_id}")

    def _handle_subscribe(self, data: Dict[str, Any]) -> None:
        """Handle chart subscription request."""
        chart_id = data.get("chart_id")
        if not chart_id:
            return

        # Add to subscriptions
        if chart_id not in WebSocketHandler.subscriptions:
            WebSocketHandler.subscriptions[chart_id] = set()

        WebSocketHandler.subscriptions[chart_id].add(self)
        self.subscribed_charts.add(chart_id)

        logger.info(f"Client {self.client_id} subscribed to chart {chart_id}")

        # Send confirmation
        self.write_message({"type": "subscription_confirmed", "chart_id": chart_id})

    def _handle_unsubscribe(self, data: Dict[str, Any]) -> None:
        """Handle chart unsubscription request."""
        chart_id = data.get("chart_id")
        if not chart_id:
            return

        # Remove from subscriptions
        if chart_id in WebSocketHandler.subscriptions:
            WebSocketHandler.subscriptions[chart_id].discard(self)

        self.subscribed_charts.discard(chart_id)

        logger.info(f"Client {self.client_id} unsubscribed from chart {chart_id}")

    def _handle_interaction(self, data: Dict[str, Any]) -> None:
        """Handle chart interaction event."""
        chart_id = data.get("chart_id")
        event_type = data.get("event_type")
        event_data = data.get("data", {})

        if not chart_id or not event_type:
            return

        # Create interaction event
        event = InteractionEvent(
            event_type=event_type,
            chart_id=chart_id,
            data=event_data,
            timestamp=time.time(),
        )

        # Broadcast to other subscribers of the same chart
        self.broadcast_to_chart(
            chart_id,
            {
                "type": "interaction_event",
                "event": {
                    "event_type": event.event_type,
                    "chart_id": event.chart_id,
                    "data": event.data,
                    "timestamp": event.timestamp,
                },
            },
            exclude_client=self,
        )

        logger.info(
            f"Interaction event from {self.client_id}: {event_type} on {chart_id}"
        )

    def _handle_data_request(self, data: Dict[str, Any]) -> None:
        """Handle data request."""
        chart_id = data.get("chart_id")
        if not chart_id:
            return

        # This would be connected to actual chart data
        # For now, send dummy response
        self.write_message(
            {
                "type": "data_response",
                "chart_id": chart_id,
                "data": {"message": "Data request received"},
            }
        )

    @classmethod
    def broadcast_to_chart(
        cls,
        chart_id: str,
        message: Dict[str, Any],
        exclude_client: Optional[WebSocketHandler] = None,
    ) -> None:
        """Broadcast message to all clients subscribed to a chart."""
        if chart_id not in cls.subscriptions:
            return

        message_json = json.dumps(message)
        disconnected_clients = set()

        for client in cls.subscriptions[chart_id]:
            if client == exclude_client:
                continue

            try:
                client.write_message(message_json)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                disconnected_clients.add(client)

        # Clean up disconnected clients
        for client in disconnected_clients:
            cls.subscriptions[chart_id].discard(client)

    @classmethod
    def broadcast_to_all(cls, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients."""
        message_json = json.dumps(message)
        disconnected_clients = set()

        for client in cls.clients.copy():
            try:
                client.write_message(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected_clients.add(client)

        # Clean up disconnected clients
        for client in disconnected_clients:
            cls.clients.discard(client)


class StaticFileHandler(tornado.web.StaticFileHandler if HAS_TORNADO else object):
    """Custom static file handler with CORS support."""

    def set_default_headers(self) -> None:
        """Set CORS headers."""
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")


class VizlyServer:
    """Web server for hosting Vizly dashboards and real-time charts."""

    def __init__(self, port: int = 8888, debug: bool = False) -> None:
        if not HAS_TORNADO:
            raise ImportError("Tornado is required for server functionality")

        self.port = port
        self.debug = debug
        self.app: Optional[tornado.web.Application] = None
        self.components: Dict[str, BaseWebComponent] = {}
        self.data_streams: Dict[str, DataStream] = {}
        self._running = False
        self._server_thread: Optional[threading.Thread] = None

    def add_component(self, component: BaseWebComponent) -> str:
        """Add a web component to the server."""
        self.components[component.id] = component

        # Set up event handlers for real-time updates
        def on_component_event(event: InteractionEvent) -> None:
            WebSocketHandler.broadcast_to_chart(
                event.chart_id,
                {
                    "type": "component_update",
                    "event": {
                        "event_type": event.event_type,
                        "chart_id": event.chart_id,
                        "data": event.data,
                        "timestamp": event.timestamp,
                    },
                },
            )

        component.on("data_update", on_component_event)
        component.on("interaction", on_component_event)

        return component.id

    def add_data_stream(self, name: str, data_stream: DataStream) -> None:
        """Add a data stream for real-time updates."""
        self.data_streams[name] = data_stream

        # Subscribe to stream updates
        def on_stream_update(source_name: str, data: Dict[str, Any]) -> None:
            WebSocketHandler.broadcast_to_all(
                {
                    "type": "stream_update",
                    "stream_name": name,
                    "source_name": source_name,
                    "data": data,
                    "timestamp": time.time(),
                }
            )

        data_stream.subscribe(on_stream_update)

    def create_application(self) -> tornado.web.Application:
        """Create Tornado web application."""
        handlers = [
            (r"/ws", WebSocketHandler),
            (r"/api/components", self._make_api_handler("components")),
            (r"/api/component/([^/]+)", self._make_api_handler("component")),
            (r"/", self._make_page_handler("index")),
            (r"/dashboard/([^/]+)", self._make_page_handler("dashboard")),
            (r"/static/(.*)", StaticFileHandler, {"path": "./static"}),
        ]

        settings = {
            "debug": self.debug,
            "autoreload": self.debug,
        }

        return tornado.web.Application(handlers, **settings)

    def _make_api_handler(self, endpoint: str):
        """Create API request handler."""

        class APIHandler(tornado.web.RequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.server = None  # Will be set by outer scope

            def set_default_headers(self):
                self.set_header("Content-Type", "application/json")
                self.set_header("Access-Control-Allow-Origin", "*")

            def get(self, *args):
                if endpoint == "components":
                    self._handle_components_get()
                elif endpoint == "component":
                    component_id = args[0] if args else None
                    self._handle_component_get(component_id)

            def _handle_components_get(self):
                components_data = {}
                for comp_id, component in self.server.components.items():
                    components_data[comp_id] = component.to_json()

                self.write({"components": components_data})

            def _handle_component_get(self, component_id: str):
                if component_id in self.server.components:
                    component = self.server.components[component_id]
                    self.write(component.to_json())
                else:
                    self.set_status(404)
                    self.write({"error": f"Component {component_id} not found"})

        # Bind server instance to handler
        def handler_factory(*args, **kwargs):
            handler = APIHandler(*args, **kwargs)
            handler.server = self
            return handler

        return handler_factory

    def _make_page_handler(self, page_type: str):
        """Create page request handler."""

        class PageHandler(tornado.web.RequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.server = None  # Will be set by outer scope

            def get(self, *args):
                if page_type == "index":
                    self._handle_index_page()
                elif page_type == "dashboard":
                    dashboard_id = args[0] if args else None
                    self._handle_dashboard_page(dashboard_id)

            def _handle_index_page(self):
                # Generate index page with list of components
                components_list = []
                for comp_id, component in self.server.components.items():
                    components_list.append(
                        f'<li><a href="/dashboard/{comp_id}">{comp_id}</a></li>'
                    )

                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Vizly Server</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        ul {{ list-style-type: none; }}
                        li {{ margin: 10px 0; }}
                        a {{ text-decoration: none; color: #007bff; }}
                        a:hover {{ text-decoration: underline; }}
                    </style>
                </head>
                <body>
                    <h1>Vizly Server</h1>
                    <p>Available dashboards:</p>
                    <ul>
                        {''.join(components_list)}
                    </ul>
                </body>
                </html>
                """
                self.write(html)

            def _handle_dashboard_page(self, dashboard_id: str):
                if dashboard_id in self.server.components:
                    component = self.server.components[dashboard_id]
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Vizly Dashboard - {dashboard_id}</title>
                        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                        <script src="https://d3js.org/d3.v7.min.js"></script>
                        <style>
                            body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}
                        </style>
                    </head>
                    <body>
                        {component.to_html()}

                        <script>
                            // WebSocket connection for real-time updates
                            const ws = new WebSocket('ws://localhost:{self.port}/ws');

                            ws.onopen = function() {{
                                console.log('WebSocket connected');
                                // Subscribe to this dashboard
                                ws.send(JSON.stringify({{
                                    type: 'subscribe',
                                    chart_id: '{dashboard_id}'
                                }}));
                            }};

                            ws.onmessage = function(event) {{
                                const data = JSON.parse(event.data);
                                console.log('WebSocket message:', data);

                                if (data.type === 'component_update') {{
                                    // Handle component updates
                                    handleComponentUpdate(data);
                                }} else if (data.type === 'stream_update') {{
                                    // Handle stream updates
                                    handleStreamUpdate(data);
                                }}
                            }};

                            ws.onclose = function() {{
                                console.log('WebSocket disconnected');
                            }};

                            function handleComponentUpdate(data) {{
                                // Update component based on event data
                                console.log('Component update:', data);
                            }}

                            function handleStreamUpdate(data) {{
                                // Update charts with new stream data
                                console.log('Stream update:', data);
                            }}
                        </script>
                    </body>
                    </html>
                    """
                    self.write(html)
                else:
                    self.set_status(404)
                    self.write(f"<h1>Dashboard {dashboard_id} not found</h1>")

        # Bind server instance to handler
        def handler_factory(*args, **kwargs):
            handler = PageHandler(*args, **kwargs)
            handler.server = self
            return handler

        return handler_factory

    def start(self, blocking: bool = True) -> None:
        """Start the web server."""
        if self._running:
            logger.warning("Server is already running")
            return

        self.app = self.create_application()
        self.app.listen(self.port)

        logger.info(f"Vizly server starting on port {self.port}")
        logger.info(f"Dashboard available at: http://localhost:{self.port}")

        self._running = True

        if blocking:
            try:
                tornado.ioloop.IOLoop.current().start()
            except KeyboardInterrupt:
                logger.info("Server interrupted by user")
                self.stop()
        else:
            # Start in separate thread
            def run_server():
                tornado.ioloop.IOLoop.current().start()

            self._server_thread = threading.Thread(target=run_server, daemon=True)
            self._server_thread.start()

    def stop(self) -> None:
        """Stop the web server."""
        if not self._running:
            return

        self._running = False

        # Stop all data streams
        for stream in self.data_streams.values():
            stream.stop_streaming()

        if tornado.ioloop.IOLoop.current():
            tornado.ioloop.IOLoop.current().stop()

        logger.info("Vizly server stopped")

    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running
