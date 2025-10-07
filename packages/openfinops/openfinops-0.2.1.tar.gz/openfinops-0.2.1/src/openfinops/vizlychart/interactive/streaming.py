"""
Real-time Data Streaming and Live Charts
========================================

Provides real-time data streaming capabilities for live visualizations.
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

import time
import threading
import warnings
from typing import Dict, List, Optional, Callable, Any, Union, Deque
from collections import deque
from datetime import datetime, timedelta
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import asyncio
    HAS_ASYNCIO = True
except ImportError:
    HAS_ASYNCIO = False

from ..charts.base import BaseChart
from ..exceptions import VizlyError


class DataStreamer:
    """Manages real-time data streams."""

    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        self.streams: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.running = False
        self._lock = threading.Lock()

    def create_stream(
        self,
        stream_id: str,
        data_source: Union[Callable, str],
        update_interval: float = 0.1,
        fields: Optional[List[str]] = None
    ) -> None:
        """Create a new data stream."""
        fields = fields or ['timestamp', 'value']

        stream_config = {
            'data_source': data_source,
            'update_interval': update_interval,
            'fields': fields,
            'buffer': {field: deque(maxlen=self.buffer_size) for field in fields},
            'last_update': 0,
            'active': False,
            'thread': None
        }

        with self._lock:
            self.streams[stream_id] = stream_config
            self.callbacks[stream_id] = []

    def add_callback(self, stream_id: str, callback: Callable) -> None:
        """Add callback for stream updates."""
        if stream_id in self.callbacks:
            self.callbacks[stream_id].append(callback)

    def start_stream(self, stream_id: str) -> None:
        """Start streaming for a specific stream."""
        if stream_id not in self.streams:
            raise VizlyError(f"Stream '{stream_id}' not found")

        stream = self.streams[stream_id]
        if stream['active']:
            return

        stream['active'] = True

        # Start streaming thread
        def stream_worker():
            while stream['active']:
                try:
                    # Get new data
                    data = self._get_stream_data(stream)
                    if data:
                        # Update buffers
                        with self._lock:
                            for field, value in data.items():
                                if field in stream['buffer']:
                                    stream['buffer'][field].append(value)

                        # Notify callbacks
                        for callback in self.callbacks[stream_id]:
                            try:
                                callback(stream_id, data)
                            except Exception as e:
                                warnings.warn(f"Callback error: {e}")

                    time.sleep(stream['update_interval'])

                except Exception as e:
                    warnings.warn(f"Stream error: {e}")
                    time.sleep(1)  # Back off on error

        stream['thread'] = threading.Thread(target=stream_worker, daemon=True)
        stream['thread'].start()

    def stop_stream(self, stream_id: str) -> None:
        """Stop streaming for a specific stream."""
        if stream_id in self.streams:
            self.streams[stream_id]['active'] = False

    def stop_all_streams(self) -> None:
        """Stop all active streams."""
        for stream_id in self.streams:
            self.stop_stream(stream_id)

    def get_stream_data(self, stream_id: str, n_points: Optional[int] = None) -> Dict[str, List]:
        """Get current data from stream buffer."""
        if stream_id not in self.streams:
            return {}

        stream = self.streams[stream_id]
        data = {}

        with self._lock:
            for field, buffer in stream['buffer'].items():
                if n_points:
                    data[field] = list(buffer)[-n_points:]
                else:
                    data[field] = list(buffer)

        return data

    def _get_stream_data(self, stream: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get new data from stream source."""
        data_source = stream['data_source']

        try:
            if callable(data_source):
                # Function-based data source
                result = data_source()
                if isinstance(result, dict):
                    return result
                elif isinstance(result, (list, tuple)):
                    # Assume timestamp, value format
                    return {
                        'timestamp': result[0] if len(result) > 0 else time.time(),
                        'value': result[1] if len(result) > 1 else 0
                    }
                else:
                    # Single value
                    return {
                        'timestamp': time.time(),
                        'value': result
                    }
            elif isinstance(data_source, str):
                # File or URL-based source (could be extended)
                return self._read_from_source(data_source)

        except Exception as e:
            warnings.warn(f"Failed to get stream data: {e}")

        return None

    def _read_from_source(self, source: str) -> Optional[Dict[str, Any]]:
        """Read data from file or URL source."""
        # Placeholder for file/URL reading
        # Could be extended to read from CSV, API endpoints, etc.
        return {
            'timestamp': time.time(),
            'value': np.random.randn()  # Placeholder
        }


