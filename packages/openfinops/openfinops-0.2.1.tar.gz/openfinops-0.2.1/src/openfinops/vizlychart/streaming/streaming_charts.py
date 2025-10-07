"""Real-time streaming chart implementations for Vizly."""

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
import time
import threading
from typing import Dict, List, Optional, Callable, Any, Union
import logging

from ..charts.pure_charts import LineChart, ScatterChart
from ..rendering.pure_engine import PureCanvas, Color
from .data_streamer import StreamingBuffer, DataPoint, StreamingCoordinator

logger = logging.getLogger(__name__)


class StreamingChart:
    """Base class for real-time streaming charts."""

    def __init__(self, width: int = 800, height: int = 600, buffer_size: int = 1000):
        self.width = width
        self.height = height
        self.buffer_size = buffer_size

        # Streaming infrastructure
        self.coordinator = StreamingCoordinator()
        self.update_callbacks: List[Callable] = []
        self.auto_update = True
        self.update_interval = 0.1  # seconds

        # Threading
        self._lock = threading.RLock()
        self._update_thread: Optional[threading.Thread] = None
        self._stop_update = False

        # Performance tracking
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0.0

    def add_stream(self, stream_id: str, streamer):
        """Add a data stream to the chart."""
        self.coordinator.add_streamer(streamer)

        # Subscribe to updates
        def on_data_update(data_point: DataPoint):
            if self.auto_update:
                self._trigger_update()

        self.coordinator.subscribe_to_stream(stream_id, on_data_update)

    def on_update(self, callback: Callable):
        """Register update callback."""
        self.update_callbacks.append(callback)

    def _trigger_update(self):
        """Trigger chart update."""
        with self._lock:
            for callback in self.update_callbacks:
                try:
                    callback(self)
                except Exception as e:
                    logger.error(f"Error in update callback: {e}")

    async def start_streaming(self):
        """Start streaming mode."""
        await self.coordinator.start_all()

        if self.auto_update:
            self._start_update_thread()

    async def stop_streaming(self):
        """Stop streaming mode."""
        await self.coordinator.stop_all()
        self._stop_update_thread()

    def _start_update_thread(self):
        """Start background update thread."""
        if self._update_thread and self._update_thread.is_alive():
            return

        self._stop_update = False

        def update_loop():
            while not self._stop_update:
                start_time = time.time()

                try:
                    self._trigger_update()

                    # Update FPS
                    self.frame_count += 1
                    current_time = time.time()
                    if current_time - self.last_fps_time >= 1.0:
                        self.current_fps = self.frame_count / (current_time - self.last_fps_time)
                        self.frame_count = 0
                        self.last_fps_time = current_time

                except Exception as e:
                    logger.error(f"Error in update thread: {e}")

                # Frame rate limiting
                elapsed = time.time() - start_time
                sleep_time = max(0, self.update_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        self._update_thread = threading.Thread(target=update_loop, daemon=True)
        self._update_thread.start()

    def _stop_update_thread(self):
        """Stop background update thread."""
        self._stop_update = True
        if self._update_thread:
            self._update_thread.join(timeout=1.0)

    def get_stream_stats(self) -> Dict[str, Any]:
        """Get streaming statistics."""
        return {
            'fps': self.current_fps,
            'update_interval': self.update_interval,
            'auto_update': self.auto_update,
            'streams': self.coordinator.data_manager.get_all_stats()
        }


class RealtimeLineChart(StreamingChart):
    """Real-time line chart with streaming data."""

    def __init__(self, width: int = 800, height: int = 600, buffer_size: int = 1000):
        super().__init__(width, height, buffer_size)

        # Chart configuration
        self.line_colors: Dict[str, str] = {}
        self.line_styles: Dict[str, Dict] = {}
        self.time_window = 30.0  # seconds
        self.auto_scale = True

        # Canvas for rendering
        self.canvas = PureCanvas(width, height)
        self.canvas.set_viewport(0, self.time_window, -1, 1)

    def add_line_stream(self, stream_id: str, streamer, color: str = 'blue',
                       linewidth: float = 1.0, alpha: float = 1.0):
        """Add a line data stream."""
        self.add_stream(stream_id, streamer)
        self.line_colors[stream_id] = color
        self.line_styles[stream_id] = {
            'linewidth': linewidth,
            'alpha': alpha
        }

    def render_frame(self) -> PureCanvas:
        """Render current frame."""
        with self._lock:
            # Clear canvas
            self.canvas.clear()

            current_time = time.time()
            start_time = current_time - self.time_window

            # Auto-scale viewport
            if self.auto_scale:
                all_values = []
                for stream_id in self.line_colors.keys():
                    buffer = self.coordinator.get_stream(stream_id)
                    if buffer:
                        points = buffer.get_range(start_time, current_time)
                        values = [p.value for p in points if isinstance(p.value, (int, float))]
                        all_values.extend(values)

                if all_values:
                    y_min, y_max = min(all_values), max(all_values)
                    y_range = y_max - y_min
                    if y_range > 0:
                        y_min -= y_range * 0.1
                        y_max += y_range * 0.1
                        self.canvas.set_viewport(start_time, current_time, y_min, y_max)

            # Render each stream
            for stream_id, color in self.line_colors.items():
                buffer = self.coordinator.get_stream(stream_id)
                if not buffer:
                    continue

                points = buffer.get_range(start_time, current_time)
                if len(points) < 2:
                    continue

                # Extract time series data
                times = np.array([p.timestamp for p in points])
                values = np.array([p.value for p in points if isinstance(p.value, (int, float))])

                if len(times) != len(values):
                    continue

                # Set line style
                style = self.line_styles.get(stream_id, {})
                self.canvas.set_stroke_color(color)
                self.canvas.set_line_width(style.get('linewidth', 1.0))

                # Draw line
                line_points = list(zip(times, values))
                if len(line_points) >= 2:
                    self.canvas.draw_polyline(line_points)

            return self.canvas

    def save_frame(self, filename: str, dpi: int = 100):
        """Save current frame."""
        canvas = self.render_frame()
        canvas.save(filename, dpi)

    def set_time_window(self, seconds: float):
        """Set time window for display."""
        self.time_window = seconds

    def set_auto_scale(self, enabled: bool):
        """Enable/disable auto-scaling."""
        self.auto_scale = enabled


class RealtimeScatterChart(StreamingChart):
    """Real-time scatter plot with streaming data."""

    def __init__(self, width: int = 800, height: int = 600, buffer_size: int = 1000):
        super().__init__(width, height, buffer_size)

        # Chart configuration
        self.point_colors: Dict[str, str] = {}
        self.point_styles: Dict[str, Dict] = {}
        self.fade_mode = True  # Fade old points
        self.max_age = 10.0   # seconds

        # Canvas for rendering
        self.canvas = PureCanvas(width, height)
        self.canvas.set_viewport(-1, 1, -1, 1)

    def add_point_stream(self, stream_id: str, streamer, color: str = 'blue',
                        size: float = 3.0, alpha: float = 1.0):
        """Add a point data stream."""
        self.add_stream(stream_id, streamer)
        self.point_colors[stream_id] = color
        self.point_styles[stream_id] = {
            'size': size,
            'alpha': alpha
        }

    def render_frame(self) -> PureCanvas:
        """Render current frame."""
        with self._lock:
            # Clear canvas
            self.canvas.clear()

            current_time = time.time()

            # Auto-scale viewport
            all_x, all_y = [], []
            for stream_id in self.point_colors.keys():
                buffer = self.coordinator.get_stream(stream_id)
                if buffer:
                    points = buffer.get_window(self.max_age)
                    for point in points:
                        if isinstance(point.value, np.ndarray) and len(point.value) >= 2:
                            all_x.append(point.value[0])
                            all_y.append(point.value[1])

            if all_x and all_y:
                x_min, x_max = min(all_x), max(all_x)
                y_min, y_max = min(all_y), max(all_y)

                # Add padding
                x_range = x_max - x_min
                y_range = y_max - y_min
                if x_range > 0:
                    x_min -= x_range * 0.1
                    x_max += x_range * 0.1
                if y_range > 0:
                    y_min -= y_range * 0.1
                    y_max += y_range * 0.1

                self.canvas.set_viewport(x_min, x_max, y_min, y_max)

            # Render each stream
            for stream_id, color in self.point_colors.items():
                buffer = self.coordinator.get_stream(stream_id)
                if not buffer:
                    continue

                points = buffer.get_window(self.max_age)
                style = self.point_styles.get(stream_id, {})
                base_size = style.get('size', 3.0)

                # Draw points with optional fading
                for point in points:
                    if not isinstance(point.value, np.ndarray) or len(point.value) < 2:
                        continue

                    x, y = point.value[0], point.value[1]

                    # Calculate alpha based on age
                    age = current_time - point.timestamp
                    if self.fade_mode and self.max_age > 0:
                        alpha = max(0.1, 1.0 - (age / self.max_age))
                    else:
                        alpha = style.get('alpha', 1.0)

                    # Draw point
                    self.canvas.set_fill_color(Color.from_name(color))
                    point_size = base_size / 100.0  # Convert to canvas units
                    self.canvas.draw_circle(x, y, point_size, fill=True)

            return self.canvas

    def save_frame(self, filename: str, dpi: int = 100):
        """Save current frame."""
        canvas = self.render_frame()
        canvas.save(filename, dpi)

    def set_fade_mode(self, enabled: bool, max_age: float = 10.0):
        """Configure point fading."""
        self.fade_mode = enabled
        self.max_age = max_age


class StreamingAnalyticsChart(StreamingChart):
    """Real-time analytics dashboard with multiple visualizations."""

    def __init__(self, width: int = 1200, height: int = 800):
        super().__init__(width, height)

        # Create sub-charts
        self.line_chart = RealtimeLineChart(width//2, height//2)
        self.scatter_chart = RealtimeScatterChart(width//2, height//2)

        # Analytics
        self.statistics: Dict[str, Dict] = {}
        self.alerts: List[Dict] = []

        # Main canvas
        self.canvas = PureCanvas(width, height)

    def add_metric_stream(self, stream_id: str, streamer, chart_type: str = 'line',
                         **style_kwargs):
        """Add a metric stream to appropriate chart."""
        if chart_type == 'line':
            self.line_chart.add_line_stream(stream_id, streamer, **style_kwargs)
        elif chart_type == 'scatter':
            self.scatter_chart.add_point_stream(stream_id, streamer, **style_kwargs)

        # Initialize statistics
        self.statistics[stream_id] = {
            'count': 0,
            'mean': 0.0,
            'std': 0.0,
            'min': float('inf'),
            'max': float('-inf')
        }

        # Subscribe to updates for analytics
        def update_stats(data_point: DataPoint):
            self._update_statistics(stream_id, data_point)

        self.coordinator.subscribe_to_stream(stream_id, update_stats)

    def _update_statistics(self, stream_id: str, data_point: DataPoint):
        """Update running statistics."""
        if not isinstance(data_point.value, (int, float)):
            return

        stats = self.statistics[stream_id]
        value = data_point.value

        # Update running statistics
        stats['count'] += 1
        stats['min'] = min(stats['min'], value)
        stats['max'] = max(stats['max'], value)

        # Running mean and std (simplified)
        old_mean = stats['mean']
        stats['mean'] = old_mean + (value - old_mean) / stats['count']

        if stats['count'] > 1:
            # Simplified running standard deviation
            buffer = self.coordinator.get_stream(stream_id)
            if buffer:
                recent_values = [p.value for p in buffer.get_latest(100)
                               if isinstance(p.value, (int, float))]
                if len(recent_values) > 1:
                    stats['std'] = np.std(recent_values)

    def render_dashboard(self) -> PureCanvas:
        """Render complete analytics dashboard."""
        with self._lock:
            self.canvas.clear()

            # Render sub-charts
            line_canvas = self.line_chart.render_frame()
            scatter_canvas = self.scatter_chart.render_frame()

            # Composite layout (simplified - would need proper blending)
            # This is a placeholder for actual canvas composition

            # Add statistics overlay
            self._render_statistics_overlay()

            return self.canvas

    def _render_statistics_overlay(self):
        """Render statistics as text overlay."""
        y_offset = 0.9
        line_height = 0.05

        self.canvas.set_fill_color(Color.from_name('white'))

        for stream_id, stats in self.statistics.items():
            if stats['count'] > 0:
                text = f"{stream_id}: μ={stats['mean']:.2f}, σ={stats['std']:.2f}, n={stats['count']}"
                # Text rendering would be implemented in canvas
                y_offset -= line_height

    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics."""
        return {
            'statistics': self.statistics,
            'alerts': self.alerts,
            'streaming_stats': self.get_stream_stats()
        }