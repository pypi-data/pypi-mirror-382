"""High-performance rendering engines for Vizly."""

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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Tuple
import threading
import time

import numpy as np

try:
    import moderngl

    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False

try:
    import cupy as cp

    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False


logger = logging.getLogger(__name__)


class RenderBackend(Enum):
    """Available rendering backends."""

    AUTO = "auto"
    CPU = "cpu"
    OPENGL = "opengl"
    CUDA = "cuda"
    VULKAN = "vulkan"  # Future implementation


@dataclass
class RenderConfig:
    """Configuration for rendering engines."""

    backend: RenderBackend = RenderBackend.AUTO
    max_fps: int = 60
    vsync: bool = True
    antialias: bool = True
    buffer_size: int = 10000
    use_threading: bool = True
    gpu_memory_limit: Optional[int] = None  # MB


class RenderTarget(Protocol):
    """Protocol for render targets (canvas, buffer, etc.)."""

    def get_size(self) -> Tuple[int, int]:
        """Get target dimensions."""
        ...

    def swap_buffers(self) -> None:
        """Present the rendered frame."""
        ...


class BaseRenderer(ABC):
    """Abstract base class for all rendering engines."""

    def __init__(self, config: RenderConfig) -> None:
        self.config = config
        self._initialized = False
        self._frame_count = 0
        self._start_time = time.time()
        self._render_times: List[float] = []

    @abstractmethod
    def initialize(self, target: Optional[RenderTarget] = None) -> bool:
        """Initialize the rendering context."""
        ...

    @abstractmethod
    def render_lines(
        self,
        vertices: np.ndarray,
        colors: Optional[np.ndarray] = None,
        thickness: float = 1.0,
    ) -> None:
        """Render line data efficiently."""
        ...

    @abstractmethod
    def render_points(
        self,
        vertices: np.ndarray,
        colors: Optional[np.ndarray] = None,
        size: float = 1.0,
    ) -> None:
        """Render point/scatter data efficiently."""
        ...

    @abstractmethod
    def render_surface(
        self,
        vertices: np.ndarray,
        indices: np.ndarray,
        colors: Optional[np.ndarray] = None,
    ) -> None:
        """Render 3D surface/mesh data."""
        ...

    @abstractmethod
    def clear(self, color: Tuple[float, float, float, float] = (0, 0, 0, 1)) -> None:
        """Clear the render target."""
        ...

    @abstractmethod
    def present(self) -> None:
        """Present the rendered frame."""
        ...

    def get_fps(self) -> float:
        """Calculate current rendering FPS."""
        if len(self._render_times) < 2:
            return 0.0
        recent_times = self._render_times[-10:]  # Last 10 frames
        return len(recent_times) / (recent_times[-1] - recent_times[0])

    def _record_frame(self) -> None:
        """Record frame timing for performance monitoring."""
        current_time = time.time()
        self._render_times.append(current_time)
        self._frame_count += 1

        # Keep only recent frame times
        if len(self._render_times) > 100:
            self._render_times = self._render_times[-50:]


class CPURenderer(BaseRenderer):
    """CPU-based renderer using matplotlib backend."""

    def __init__(self, config: RenderConfig) -> None:
        super().__init__(config)
        self._matplotlib_backend = None

    def initialize(self, target: Optional[RenderTarget] = None) -> bool:
        """Initialize matplotlib-based CPU rendering."""
        try:
            import matplotlib
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_agg import FigureCanvasAgg

            self._matplotlib_backend = matplotlib.get_backend()
            self._canvas = FigureCanvasAgg
            self._initialized = True
            logger.info("CPU renderer initialized with matplotlib")
            return True
        except ImportError as e:
            logger.error(f"Failed to initialize CPU renderer: {e}")
            return False

    def render_lines(
        self,
        vertices: np.ndarray,
        colors: Optional[np.ndarray] = None,
        thickness: float = 1.0,
    ) -> None:
        """Render lines using matplotlib."""
        # Implementation would use matplotlib's optimized line collections
        pass

    def render_points(
        self,
        vertices: np.ndarray,
        colors: Optional[np.ndarray] = None,
        size: float = 1.0,
    ) -> None:
        """Render points using matplotlib."""
        # Implementation would use matplotlib's scatter with optimizations
        pass

    def render_surface(
        self,
        vertices: np.ndarray,
        indices: np.ndarray,
        colors: Optional[np.ndarray] = None,
    ) -> None:
        """Render 3D surfaces using matplotlib."""
        # Implementation would use mplot3d with optimizations
        pass

    def clear(self, color: Tuple[float, float, float, float] = (0, 0, 0, 1)) -> None:
        """Clear using matplotlib."""
        pass

    def present(self) -> None:
        """Present frame via matplotlib."""
        self._record_frame()


