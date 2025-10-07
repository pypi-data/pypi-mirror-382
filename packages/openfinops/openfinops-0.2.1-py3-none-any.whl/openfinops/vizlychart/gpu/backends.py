"""GPU backend implementations for different compute platforms."""

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

import logging
import numpy as np
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Any
import warnings

logger = logging.getLogger(__name__)


class GPUBackend(ABC):
    """Abstract base class for GPU compute backends."""

    def __init__(self):
        self.is_initialized = False
        self.device_info = {}

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available."""
        pass

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the backend."""
        pass

    @abstractmethod
    def list_devices(self) -> List[dict]:
        """List available devices."""
        pass

    @abstractmethod
    def compute_distances(self, points: np.ndarray) -> np.ndarray:
        """Compute pairwise distances (benchmark function)."""
        pass

    @abstractmethod
    def render_points(self, points: np.ndarray, canvas_size: Tuple[int, int]) -> np.ndarray:
        """Render points to pixel buffer."""
        pass


class CUDABackend(GPUBackend):
    """NVIDIA CUDA backend for GPU acceleration."""

    def __init__(self):
        super().__init__()
        self.cuda_context = None

    def is_available(self) -> bool:
        """Check if CUDA is available."""
        try:
            import cupy as cp
            return cp.cuda.is_available()
        except ImportError:
            return False

    def initialize(self) -> bool:
        """Initialize CUDA backend."""
        if self.is_initialized:
            return True

        try:
            import cupy as cp

            # Get device info
            device = cp.cuda.Device()
            self.device_info = {
                'name': device.attributes['Name'].decode(),
                'compute_capability': device.compute_capability,
                'memory': device.mem_info[1],  # Total memory
                'multiprocessors': device.attributes['MultiProcessorCount'],
                'backend': 'CUDA'
            }

            self.is_initialized = True
            logger.info(f"CUDA backend initialized: {self.device_info['name']}")
            return True

        except Exception as e:
            logger.warning(f"Failed to initialize CUDA backend: {e}")
            return False

    def list_devices(self) -> List[dict]:
        """List CUDA devices."""
        devices = []
        try:
            import cupy as cp

            for i in range(cp.cuda.runtime.getDeviceCount()):
                device = cp.cuda.Device(i)
                devices.append({
                    'id': i,
                    'name': device.attributes['Name'].decode(),
                    'memory': device.mem_info[1],
                    'compute_capability': device.compute_capability,
                    'backend': 'CUDA'
                })
        except Exception as e:
            logger.warning(f"Failed to list CUDA devices: {e}")

        return devices

    def compute_distances(self, points: np.ndarray) -> np.ndarray:
        """Compute pairwise distances using CUDA."""
        try:
            import cupy as cp

            # Transfer to GPU
            gpu_points = cp.asarray(points)

            # Compute pairwise distances using broadcasting
            diff = gpu_points[:, None, :] - gpu_points[None, :, :]
            distances = cp.sqrt(cp.sum(diff ** 2, axis=2))

            # Transfer back to CPU
            return cp.asnumpy(distances)

        except ImportError:
            raise RuntimeError("CuPy not available for CUDA backend")

    def render_points(self, points: np.ndarray, canvas_size: Tuple[int, int]) -> np.ndarray:
        """Render points to pixel buffer using CUDA."""
        try:
            import cupy as cp

            width, height = canvas_size
            canvas = cp.zeros((height, width, 4), dtype=cp.float32)
            gpu_points = cp.asarray(points)

            # Simple point rendering kernel (simplified)
            # In practice, this would use custom CUDA kernels
            for i in range(len(points)):
                x, y = int(gpu_points[i, 0]), int(gpu_points[i, 1])
                if 0 <= x < width and 0 <= y < height:
                    canvas[y, x] = [1.0, 0.0, 0.0, 1.0]  # Red point

            return cp.asnumpy(canvas)

        except ImportError:
            raise RuntimeError("CuPy not available for CUDA backend")


