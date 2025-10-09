"""Real-time data streaming infrastructure for Vizly."""

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

import numpy as np
import json
import time
import threading
import queue
import logging
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass, field
from collections import deque
from abc import ABC, abstractmethod
import asyncio
import weakref

logger = logging.getLogger(__name__)


@dataclass
class DataPoint:
    """Single data point with timestamp."""
    timestamp: float
    value: Union[float, int, np.ndarray]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'timestamp': self.timestamp,
            'value': self.value.tolist() if isinstance(self.value, np.ndarray) else self.value,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataPoint':
        """Create from dictionary."""
        value = data['value']
        if isinstance(value, list):
            value = np.array(value)

        return cls(
            timestamp=data['timestamp'],
            value=value,
            metadata=data.get('metadata', {})
        )


class StreamingBuffer:
    """High-performance circular buffer for streaming data."""

    def __init__(self, max_size: int = 10000, data_type: str = 'numeric'):
        self.max_size = max_size
        self.data_type = data_type
        self._buffer = deque(maxlen=max_size)
        self._lock = threading.RLock()

        # Statistics
        self.total_points = 0
        self.last_update = 0.0
        self.update_rate = 0.0
        self._rate_window = deque(maxlen=100)

    def append(self, point: DataPoint):
        """Add new data point."""
        with self._lock:
            self._buffer.append(point)
            self.total_points += 1

            # Update rate calculation
            current_time = time.time()
            if self.last_update > 0:
                delta = current_time - self.last_update
                if delta > 0:
                    self._rate_window.append(1.0 / delta)
                    if self._rate_window:
                        self.update_rate = sum(self._rate_window) / len(self._rate_window)

            self.last_update = current_time

    def append_batch(self, points: List[DataPoint]):
        """Add multiple data points efficiently."""
        with self._lock:
            for point in points:
                self._buffer.append(point)

            self.total_points += len(points)
            self.last_update = time.time()

    def get_latest(self, count: int = 1) -> List[DataPoint]:
        """Get latest N points."""
        with self._lock:
            if count >= len(self._buffer):
                return list(self._buffer)
            return list(self._buffer)[-count:]

    def get_range(self, start_time: float, end_time: float) -> List[DataPoint]:
        """Get points within time range."""
        with self._lock:
            return [
                point for point in self._buffer
                if start_time <= point.timestamp <= end_time
            ]

    def get_window(self, duration: float) -> List[DataPoint]:
        """Get points from last N seconds."""
        current_time = time.time()
        return self.get_range(current_time - duration, current_time)

    def clear(self):
        """Clear all data."""
        with self._lock:
            self._buffer.clear()
            self.total_points = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        with self._lock:
            return {
                'size': len(self._buffer),
                'max_size': self.max_size,
                'total_points': self.total_points,
                'update_rate': self.update_rate,
                'last_update': self.last_update,
                'data_type': self.data_type
            }

    def to_numpy(self, field: str = 'value') -> np.ndarray:
        """Convert buffer to numpy array."""
        with self._lock:
            if field == 'value':
                values = [point.value for point in self._buffer]
            elif field == 'timestamp':
                values = [point.timestamp for point in self._buffer]
            else:
                values = [point.metadata.get(field) for point in self._buffer]

            return np.array(values)


class StreamingDataManager:
    """Manages multiple streaming data sources."""

    def __init__(self):
        self.streams: Dict[str, StreamingBuffer] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()

    def create_stream(self, stream_id: str, max_size: int = 10000,
                     data_type: str = 'numeric') -> StreamingBuffer:
        """Create new data stream."""
        with self._lock:
            buffer = StreamingBuffer(max_size, data_type)
            self.streams[stream_id] = buffer
            self.subscribers[stream_id] = []
            logger.info(f"Created stream {stream_id} with buffer size {max_size}")
            return buffer

    def get_stream(self, stream_id: str) -> Optional[StreamingBuffer]:
        """Get existing stream."""
        return self.streams.get(stream_id)

    def remove_stream(self, stream_id: str):
        """Remove stream."""
        with self._lock:
            if stream_id in self.streams:
                del self.streams[stream_id]
                del self.subscribers[stream_id]
                logger.info(f"Removed stream {stream_id}")

    def subscribe(self, stream_id: str, callback: Callable[[DataPoint], None]):
        """Subscribe to stream updates."""
        with self._lock:
            if stream_id not in self.subscribers:
                self.subscribers[stream_id] = []
            self.subscribers[stream_id].append(callback)

    def unsubscribe(self, stream_id: str, callback: Callable):
        """Unsubscribe from stream."""
        with self._lock:
            if stream_id in self.subscribers:
                try:
                    self.subscribers[stream_id].remove(callback)
                except ValueError:
                    pass

    def push_data(self, stream_id: str, value: Union[float, int, np.ndarray],
                  timestamp: Optional[float] = None, metadata: Optional[Dict] = None):
        """Push data to stream."""
        if stream_id not in self.streams:
            self.create_stream(stream_id)

        if timestamp is None:
            timestamp = time.time()

        point = DataPoint(timestamp, value, metadata or {})

        with self._lock:
            self.streams[stream_id].append(point)

            # Notify subscribers
            for callback in self.subscribers.get(stream_id, []):
                try:
                    callback(point)
                except Exception as e:
                    logger.error(f"Error in subscriber callback: {e}")

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all streams."""
        with self._lock:
            return {
                stream_id: buffer.get_stats()
                for stream_id, buffer in self.streams.items()
            }


class DataStreamer(ABC):
    """Abstract base class for data streamers."""

    def __init__(self, stream_id: str):
        self.stream_id = stream_id
        self.is_active = False
        self.data_manager: Optional[StreamingDataManager] = None
        self.error_callbacks: List[Callable[[Exception], None]] = []

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to data source."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Disconnect from data source."""
        pass

    @abstractmethod
    async def start_streaming(self):
        """Start streaming data."""
        pass

    def attach_manager(self, manager: StreamingDataManager):
        """Attach to data manager."""
        self.data_manager = manager

    def on_error(self, callback: Callable[[Exception], None]):
        """Register error callback."""
        self.error_callbacks.append(callback)

    def _handle_error(self, error: Exception):
        """Handle streaming error."""
        logger.error(f"Streaming error in {self.stream_id}: {error}")
        for callback in self.error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")


