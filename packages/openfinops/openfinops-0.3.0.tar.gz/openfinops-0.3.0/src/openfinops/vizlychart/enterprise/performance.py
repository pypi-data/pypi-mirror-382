"""
Enterprise Performance & Scalability Engine
===========================================

High-performance distributed computing and GPU acceleration for massive
enterprise datasets and real-time visualization requirements.
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
import multiprocessing
import threading
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import warnings
import queue

import numpy as np

# Optional high-performance computing dependencies
try:
    import dask
    import dask.dataframe as dd
    from dask.distributed import Client, as_completed
    HAS_DASK = True
except ImportError:
    HAS_DASK = False

try:
    import cupy as cp
    import cudf
    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False

try:
    import ray
    HAS_RAY = True
except ImportError:
    HAS_RAY = False

from ..core.performance import PerformanceMonitor, BufferManager


@dataclass
class ComputeClusterConfig:
    """Configuration for distributed compute cluster."""
    cluster_type: str = "local"  # local, dask, ray, spark
    worker_count: int = multiprocessing.cpu_count()
    memory_per_worker: str = "4GB"
    gpu_enabled: bool = False
    scheduler_address: Optional[str] = None
    worker_timeout: int = 300  # seconds


@dataclass
class RenderingJob:
    """High-performance rendering job specification."""
    job_id: str
    data_source: Any
    visualization_spec: Dict[str, Any]
    priority: int = 5  # 1-10, higher is more urgent
    estimated_points: int = 0
    requires_gpu: bool = False
    callback: Optional[Callable] = None
    created_at: float = field(default_factory=time.time)


class DistributedDataEngine:
    """
    Enterprise-grade distributed data processing engine for massive datasets.

    Supports multiple compute backends:
    - Dask for distributed computing
    - Ray for ML workloads
    - Native multiprocessing for simple parallelization
    - GPU acceleration with CuPy
    """

    def __init__(self, config: ComputeClusterConfig):
        self.config = config
        self.client: Optional[Any] = None
        self.performance_monitor = PerformanceMonitor()
        self.buffer_manager = BufferManager(
            max_cpu_memory=8 * 1024 * 1024 * 1024,  # 8GB
            max_gpu_memory=4 * 1024 * 1024 * 1024   # 4GB
        )
        self.active_jobs: Dict[str, RenderingJob] = {}
        self.job_queue = queue.PriorityQueue()

        self._initialize_cluster()

    def _initialize_cluster(self) -> None:
        """Initialize distributed computing cluster."""
        if self.config.cluster_type == "dask" and HAS_DASK:
            self._initialize_dask_cluster()
        elif self.config.cluster_type == "ray" and HAS_RAY:
            self._initialize_ray_cluster()
        elif self.config.cluster_type == "local":
            self._initialize_local_cluster()
        else:
            warnings.warn(f"Cluster type '{self.config.cluster_type}' not available, using local")
            self._initialize_local_cluster()

    def _initialize_dask_cluster(self) -> None:
        """Initialize Dask distributed cluster."""
        try:
            if self.config.scheduler_address:
                self.client = Client(self.config.scheduler_address)
            else:
                # Create local cluster
                from dask.distributed import LocalCluster
                cluster = LocalCluster(
                    n_workers=self.config.worker_count,
                    threads_per_worker=2,
                    memory_limit=self.config.memory_per_worker
                )
                self.client = Client(cluster)

            print(f"Dask cluster initialized: {self.client}")
        except Exception as e:
            warnings.warn(f"Failed to initialize Dask cluster: {e}")
            self._initialize_local_cluster()

    def _initialize_ray_cluster(self) -> None:
        """Initialize Ray cluster for ML workloads."""
        try:
            if self.config.scheduler_address:
                ray.init(address=self.config.scheduler_address)
            else:
                ray.init(
                    num_cpus=self.config.worker_count,
                    object_store_memory=2 * 1024 * 1024 * 1024  # 2GB
                )

            self.client = ray
            print(f"Ray cluster initialized with {self.config.worker_count} workers")
        except Exception as e:
            warnings.warn(f"Failed to initialize Ray cluster: {e}")
            self._initialize_local_cluster()

    def _initialize_local_cluster(self) -> None:
        """Initialize local multiprocessing cluster."""
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.worker_count)
        self.process_pool = ProcessPoolExecutor(max_workers=self.config.worker_count)
        print(f"Local cluster initialized with {self.config.worker_count} workers")

    def submit_rendering_job(self, job: RenderingJob) -> str:
        """Submit high-priority rendering job to cluster."""
        self.active_jobs[job.job_id] = job

        # Add to priority queue (negative priority for max-heap behavior)
        self.job_queue.put((-job.priority, job.created_at, job.job_id))

        return job.job_id

    def process_massive_dataset(self, data_source: Any, chunk_size: int = 100_000) -> Any:
        """
        Process massive datasets using distributed computing.
        """
        if self.config.cluster_type == "dask" and self.client:
            return self._process_with_dask(data_source, chunk_size)
        elif self.config.cluster_type == "ray" and self.client:
            return self._process_with_ray(data_source, chunk_size)
        else:
            return self._process_with_multiprocessing(data_source, chunk_size)

    def _process_with_dask(self, data_source: Any, chunk_size: int) -> Any:
        """Process data using Dask distributed computing."""
        try:
            # Convert to Dask DataFrame for distributed processing
            if isinstance(data_source, np.ndarray):
                # Create Dask array from NumPy array
                dask_array = dask.array.from_array(data_source, chunks=(chunk_size,))
                return dask_array.compute()
            elif hasattr(data_source, 'to_dask'):
                # Use native Dask conversion if available
                dask_df = data_source.to_dask()
                return dask_df.compute()
            else:
                # Fallback to multiprocessing
                return self._process_with_multiprocessing(data_source, chunk_size)
        except Exception as e:
            warnings.warn(f"Dask processing failed: {e}")
            return self._process_with_multiprocessing(data_source, chunk_size)

    def _process_with_ray(self, data_source: Any, chunk_size: int) -> Any:
        """Process data using Ray distributed computing."""
        try:
            @ray.remote
            def process_chunk(chunk):
                # Process individual chunk
                return self._process_data_chunk(chunk)

            # Split data into chunks
            chunks = self._split_data_into_chunks(data_source, chunk_size)

            # Submit remote tasks
            futures = [process_chunk.remote(chunk) for chunk in chunks]

            # Collect results
            results = ray.get(futures)
            return self._combine_chunk_results(results)

        except Exception as e:
            warnings.warn(f"Ray processing failed: {e}")
            return self._process_with_multiprocessing(data_source, chunk_size)

    def _process_with_multiprocessing(self, data_source: Any, chunk_size: int) -> Any:
        """Process data using local multiprocessing."""
        try:
            chunks = self._split_data_into_chunks(data_source, chunk_size)

            with ProcessPoolExecutor(max_workers=self.config.worker_count) as executor:
                futures = [executor.submit(self._process_data_chunk, chunk) for chunk in chunks]
                results = [future.result() for future in futures]

            return self._combine_chunk_results(results)

        except Exception as e:
            warnings.warn(f"Multiprocessing failed: {e}")
            # Single-threaded fallback
            return self._process_data_chunk(data_source)

    def _split_data_into_chunks(self, data: Any, chunk_size: int) -> List[Any]:
        """Split data into processable chunks."""
        if isinstance(data, np.ndarray):
            return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        elif hasattr(data, '__len__'):
            return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
        else:
            return [data]  # Cannot split, return as single chunk

    def _process_data_chunk(self, chunk: Any) -> Any:
        """Process individual data chunk."""
        # Placeholder for actual data processing
        # This would contain the visualization-specific logic
        if isinstance(chunk, np.ndarray):
            # Example: Apply some computation to the chunk
            return np.mean(chunk, axis=0) if len(chunk.shape) > 1 else np.mean(chunk)
        return chunk

    def _combine_chunk_results(self, results: List[Any]) -> Any:
        """Combine results from multiple chunks."""
        if all(isinstance(r, np.ndarray) for r in results):
            return np.concatenate(results)
        elif all(isinstance(r, (int, float)) for r in results):
            return np.array(results)
        else:
            return results

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get current cluster status and performance metrics."""
        status = {
            "cluster_type": self.config.cluster_type,
            "worker_count": self.config.worker_count,
            "active_jobs": len(self.active_jobs),
            "queue_size": self.job_queue.qsize(),
        }

        if self.config.cluster_type == "dask" and self.client:
            scheduler_info = self.client.scheduler_info()
            status.update({
                "dask_workers": len(scheduler_info["workers"]),
                "dask_tasks": scheduler_info.get("processing", {}),
            })
        elif self.config.cluster_type == "ray" and ray.is_initialized():
            status.update({
                "ray_nodes": len(ray.nodes()),
                "ray_resources": ray.cluster_resources(),
            })

        return status

    def shutdown_cluster(self) -> None:
        """Gracefully shutdown the compute cluster."""
        if self.config.cluster_type == "dask" and self.client:
            self.client.close()
        elif self.config.cluster_type == "ray" and ray.is_initialized():
            ray.shutdown()
        elif hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=True)
            self.process_pool.shutdown(wait=True)


