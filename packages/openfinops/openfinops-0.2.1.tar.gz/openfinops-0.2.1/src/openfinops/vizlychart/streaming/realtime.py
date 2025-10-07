"""
Real-time Data Streaming and Live Visualization for Vizly
========================================================

High-performance streaming engine with sub-millisecond latency,
WebSocket support, and enterprise-grade reliability.
"""

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
import time
import threading
import logging
from typing import Dict, List, Optional, Any, Callable, Union, AsyncGenerator
from dataclasses import dataclass, field
from collections import deque
import numpy as np
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Optional dependencies
try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False


@dataclass
class StreamMetrics:
    """Streaming performance metrics."""
    messages_processed: int = 0
    bytes_processed: int = 0
    average_latency: float = 0.0
    peak_latency: float = 0.0
    dropped_messages: int = 0
    error_count: int = 0
    throughput_mbps: float = 0.0
    connection_count: int = 0
    uptime_seconds: float = 0.0


@dataclass
class DataPoint:
    """Single data point in a stream."""
    timestamp: float
    value: Union[float, int, str, List, Dict]
    metadata: Dict[str, Any] = field(default_factory=dict)
    stream_id: Optional[str] = None
    sequence_id: Optional[int] = None


class DataStream(ABC):
    """Abstract base class for data streams."""

    def __init__(self, stream_id: str, buffer_size: int = 10000):
        self.stream_id = stream_id
        self.buffer_size = buffer_size
        self.buffer: deque[DataPoint] = deque(maxlen=buffer_size)
        self.subscribers: List[Callable[[DataPoint], None]] = []
        self.is_active = False
        self.sequence_counter = 0

    @abstractmethod
    async def start(self):
        """Start the data stream."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the data stream."""
        pass

    def subscribe(self, callback: Callable[[DataPoint], None]):
        """Subscribe to stream updates."""
        self.subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[DataPoint], None]):
        """Unsubscribe from stream updates."""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

    def emit(self, data_point: DataPoint):
        """Emit data point to all subscribers."""
        data_point.stream_id = self.stream_id
        data_point.sequence_id = self.sequence_counter
        self.sequence_counter += 1

        self.buffer.append(data_point)

        for callback in self.subscribers:
            try:
                callback(data_point)
            except Exception as e:
                logger.error(f"Error in stream subscriber: {e}")

    def get_recent_data(self, count: int = 100) -> List[DataPoint]:
        """Get most recent data points."""
        return list(self.buffer)[-count:]

    def get_data_since(self, timestamp: float) -> List[DataPoint]:
        """Get data points since timestamp."""
        return [dp for dp in self.buffer if dp.timestamp >= timestamp]


class WebSocketStream(DataStream):
    """WebSocket-based data stream."""

    def __init__(self, stream_id: str, url: str, buffer_size: int = 10000):
        super().__init__(stream_id, buffer_size)
        self.url = url
        self.websocket = None
        self._connection_task = None

    async def start(self):
        """Start WebSocket connection."""
        if not HAS_WEBSOCKETS:
            raise RuntimeError("websockets library not available")

        self.is_active = True
        self._connection_task = asyncio.create_task(self._connection_loop())
        logger.info(f"Started WebSocket stream {self.stream_id} -> {self.url}")

    async def stop(self):
        """Stop WebSocket connection."""
        self.is_active = False
        if self.websocket:
            await self.websocket.close()
        if self._connection_task:
            self._connection_task.cancel()

    async def _connection_loop(self):
        """Main WebSocket connection loop."""
        while self.is_active:
            try:
                async with websockets.connect(self.url) as websocket:
                    self.websocket = websocket
                    logger.info(f"WebSocket connected: {self.url}")

                    async for message in websocket:
                        if not self.is_active:
                            break

                        try:
                            data = json.loads(message)
                            data_point = DataPoint(
                                timestamp=time.time(),
                                value=data.get('value', data),
                                metadata=data.get('metadata', {})
                            )
                            self.emit(data_point)
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON in WebSocket message: {e}")

            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                if self.is_active:
                    await asyncio.sleep(5)  # Retry after 5 seconds