class OpenCLBackend(GPUBackend):
    """OpenCL backend for cross-platform GPU acceleration."""

    def __init__(self):
        super().__init__()
        self.context = None
        self.queue = None

    def is_available(self) -> bool:
        """Check if OpenCL is available."""
        try:
            import pyopencl as cl
            platforms = cl.get_platforms()
            return len(platforms) > 0
        except ImportError:
            return False

    def initialize(self) -> bool:
        """Initialize OpenCL backend."""
        if self.is_initialized:
            return True

        try:
            import pyopencl as cl

            # Create context and queue
            self.context = cl.create_some_context(interactive=False)
            self.queue = cl.CommandQueue(self.context)

            # Get device info
            device = self.context.devices[0]
            self.device_info = {
                'name': device.name.strip(),
                'vendor': device.vendor.strip(),
                'memory': device.global_mem_size,
                'compute_units': device.max_compute_units,
                'backend': 'OpenCL'
            }

            self.is_initialized = True
            logger.info(f"OpenCL backend initialized: {self.device_info['name']}")
            return True

        except Exception as e:
            logger.warning(f"Failed to initialize OpenCL backend: {e}")
            return False

    def list_devices(self) -> List[dict]:
        """List OpenCL devices."""
        devices = []
        try:
            import pyopencl as cl

            for platform in cl.get_platforms():
                for device in platform.get_devices():
                    devices.append({
                        'name': device.name.strip(),
                        'vendor': device.vendor.strip(),
                        'memory': device.global_mem_size,
                        'compute_units': device.max_compute_units,
                        'backend': 'OpenCL'
                    })
        except Exception as e:
            logger.warning(f"Failed to list OpenCL devices: {e}")

        return devices

    def compute_distances(self, points: np.ndarray) -> np.ndarray:
        """Compute pairwise distances using OpenCL."""
        try:
            import pyopencl as cl
            import pyopencl.array as cl_array

            if not self.is_initialized:
                self.initialize()

            # OpenCL kernel for distance computation
            kernel_source = """
            __kernel void compute_distances(
                __global const float2* points,
                __global float* distances,
                const int n_points)
            {
                int i = get_global_id(0);
                int j = get_global_id(1);

                if (i < n_points && j < n_points) {
                    float2 diff = points[i] - points[j];
                    distances[i * n_points + j] = sqrt(diff.x * diff.x + diff.y * diff.y);
                }
            }
            """

            program = cl.Program(self.context, kernel_source).build()

            n_points = len(points)
            points_gpu = cl_array.to_device(self.queue, points.astype(np.float32))
            distances_gpu = cl_array.zeros(self.queue, (n_points, n_points), np.float32)

            program.compute_distances(
                self.queue, (n_points, n_points), None,
                points_gpu.data, distances_gpu.data, np.int32(n_points)
            )

            return distances_gpu.get()

        except ImportError:
            raise RuntimeError("PyOpenCL not available for OpenCL backend")

    def render_points(self, points: np.ndarray, canvas_size: Tuple[int, int]) -> np.ndarray:
        """Render points to pixel buffer using OpenCL."""
        try:
            import pyopencl as cl
            import pyopencl.array as cl_array

            if not self.is_initialized:
                self.initialize()

            width, height = canvas_size
            canvas = np.zeros((height, width, 4), dtype=np.float32)

            # Simple CPU fallback for rendering (OpenCL rendering kernel would be complex)
            for point in points:
                x, y = int(point[0]), int(point[1])
                if 0 <= x < width and 0 <= y < height:
                    canvas[y, x] = [0.0, 1.0, 0.0, 1.0]  # Green point

            return canvas

        except ImportError:
            raise RuntimeError("PyOpenCL not available for OpenCL backend")


class CPUBackend(GPUBackend):
    """CPU fallback backend using NumPy."""

    def __init__(self):
        super().__init__()

    def is_available(self) -> bool:
        """CPU is always available."""
        return True

    def initialize(self) -> bool:
        """Initialize CPU backend."""
        import multiprocessing

        self.device_info = {
            'name': 'CPU (NumPy)',
            'cores': multiprocessing.cpu_count(),
            'backend': 'CPU'
        }

        self.is_initialized = True
        logger.info(f"CPU backend initialized: {self.device_info['cores']} cores")
        return True

    def list_devices(self) -> List[dict]:
        """List CPU as device."""
        import multiprocessing
        return [{
            'name': 'CPU (NumPy)',
            'cores': multiprocessing.cpu_count(),
            'backend': 'CPU'
        }]

    def compute_distances(self, points: np.ndarray) -> np.ndarray:
        """Compute pairwise distances using NumPy."""
        # Vectorized distance computation
        diff = points[:, None, :] - points[None, :, :]
        distances = np.sqrt(np.sum(diff ** 2, axis=2))
        return distances

    def render_points(self, points: np.ndarray, canvas_size: Tuple[int, int]) -> np.ndarray:
        """Render points to pixel buffer using NumPy."""
        width, height = canvas_size
        canvas = np.zeros((height, width, 4), dtype=np.float32)

        # Render each point
        for point in points:
            x, y = int(point[0]), int(point[1])
            if 0 <= x < width and 0 <= y < height:
                canvas[y, x] = [0.0, 0.0, 1.0, 1.0]  # Blue point

        return canvas


def get_best_backend():
    """Get the best available GPU backend."""
    # Try CUDA first (fastest for NVIDIA)
    try:
        backend = CUDABackend()
        if backend.is_available():
            return backend
    except ImportError:
        pass

    # Try OpenCL (cross-platform)
    try:
        backend = OpenCLBackend()
        if backend.is_available():
            return backend
    except ImportError:
        pass

    # Fallback to CPU
    return CPUBackend()