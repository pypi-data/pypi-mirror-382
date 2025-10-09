"""Real-time data streaming and chart updating capabilities."""

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
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Deque, Dict, List, Optional, Protocol, Union
import logging

import numpy as np

from .renderer import RenderEngine
from ..figure import VizlyFigure


logger = logging.getLogger(__name__)


class DataSource(Protocol):
    """Protocol for data sources that can provide streaming data."""

    def get_latest_data(self) -> Dict[str, np.ndarray]:
        """Get the most recent data."""
        ...

    def subscribe(self, callback: Callable[[Dict[str, np.ndarray]], None]) -> None:
        """Subscribe to data updates."""
        ...

    def unsubscribe(self, callback: Callable[[Dict[str, np.ndarray]], None]) -> None:
        """Unsubscribe from data updates."""
        ...


@dataclass
class StreamConfig:
    """Configuration for data streaming."""

    max_buffer_size: int = 10000
    update_frequency: float = 30.0  # Hz
    decimation_factor: int = 1
    auto_scale: bool = True
    smoothing_window: int = 1
    compression_enabled: bool = False
    batch_size: int = 100


class DataBuffer:
    """Efficient circular buffer for streaming data."""

    def __init__(self, max_size: int, columns: List[str]) -> None:
        self.max_size = max_size
        self.columns = columns
        self._data: Dict[str, Deque[float]] = {
            col: deque(maxlen=max_size) for col in columns
        }
        self._timestamps: Deque[float] = deque(maxlen=max_size)
        self._lock = threading.RLock()

    def append(
        self,
        data: Dict[str, Union[float, np.ndarray]],
        timestamp: Optional[float] = None,
    ) -> None:
        """Add new data point(s) to the buffer."""
        if timestamp is None:
            timestamp = time.time()

        with self._lock:
            # Handle single values or arrays
            if isinstance(next(iter(data.values())), (int, float)):
                # Single data point
                for col in self.columns:
                    if col in data:
                        self._data[col].append(float(data[col]))
                    else:
                        self._data[col].append(0.0)
                self._timestamps.append(timestamp)
            else:
                # Array of data points
                arrays = {col: np.asarray(data.get(col, [])) for col in self.columns}
                max_len = max(len(arr) for arr in arrays.values() if len(arr) > 0)

                for i in range(max_len):
                    for col in self.columns:
                        arr = arrays[col]
                        if i < len(arr):
                            self._data[col].append(float(arr[i]))
                        else:
                            self._data[col].append(0.0)
                    self._timestamps.append(timestamp + i * 0.001)  # Spread timestamps

    def get_data(
        self, start_idx: Optional[int] = None, end_idx: Optional[int] = None
    ) -> Dict[str, np.ndarray]:
        """Get data as numpy arrays."""
        with self._lock:
            result = {}
            for col in self.columns:
                data_list = list(self._data[col])
                if start_idx is not None or end_idx is not None:
                    data_list = data_list[start_idx:end_idx]
                result[col] = np.array(data_list)

            timestamps = list(self._timestamps)
            if start_idx is not None or end_idx is not None:
                timestamps = timestamps[start_idx:end_idx]
            result["timestamp"] = np.array(timestamps)

            return result

    def get_latest(self, n: int = 1) -> Dict[str, np.ndarray]:
        """Get the last n data points."""
        return self.get_data(start_idx=-n if n > 0 else None)

    def clear(self) -> None:
        """Clear all data from the buffer."""
        with self._lock:
            for col in self.columns:
                self._data[col].clear()
            self._timestamps.clear()

    def __len__(self) -> int:
        """Get the number of data points in the buffer."""
        return len(self._timestamps)