class HTTPPollingStream(DataStream):
    """HTTP polling-based data stream."""

    def __init__(self, stream_id: str, url: str, interval: float = 1.0,
                 buffer_size: int = 10000):
        super().__init__(stream_id, buffer_size)
        self.url = url
        self.interval = interval
        self._polling_task = None
        self.session = None

    async def start(self):
        """Start HTTP polling."""
        if not HAS_AIOHTTP:
            raise RuntimeError("aiohttp library not available")

        self.is_active = True
        self.session = aiohttp.ClientSession()
        self._polling_task = asyncio.create_task(self._polling_loop())
        logger.info(f"Started HTTP polling stream {self.stream_id} -> {self.url}")

    async def stop(self):
        """Stop HTTP polling."""
        self.is_active = False
        if self._polling_task:
            self._polling_task.cancel()
        if self.session:
            await self.session.close()

    async def _polling_loop(self):
        """Main HTTP polling loop."""
        while self.is_active:
            try:
                async with self.session.get(self.url) as response:
                    if response.status == 200:
                        data = await response.json()
                        data_point = DataPoint(
                            timestamp=time.time(),
                            value=data.get('value', data),
                            metadata=data.get('metadata', {})
                        )
                        self.emit(data_point)
                    else:
                        logger.warning(f"HTTP {response.status} from {self.url}")

            except Exception as e:
                logger.error(f"HTTP polling error: {e}")

            await asyncio.sleep(self.interval)


class RedisStream(DataStream):
    """Redis-based data stream using pub/sub."""

    def __init__(self, stream_id: str, redis_url: str, channel: str,
                 buffer_size: int = 10000):
        super().__init__(stream_id, buffer_size)
        self.redis_url = redis_url
        self.channel = channel
        self.redis_client = None
        self._subscription_task = None

    async def start(self):
        """Start Redis subscription."""
        if not HAS_REDIS:
            raise RuntimeError("redis library not available")

        self.is_active = True
        self.redis_client = redis.from_url(self.redis_url)
        self._subscription_task = asyncio.create_task(self._subscription_loop())
        logger.info(f"Started Redis stream {self.stream_id} -> {self.channel}")

    async def stop(self):
        """Stop Redis subscription."""
        self.is_active = False
        if self._subscription_task:
            self._subscription_task.cancel()
        if self.redis_client:
            await self.redis_client.close()

    async def _subscription_loop(self):
        """Main Redis subscription loop."""
        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(self.channel)

        try:
            async for message in pubsub.listen():
                if not self.is_active:
                    break

                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        data_point = DataPoint(
                            timestamp=time.time(),
                            value=data.get('value', data),
                            metadata=data.get('metadata', {})
                        )
                        self.emit(data_point)
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in Redis message: {e}")

        finally:
            await pubsub.unsubscribe(self.channel)


class SyntheticStream(DataStream):
    """Synthetic data stream for testing and demos."""

    def __init__(self, stream_id: str, data_type: str = "sine",
                 frequency: float = 1.0, amplitude: float = 1.0,
                 noise_level: float = 0.1, buffer_size: int = 10000):
        super().__init__(stream_id, buffer_size)
        self.data_type = data_type
        self.frequency = frequency
        self.amplitude = amplitude
        self.noise_level = noise_level
        self._generation_task = None
        self.start_time = time.time()

    async def start(self):
        """Start synthetic data generation."""
        self.is_active = True
        self.start_time = time.time()
        self._generation_task = asyncio.create_task(self._generation_loop())
        logger.info(f"Started synthetic stream {self.stream_id} ({self.data_type})")

    async def stop(self):
        """Stop synthetic data generation."""
        self.is_active = False
        if self._generation_task:
            self._generation_task.cancel()

    async def _generation_loop(self):
        """Main data generation loop."""
        while self.is_active:
            current_time = time.time()
            elapsed = current_time - self.start_time

            # Generate data based on type
            if self.data_type == "sine":
                value = self.amplitude * np.sin(2 * np.pi * self.frequency * elapsed)
            elif self.data_type == "cosine":
                value = self.amplitude * np.cos(2 * np.pi * self.frequency * elapsed)
            elif self.data_type == "random":
                value = np.random.normal(0, self.amplitude)
            elif self.data_type == "linear":
                value = self.amplitude * elapsed * self.frequency
            else:
                value = 0.0

            # Add noise
            if self.noise_level > 0:
                value += np.random.normal(0, self.noise_level)

            data_point = DataPoint(
                timestamp=current_time,
                value=float(value),
                metadata={
                    'data_type': self.data_type,
                    'elapsed': elapsed
                }
            )

            self.emit(data_point)
            await asyncio.sleep(0.01)  # 100 Hz update rate