class GPUAcceleratedRenderer:
    """
    GPU-accelerated rendering engine for massive datasets using CUDA/OpenCL.
    """

    def __init__(self, device_id: int = 0, memory_pool_size: Optional[int] = None):
        self.device_id = device_id
        self.gpu_available = HAS_CUPY
        self.memory_pool = None

        if self.gpu_available:
            self._initialize_gpu()
        else:
            warnings.warn("GPU acceleration not available. Install CuPy for CUDA support.")

    def _initialize_gpu(self) -> None:
        """Initialize GPU for high-performance computing."""
        try:
            cp.cuda.Device(self.device_id).use()

            # Initialize memory pool for efficient GPU memory management
            if not self.memory_pool:
                self.memory_pool = cp.get_default_memory_pool()

            # Get GPU information
            device = cp.cuda.Device(self.device_id)
            props = cp.cuda.runtime.getDeviceProperties(self.device_id)

            print(f"GPU initialized: {props['name'].decode()} with {props['totalGlobalMem'] // (1024**3)} GB")

        except Exception as e:
            warnings.warn(f"Failed to initialize GPU: {e}")
            self.gpu_available = False

    def render_massive_scatter(self, x_data: np.ndarray, y_data: np.ndarray,
                              colors: Optional[np.ndarray] = None,
                              sizes: Optional[np.ndarray] = None,
                              alpha: float = 0.7) -> Dict[str, Any]:
        """
        GPU-accelerated scatter plot rendering for millions of points.
        """
        if not self.gpu_available:
            return self._fallback_cpu_render(x_data, y_data, colors, sizes, alpha)

        try:
            # Transfer data to GPU
            x_gpu = cp.asarray(x_data)
            y_gpu = cp.asarray(y_data)

            # Apply GPU-accelerated transformations
            if colors is not None:
                colors_gpu = cp.asarray(colors)
                # Normalize colors
                colors_normalized = (colors_gpu - cp.min(colors_gpu)) / (cp.max(colors_gpu) - cp.min(colors_gpu))
            else:
                colors_normalized = cp.ones(len(x_gpu)) * 0.5

            if sizes is not None:
                sizes_gpu = cp.asarray(sizes)
                sizes_normalized = (sizes_gpu - cp.min(sizes_gpu)) / (cp.max(sizes_gpu) - cp.min(sizes_gpu))
                sizes_normalized = sizes_normalized * 50 + 10  # Scale to reasonable point sizes
            else:
                sizes_normalized = cp.ones(len(x_gpu)) * 20

            # Perform GPU-accelerated data binning for performance
            if len(x_gpu) > 1_000_000:
                x_binned, y_binned, colors_binned, sizes_binned = self._gpu_data_binning(
                    x_gpu, y_gpu, colors_normalized, sizes_normalized, bins=10000
                )
            else:
                x_binned, y_binned, colors_binned, sizes_binned = x_gpu, y_gpu, colors_normalized, sizes_normalized

            # Transfer results back to CPU
            result = {
                "x": cp.asnumpy(x_binned),
                "y": cp.asnumpy(y_binned),
                "colors": cp.asnumpy(colors_binned),
                "sizes": cp.asnumpy(sizes_binned),
                "alpha": alpha,
                "point_count": len(x_binned),
                "gpu_accelerated": True
            }

            return result

        except Exception as e:
            warnings.warn(f"GPU rendering failed: {e}")
            return self._fallback_cpu_render(x_data, y_data, colors, sizes, alpha)

    def _gpu_data_binning(self, x: cp.ndarray, y: cp.ndarray, colors: cp.ndarray,
                         sizes: cp.ndarray, bins: int = 10000) -> Tuple[cp.ndarray, ...]:
        """
        GPU-accelerated data binning for performance optimization.
        """
        # Create 2D histogram for binning
        x_bins = cp.linspace(cp.min(x), cp.max(x), int(np.sqrt(bins)))
        y_bins = cp.linspace(cp.min(y), cp.max(y), int(np.sqrt(bins)))

        # Digitize data into bins
        x_indices = cp.digitize(x, x_bins)
        y_indices = cp.digitize(y, y_bins)

        # Combine indices for unique bin identification
        bin_ids = x_indices * len(y_bins) + y_indices

        # Get unique bins and their counts
        unique_bins, inverse_indices, counts = cp.unique(bin_ids, return_inverse=True, return_counts=True)

        # Calculate bin centers and aggregate properties
        x_binned = cp.zeros(len(unique_bins))
        y_binned = cp.zeros(len(unique_bins))
        colors_binned = cp.zeros(len(unique_bins))
        sizes_binned = cp.zeros(len(unique_bins))

        for i in range(len(unique_bins)):
            mask = inverse_indices == i
            x_binned[i] = cp.mean(x[mask])
            y_binned[i] = cp.mean(y[mask])
            colors_binned[i] = cp.mean(colors[mask])
            sizes_binned[i] = cp.mean(sizes[mask]) * cp.log10(counts[i] + 1)  # Size by density

        return x_binned, y_binned, colors_binned, sizes_binned

    def render_massive_heatmap(self, x_data: np.ndarray, y_data: np.ndarray,
                              values: Optional[np.ndarray] = None,
                              grid_size: int = 1000) -> Dict[str, Any]:
        """
        GPU-accelerated heatmap rendering for large datasets.
        """
        if not self.gpu_available:
            return self._fallback_cpu_heatmap(x_data, y_data, values, grid_size)

        try:
            # Transfer to GPU
            x_gpu = cp.asarray(x_data)
            y_gpu = cp.asarray(y_data)

            if values is not None:
                values_gpu = cp.asarray(values)
            else:
                values_gpu = cp.ones(len(x_gpu))

            # Create grid
            x_min, x_max = cp.min(x_gpu), cp.max(x_gpu)
            y_min, y_max = cp.min(y_gpu), cp.max(y_gpu)

            x_edges = cp.linspace(x_min, x_max, grid_size + 1)
            y_edges = cp.linspace(y_min, y_max, grid_size + 1)

            # GPU-accelerated 2D histogram
            heatmap, _, _ = cp.histogram2d(x_gpu, y_gpu, bins=[x_edges, y_edges], weights=values_gpu)

            # Apply Gaussian smoothing for better visualization
            heatmap_smoothed = self._gpu_gaussian_filter(heatmap, sigma=1.0)

            return {
                "heatmap": cp.asnumpy(heatmap_smoothed),
                "x_edges": cp.asnumpy(x_edges),
                "y_edges": cp.asnumpy(y_edges),
                "max_value": float(cp.max(heatmap_smoothed)),
                "gpu_accelerated": True
            }

        except Exception as e:
            warnings.warn(f"GPU heatmap rendering failed: {e}")
            return self._fallback_cpu_heatmap(x_data, y_data, values, grid_size)

    def _gpu_gaussian_filter(self, data: cp.ndarray, sigma: float) -> cp.ndarray:
        """
        GPU-accelerated Gaussian filtering using custom CUDA kernel.
        """
        try:
            # Use CuPy's built-in Gaussian filter if available
            from cupyx.scipy.ndimage import gaussian_filter
            return gaussian_filter(data, sigma=sigma)
        except ImportError:
            # Fallback to simple smoothing
            return data

    def _fallback_cpu_render(self, x_data: np.ndarray, y_data: np.ndarray,
                            colors: Optional[np.ndarray], sizes: Optional[np.ndarray],
                            alpha: float) -> Dict[str, Any]:
        """
        CPU fallback rendering for when GPU is not available.
        """
        # Apply data sampling for performance
        if len(x_data) > 100_000:
            indices = np.random.choice(len(x_data), 100_000, replace=False)
            x_sampled = x_data[indices]
            y_sampled = y_data[indices]
            colors_sampled = colors[indices] if colors is not None else None
            sizes_sampled = sizes[indices] if sizes is not None else None
        else:
            x_sampled, y_sampled = x_data, y_data
            colors_sampled, sizes_sampled = colors, sizes

        return {
            "x": x_sampled,
            "y": y_sampled,
            "colors": colors_sampled,
            "sizes": sizes_sampled,
            "alpha": alpha,
            "point_count": len(x_sampled),
            "gpu_accelerated": False
        }

    def _fallback_cpu_heatmap(self, x_data: np.ndarray, y_data: np.ndarray,
                             values: Optional[np.ndarray], grid_size: int) -> Dict[str, Any]:
        """
        CPU fallback heatmap rendering.
        """
        if values is None:
            values = np.ones(len(x_data))

        heatmap, x_edges, y_edges = np.histogram2d(x_data, y_data, bins=grid_size, weights=values)

        return {
            "heatmap": heatmap,
            "x_edges": x_edges,
            "y_edges": y_edges,
            "max_value": np.max(heatmap),
            "gpu_accelerated": False
        }

    def get_gpu_memory_usage(self) -> Dict[str, Any]:
        """
        Get current GPU memory usage statistics.
        """
        if not self.gpu_available:
            return {"gpu_available": False}

        try:
            mempool = cp.get_default_memory_pool()

            # Get memory info from CUDA runtime
            free_mem, total_mem = cp.cuda.runtime.memGetInfo()

            return {
                "gpu_available": True,
                "device_id": self.device_id,
                "total_memory": total_mem,
                "free_memory": free_mem,
                "used_memory": total_mem - free_mem,
                "memory_pool_used": mempool.used_bytes(),
                "memory_pool_total": mempool.total_bytes(),
                "utilization_percent": ((total_mem - free_mem) / total_mem) * 100
            }
        except Exception as e:
            return {"gpu_available": True, "error": str(e)}

    def cleanup_gpu_memory(self) -> None:
        """
        Clean up GPU memory and reset memory pool.
        """
        if self.gpu_available and self.memory_pool:
            self.memory_pool.free_all_blocks()
            cp.cuda.Stream.null.synchronize()


