"""WebSocket server infrastructure for real-time streaming."""

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

import asyncio
import json
import logging
import time
import weakref
from typing import Dict, List, Optional, Set, Any, Callable
import threading
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StreamingClient:
    """Represents a connected streaming client."""
    client_id: str
    websocket: Any  # WebSocket connection
    subscriptions: Set[str]  # Stream IDs this client subscribes to
    connected_at: float
    last_ping: float

    def __post_init__(self):
        if not hasattr(self, 'last_ping'):
            self.last_ping = time.time()


class WebSocketStreamer:
    """WebSocket-based streaming server for real-time data."""

    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.host = host
        self.port = port
        self.is_running = False

        # Client management
        self.clients: Dict[str, StreamingClient] = {}
        self.client_counter = 0
        self._lock = threading.RLock()

        # Message handlers
        self.message_handlers: Dict[str, Callable] = {
            'subscribe': self._handle_subscribe,
            'unsubscribe': self._handle_unsubscribe,
            'ping': self._handle_ping,
            'get_streams': self._handle_get_streams,
        }

        # Data streams
        self.streams: Dict[str, List[Any]] = {}  # stream_id -> list of recent data
        self.stream_metadata: Dict[str, Dict] = {}

        # Performance tracking
        self.messages_sent = 0
        self.messages_received = 0
        self.start_time = 0.0

    async def start_server(self):
        """Start the WebSocket server."""
        try:
            import websockets

            self.start_time = time.time()
            self.is_running = True

            logger.info(f"Starting WebSocket server on {self.host}:{self.port}")

            async def handle_client(websocket, path):
                await self._handle_client_connection(websocket, path)

            server = await websockets.serve(handle_client, self.host, self.port)
            logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")

            # Keep server running
            await server.wait_closed()

        except ImportError:
            logger.error("websockets library not available. Install with: pip install websockets")
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")

    async def stop_server(self):
        """Stop the WebSocket server."""
        self.is_running = False
        logger.info("WebSocket server stopped")

    async def _handle_client_connection(self, websocket, path):
        """Handle new client connection."""
        client_id = f"client_{self.client_counter}"
        self.client_counter += 1

        client = StreamingClient(
            client_id=client_id,
            websocket=websocket,
            subscriptions=set(),
            connected_at=time.time(),
            last_ping=time.time()
        )

        with self._lock:
            self.clients[client_id] = client

        logger.info(f"Client {client_id} connected from {websocket.remote_address}")

        try:
            # Send welcome message
            await self._send_to_client(client, {
                'type': 'welcome',
                'client_id': client_id,
                'server_time': time.time(),
                'available_streams': list(self.streams.keys())
            })

            # Handle messages
            async for message in websocket:
                await self._handle_client_message(client, message)

        except Exception as e:
            logger.info(f"Client {client_id} disconnected: {e}")
        finally:
            with self._lock:
                if client_id in self.clients:
                    del self.clients[client_id]

    async def _handle_client_message(self, client: StreamingClient, message: str):
        """Handle message from client."""
        try:
            data = json.loads(message)
            message_type = data.get('type')

            if message_type in self.message_handlers:
                await self.message_handlers[message_type](client, data)
            else:
                await self._send_error(client, f"Unknown message type: {message_type}")

            self.messages_received += 1

        except json.JSONDecodeError:
            await self._send_error(client, "Invalid JSON message")
        except Exception as e:
            await self._send_error(client, f"Error processing message: {e}")

    async def _handle_subscribe(self, client: StreamingClient, data: Dict):
        """Handle stream subscription."""
        stream_id = data.get('stream_id')
        if not stream_id:
            await self._send_error(client, "Missing stream_id")
            return

        with self._lock:
            client.subscriptions.add(stream_id)

        await self._send_to_client(client, {
            'type': 'subscribed',
            'stream_id': stream_id,
            'metadata': self.stream_metadata.get(stream_id, {})
        })

        # Send recent data if available
        if stream_id in self.streams:
            recent_data = self.streams[stream_id][-100:]  # Last 100 points
            for data_point in recent_data:
                await self._send_to_client(client, {
                    'type': 'data',
                    'stream_id': stream_id,
                    'data': data_point
                })

    async def _handle_unsubscribe(self, client: StreamingClient, data: Dict):
        """Handle stream unsubscription."""
        stream_id = data.get('stream_id')
        if not stream_id:
            await self._send_error(client, "Missing stream_id")
            return

        with self._lock:
            client.subscriptions.discard(stream_id)

        await self._send_to_client(client, {
            'type': 'unsubscribed',
            'stream_id': stream_id
        })

    async def _handle_ping(self, client: StreamingClient, data: Dict):
        """Handle ping message."""
        client.last_ping = time.time()
        await self._send_to_client(client, {
            'type': 'pong',
            'timestamp': client.last_ping
        })

    async def _handle_get_streams(self, client: StreamingClient, data: Dict):
        """Handle request for available streams."""
        await self._send_to_client(client, {
            'type': 'streams_list',
            'streams': {
                stream_id: self.stream_metadata.get(stream_id, {})
                for stream_id in self.streams.keys()
            }
        })

    async def _send_to_client(self, client: StreamingClient, message: Dict):
        """Send message to specific client."""
        try:
            await client.websocket.send(json.dumps(message))
            self.messages_sent += 1
        except Exception as e:
            logger.warning(f"Failed to send message to {client.client_id}: {e}")

    async def _send_error(self, client: StreamingClient, error_message: str):
        """Send error message to client."""
        await self._send_to_client(client, {
            'type': 'error',
            'message': error_message,
            'timestamp': time.time()
        })

    async def broadcast_data(self, stream_id: str, data: Any, metadata: Optional[Dict] = None):
        """Broadcast data to all subscribed clients."""
        message = {
            'type': 'data',
            'stream_id': stream_id,
            'data': data,
            'timestamp': time.time()
        }

        if metadata:
            message['metadata'] = metadata

        # Store data for new subscribers
        if stream_id not in self.streams:
            self.streams[stream_id] = []

        self.streams[stream_id].append(data)

        # Keep only recent data
        if len(self.streams[stream_id]) > 1000:
            self.streams[stream_id] = self.streams[stream_id][-1000:]

        # Broadcast to subscribed clients
        with self._lock:
            subscribed_clients = [
                client for client in self.clients.values()
                if stream_id in client.subscriptions
            ]

        for client in subscribed_clients:
            try:
                await self._send_to_client(client, message)
            except Exception as e:
                logger.warning(f"Failed to broadcast to {client.client_id}: {e}")

    def register_stream(self, stream_id: str, metadata: Optional[Dict] = None):
        """Register a new data stream."""
        if stream_id not in self.streams:
            self.streams[stream_id] = []

        self.stream_metadata[stream_id] = metadata or {}
        logger.info(f"Registered stream: {stream_id}")

    def unregister_stream(self, stream_id: str):
        """Unregister a data stream."""
        if stream_id in self.streams:
            del self.streams[stream_id]
        if stream_id in self.stream_metadata:
            del self.stream_metadata[stream_id]
        logger.info(f"Unregistered stream: {stream_id}")

    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        uptime = time.time() - self.start_time if self.start_time > 0 else 0

        with self._lock:
            client_count = len(self.clients)
            total_subscriptions = sum(len(client.subscriptions) for client in self.clients.values())

        return {
            'uptime': uptime,
            'clients': {
                'connected': client_count,
                'total_subscriptions': total_subscriptions
            },
            'streams': {
                'registered': len(self.streams),
                'total_data_points': sum(len(data_list) for data_list in self.streams.values())
            },
            'messages': {
                'sent': self.messages_sent,
                'received': self.messages_received,
                'rate_sent': self.messages_sent / max(uptime, 1),
                'rate_received': self.messages_received / max(uptime, 1)
            },
            'performance': {
                'is_running': self.is_running,
                'host': self.host,
                'port': self.port
            }
        }

    async def cleanup_stale_clients(self, timeout: float = 300.0):
        """Remove clients that haven't pinged recently."""
        current_time = time.time()
        stale_clients = []

        with self._lock:
            for client_id, client in self.clients.items():
                if current_time - client.last_ping > timeout:
                    stale_clients.append(client_id)

        for client_id in stale_clients:
            logger.info(f"Removing stale client: {client_id}")
            with self._lock:
                if client_id in self.clients:
                    del self.clients[client_id]