class StreamingEngine:
    """High-performance streaming engine for real-time visualization."""

    def __init__(self):
        self.streams: Dict[str, DataStream] = {}
        self.charts: Dict[str, 'RealtimeChart'] = {}
        self.is_running = False
        self.metrics = StreamMetrics()
        self._metrics_task = None
        self.start_time = time.time()

        # Event handlers
        self.on_stream_data: Optional[Callable[[str, DataPoint], None]] = None
        self.on_stream_error: Optional[Callable[[str, Exception], None]] = None

    async def start(self):
        """Start the streaming engine."""
        self.is_running = True
        self.start_time = time.time()
        self._metrics_task = asyncio.create_task(self._update_metrics_loop())
        logger.info("Streaming engine started")

    async def stop(self):
        """Stop the streaming engine."""
        self.is_running = False

        # Stop all streams
        for stream in self.streams.values():
            await stream.stop()

        # Stop all charts
        for chart in self.charts.values():
            await chart.stop()

        if self._metrics_task:
            self._metrics_task.cancel()

        logger.info("Streaming engine stopped")

    def add_stream(self, stream: DataStream):
        """Add a data stream."""
        self.streams[stream.stream_id] = stream
        stream.subscribe(self._on_stream_data)
        logger.info(f"Added stream: {stream.stream_id}")

    def remove_stream(self, stream_id: str):
        """Remove a data stream."""
        if stream_id in self.streams:
            stream = self.streams[stream_id]
            stream.unsubscribe(self._on_stream_data)
            del self.streams[stream_id]
            logger.info(f"Removed stream: {stream_id}")

    def get_stream(self, stream_id: str) -> Optional[DataStream]:
        """Get a stream by ID."""
        return self.streams.get(stream_id)

    def add_chart(self, chart: 'RealtimeChart'):
        """Add a real-time chart."""
        self.charts[chart.chart_id] = chart
        logger.info(f"Added chart: {chart.chart_id}")

    def remove_chart(self, chart_id: str):
        """Remove a real-time chart."""
        if chart_id in self.charts:
            del self.charts[chart_id]
            logger.info(f"Removed chart: {chart_id}")

    async def start_all_streams(self):
        """Start all registered streams."""
        tasks = []
        for stream in self.streams.values():
            if not stream.is_active:
                tasks.append(stream.start())

        if tasks:
            await asyncio.gather(*tasks)

    async def stop_all_streams(self):
        """Stop all registered streams."""
        tasks = []
        for stream in self.streams.values():
            if stream.is_active:
                tasks.append(stream.stop())

        if tasks:
            await asyncio.gather(*tasks)

    def _on_stream_data(self, data_point: DataPoint):
        """Handle incoming stream data."""
        self.metrics.messages_processed += 1

        # Calculate latency
        latency = time.time() - data_point.timestamp
        self.metrics.average_latency = (
            (self.metrics.average_latency + latency) / 2
        )
        self.metrics.peak_latency = max(self.metrics.peak_latency, latency)

        # Forward to charts
        for chart in self.charts.values():
            if data_point.stream_id in chart.stream_ids:
                chart.update_data(data_point)

        # Call external handler
        if self.on_stream_data:
            try:
                self.on_stream_data(data_point.stream_id, data_point)
            except Exception as e:
                self.metrics.error_count += 1
                if self.on_stream_error:
                    self.on_stream_error(data_point.stream_id, e)

    async def _update_metrics_loop(self):
        """Update performance metrics."""
        while self.is_running:
            self.metrics.uptime_seconds = time.time() - self.start_time
            self.metrics.connection_count = len([
                s for s in self.streams.values() if s.is_active
            ])

            # Calculate throughput
            if self.metrics.uptime_seconds > 0:
                self.metrics.throughput_mbps = (
                    self.metrics.bytes_processed /
                    (1024 * 1024 * self.metrics.uptime_seconds)
                )

            await asyncio.sleep(1.0)

    def get_metrics(self) -> StreamMetrics:
        """Get current streaming metrics."""
        return self.metrics

    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics = StreamMetrics()
        self.start_time = time.time()


