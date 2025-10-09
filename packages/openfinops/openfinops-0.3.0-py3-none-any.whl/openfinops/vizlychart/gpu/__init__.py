"""
Vizly GPU Acceleration Module
============================

High-performance GPU acceleration for Vizly visualization using OpenCL and CUDA.
Falls back gracefully to CPU when GPU not available.

Supported backends:
- OpenCL (cross-platform)
- CUDA (NVIDIA GPUs)
- CPU fallback (always available)

Basic Usage:
    >>> import vizly.gpu as vgpu
    >>> backend = vgpu.get_best_backend()
    >>> accelerated_chart = vizly.LineChart(backend='gpu')
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



from .backends import GPUBackend, OpenCLBackend, CUDABackend, CPUBackend
from .acceleration import GPUAcceleratedCanvas, AcceleratedRenderer
from .memory import GPUMemoryManager
from .kernels import RenderingKernels

__version__ = "0.4.0"
__all__ = [
    # Core GPU functionality
    "GPUBackend", "OpenCLBackend", "CUDABackend", "CPUBackend",
    # Accelerated rendering
    "GPUAcceleratedCanvas", "AcceleratedRenderer",
    # Memory management
    "GPUMemoryManager",
    # Compute kernels
    "RenderingKernels",
    # Utility functions
    "get_best_backend", "list_gpu_devices", "benchmark_backends",
]


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


def list_gpu_devices():
    """List all available GPU devices."""
    devices = []

    # CUDA devices
    try:
        cuda_backend = CUDABackend()
        devices.extend(cuda_backend.list_devices())
    except ImportError:
        pass

    # OpenCL devices
    try:
        opencl_backend = OpenCLBackend()
        devices.extend(opencl_backend.list_devices())
    except ImportError:
        pass

    return devices


def benchmark_backends():
    """Benchmark all available backends."""
    import time
    import numpy as np

    results = {}
    test_data = np.random.randn(10000, 2).astype(np.float32)

    backends = [
        ('CPU', CPUBackend()),
        ('OpenCL', OpenCLBackend() if OpenCLBackend().is_available() else None),
        ('CUDA', CUDABackend() if CUDABackend().is_available() else None),
    ]

    for name, backend in backends:
        if backend is None:
            results[name] = "Not Available"
            continue

        try:
            start_time = time.time()
            # Simple compute test
            result = backend.compute_distances(test_data)
            end_time = time.time()

            results[name] = {
                'time': end_time - start_time,
                'points_per_second': len(test_data) / (end_time - start_time),
                'available': True
            }
        except Exception as e:
            results[name] = {'error': str(e), 'available': False}

    return results