class DataStream:
    """Manages streaming data from various sources."""

    def __init__(self, config: Optional[StreamConfig] = None) -> None:
        self.config = config or StreamConfig()
        self._sources: List[DataSource] = []
        self._buffers: Dict[str, DataBuffer] = {}
        self._subscribers: List[Callable[[str, Dict[str, np.ndarray]], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None

    def add_source(self, name: str, source: DataSource, columns: List[str]) -> None:
        """Add a data source to the stream."""
        self._buffers[name] = DataBuffer(self.config.max_buffer_size, columns)
        self._sources.append(source)

        # Subscribe to source updates
        def on_data_update(data: Dict[str, np.ndarray]) -> None:
            self._buffers[name].append(data)
            self._notify_subscribers(name, data)

        source.subscribe(on_data_update)

    def _notify_subscribers(
        self, source_name: str, data: Dict[str, np.ndarray]
    ) -> None:
        """Notify all subscribers of new data."""
        for callback in self._subscribers:
            try:
                callback(source_name, data)
            except Exception as e:
                logger.error(f"Error in stream subscriber: {e}")

    def subscribe(self, callback: Callable[[str, Dict[str, np.ndarray]], None]) -> None:
        """Subscribe to stream updates."""
        self._subscribers.append(callback)

    def unsubscribe(
        self, callback: Callable[[str, Dict[str, np.ndarray]], None]
    ) -> None:
        """Unsubscribe from stream updates."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def get_buffer(self, name: str) -> Optional[DataBuffer]:
        """Get a named data buffer."""
        return self._buffers.get(name)

    def start_streaming(self) -> None:
        """Start the streaming process."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._stream_loop, daemon=True)
        self._thread.start()
        logger.info("Data streaming started")

    def stop_streaming(self) -> None:
        """Stop the streaming process."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        logger.info("Data streaming stopped")

    def _stream_loop(self) -> None:
        """Main streaming loop."""
        target_interval = 1.0 / self.config.update_frequency

        while self._running:
            loop_start = time.time()

            # Process any pending data updates
            # (Data updates happen via callbacks from sources)

            # Sleep to maintain target frequency
            elapsed = time.time() - loop_start
            sleep_time = target_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)


class RealTimeChart:
    """Chart that automatically updates with streaming data."""

    def __init__(
        self,
        figure: Optional[VizlyFigure] = None,
        stream: Optional[DataStream] = None,
        render_engine: Optional[RenderEngine] = None,
    ) -> None:
        self.figure = figure or VizlyFigure()
        self.stream = stream or DataStream()
        self.render_engine = render_engine

        self._chart_configs: Dict[str, Dict[str, Any]] = {}
        self._update_callbacks: List[Callable[[], None]] = []
        self._last_update = 0.0
        self._update_lock = threading.Lock()

        # Subscribe to stream updates
        self.stream.subscribe(self._on_stream_update)

    def add_line_series(
        self,
        source_name: str,
        x_column: str,
        y_column: str,
        label: Optional[str] = None,
        **plot_kwargs,
    ) -> None:
        """Add a line series that updates with streaming data."""
        config = {
            "type": "line",
            "source": source_name,
            "x_column": x_column,
            "y_column": y_column,
            "label": label or f"{source_name}_{y_column}",
            "plot_kwargs": plot_kwargs,
            "line_obj": None,
        }

        series_id = f"{source_name}_{x_column}_{y_column}"
        self._chart_configs[series_id] = config

    def add_scatter_series(
        self,
        source_name: str,
        x_column: str,
        y_column: str,
        label: Optional[str] = None,
        **plot_kwargs,
    ) -> None:
        """Add a scatter series that updates with streaming data."""
        config = {
            "type": "scatter",
            "source": source_name,
            "x_column": x_column,
            "y_column": y_column,
            "label": label or f"{source_name}_{y_column}",
            "plot_kwargs": plot_kwargs,
            "scatter_obj": None,
        }

        series_id = f"{source_name}_{x_column}_{y_column}_scatter"
        self._chart_configs[series_id] = config

    def _on_stream_update(self, source_name: str, data: Dict[str, np.ndarray]) -> None:
        """Handle incoming stream data."""
        current_time = time.time()

        # Rate limiting
        if current_time - self._last_update < 1.0 / 30.0:  # Max 30 FPS
            return

        with self._update_lock:
            self._update_charts()
            self._last_update = current_time

    def _update_charts(self) -> None:
        """Update all chart series with latest data."""
        for series_id, config in self._chart_configs.items():
            buffer = self.stream.get_buffer(config["source"])
            if not buffer or len(buffer) == 0:
                continue

            # Get latest data
            data = buffer.get_data()
            x_data = data.get(config["x_column"])
            y_data = data.get(config["y_column"])

            if x_data is None or y_data is None or len(x_data) == 0:
                continue

            # Update or create plot
            if config["type"] == "line":
                self._update_line_series(config, x_data, y_data)
            elif config["type"] == "scatter":
                self._update_scatter_series(config, x_data, y_data)

        # Trigger figure update
        if hasattr(self.figure.figure, "canvas") and self.figure.figure.canvas:
            self.figure.figure.canvas.draw_idle()

        # Call update callbacks
        for callback in self._update_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in update callback: {e}")

    def _update_line_series(
        self, config: Dict[str, Any], x_data: np.ndarray, y_data: np.ndarray
    ) -> None:
        """Update a line series."""
        if config["line_obj"] is None:
            # Create new line
            (line,) = self.figure.axes.plot(
                x_data, y_data, label=config["label"], **config["plot_kwargs"]
            )
            config["line_obj"] = line
        else:
            # Update existing line
            config["line_obj"].set_data(x_data, y_data)

        # Auto-scale if enabled
        if self.stream.config.auto_scale:
            self.figure.axes.relim()
            self.figure.axes.autoscale_view()

    def _update_scatter_series(
        self, config: Dict[str, Any], x_data: np.ndarray, y_data: np.ndarray
    ) -> None:
        """Update a scatter series."""
        if config["scatter_obj"] is None:
            # Create new scatter
            scatter = self.figure.axes.scatter(
                x_data, y_data, label=config["label"], **config["plot_kwargs"]
            )
            config["scatter_obj"] = scatter
        else:
            # Update existing scatter - this is more complex with matplotlib
            # For now, clear and redraw
            config["scatter_obj"].remove()
            scatter = self.figure.axes.scatter(
                x_data, y_data, label=config["label"], **config["plot_kwargs"]
            )
            config["scatter_obj"] = scatter

        # Auto-scale if enabled
        if self.stream.config.auto_scale:
            self.figure.axes.relim()
            self.figure.axes.autoscale_view()

    def add_update_callback(self, callback: Callable[[], None]) -> None:
        """Add a callback that gets called on every chart update."""
        self._update_callbacks.append(callback)

    def remove_update_callback(self, callback: Callable[[], None]) -> None:
        """Remove an update callback."""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)

    def start(self) -> None:
        """Start real-time updating."""
        self.stream.start_streaming()

    def stop(self) -> None:
        """Stop real-time updating."""
        self.stream.stop_streaming()

    def clear_all_series(self) -> None:
        """Clear all chart series."""
        for config in self._chart_configs.values():
            if config.get("line_obj"):
                config["line_obj"].remove()
            if config.get("scatter_obj"):
                config["scatter_obj"].remove()

        self._chart_configs.clear()
        self.figure.axes.clear()


# Example data sources for common use cases


class RandomDataSource:
    """Example data source that generates random data."""

    def __init__(self, frequency: float = 1.0) -> None:
        self.frequency = frequency
        self._callbacks: List[Callable[[Dict[str, np.ndarray]], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def get_latest_data(self) -> Dict[str, np.ndarray]:
        """Generate random data point."""
        return {
            "x": np.array([time.time()]),
            "y": np.array([np.random.randn()]),
            "z": np.array([np.random.randn()]),
        }

    def subscribe(self, callback: Callable[[Dict[str, np.ndarray]], None]) -> None:
        """Subscribe to updates."""
        self._callbacks.append(callback)
        if not self._running:
            self._start_generation()

    def unsubscribe(self, callback: Callable[[Dict[str, np.ndarray]], None]) -> None:
        """Unsubscribe from updates."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

        if len(self._callbacks) == 0 and self._running:
            self._stop_generation()

    def _start_generation(self) -> None:
        """Start generating data."""
        self._running = True
        self._thread = threading.Thread(target=self._generate_loop, daemon=True)
        self._thread.start()

    def _stop_generation(self) -> None:
        """Stop generating data."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _generate_loop(self) -> None:
        """Main data generation loop."""
        interval = 1.0 / self.frequency

        while self._running:
            data = self.get_latest_data()
            for callback in self._callbacks:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in data source callback: {e}")

            time.sleep(interval)


class CSVDataSource:
    """Data source that reads from CSV files in real-time."""

    def __init__(
        self, file_path: str, columns: List[str], poll_interval: float = 1.0
    ) -> None:
        self.file_path = file_path
        self.columns = columns
        self.poll_interval = poll_interval
        self._callbacks: List[Callable[[Dict[str, np.ndarray]], None]] = []
        self._last_position = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def get_latest_data(self) -> Dict[str, np.ndarray]:
        """Read new data from CSV file."""
        import pandas as pd

        try:
            # Read only new lines since last read
            df = pd.read_csv(self.file_path, skiprows=self._last_position, nrows=1000)
            self._last_position += len(df)

            result = {}
            for col in self.columns:
                if col in df.columns:
                    result[col] = df[col].values
                else:
                    result[col] = np.array([])

            return result
        except Exception as e:
            logger.error(f"Error reading CSV data: {e}")
            return {col: np.array([]) for col in self.columns}

    def subscribe(self, callback: Callable[[Dict[str, np.ndarray]], None]) -> None:
        """Subscribe to file updates."""
        self._callbacks.append(callback)
        if not self._running:
            self._start_polling()

    def unsubscribe(self, callback: Callable[[Dict[str, np.ndarray]], None]) -> None:
        """Unsubscribe from file updates."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

        if len(self._callbacks) == 0 and self._running:
            self._stop_polling()

    def _start_polling(self) -> None:
        """Start polling the file."""
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _stop_polling(self) -> None:
        """Stop polling the file."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)

    def _poll_loop(self) -> None:
        """Main file polling loop."""
        while self._running:
            data = self.get_latest_data()
            if any(len(arr) > 0 for arr in data.values()):
                for callback in self._callbacks:
                    try:
                        callback(data)
                    except Exception as e:
                        logger.error(f"Error in CSV source callback: {e}")

            time.sleep(self.poll_interval)