class GPURenderer(BaseRenderer):
    """GPU-accelerated renderer using OpenGL/CUDA."""

    def __init__(self, config: RenderConfig) -> None:
        super().__init__(config)
        self._gl_context: Optional[Any] = None
        self._cuda_context: Optional[Any] = None
        self._vertex_buffers: Dict[str, Any] = {}
        self._shaders: Dict[str, Any] = {}

    def initialize(self, target: Optional[RenderTarget] = None) -> bool:
        """Initialize GPU rendering context."""
        if self.config.backend == RenderBackend.OPENGL and HAS_OPENGL:
            return self._init_opengl(target)
        elif self.config.backend == RenderBackend.CUDA and HAS_CUPY:
            return self._init_cuda()
        return False

    def _init_opengl(self, target: Optional[RenderTarget]) -> bool:
        """Initialize OpenGL context."""
        try:
            self._gl_context = moderngl.create_context()
            self._create_shaders()
            self._initialized = True
            logger.info("OpenGL GPU renderer initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenGL: {e}")
            return False

    def _init_cuda(self) -> bool:
        """Initialize CUDA context."""
        try:
            if not HAS_CUPY:
                return False
            # Initialize CUDA context
            self._cuda_context = cp.cuda.Device(0)
            self._initialized = True
            logger.info("CUDA GPU renderer initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize CUDA: {e}")
            return False

    def _create_shaders(self) -> None:
        """Create basic shaders for rendering."""
        if not self._gl_context:
            return

        # Vertex shader for lines/points
        vertex_shader = """
        #version 330
        in vec3 position;
        in vec3 color;
        out vec3 vertex_color;
        uniform mat4 mvp_matrix;

        void main() {
            gl_Position = mvp_matrix * vec4(position, 1.0);
            vertex_color = color;
        }
        """

        # Fragment shader
        fragment_shader = """
        #version 330
        in vec3 vertex_color;
        out vec4 frag_color;

        void main() {
            frag_color = vec4(vertex_color, 1.0);
        }
        """

        try:
            self._shaders["basic"] = self._gl_context.program(
                vertex_shader=vertex_shader, fragment_shader=fragment_shader
            )
        except Exception as e:
            logger.error(f"Failed to create shaders: {e}")

    def render_lines(
        self,
        vertices: np.ndarray,
        colors: Optional[np.ndarray] = None,
        thickness: float = 1.0,
    ) -> None:
        """High-performance line rendering."""
        if not self._initialized or not self._gl_context:
            return

        # Create or update vertex buffer
        vertex_data = vertices.astype(np.float32)
        if colors is not None:
            color_data = colors.astype(np.float32)
        else:
            color_data = np.ones((len(vertices), 3), dtype=np.float32)

        # Interleave vertex and color data
        interleaved = np.column_stack((vertex_data, color_data))

        # Upload to GPU and render
        vbo = self._gl_context.buffer(interleaved.tobytes())
        vao = self._gl_context.vertex_array(
            self._shaders["basic"], [(vbo, "3f 3f", "position", "color")]
        )

        self._gl_context.line_width = thickness
        vao.render(
            mode=moderngl.LINES if vertices.shape[0] % 2 == 0 else moderngl.LINE_STRIP
        )

        self._record_frame()

    def render_points(
        self,
        vertices: np.ndarray,
        colors: Optional[np.ndarray] = None,
        size: float = 1.0,
    ) -> None:
        """High-performance point rendering."""
        if not self._initialized or not self._gl_context:
            return

        self._gl_context.point_size = size
        # Similar implementation to render_lines but with POINTS mode
        self._record_frame()

    def render_surface(
        self,
        vertices: np.ndarray,
        indices: np.ndarray,
        colors: Optional[np.ndarray] = None,
    ) -> None:
        """High-performance surface rendering."""
        if not self._initialized or not self._gl_context:
            return

        # Enable depth testing for 3D surfaces
        self._gl_context.enable(moderngl.DEPTH_TEST)
        # Implementation for indexed triangle rendering
        self._record_frame()

    def clear(self, color: Tuple[float, float, float, float] = (0, 0, 0, 1)) -> None:
        """Clear GPU framebuffer."""
        if self._gl_context:
            self._gl_context.clear(color=color)

    def present(self) -> None:
        """Present GPU-rendered frame."""
        if self._gl_context:
            # Swap buffers or blit to target
            pass


