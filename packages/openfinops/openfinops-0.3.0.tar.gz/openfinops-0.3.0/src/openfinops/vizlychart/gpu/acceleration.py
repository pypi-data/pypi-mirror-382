"""GPU-accelerated rendering components for Vizly."""

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
from typing import Optional, Tuple, Union
import logging

from .backends import GPUBackend, get_best_backend
from ..rendering.pure_engine import PureCanvas, Color

logger = logging.getLogger(__name__)


class GPUAcceleratedCanvas(PureCanvas):
    """GPU-accelerated version of PureCanvas."""

    def __init__(self, width: int, height: int, backend: Optional[GPUBackend] = None,
                 background: Color = None):
        super().__init__(width, height, background)

        # GPU backend
        self.gpu_backend = backend or get_best_backend()
        self.gpu_enabled = self.gpu_backend.initialize()

        if self.gpu_enabled:
            logger.info(f"GPU acceleration enabled: {self.gpu_backend.device_info.get('name', 'Unknown')}")
        else:
            logger.warning("GPU acceleration not available, falling back to CPU")

    def draw_points_gpu(self, points: np.ndarray, color: Color, size: float = 1.0):
        """Draw multiple points using GPU acceleration."""
        if not self.gpu_enabled:
            # Fallback to CPU implementation
            for point in points:
                self.draw_circle(point[0], point[1], size, fill=True)
            return

        try:
            # Transform points to canvas coordinates
            transformed_points = np.zeros_like(points)
            for i, (x, y) in enumerate(points):
                tx, ty = self._transform_point(x, y)
                transformed_points[i] = [tx, ty]

            # Use GPU to render points
            canvas_buffer = self.gpu_backend.render_points(
                transformed_points, (self.width, self.height)
            )

            # Blend with existing canvas
            self._blend_gpu_buffer(canvas_buffer, color)

        except Exception as e:
            logger.warning(f"GPU rendering failed, falling back to CPU: {e}")
            # Fallback to CPU
            for point in points:
                self.draw_circle(point[0], point[1], size, fill=True)

    def _blend_gpu_buffer(self, gpu_buffer: np.ndarray, color: Color):
        """Blend GPU-rendered buffer with canvas."""
        # Simple alpha blending
        mask = gpu_buffer[:, :, 3] > 0  # Where GPU rendered something

        for y in range(self.height):
            for x in range(self.width):
                if mask[y, x]:
                    self.pixels[y, x] = [color.r, color.g, color.b, color.a]

    def compute_distances_gpu(self, points: np.ndarray) -> np.ndarray:
        """Compute pairwise distances using GPU."""
        if not self.gpu_enabled:
            # CPU fallback
            diff = points[:, None, :] - points[None, :, :]
            return np.sqrt(np.sum(diff ** 2, axis=2))

        try:
            return self.gpu_backend.compute_distances(points)
        except Exception as e:
            logger.warning(f"GPU distance computation failed: {e}")
            # CPU fallback
            diff = points[:, None, :] - points[None, :, :]
            return np.sqrt(np.sum(diff ** 2, axis=2))