class RealTimeChart(BaseChart):
    """Real-time chart with live data updates."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.streamer = DataStreamer()
        self.animation = None
        self.plot_elements = {}
        self.data_history = {}
        self.max_points = 100
        self.update_interval = 100  # milliseconds

    def add_stream(
        self,
        stream_id: str,
        data_source: Union[Callable, str],
        plot_type: str = 'line',
        update_interval: float = 0.1,
        **plot_kwargs
    ) -> 'RealTimeChart':
        """Add a data stream to the chart."""
        # Create stream
        self.streamer.create_stream(
            stream_id, data_source, update_interval,
            fields=['timestamp', 'value']
        )

        # Add callback to update chart
        self.streamer.add_callback(stream_id, self._on_stream_update)

        # Initialize plot element
        if plot_type == 'line':
            line, = self.axes.plot([], [], label=stream_id, **plot_kwargs)
            self.plot_elements[stream_id] = {
                'type': 'line',
                'element': line,
                'kwargs': plot_kwargs
            }
        elif plot_type == 'scatter':
            scatter = self.axes.scatter([], [], label=stream_id, **plot_kwargs)
            self.plot_elements[stream_id] = {
                'type': 'scatter',
                'element': scatter,
                'kwargs': plot_kwargs
            }

        # Initialize data history
        self.data_history[stream_id] = {
            'x': deque(maxlen=self.max_points),
            'y': deque(maxlen=self.max_points)
        }

        return self

    def start_streaming(self) -> None:
        """Start real-time streaming and animation."""
        if not HAS_MATPLOTLIB:
            warnings.warn("Matplotlib required for real-time charts")
            return

        # Start all streams
        for stream_id in self.streamer.streams:
            self.streamer.start_stream(stream_id)

        # Start animation
        self.animation = animation.FuncAnimation(
            self.figure.figure, self._animate,
            interval=self.update_interval, blit=False
        )

        self.show()

    def stop_streaming(self) -> None:
        """Stop streaming and animation."""
        self.streamer.stop_all_streams()
        if self.animation:
            self.animation.event_source.stop()

    def set_max_points(self, max_points: int) -> None:
        """Set maximum number of points to display."""
        self.max_points = max_points
        for history in self.data_history.values():
            history['x'] = deque(history['x'], maxlen=max_points)
            history['y'] = deque(history['y'], maxlen=max_points)

    def _on_stream_update(self, stream_id: str, data: Dict[str, Any]) -> None:
        """Handle stream data updates."""
        if stream_id in self.data_history:
            timestamp = data.get('timestamp', time.time())
            value = data.get('value', 0)

            self.data_history[stream_id]['x'].append(timestamp)
            self.data_history[stream_id]['y'].append(value)

    def _animate(self, frame) -> List[Any]:
        """Animation function for real-time updates."""
        artists = []

        for stream_id, plot_info in self.plot_elements.items():
            if stream_id in self.data_history:
                history = self.data_history[stream_id]
                x_data = list(history['x'])
                y_data = list(history['y'])

                if len(x_data) > 0:
                    if plot_info['type'] == 'line':
                        line = plot_info['element']
                        line.set_data(x_data, y_data)
                        artists.append(line)
                    elif plot_info['type'] == 'scatter':
                        scatter = plot_info['element']
                        if len(x_data) > 0:
                            scatter.set_offsets(np.column_stack((x_data, y_data)))
                        artists.append(scatter)

        # Auto-scale axes
        self._auto_scale()

        return artists

    def _auto_scale(self) -> None:
        """Auto-scale axes based on current data."""
        all_x, all_y = [], []

        for history in self.data_history.values():
            if len(history['x']) > 0:
                all_x.extend(history['x'])
                all_y.extend(history['y'])

        if all_x and all_y:
            margin = 0.1
            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)

            x_margin = (x_max - x_min) * margin if x_max != x_min else 1
            y_margin = (y_max - y_min) * margin if y_max != y_min else 1

            self.axes.set_xlim(x_min - x_margin, x_max + x_margin)
            self.axes.set_ylim(y_min - y_margin, y_max + y_margin)


class FinancialStreamChart(RealTimeChart):
    """Real-time financial chart with OHLC data."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ohlc_data = deque(maxlen=100)
        self.candlestick_patches = []

    def add_price_stream(
        self,
        data_source: Callable,
        timeframe: str = '1min'
    ) -> 'FinancialStreamChart':
        """Add real-time price stream for financial data."""
        def price_callback(stream_id: str, data: Dict[str, Any]) -> None:
            if 'ohlc' in data:
                ohlc = data['ohlc']
                self.ohlc_data.append(ohlc)
                self._update_candlesticks()

        self.streamer.create_stream(
            'price_stream', data_source, 1.0,  # 1 second updates
            fields=['timestamp', 'ohlc']
        )
        self.streamer.add_callback('price_stream', price_callback)

        return self

    def _update_candlesticks(self) -> None:
        """Update candlestick visualization."""
        # Clear previous candlesticks
        for patch in self.candlestick_patches:
            patch.remove()
        self.candlestick_patches.clear()

        # Draw new candlesticks
        for i, ohlc in enumerate(self.ohlc_data):
            open_price, high_price, low_price, close_price = ohlc

            # Determine color
            color = 'green' if close_price >= open_price else 'red'

            # Draw body
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)

            body = plt.Rectangle(
                (i - 0.3, body_bottom), 0.6, body_height,
                facecolor=color, alpha=0.8
            )
            self.axes.add_patch(body)
            self.candlestick_patches.append(body)

            # Draw wicks
            wick_line = plt.Line2D(
                [i, i], [low_price, high_price],
                color='black', linewidth=1
            )
            self.axes.add_line(wick_line)
            self.candlestick_patches.append(wick_line)