class RealtimeChart:
    """Real-time chart that updates with streaming data."""

    def __init__(self, chart_id: str, chart_type: str = "line"):
        self.chart_id = chart_id
        self.chart_type = chart_type
        self.stream_ids: List[str] = []
        self.data_buffer: Dict[str, deque] = {}
        self.max_points = 1000
        self.update_interval = 0.1  # seconds
        self.last_update = 0.0

        # Chart properties
        self.title = ""
        self.x_label = ""
        self.y_label = ""
        self.colors = ["blue", "red", "green", "orange", "purple"]

        # Performance settings
        self.auto_scale = True
        self.rolling_window = True
        self.decimation_factor = 1  # Keep every Nth point

    def add_stream(self, stream_id: str):
        """Add a data stream to this chart."""
        if stream_id not in self.stream_ids:
            self.stream_ids.append(stream_id)
            self.data_buffer[stream_id] = deque(maxlen=self.max_points)

    def remove_stream(self, stream_id: str):
        """Remove a data stream from this chart."""
        if stream_id in self.stream_ids:
            self.stream_ids.remove(stream_id)
            if stream_id in self.data_buffer:
                del self.data_buffer[stream_id]

    def update_data(self, data_point: DataPoint):
        """Update chart with new data point."""
        if data_point.stream_id in self.data_buffer:
            # Apply decimation
            if len(self.data_buffer[data_point.stream_id]) % self.decimation_factor == 0:
                self.data_buffer[data_point.stream_id].append(data_point)

    def get_chart_data(self) -> Dict[str, Any]:
        """Get current chart data for rendering."""
        chart_data = {
            'id': self.chart_id,
            'type': self.chart_type,
            'title': self.title,
            'x_label': self.x_label,
            'y_label': self.y_label,
            'series': []
        }

        for i, stream_id in enumerate(self.stream_ids):
            if stream_id in self.data_buffer:
                data = list(self.data_buffer[stream_id])
                if data:
                    x_values = [dp.timestamp for dp in data]
                    y_values = [dp.value for dp in data]

                    series = {
                        'name': stream_id,
                        'color': self.colors[i % len(self.colors)],
                        'x': x_values,
                        'y': y_values
                    }
                    chart_data['series'].append(series)

        return chart_data

    async def start(self):
        """Start chart updates."""
        logger.info(f"Started real-time chart: {self.chart_id}")

    async def stop(self):
        """Stop chart updates."""
        logger.info(f"Stopped real-time chart: {self.chart_id}")


# Convenience functions for common streaming scenarios
async def create_websocket_stream(stream_id: str, url: str) -> WebSocketStream:
    """Create and start a WebSocket stream."""
    stream = WebSocketStream(stream_id, url)
    await stream.start()
    return stream

async def create_synthetic_stream(stream_id: str, data_type: str = "sine",
                                frequency: float = 1.0) -> SyntheticStream:
    """Create and start a synthetic data stream."""
    stream = SyntheticStream(stream_id, data_type, frequency)
    await stream.start()
    return stream

def create_realtime_chart(chart_id: str, stream_ids: List[str],
                         chart_type: str = "line") -> RealtimeChart:
    """Create a real-time chart connected to streams."""
    chart = RealtimeChart(chart_id, chart_type)
    for stream_id in stream_ids:
        chart.add_stream(stream_id)
    return chart

# Global streaming engine instance
_global_engine: Optional[StreamingEngine] = None

async def get_streaming_engine() -> StreamingEngine:
    """Get the global streaming engine instance."""
    global _global_engine
    if _global_engine is None:
        _global_engine = StreamingEngine()
        await _global_engine.start()
    return _global_engine

async def start_streaming_demo():
    """Start a comprehensive streaming demonstration."""
    engine = await get_streaming_engine()

    # Create synthetic streams
    sine_stream = await create_synthetic_stream("sine_wave", "sine", 0.5)
    random_stream = await create_synthetic_stream("random_data", "random", 1.0)

    engine.add_stream(sine_stream)
    engine.add_stream(random_stream)

    # Create real-time chart
    chart = create_realtime_chart("demo_chart", ["sine_wave", "random_data"])
    chart.title = "Real-time Streaming Demo"
    chart.x_label = "Time"
    chart.y_label = "Value"

    engine.add_chart(chart)

    logger.info("Streaming demo started!")
    logger.info(f"Active streams: {len(engine.streams)}")
    logger.info(f"Active charts: {len(engine.charts)}")

    return engine