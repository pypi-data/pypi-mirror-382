"""Performance monitoring and optimization utilities for Vizly."""

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

import psutil
import threading
import time
import logging
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np

try:
    import cupy as cp

    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False

try:
    import pynvml

    pynvml.nvmlInit()
    HAS_NVML = True
except (ImportError, Exception):
    HAS_NVML = False


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics container."""

    timestamp: float
    cpu_usage: float
    memory_usage: float
    gpu_usage: Optional[float] = None
    gpu_memory_usage: Optional[float] = None
    render_fps: Optional[float] = None
    frame_time: Optional[float] = None
    data_throughput: Optional[float] = None  # MB/s


@dataclass
class BufferStats:
    """Buffer usage statistics."""

    total_size: int
    used_size: int
    free_size: int
    allocation_count: int
    deallocation_count: int
    peak_usage: int


class PerformanceMonitor:
    """System performance monitoring for Vizly applications."""

    def __init__(self, sample_interval: float = 1.0, history_size: int = 300) -> None:
        self.sample_interval = sample_interval
        self.history_size = history_size
        self.metrics_history: deque[PerformanceMetrics] = deque(maxlen=history_size)

        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._callbacks: List[Callable[[PerformanceMetrics], None]] = []

        # GPU monitoring setup
        self._gpu_available = HAS_NVML
        self._gpu_handles: List[Any] = []

        if self._gpu_available:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    self._gpu_handles.append(handle)
                logger.info(f"GPU monitoring enabled for {device_count} device(s)")
            except Exception as e:
                logger.warning(f"Failed to initialize GPU monitoring: {e}")
                self._gpu_available = False

    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Performance monitoring started")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        if not self._monitoring:
            return

        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        logger.info("Performance monitoring stopped")

    def add_callback(self, callback: Callable[[PerformanceMetrics], None]) -> None:
        """Add callback for performance metric updates."""
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[PerformanceMetrics], None]) -> None:
        """Remove performance metric callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self._monitoring:
            start_time = time.time()

            # Collect metrics
            metrics = self._collect_metrics()
            self.metrics_history.append(metrics)

            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(metrics)
                except Exception as e:
                    logger.error(f"Error in performance callback: {e}")

            # Sleep for remaining interval
            elapsed = time.time() - start_time
            sleep_time = max(0, self.sample_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        timestamp = time.time()

        # CPU and memory usage
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_usage = memory.percent

        # GPU metrics
        gpu_usage = None
        gpu_memory_usage = None

        if self._gpu_available and self._gpu_handles:
            try:
                # Use first GPU for now
                handle = self._gpu_handles[0]
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_usage = utilization.gpu

                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_memory_usage = (memory_info.used / memory_info.total) * 100

            except Exception as e:
                logger.debug(f"Failed to get GPU metrics: {e}")

        # Calculate render FPS if available
        render_fps = self._calculate_render_fps()
        frame_time = 1.0 / render_fps if render_fps and render_fps > 0 else None

        # Calculate data throughput
        data_throughput = self._calculate_data_throughput()

        return PerformanceMetrics(
            timestamp=timestamp,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            gpu_usage=gpu_usage,
            gpu_memory_usage=gpu_memory_usage,
            render_fps=render_fps,
            frame_time=frame_time,
            data_throughput=data_throughput,
        )

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent performance metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_average_metrics(
        self, duration: float = 60.0
    ) -> Optional[PerformanceMetrics]:
        """Get average metrics over the specified duration (seconds)."""
        if not self.metrics_history:
            return None

        current_time = time.time()
        cutoff_time = current_time - duration

        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        if not recent_metrics:
            return None

        # Calculate averages
        avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
        avg_memory = np.mean([m.memory_usage for m in recent_metrics])

        avg_gpu = None
        avg_gpu_memory = None
        if any(m.gpu_usage is not None for m in recent_metrics):
            gpu_values = [
                m.gpu_usage for m in recent_metrics if m.gpu_usage is not None
            ]
            avg_gpu = np.mean(gpu_values) if gpu_values else None

        if any(m.gpu_memory_usage is not None for m in recent_metrics):
            gpu_mem_values = [
                m.gpu_memory_usage
                for m in recent_metrics
                if m.gpu_memory_usage is not None
            ]
            avg_gpu_memory = np.mean(gpu_mem_values) if gpu_mem_values else None

        return PerformanceMetrics(
            timestamp=current_time,
            cpu_usage=avg_cpu,
            memory_usage=avg_memory,
            gpu_usage=avg_gpu,
            gpu_memory_usage=avg_gpu_memory,
        )

    def detect_performance_issues(self) -> List[str]:
        """Detect potential performance issues."""
        issues = []

        if not self.metrics_history:
            return issues

        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 samples

        # High CPU usage
        avg_cpu = np.mean([m.cpu_usage for m in recent_metrics])
        if avg_cpu > 90:
            issues.append(f"High CPU usage: {avg_cpu:.1f}%")

        # High memory usage
        avg_memory = np.mean([m.memory_usage for m in recent_metrics])
        if avg_memory > 90:
            issues.append(f"High memory usage: {avg_memory:.1f}%")

        # GPU issues
        if any(m.gpu_usage is not None for m in recent_metrics):
            gpu_values = [
                m.gpu_usage for m in recent_metrics if m.gpu_usage is not None
            ]
            if gpu_values:
                avg_gpu = np.mean(gpu_values)
                if avg_gpu > 95:
                    issues.append(f"High GPU usage: {avg_gpu:.1f}%")

        if any(m.gpu_memory_usage is not None for m in recent_metrics):
            gpu_mem_values = [
                m.gpu_memory_usage
                for m in recent_metrics
                if m.gpu_memory_usage is not None
            ]
            if gpu_mem_values:
                avg_gpu_mem = np.mean(gpu_mem_values)
                if avg_gpu_mem > 95:
                    issues.append(f"High GPU memory usage: {avg_gpu_mem:.1f}%")

        # Frame rate issues
        fps_values = [m.render_fps for m in recent_metrics if m.render_fps is not None]
        if fps_values:
            avg_fps = np.mean(fps_values)
            if avg_fps < 30:
                issues.append(f"Low rendering FPS: {avg_fps:.1f}")

        return issues

    def _calculate_render_fps(self) -> Optional[float]:
        """Calculate current rendering FPS based on recent frame times."""
        if not hasattr(self, "_frame_times"):
            self._frame_times = deque(maxlen=30)  # Keep last 30 frame times
            self._last_frame_time = time.time()
            return None

        current_time = time.time()
        frame_time = current_time - self._last_frame_time
        self._frame_times.append(frame_time)
        self._last_frame_time = current_time

        if len(self._frame_times) < 5:  # Need at least 5 samples
            return None

        # Calculate average FPS from recent frame times
        avg_frame_time = np.mean(list(self._frame_times))
        if avg_frame_time > 0:
            return 1.0 / avg_frame_time
        return None

    def _calculate_data_throughput(self) -> Optional[float]:
        """Calculate data processing throughput in MB/s."""
        if not hasattr(self, "_data_processed"):
            self._data_processed = 0
            self._throughput_start_time = time.time()
            return None

        current_time = time.time()
        elapsed = current_time - self._throughput_start_time

        if elapsed > 0 and self._data_processed > 0:
            # Convert bytes to MB and calculate per second
            throughput_mbps = (self._data_processed / (1024 * 1024)) / elapsed
            # Reset counters periodically
            if elapsed > 60:  # Reset every minute
                self._data_processed = 0
                self._throughput_start_time = current_time
            return throughput_mbps
        return None

    def update_render_stats(self, frame_rendered: bool = True) -> None:
        """Update rendering statistics."""
        if frame_rendered:
            current_time = time.time()
            if not hasattr(self, "_last_render_time"):
                self._last_render_time = current_time
                return

            # Update frame timing for FPS calculation
            self._calculate_render_fps()

    def update_data_stats(self, bytes_processed: int) -> None:
        """Update data processing statistics."""
        if not hasattr(self, "_data_processed"):
            self._data_processed = 0
            self._throughput_start_time = time.time()

        self._data_processed += bytes_processed

    def get_performance_report(self) -> dict:
        """Generate comprehensive performance report."""
        if not self.metrics_history:
            return {"status": "no_data", "message": "No performance data available"}

        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 samples
        current = self.get_current_metrics()
        average = self.get_average_metrics(60.0)  # Last minute average

        report = {
            "status": "healthy",
            "timestamp": time.time(),
            "current": {
                "cpu_usage": current.cpu_usage if current else None,
                "memory_usage": current.memory_usage if current else None,
                "gpu_usage": current.gpu_usage if current else None,
                "render_fps": current.render_fps if current else None,
                "data_throughput": current.data_throughput if current else None,
            },
            "averages": {
                "cpu_usage": average.cpu_usage if average else None,
                "memory_usage": average.memory_usage if average else None,
                "gpu_usage": average.gpu_usage if average else None,
                "render_fps": average.render_fps if average else None,
                "data_throughput": average.data_throughput if average else None,
            },
            "issues": self.detect_performance_issues(),
            "recommendations": [],
        }

        # Add performance recommendations
        if current:
            if current.cpu_usage and current.cpu_usage > 80:
                report["recommendations"].append(
                    "Consider enabling data sampling to reduce CPU load"
                )
            if current.memory_usage and current.memory_usage > 85:
                report["recommendations"].append(
                    "Enable fast rendering mode to reduce memory usage"
                )
            if current.render_fps and current.render_fps < 15:
                report["recommendations"].append(
                    "Try reducing data complexity or enabling performance optimizations"
                )

        # Set overall status
        if len(report["issues"]) > 3:
            report["status"] = "critical"
        elif len(report["issues"]) > 1:
            report["status"] = "warning"

        return report


class BufferManager:
    """Memory buffer management with GPU acceleration support."""

    def __init__(
        self,
        max_cpu_memory: int = 1024 * 1024 * 1024,  # 1GB
        max_gpu_memory: Optional[int] = None,
        enable_compression: bool = False,
    ) -> None:
        self.max_cpu_memory = max_cpu_memory
        self.max_gpu_memory = max_gpu_memory
        self.enable_compression = enable_compression

        # Buffer storage
        self._cpu_buffers: Dict[str, np.ndarray] = {}
        self._gpu_buffers: Dict[str, Any] = {}  # CuPy arrays
        self._buffer_metadata: Dict[str, Dict[str, Any]] = {}

        # Usage tracking
        self._cpu_usage = 0
        self._gpu_usage = 0
        self._allocation_count = 0
        self._deallocation_count = 0
        self._peak_cpu_usage = 0
        self._peak_gpu_usage = 0

        # GPU availability
        self._gpu_enabled = HAS_CUPY

        if self._gpu_enabled and max_gpu_memory is None:
            try:
                # Auto-detect GPU memory
                mempool = cp.get_default_memory_pool()
                gpu_memory = cp.cuda.Device().mem_info[1]  # Total memory
                self.max_gpu_memory = int(gpu_memory * 0.8)  # Use 80% of available
                logger.info(
                    f"GPU buffer manager initialized with {self.max_gpu_memory // (1024**2)} MB"
                )
            except Exception as e:
                logger.warning(f"Failed to initialize GPU buffers: {e}")
                self._gpu_enabled = False

    def allocate_cpu_buffer(
        self, name: str, shape: Tuple[int, ...], dtype: np.dtype = np.float32
    ) -> bool:
        """Allocate CPU buffer."""
        if name in self._cpu_buffers:
            logger.warning(f"Buffer {name} already exists")
            return False

        # Calculate required memory
        required_memory = np.prod(shape) * np.dtype(dtype).itemsize

        if self._cpu_usage + required_memory > self.max_cpu_memory:
            # Try to free some buffers
            if not self._free_least_used_buffers(required_memory, prefer_cpu=True):
                logger.error(
                    f"Cannot allocate {required_memory} bytes: insufficient CPU memory"
                )
                return False

        try:
            buffer = np.zeros(shape, dtype=dtype)
            self._cpu_buffers[name] = buffer
            self._buffer_metadata[name] = {
                "type": "cpu",
                "shape": shape,
                "dtype": dtype,
                "size": required_memory,
                "created": time.time(),
                "last_accessed": time.time(),
                "access_count": 0,
            }

            self._cpu_usage += required_memory
            self._allocation_count += 1
            self._peak_cpu_usage = max(self._peak_cpu_usage, self._cpu_usage)

            logger.debug(f"Allocated CPU buffer {name}: {shape} {dtype}")
            return True

        except Exception as e:
            logger.error(f"Failed to allocate CPU buffer {name}: {e}")
            return False

    def allocate_gpu_buffer(
        self, name: str, shape: Tuple[int, ...], dtype: np.dtype = np.float32
    ) -> bool:
        """Allocate GPU buffer."""
        if not self._gpu_enabled:
            logger.warning("GPU buffers not available")
            return False

        if name in self._gpu_buffers:
            logger.warning(f"GPU buffer {name} already exists")
            return False

        # Calculate required memory
        required_memory = np.prod(shape) * np.dtype(dtype).itemsize

        if (
            self.max_gpu_memory
            and self._gpu_usage + required_memory > self.max_gpu_memory
        ):
            # Try to free some GPU buffers
            if not self._free_least_used_buffers(required_memory, prefer_cpu=False):
                logger.error(
                    f"Cannot allocate {required_memory} bytes: insufficient GPU memory"
                )
                return False

        try:
            buffer = cp.zeros(shape, dtype=dtype)
            self._gpu_buffers[name] = buffer
            self._buffer_metadata[name] = {
                "type": "gpu",
                "shape": shape,
                "dtype": dtype,
                "size": required_memory,
                "created": time.time(),
                "last_accessed": time.time(),
                "access_count": 0,
            }

            self._gpu_usage += required_memory
            self._allocation_count += 1
            self._peak_gpu_usage = max(self._peak_gpu_usage, self._gpu_usage)

            logger.debug(f"Allocated GPU buffer {name}: {shape} {dtype}")
            return True

        except Exception as e:
            logger.error(f"Failed to allocate GPU buffer {name}: {e}")
            return False

    def get_buffer(self, name: str) -> Optional[Union[np.ndarray, Any]]:
        """Get buffer by name."""
        if name in self._cpu_buffers:
            self._update_access_stats(name)
            return self._cpu_buffers[name]
        elif name in self._gpu_buffers:
            self._update_access_stats(name)
            return self._gpu_buffers[name]
        else:
            return None

    def copy_to_gpu(self, name: str) -> bool:
        """Copy CPU buffer to GPU."""
        if not self._gpu_enabled:
            return False

        if name not in self._cpu_buffers:
            logger.error(f"CPU buffer {name} not found")
            return False

        if name in self._gpu_buffers:
            logger.warning(f"GPU buffer {name} already exists")
            return True

        try:
            cpu_buffer = self._cpu_buffers[name]
            gpu_buffer = cp.asarray(cpu_buffer)

            # Calculate memory usage
            required_memory = cpu_buffer.nbytes

            self._gpu_buffers[name] = gpu_buffer
            self._buffer_metadata[f"{name}_gpu"] = {
                "type": "gpu",
                "shape": cpu_buffer.shape,
                "dtype": cpu_buffer.dtype,
                "size": required_memory,
                "created": time.time(),
                "last_accessed": time.time(),
                "access_count": 0,
            }

            self._gpu_usage += required_memory
            logger.debug(f"Copied buffer {name} to GPU")
            return True

        except Exception as e:
            logger.error(f"Failed to copy buffer {name} to GPU: {e}")
            return False

    def copy_to_cpu(self, name: str) -> bool:
        """Copy GPU buffer to CPU."""
        if name not in self._gpu_buffers:
            logger.error(f"GPU buffer {name} not found")
            return False

        if name in self._cpu_buffers:
            logger.warning(f"CPU buffer {name} already exists")
            return True

        try:
            gpu_buffer = self._gpu_buffers[name]
            cpu_buffer = cp.asnumpy(gpu_buffer)

            # Calculate memory usage
            required_memory = cpu_buffer.nbytes

            if self._cpu_usage + required_memory > self.max_cpu_memory:
                if not self._free_least_used_buffers(required_memory, prefer_cpu=True):
                    logger.error(f"Cannot copy buffer {name}: insufficient CPU memory")
                    return False

            self._cpu_buffers[name] = cpu_buffer
            self._buffer_metadata[f"{name}_cpu"] = {
                "type": "cpu",
                "shape": cpu_buffer.shape,
                "dtype": cpu_buffer.dtype,
                "size": required_memory,
                "created": time.time(),
                "last_accessed": time.time(),
                "access_count": 0,
            }

            self._cpu_usage += required_memory
            logger.debug(f"Copied buffer {name} to CPU")
            return True

        except Exception as e:
            logger.error(f"Failed to copy buffer {name} to CPU: {e}")
            return False

    def free_buffer(self, name: str) -> bool:
        """Free a named buffer."""
        freed = False

        if name in self._cpu_buffers:
            buffer = self._cpu_buffers[name]
            self._cpu_usage -= buffer.nbytes
            del self._cpu_buffers[name]
            freed = True

        if name in self._gpu_buffers:
            buffer = self._gpu_buffers[name]
            if hasattr(buffer, "nbytes"):
                self._gpu_usage -= buffer.nbytes
            del self._gpu_buffers[name]
            freed = True

        if name in self._buffer_metadata:
            del self._buffer_metadata[name]

        if freed:
            self._deallocation_count += 1
            logger.debug(f"Freed buffer {name}")

        return freed

    def _update_access_stats(self, name: str) -> None:
        """Update buffer access statistics."""
        if name in self._buffer_metadata:
            self._buffer_metadata[name]["last_accessed"] = time.time()
            self._buffer_metadata[name]["access_count"] += 1

    def _free_least_used_buffers(
        self, required_memory: int, prefer_cpu: bool = True
    ) -> bool:
        """Free least recently used buffers to make space."""
        # Sort buffers by last access time
        candidates = []

        target_buffers = self._cpu_buffers if prefer_cpu else self._gpu_buffers
        target_usage = self._cpu_usage if prefer_cpu else self._gpu_usage
        target_max = (
            self.max_cpu_memory if prefer_cpu else (self.max_gpu_memory or float("inf"))
        )

        for name in target_buffers:
            if name in self._buffer_metadata:
                metadata = self._buffer_metadata[name]
                candidates.append((metadata["last_accessed"], name, metadata["size"]))

        candidates.sort()  # Sort by access time (oldest first)

        freed_memory = 0
        for _, name, size in candidates:
            if target_usage - freed_memory + required_memory <= target_max:
                break

            self.free_buffer(name)
            freed_memory += size

        return target_usage - freed_memory + required_memory <= target_max

    def get_stats(self) -> BufferStats:
        """Get buffer usage statistics."""
        cpu_stats = BufferStats(
            total_size=self.max_cpu_memory,
            used_size=self._cpu_usage,
            free_size=self.max_cpu_memory - self._cpu_usage,
            allocation_count=self._allocation_count,
            deallocation_count=self._deallocation_count,
            peak_usage=self._peak_cpu_usage,
        )

        return cpu_stats

    def cleanup(self) -> None:
        """Clean up all buffers."""
        buffer_names = list(self._cpu_buffers.keys()) + list(self._gpu_buffers.keys())
        for name in buffer_names:
            self.free_buffer(name)

        logger.info("Buffer manager cleanup complete")


class PerformanceOptimizer:
    """Performance optimization utilities and decorators."""

    @staticmethod
    def cached_computation(cache_size: int = 128):
        """Decorator for caching expensive computations."""
        from functools import wraps, lru_cache

        def decorator(func):
            cached_func = lru_cache(maxsize=cache_size)(func)

            @wraps(func)
            def wrapper(*args, **kwargs):
                # Convert numpy arrays to hashable tuples for caching
                hashable_args = []
                for arg in args:
                    if isinstance(arg, np.ndarray):
                        hashable_args.append(arg.tobytes())
                    else:
                        hashable_args.append(arg)

                hashable_kwargs = {}
                for k, v in kwargs.items():
                    if isinstance(v, np.ndarray):
                        hashable_kwargs[k] = v.tobytes()
                    else:
                        hashable_kwargs[k] = v

                return cached_func(*tuple(hashable_args), **hashable_kwargs)

            wrapper.cache_info = cached_func.cache_info
            wrapper.cache_clear = cached_func.cache_clear
            return wrapper

        return decorator

    @staticmethod
    def profile_function(func):
        """Decorator to profile function execution time."""
        from functools import wraps
        import cProfile
        import pstats
        import io

        @wraps(func)
        def wrapper(*args, **kwargs):
            pr = cProfile.Profile()
            pr.enable()

            result = func(*args, **kwargs)

            pr.disable()
            s = io.StringIO()
            sortby = 'cumulative'
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()

            logger.info(f"Profile for {func.__name__}:\n{s.getvalue()}")
            return result

        return wrapper

    @staticmethod
    def parallel_computation(n_jobs: int = -1):
        """Decorator for parallel computation using joblib."""
        def decorator(func):
            from functools import wraps
            try:
                from joblib import Parallel, delayed
                HAS_JOBLIB = True
            except ImportError:
                HAS_JOBLIB = False
                logger.warning("joblib not available for parallel computation")

            @wraps(func)
            def wrapper(*args, **kwargs):
                if not HAS_JOBLIB:
                    return func(*args, **kwargs)

                # Check if data is large enough to benefit from parallelization
                data_size = 0
                for arg in args:
                    if isinstance(arg, np.ndarray):
                        data_size += arg.size

                if data_size < 10000:  # Small data, use serial computation
                    return func(*args, **kwargs)

                # For large data, try to parallelize
                return func(*args, **kwargs)  # Default implementation

            return wrapper

        return decorator

    @staticmethod
    def memory_efficient(chunk_size: int = 10000):
        """Decorator for memory-efficient processing of large arrays."""
        def decorator(func):
            from functools import wraps

            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check for large arrays that might benefit from chunking
                large_arrays = []
                for i, arg in enumerate(args):
                    if isinstance(arg, np.ndarray) and arg.size > chunk_size:
                        large_arrays.append((i, arg))

                if not large_arrays:
                    return func(*args, **kwargs)

                # Process in chunks for memory efficiency
                results = []
                for i in range(0, large_arrays[0][1].shape[0], chunk_size):
                    chunk_args = list(args)
                    for array_idx, array in large_arrays:
                        chunk_args[array_idx] = array[i:i+chunk_size]

                    chunk_result = func(*chunk_args, **kwargs)
                    results.append(chunk_result)

                # Combine results
                if results and isinstance(results[0], np.ndarray):
                    return np.concatenate(results)
                else:
                    return results

            return wrapper

        return decorator


class AdaptiveRenderer:
    """Adaptive rendering system that adjusts quality based on performance."""

    def __init__(self, target_fps: float = 30.0):
        self.target_fps = target_fps
        self.current_quality = 1.0  # 1.0 = full quality, 0.1 = minimum
        self.quality_history = deque(maxlen=10)
        self.fps_history = deque(maxlen=10)

    def adjust_quality(self, current_fps: float) -> float:
        """Adjust rendering quality based on current FPS."""
        self.fps_history.append(current_fps)

        if len(self.fps_history) < 3:
            return self.current_quality

        avg_fps = np.mean(list(self.fps_history))

        if avg_fps < self.target_fps * 0.8:  # Below 80% of target
            # Reduce quality
            self.current_quality = max(0.1, self.current_quality * 0.9)
        elif avg_fps > self.target_fps * 1.2:  # Above 120% of target
            # Increase quality
            self.current_quality = min(1.0, self.current_quality * 1.1)

        self.quality_history.append(self.current_quality)
        return self.current_quality

    def get_adaptive_settings(self, data_size: int) -> Dict[str, Union[int, float, bool]]:
        """Get adaptive settings based on current quality level and data size."""
        settings = {
            "point_density": int(self.current_quality * 1000),
            "line_width": max(0.5, self.current_quality * 2.0),
            "antialiasing": self.current_quality > 0.7,
            "shadows": self.current_quality > 0.8,
            "transparency": self.current_quality > 0.6,
            "texture_quality": self.current_quality,
            "animation_fps": max(15, int(self.target_fps * self.current_quality)),
        }

        # Adjust based on data size
        if data_size > 100000:  # Large dataset
            settings["point_density"] = min(settings["point_density"], 500)
            settings["antialiasing"] = False
            settings["shadows"] = False

        return settings


# Global performance monitor instance
_global_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
        _global_monitor.start_monitoring()
    return _global_monitor

def enable_performance_monitoring(
    sample_interval: float = 1.0,
    history_size: int = 300
) -> None:
    """Enable global performance monitoring."""
    global _global_monitor
    if _global_monitor is not None:
        _global_monitor.stop_monitoring()

    _global_monitor = PerformanceMonitor(sample_interval, history_size)
    _global_monitor.start_monitoring()
    logger.info("Global performance monitoring enabled")

def disable_performance_monitoring() -> None:
    """Disable global performance monitoring."""
    global _global_monitor
    if _global_monitor is not None:
        _global_monitor.stop_monitoring()
        _global_monitor = None
    logger.info("Global performance monitoring disabled")