class WebSocketStreamer:
    """WebSocket-based real-time data streaming."""

    def __init__(self):
        self.connections = {}
        self.charts = {}

    async def connect_websocket(
        self,
        url: str,
        chart: RealTimeChart,
        data_parser: Optional[Callable] = None
    ) -> None:
        """Connect to WebSocket for real-time data."""
        if not HAS_ASYNCIO:
            warnings.warn("asyncio required for WebSocket streaming")
            return

        try:
            import websockets

            async def websocket_handler():
                async with websockets.connect(url) as websocket:
                    async for message in websocket:
                        try:
                            if data_parser:
                                data = data_parser(message)
                            else:
                                data = {'timestamp': time.time(), 'value': float(message)}

                            # Update chart
                            chart._on_stream_update('websocket', data)

                        except Exception as e:
                            warnings.warn(f"WebSocket data parsing error: {e}")

            # Run websocket in event loop
            asyncio.create_task(websocket_handler())

        except ImportError:
            warnings.warn("websockets library required for WebSocket streaming")


class DataGenerator:
    """Utility class for generating sample streaming data."""

    @staticmethod
    def random_walk(start_value: float = 0, volatility: float = 1) -> Callable:
        """Generate random walk data."""
        current_value = start_value

        def generator():
            nonlocal current_value
            current_value += np.random.normal(0, volatility)
            return {
                'timestamp': time.time(),
                'value': current_value
            }

        return generator

    @staticmethod
    def sine_wave(frequency: float = 1, amplitude: float = 1, phase: float = 0) -> Callable:
        """Generate sine wave data."""
        start_time = time.time()

        def generator():
            current_time = time.time()
            elapsed = current_time - start_time
            value = amplitude * np.sin(2 * np.pi * frequency * elapsed + phase)
            return {
                'timestamp': current_time,
                'value': value
            }

        return generator

    @staticmethod
    def stock_price_simulator(
        initial_price: float = 100,
        volatility: float = 0.02,
        trend: float = 0.0001
    ) -> Callable:
        """Generate realistic stock price data."""
        current_price = initial_price

        def generator():
            nonlocal current_price
            # Geometric Brownian Motion
            dt = 1  # 1 second intervals
            random_shock = np.random.normal(0, 1)
            drift = trend * dt
            diffusion = volatility * np.sqrt(dt) * random_shock

            current_price = current_price * np.exp(drift + diffusion)

            return {
                'timestamp': time.time(),
                'value': current_price
            }

        return generator

    @staticmethod
    def ohlc_generator(base_price: float = 100, volatility: float = 0.01) -> Callable:
        """Generate OHLC (candlestick) data."""
        current_price = base_price

        def generator():
            nonlocal current_price

            # Generate random price movement
            price_change = np.random.normal(0, volatility * current_price)
            open_price = current_price
            close_price = current_price + price_change

            # Generate high and low
            high_extra = abs(np.random.normal(0, volatility * current_price * 0.5))
            low_extra = abs(np.random.normal(0, volatility * current_price * 0.5))

            high_price = max(open_price, close_price) + high_extra
            low_price = min(open_price, close_price) - low_extra

            current_price = close_price

            return {
                'timestamp': time.time(),
                'ohlc': (open_price, high_price, low_price, close_price)
            }

        return generator