class WebSocketDataStreamer(DataStreamer):
    """WebSocket-based data streamer."""

    def __init__(self, stream_id: str, websocket_url: str):
        super().__init__(stream_id)
        self.websocket_url = websocket_url
        self.websocket = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0

    async def connect(self) -> bool:
        """Connect to WebSocket."""
        try:
            import websockets
            self.websocket = await websockets.connect(self.websocket_url)
            self.reconnect_attempts = 0
            logger.info(f"Connected to WebSocket: {self.websocket_url}")
            return True
        except Exception as e:
            self._handle_error(e)
            return False

    async def disconnect(self):
        """Disconnect from WebSocket."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.is_active = False

    async def start_streaming(self):
        """Start streaming from WebSocket."""
        if not self.websocket:
            if not await self.connect():
                return

        self.is_active = True

        try:
            async for message in self.websocket:
                if not self.is_active:
                    break

                try:
                    data = json.loads(message)

                    if self.data_manager:
                        self.data_manager.push_data(
                            self.stream_id,
                            data.get('value'),
                            data.get('timestamp'),
                            data.get('metadata')
                        )

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON in stream {self.stream_id}: {e}")
                except Exception as e:
                    self._handle_error(e)

        except Exception as e:
            self._handle_error(e)

            # Attempt reconnection
            if self.reconnect_attempts < self.max_reconnect_attempts:
                self.reconnect_attempts += 1
                await asyncio.sleep(self.reconnect_delay)
                logger.info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
                await self.start_streaming()


class SimulatedDataStreamer(DataStreamer):
    """Simulated data streamer for testing."""

    def __init__(self, stream_id: str, data_function: Callable[[float], float],
                 interval: float = 0.1):
        super().__init__(stream_id)
        self.data_function = data_function
        self.interval = interval
        self._task: Optional[asyncio.Task] = None

    async def connect(self) -> bool:
        """Always succeeds for simulated data."""
        return True

    async def disconnect(self):
        """Stop simulation."""
        self.is_active = False
        if self._task:
            self._task.cancel()

    async def start_streaming(self):
        """Start generating simulated data."""
        self.is_active = True

        async def generate_data():
            start_time = time.time()

            while self.is_active:
                current_time = time.time()
                elapsed = current_time - start_time

                try:
                    value = self.data_function(elapsed)

                    if self.data_manager:
                        self.data_manager.push_data(
                            self.stream_id,
                            value,
                            current_time
                        )

                    await asyncio.sleep(self.interval)

                except Exception as e:
                    self._handle_error(e)
                    break

        self._task = asyncio.create_task(generate_data())


class StreamingCoordinator:
    """Coordinates multiple streaming data sources."""

    def __init__(self):
        self.data_manager = StreamingDataManager()
        self.streamers: Dict[str, DataStreamer] = {}
        self.is_running = False
        self._tasks: List[asyncio.Task] = []

    def add_streamer(self, streamer: DataStreamer):
        """Add a data streamer."""
        streamer.attach_manager(self.data_manager)
        self.streamers[streamer.stream_id] = streamer
        logger.info(f"Added streamer: {streamer.stream_id}")

    def remove_streamer(self, stream_id: str):
        """Remove a data streamer."""
        if stream_id in self.streamers:
            del self.streamers[stream_id]
            self.data_manager.remove_stream(stream_id)

    async def start_all(self):
        """Start all streamers."""
        if self.is_running:
            return

        self.is_running = True

        for streamer in self.streamers.values():
            task = asyncio.create_task(streamer.start_streaming())
            self._tasks.append(task)

        logger.info(f"Started {len(self.streamers)} streamers")

    async def stop_all(self):
        """Stop all streamers."""
        self.is_running = False

        # Cancel all tasks
        for task in self._tasks:
            task.cancel()

        # Disconnect streamers
        for streamer in self.streamers.values():
            await streamer.disconnect()

        self._tasks.clear()
        logger.info("Stopped all streamers")

    def get_stream(self, stream_id: str) -> Optional[StreamingBuffer]:
        """Get stream buffer."""
        return self.data_manager.get_stream(stream_id)

    def subscribe_to_stream(self, stream_id: str, callback: Callable[[DataPoint], None]):
        """Subscribe to stream updates."""
        self.data_manager.subscribe(stream_id, callback)