class StreamingServer:
    """High-level streaming server with integrated data management."""

    def __init__(self, host: str = 'localhost', port: int = 8765):
        self.websocket_streamer = WebSocketStreamer(host, port)
        self.data_generators: Dict[str, Callable] = {}
        self.is_running = False

        # Background tasks
        self._server_task: Optional[asyncio.Task] = None
        self._data_tasks: List[asyncio.Task] = []

    def register_data_generator(self, stream_id: str, generator: Callable[[float], Any],
                               interval: float = 1.0, metadata: Optional[Dict] = None):
        """Register a data generator function."""
        self.data_generators[stream_id] = {
            'generator': generator,
            'interval': interval,
            'metadata': metadata or {}
        }

        self.websocket_streamer.register_stream(stream_id, metadata)

    async def start(self):
        """Start the streaming server."""
        if self.is_running:
            return

        self.is_running = True

        # Start WebSocket server
        self._server_task = asyncio.create_task(self.websocket_streamer.start_server())

        # Start data generators
        for stream_id, config in self.data_generators.items():
            task = asyncio.create_task(self._run_data_generator(stream_id, config))
            self._data_tasks.append(task)

        logger.info(f"Streaming server started with {len(self.data_generators)} data generators")

    async def stop(self):
        """Stop the streaming server."""
        self.is_running = False

        # Stop data generators
        for task in self._data_tasks:
            task.cancel()

        # Stop WebSocket server
        if self._server_task:
            self._server_task.cancel()

        await self.websocket_streamer.stop_server()

    async def _run_data_generator(self, stream_id: str, config: Dict):
        """Run a data generator in a loop."""
        generator = config['generator']
        interval = config['interval']
        start_time = time.time()

        while self.is_running:
            try:
                elapsed = time.time() - start_time
                data = generator(elapsed)

                await self.websocket_streamer.broadcast_data(stream_id, data)

                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"Error in data generator {stream_id}: {e}")
                await asyncio.sleep(interval)

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive server statistics."""
        return {
            'server': self.websocket_streamer.get_server_stats(),
            'data_generators': {
                'count': len(self.data_generators),
                'streams': list(self.data_generators.keys())
            },
            'running': self.is_running
        }