class RealTimeDataProcessor:
    """
    Real-time data processing engine for streaming visualization updates.
    """

    def __init__(self, buffer_size: int = 10000, update_frequency: float = 1.0):
        self.buffer_size = buffer_size
        self.update_frequency = update_frequency
        self.data_buffer = queue.Queue(maxsize=buffer_size)
        self.subscribers: List[Callable] = []
        self.processing_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.performance_stats = {
            "throughput": 0.0,
            "latency": 0.0,
            "dropped_samples": 0
        }

    def start_processing(self) -> None:
        """Start real-time data processing."""
        if self.is_running:
            return

        self.is_running = True
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def stop_processing(self) -> None:
        """Stop real-time data processing."""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)

    def add_data_point(self, data_point: Any) -> bool:
        """Add data point to processing buffer."""
        try:
            self.data_buffer.put_nowait(data_point)
            return True
        except queue.Full:
            return False

    def subscribe_to_updates(self, callback: Callable) -> None:
        """Subscribe to real-time updates."""
        self.subscribers.append(callback)

    def _processing_loop(self) -> None:
        """Main processing loop for real-time updates."""
        batch_data = []
        last_update = time.time()

        while self.is_running:
            try:
                # Collect data points
                while not self.data_buffer.empty() and len(batch_data) < 1000:
                    data_point = self.data_buffer.get_nowait()
                    batch_data.append(data_point)

                # Process batch if enough data or time elapsed
                current_time = time.time()
                if (batch_data and
                    (len(batch_data) >= 100 or current_time - last_update >= self.update_frequency)):

                    processed_data = self._process_batch(batch_data)

                    # Notify subscribers
                    for callback in self.subscribers:
                        try:
                            callback(processed_data)
                        except Exception as e:
                            warnings.warn(f"Subscriber callback failed: {e}")

                    batch_data.clear()
                    last_update = current_time

                time.sleep(0.01)  # Small sleep to prevent excessive CPU usage

            except Exception as e:
                warnings.warn(f"Processing loop error: {e}")

    def _process_batch(self, batch_data: List[Any]) -> Dict[str, Any]:
        """Process batch of data points."""
        return {
            "timestamp": time.time(),
            "batch_size": len(batch_data),
            "data": batch_data,
            "summary": {
                "count": len(batch_data),
                "processing_time": time.time()
            }
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        return {
            "throughput": self.performance_stats.get("throughput", 0.0),
            "latency": self.performance_stats.get("latency", 0.0),
            "dropped_samples": self.performance_stats.get("dropped_samples", 0),
            "buffer_size": self.buffer_size,
            "update_frequency": self.update_frequency
        }


class IntelligentDataSampler:
    """
    Advanced data sampling algorithms for enterprise-scale datasets.

    Features:
    - Adaptive sampling based on data characteristics
    - Peak-preserving algorithms for time series
    - Stratified sampling for statistical significance
    - LTTB (Largest Triangle Three Buckets) for time series
    """

    def __init__(self):
        self.sampling_strategies = {
            "adaptive": self._adaptive_sampling,
            "peak_preserving": self._peak_preserving_sampling,
            "lttb": self._lttb_sampling,
            "stratified": self._stratified_sampling,
            "uniform": self._uniform_sampling
        }

    def sample_dataset(self, data: np.ndarray, target_size: int,
                      strategy: str = "adaptive", **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Sample large dataset using specified strategy.

        Args:
            data: Input data (2D array with columns [x, y, ...])
            target_size: Desired number of samples
            strategy: Sampling strategy to use

        Returns:
            Tuple of (sampled_data, selected_indices)
        """
        if len(data) <= target_size:
            return data, np.arange(len(data))

        if strategy not in self.sampling_strategies:
            warnings.warn(f"Unknown strategy '{strategy}', using adaptive")
            strategy = "adaptive"

        return self.sampling_strategies[strategy](data, target_size, **kwargs)

    def _adaptive_sampling(self, data: np.ndarray, target_size: int, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Adaptive sampling based on local data density and importance.
        """
        # Calculate importance scores based on local variance
        if len(data.shape) == 1:
            importance = self._calculate_1d_importance(data)
        else:
            importance = self._calculate_nd_importance(data)

        # Normalize importance scores
        importance = importance / np.sum(importance)

        # Sample based on importance
        indices = np.random.choice(
            len(data), size=target_size, replace=False, p=importance
        )

        return data[indices], indices

    def _peak_preserving_sampling(self, data: np.ndarray, target_size: int, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Peak-preserving sampling for time series data.
        """
        if len(data.shape) == 1:
            y_values = data
            x_values = np.arange(len(data))
        else:
            x_values = data[:, 0]
            y_values = data[:, 1]

        # Find peaks and valleys
        peaks = self._find_peaks(y_values)
        valleys = self._find_valleys(y_values)
        critical_points = np.concatenate([peaks, valleys])

        # Always include critical points
        remaining_budget = max(0, target_size - len(critical_points))

        if remaining_budget > 0:
            # Sample remaining points uniformly
            all_indices = set(range(len(data)))
            critical_set = set(critical_points)
            regular_points = list(all_indices - critical_set)

            if len(regular_points) > remaining_budget:
                regular_sample = np.random.choice(
                    regular_points, size=remaining_budget, replace=False
                )
                final_indices = np.concatenate([critical_points, regular_sample])
            else:
                final_indices = np.concatenate([critical_points, regular_points])
        else:
            # Too many critical points, sample from them
            final_indices = np.random.choice(
                critical_points, size=target_size, replace=False
            )

        final_indices = np.sort(final_indices)
        return data[final_indices], final_indices

    def _lttb_sampling(self, data: np.ndarray, target_size: int, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Largest Triangle Three Buckets (LTTB) downsampling.
        """
        if len(data.shape) == 1:
            y_values = data
            x_values = np.arange(len(data))
        else:
            x_values = data[:, 0]
            y_values = data[:, 1]

        if len(x_values) <= target_size:
            return data, np.arange(len(data))

        # Always include first and last points
        if target_size < 3:
            indices = [0, len(x_values) - 1]
            return data[indices], np.array(indices)

        sampled_indices = [0]
        bucket_size = (len(x_values) - 2) / (target_size - 2)

        for i in range(1, target_size - 1):
            bucket_start = int(i * bucket_size) + 1
            bucket_end = int((i + 1) * bucket_size) + 1
            bucket_end = min(bucket_end, len(x_values) - 1)

            # Previous point
            prev_idx = sampled_indices[-1]
            prev_point = (x_values[prev_idx], y_values[prev_idx])

            # Next bucket average
            if i < target_size - 2:
                next_bucket_start = bucket_end
                next_bucket_end = min(int((i + 2) * bucket_size) + 1, len(x_values))
                next_avg_x = np.mean(x_values[next_bucket_start:next_bucket_end])
                next_avg_y = np.mean(y_values[next_bucket_start:next_bucket_end])
            else:
                next_avg_x, next_avg_y = x_values[-1], y_values[-1]

            # Find point that creates largest triangle
            max_area = -1
            selected_idx = bucket_start

            for j in range(bucket_start, bucket_end):
                area = abs(
                    (prev_point[0] * (y_values[j] - next_avg_y) +
                     x_values[j] * (next_avg_y - prev_point[1]) +
                     next_avg_x * (prev_point[1] - y_values[j])) / 2
                )

                if area > max_area:
                    max_area = area
                    selected_idx = j

            sampled_indices.append(selected_idx)

        sampled_indices.append(len(x_values) - 1)
        return data[sampled_indices], np.array(sampled_indices)

    def _stratified_sampling(self, data: np.ndarray, target_size: int, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Stratified sampling to preserve statistical distribution.
        """
        n_strata = min(10, target_size // 10)  # At least 10 samples per stratum

        if len(data.shape) == 1:
            strata_values = data
        else:
            # Use first column for stratification
            strata_values = data[:, 0]

        # Create strata based on quantiles
        quantiles = np.linspace(0, 100, n_strata + 1)
        strata_bounds = np.percentile(strata_values, quantiles)

        # Assign each point to a stratum
        strata_assignment = np.digitize(strata_values, strata_bounds) - 1
        strata_assignment = np.clip(strata_assignment, 0, n_strata - 1)

        # Sample from each stratum
        samples_per_stratum = target_size // n_strata
        remaining_samples = target_size % n_strata

        selected_indices = []

        for stratum in range(n_strata):
            stratum_indices = np.where(strata_assignment == stratum)[0]

            if len(stratum_indices) == 0:
                continue

            # Number of samples for this stratum
            n_samples = samples_per_stratum
            if stratum < remaining_samples:
                n_samples += 1

            # Sample from this stratum
            if len(stratum_indices) <= n_samples:
                selected_indices.extend(stratum_indices)
            else:
                stratum_sample = np.random.choice(
                    stratum_indices, size=n_samples, replace=False
                )
                selected_indices.extend(stratum_sample)

        selected_indices = np.array(selected_indices)
        return data[selected_indices], selected_indices

    def _uniform_sampling(self, data: np.ndarray, target_size: int, **kwargs) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simple uniform random sampling.
        """
        indices = np.random.choice(len(data), size=target_size, replace=False)
        return data[indices], indices

    def _calculate_1d_importance(self, data: np.ndarray, window_size: int = 5) -> np.ndarray:
        """Calculate importance scores for 1D data."""
        importance = np.zeros(len(data))
        half_window = window_size // 2

        for i in range(len(data)):
            start = max(0, i - half_window)
            end = min(len(data), i + half_window + 1)
            window_data = data[start:end]
            importance[i] = np.var(window_data) if len(window_data) > 1 else 0

        return importance + 1e-10  # Avoid zero probabilities

    def _calculate_nd_importance(self, data: np.ndarray) -> np.ndarray:
        """Calculate importance scores for multi-dimensional data."""
        # Use distance to k-nearest neighbors as importance measure
        from scipy.spatial.distance import cdist

        k = min(10, len(data) // 100)  # Adaptive k based on data size
        importance = np.zeros(len(data))

        # Calculate pairwise distances (sample if too large)
        if len(data) > 10000:
            sample_size = 5000
            sample_indices = np.random.choice(len(data), sample_size, replace=False)
            sample_data = data[sample_indices]
        else:
            sample_data = data
            sample_indices = np.arange(len(data))

        distances = cdist(data, sample_data)

        for i in range(len(data)):
            # Find k nearest neighbors
            nearest_distances = np.partition(distances[i], k)[:k]
            importance[i] = np.mean(nearest_distances)

        return importance

    def _find_peaks(self, y: np.ndarray, prominence: float = 0.1) -> np.ndarray:
        """Find peaks in 1D signal."""
        peaks = []
        threshold = prominence * (np.max(y) - np.min(y))

        for i in range(1, len(y) - 1):
            if y[i] > y[i-1] and y[i] > y[i+1] and y[i] > threshold:
                peaks.append(i)

        return np.array(peaks)

    def _find_valleys(self, y: np.ndarray, prominence: float = 0.1) -> np.ndarray:
        """Find valleys in 1D signal."""
        valleys = []
        threshold = np.min(y) + prominence * (np.max(y) - np.min(y))

        for i in range(1, len(y) - 1):
            if y[i] < y[i-1] and y[i] < y[i+1] and y[i] < threshold:
                valleys.append(i)

        return np.array(valleys)


class EnterprisePerformanceBenchmark:
    """
    Comprehensive performance benchmarking suite for enterprise deployments.
    """

    def __init__(self):
        self.benchmark_results: List[Dict[str, Any]] = []
        self.distributed_engine = None
        self.gpu_renderer = None

    def run_comprehensive_benchmark(self, data_sizes: List[int] = None,
                                   backends: List[str] = None) -> Dict[str, Any]:
        """
        Run comprehensive performance benchmark across different configurations.
        """
        if data_sizes is None:
            data_sizes = [1_000, 10_000, 100_000, 1_000_000, 10_000_000]

        if backends is None:
            backends = ["cpu_single", "cpu_multicore", "dask_local", "gpu_cuda"]

        results = {
            "timestamp": time.time(),
            "system_info": self._get_system_info(),
            "benchmarks": []
        }

        for data_size in data_sizes:
            for backend in backends:
                benchmark_result = self._run_single_benchmark(data_size, backend)
                results["benchmarks"].append(benchmark_result)
                self.benchmark_results.append(benchmark_result)

        return results

    def _run_single_benchmark(self, data_size: int, backend: str) -> Dict[str, Any]:
        """
        Run single benchmark configuration.
        """
        print(f"Benchmarking {backend} with {data_size:,} points...")

        # Generate test data
        x_data = np.random.random(data_size).astype(np.float32)
        y_data = np.random.random(data_size).astype(np.float32)
        colors = np.random.random(data_size).astype(np.float32)

        start_time = time.time()
        memory_before = self._get_memory_usage()

        try:
            if backend == "gpu_cuda" and HAS_CUPY:
                # GPU benchmark
                gpu_renderer = GPUAcceleratedRenderer()
                result = gpu_renderer.render_massive_scatter(x_data, y_data, colors)
                success = result.get("gpu_accelerated", False)
            elif backend.startswith("dask") and HAS_DASK:
                # Dask benchmark
                config = ComputeClusterConfig(cluster_type="dask")
                engine = DistributedDataEngine(config)
                result = engine.process_massive_dataset(np.column_stack([x_data, y_data]))
                success = True
            elif backend == "cpu_multicore":
                # Multicore CPU benchmark
                config = ComputeClusterConfig(cluster_type="local")
                engine = DistributedDataEngine(config)
                result = engine.process_massive_dataset(np.column_stack([x_data, y_data]))
                success = True
            else:
                # Single-threaded benchmark
                result = np.mean(np.column_stack([x_data, y_data]), axis=0)
                success = True

        except Exception as e:
            success = False
            result = {"error": str(e)}

        end_time = time.time()
        memory_after = self._get_memory_usage()

        processing_time = end_time - start_time
        throughput = data_size / processing_time if processing_time > 0 else 0

        return {
            "data_size": data_size,
            "backend": backend,
            "processing_time": processing_time,
            "throughput": throughput,
            "memory_usage": memory_after - memory_before,
            "success": success,
            "timestamp": start_time
        }

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmark context."""
        import platform
        try:
            import psutil
            HAS_PSUTIL = True
        except ImportError:
            HAS_PSUTIL = False

        info = {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "cpu_count": multiprocessing.cpu_count(),
            "python_version": platform.python_version(),
        }

        if HAS_PSUTIL:
            info["memory_total"] = psutil.virtual_memory().total

        # GPU information if available
        if HAS_CUPY:
            try:
                device_count = cp.cuda.runtime.getDeviceCount()
                info["gpu_count"] = device_count
                if device_count > 0:
                    props = cp.cuda.runtime.getDeviceProperties(0)
                    info["gpu_name"] = props["name"].decode()
                    info["gpu_memory"] = props["totalGlobalMem"]
            except Exception:
                info["gpu_available"] = False

        return info

    def _get_memory_usage(self) -> float:
        """Get current memory usage in bytes."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            return 0.0

    def generate_performance_report(self) -> str:
        """
        Generate comprehensive performance report.
        """
        if not self.benchmark_results:
            return "No benchmark results available. Run benchmarks first."

        report = ["=" * 60]
        report.append("ENTERPRISE PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 60)
        report.append("")

        # Summary statistics
        report.append("PERFORMANCE SUMMARY")
        report.append("-" * 30)

        by_backend = {}
        for result in self.benchmark_results:
            backend = result["backend"]
            if backend not in by_backend:
                by_backend[backend] = []
            by_backend[backend].append(result)

        for backend, results in by_backend.items():
            successful = [r for r in results if r["success"]]
            if successful:
                avg_throughput = np.mean([r["throughput"] for r in successful])
                max_throughput = np.max([r["throughput"] for r in successful])
                report.append(f"{backend:15} | Avg: {avg_throughput:10.0f} pts/sec | Max: {max_throughput:10.0f} pts/sec")

        report.append("")

        # Detailed results
        report.append("DETAILED RESULTS")
        report.append("-" * 30)
        report.append(f"{'Backend':<15} {'Data Size':<12} {'Time (s)':<10} {'Throughput':<12} {'Memory (MB)':<12} {'Status'}")
        report.append("-" * 80)

        for result in self.benchmark_results:
            status = "✓" if result["success"] else "✗"
            memory_mb = result["memory_usage"] / (1024 * 1024)
            report.append(
                f"{result['backend']:<15} "
                f"{result['data_size']:<12,} "
                f"{result['processing_time']:<10.3f} "
                f"{result['throughput']:<12.0f} "
                f"{memory_mb:<12.1f} "
                f"{status}"
            )

        return "\n".join(report)