class RenderEngine:
    """High-level rendering engine that manages different backends."""

    def __init__(self, config: Optional[RenderConfig] = None) -> None:
        self.config = config or RenderConfig()
        self._renderer: Optional[BaseRenderer] = None
        self._render_thread: Optional[threading.Thread] = None
        self._render_queue: List[Any] = []
        self._queue_lock = threading.Lock()
        self._running = False

    def initialize(self, target: Optional[RenderTarget] = None) -> bool:
        """Initialize the best available renderer."""
        if self.config.backend == RenderBackend.AUTO:
            # Try GPU first, fallback to CPU
            for backend in [
                RenderBackend.OPENGL,
                RenderBackend.CUDA,
                RenderBackend.CPU,
            ]:
                temp_config = RenderConfig(backend=backend)
                renderer = self._create_renderer(temp_config)
                if renderer and renderer.initialize(target):
                    self._renderer = renderer
                    self.config.backend = backend
                    break
        else:
            self._renderer = self._create_renderer(self.config)
            if self._renderer:
                self._renderer.initialize(target)

        if self._renderer:
            logger.info(
                f"Render engine initialized with {self.config.backend.value} backend"
            )
            if self.config.use_threading:
                self._start_render_thread()
            return True

        logger.error("Failed to initialize any rendering backend")
        return False

    def _create_renderer(self, config: RenderConfig) -> Optional[BaseRenderer]:
        """Create appropriate renderer based on config."""
        if config.backend in [RenderBackend.OPENGL, RenderBackend.CUDA]:
            if HAS_OPENGL or HAS_CUPY:
                return GPURenderer(config)
        elif config.backend == RenderBackend.CPU:
            return CPURenderer(config)
        return None

    def _start_render_thread(self) -> None:
        """Start background rendering thread."""
        self._running = True
        self._render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self._render_thread.start()

    def _render_loop(self) -> None:
        """Main rendering loop for threaded rendering."""
        target_frame_time = 1.0 / self.config.max_fps

        while self._running:
            frame_start = time.time()

            # Process render queue
            with self._queue_lock:
                commands = self._render_queue.copy()
                self._render_queue.clear()

            if self._renderer:
                self._renderer.clear()

                for command in commands:
                    self._execute_render_command(command)

                self._renderer.present()

            # Frame rate limiting
            frame_time = time.time() - frame_start
            sleep_time = target_frame_time - frame_time
            if sleep_time > 0:
                time.sleep(sleep_time)

    def _execute_render_command(self, command: Dict[str, Any]) -> None:
        """Execute a render command."""
        if not self._renderer:
            return

        cmd_type = command.get("type")
        if cmd_type == "lines":
            self._renderer.render_lines(**command.get("args", {}))
        elif cmd_type == "points":
            self._renderer.render_points(**command.get("args", {}))
        elif cmd_type == "surface":
            self._renderer.render_surface(**command.get("args", {}))

    def render_lines(self, vertices: np.ndarray, **kwargs) -> None:
        """Queue line rendering command."""
        command = {"type": "lines", "args": {"vertices": vertices, **kwargs}}

        if self.config.use_threading:
            with self._queue_lock:
                self._render_queue.append(command)
        else:
            if self._renderer:
                self._renderer.clear()
                self._execute_render_command(command)
                self._renderer.present()

    def render_points(self, vertices: np.ndarray, **kwargs) -> None:
        """Queue point rendering command."""
        command = {"type": "points", "args": {"vertices": vertices, **kwargs}}

        if self.config.use_threading:
            with self._queue_lock:
                self._render_queue.append(command)
        else:
            if self._renderer:
                self._renderer.clear()
                self._execute_render_command(command)
                self._renderer.present()

    def render_surface(
        self, vertices: np.ndarray, indices: np.ndarray, **kwargs
    ) -> None:
        """Queue surface rendering command."""
        command = {
            "type": "surface",
            "args": {"vertices": vertices, "indices": indices, **kwargs},
        }

        if self.config.use_threading:
            with self._queue_lock:
                self._render_queue.append(command)
        else:
            if self._renderer:
                self._renderer.clear()
                self._execute_render_command(command)
                self._renderer.present()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get rendering performance statistics."""
        if not self._renderer:
            return {}

        return {
            "backend": self.config.backend.value,
            "fps": self._renderer.get_fps(),
            "frame_count": self._renderer._frame_count,
            "uptime": time.time() - self._renderer._start_time,
        }

    def shutdown(self) -> None:
        """Shutdown the rendering engine."""
        self._running = False
        if self._render_thread:
            self._render_thread.join(timeout=1.0)
        logger.info("Render engine shutdown complete")