class AcceleratedRenderer:
    """GPU-accelerated renderer for high-performance visualization."""

    def __init__(self, width: int = 800, height: int = 600, backend: Optional[str] = None):
        self.width = width
        self.height = height

        # Initialize GPU backend
        if backend == 'cuda':
            from .backends import CUDABackend
            self.gpu_backend = CUDABackend()
        elif backend == 'opencl':
            from .backends import OpenCLBackend
            self.gpu_backend = OpenCLBackend()
        elif backend == 'cpu':
            from .backends import CPUBackend
            self.gpu_backend = CPUBackend()
        else:
            # Auto-detect best backend
            from . import get_best_backend
            self.gpu_backend = get_best_backend()

        self.gpu_enabled = self.gpu_backend.initialize()
        self.canvas = GPUAcceleratedCanvas(width, height, self.gpu_backend)

    def scatter_gpu(self, x: np.ndarray, y: np.ndarray, color: str = 'blue', size: float = 20):
        """GPU-accelerated scatter plot."""
        if len(x) != len(y):
            raise ValueError("x and y must have the same length")

        # Set up viewport
        x_min, x_max = float(np.min(x)), float(np.max(x))
        y_min, y_max = float(np.min(y)), float(np.max(y))

        # Add padding
        x_range = x_max - x_min
        y_range = y_max - y_min
        x_min -= x_range * 0.1
        x_max += x_range * 0.1
        y_min -= y_range * 0.1
        y_max += y_range * 0.1

        self.canvas.set_viewport(x_min, x_max, y_min, y_max)

        # Convert color
        if isinstance(color, str):
            if color.startswith('#'):
                canvas_color = Color.from_hex(color)
            else:
                canvas_color = Color.from_name(color)
        else:
            canvas_color = color

        # Prepare points for GPU rendering
        points = np.column_stack([x, y]).astype(np.float32)

        # Use GPU acceleration for large datasets
        if len(points) > 1000 and self.gpu_enabled:
            logger.info(f"Using GPU acceleration for {len(points)} points")
            self.canvas.draw_points_gpu(points, canvas_color, size / 100.0)
        else:
            # Use CPU for small datasets or when GPU unavailable
            logger.info(f"Using CPU rendering for {len(points)} points")
            for i in range(len(x)):
                self.canvas.draw_circle(float(x[i]), float(y[i]), size / 100.0, fill=True)

        return self

    def line_gpu(self, x: np.ndarray, y: np.ndarray, color: str = 'blue', linewidth: float = 1.0):
        """GPU-accelerated line plot."""
        if len(x) != len(y):
            raise ValueError("x and y must have the same length")

        # Set up viewport
        x_min, x_max = float(np.min(x)), float(np.max(x))
        y_min, y_max = float(np.min(y)), float(np.max(y))

        # Add padding
        x_range = x_max - x_min
        y_range = y_max - y_min
        x_min -= x_range * 0.1
        x_max += x_range * 0.1
        y_min -= y_range * 0.1
        y_max += y_range * 0.1

        self.canvas.set_viewport(x_min, x_max, y_min, y_max)
        self.canvas.set_stroke_color(color)
        self.canvas.set_line_width(linewidth)

        # Draw line segments (CPU implementation for now)
        # GPU line rendering would require more complex kernels
        points = [(float(x[i]), float(y[i])) for i in range(len(x))]
        self.canvas.draw_polyline(points)

        return self

    def surface_gpu(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray, cmap: str = 'viridis'):
        """GPU-accelerated surface plot."""
        if X.shape != Y.shape or X.shape != Z.shape:
            raise ValueError("X, Y, and Z must have the same shape")

        # Set viewport
        x_min, x_max = np.min(X), np.max(X)
        y_min, y_max = np.min(Y), np.max(Y)
        self.canvas.set_viewport(x_min, x_max, y_min, y_max)

        # GPU-accelerated contour computation for large surfaces
        if X.size > 10000 and self.gpu_enabled:
            logger.info(f"Using GPU acceleration for surface with {X.size} points")

            # Flatten surface data for GPU processing
            points = np.column_stack([X.flatten(), Y.flatten()])
            z_values = Z.flatten()

            # Use GPU to compute point relationships
            distances = self.canvas.compute_distances_gpu(points)

            # Simple contour-like visualization
            # More sophisticated GPU surface rendering would go here
            colors = ['blue', 'green', 'yellow', 'orange', 'red']
            z_min, z_max = np.min(Z), np.max(Z)
            levels = np.linspace(z_min, z_max, len(colors))

            for i, level in enumerate(levels):
                color = colors[i]
                self.canvas.set_stroke_color(color)

                # Find points close to this level
                mask = np.abs(z_values - level) < (z_max - z_min) / 20
                level_points = points[mask]

                if len(level_points) > 0:
                    # Draw level points
                    for point in level_points:
                        self.canvas.draw_circle(point[0], point[1], 0.5, fill=True)
        else:
            # CPU fallback for smaller surfaces
            self._surface_cpu_fallback(X, Y, Z, cmap)

        return self

    def _surface_cpu_fallback(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray, cmap: str):
        """CPU fallback for surface rendering."""
        # Simplified contour representation
        z_min, z_max = np.min(Z), np.max(Z)
        levels = np.linspace(z_min, z_max, 10)
        colors = ['blue', 'green', 'yellow', 'orange', 'red']

        for i, level in enumerate(levels[::2]):
            color = colors[i % len(colors)]
            self.canvas.set_stroke_color(color)

            # Find points close to this level
            mask = np.abs(Z - level) < (z_max - z_min) / 20
            x_points = X[mask]
            y_points = Y[mask]

            # Draw points at this level
            for j in range(len(x_points)):
                if j < len(x_points) - 1:
                    self.canvas.draw_line(
                        float(x_points[j]), float(y_points[j]),
                        float(x_points[j+1]), float(y_points[j+1])
                    )

    def save(self, filename: str, dpi: int = 100):
        """Save the accelerated rendering."""
        self.canvas.save(filename, dpi)

    def show(self):
        """Display performance information."""
        backend_info = self.gpu_backend.device_info
        print(f"🚀 Accelerated Renderer")
        print(f"Backend: {backend_info.get('backend', 'Unknown')}")
        print(f"Device: {backend_info.get('name', 'Unknown')}")
        if 'memory' in backend_info:
            memory_gb = backend_info['memory'] / (1024**3)
            print(f"Memory: {memory_gb:.1f} GB")
        print(f"Canvas: {self.canvas.width}x{self.canvas.height} pixels")
        print("Use .save() to export to PNG or SVG format")

    def get_backend_info(self) -> dict:
        """Get information about the current backend."""
        return {
            'backend': self.gpu_backend.device_info.get('backend', 'Unknown'),
            'device': self.gpu_backend.device_info.get('name', 'Unknown'),
            'enabled': self.gpu_enabled,
            'canvas_size': (self.canvas.width, self.canvas.height)
        }