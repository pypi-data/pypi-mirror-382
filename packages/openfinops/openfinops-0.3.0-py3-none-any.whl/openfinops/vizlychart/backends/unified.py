"""
Unified Backend API
==================

Seamless switching between different visualization backends (matplotlib, plotly, etc.)
while maintaining the same API surface.
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

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import warnings

from ..figure import VizlyFigure
from ..theme import VizlyTheme


class BackendType(Enum):
    """Available visualization backends."""
    MATPLOTLIB = "matplotlib"
    PLOTLY = "plotly"
    BOKEH = "bokeh"
    ALTAIR = "altair"
    PURE = "pure"  # OpenFinOps's pure Python backend


@dataclass
class BackendCapabilities:
    """Capabilities supported by a backend."""
    interactive: bool = False
    web_ready: bool = False
    export_formats: List[str] = None
    supports_3d: bool = False
    supports_animation: bool = False
    supports_streaming: bool = False
    gpu_accelerated: bool = False

    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ['png']


class BackendAdapter(ABC):
    """Abstract adapter for different visualization backends."""

    def __init__(self):
        self.available = self._check_availability()
        self.capabilities = self._get_capabilities()

    @abstractmethod
    def _check_availability(self) -> bool:
        """Check if this backend is available."""
        pass

    @abstractmethod
    def _get_capabilities(self) -> BackendCapabilities:
        """Get backend capabilities."""
        pass

    @abstractmethod
    def create_figure(self, width: int, height: int, theme: VizlyTheme) -> Any:
        """Create a figure object for this backend."""
        pass

    @abstractmethod
    def plot_line(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        """Plot line data."""
        pass

    @abstractmethod
    def plot_scatter(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        """Plot scatter data."""
        pass

    @abstractmethod
    def plot_bar(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        """Plot bar data."""
        pass

    @abstractmethod
    def plot_surface(self, figure: Any, X: np.ndarray, Y: np.ndarray, Z: np.ndarray, **kwargs) -> Any:
        """Plot 3D surface data."""
        pass

    @abstractmethod
    def set_title(self, figure: Any, title: str) -> None:
        """Set figure title."""
        pass

    @abstractmethod
    def set_labels(self, figure: Any, xlabel: str, ylabel: str) -> None:
        """Set axis labels."""
        pass

    @abstractmethod
    def show(self, figure: Any) -> None:
        """Display the figure."""
        pass

    @abstractmethod
    def save(self, figure: Any, filepath: str, dpi: int = 300) -> None:
        """Save figure to file."""
        pass


class MatplotlibAdapter(BackendAdapter):
    """Adapter for matplotlib backend."""

    def _check_availability(self) -> bool:
        try:
            import matplotlib
            import matplotlib.pyplot as plt
            return True
        except ImportError:
            return False

    def _get_capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            interactive=False,
            web_ready=False,
            export_formats=['png', 'jpg', 'pdf', 'svg', 'eps'],
            supports_3d=True,
            supports_animation=True,
            supports_streaming=False,
            gpu_accelerated=False
        )

    def create_figure(self, width: int, height: int, theme: VizlyTheme) -> Any:
        """Create matplotlib figure with theme."""
        import matplotlib.pyplot as plt

        # Apply theme
        theme.apply()

        fig, ax = plt.subplots(figsize=(width/100, height/100))
        return {'figure': fig, 'axes': ax}

    def plot_line(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        ax = figure['axes']
        return ax.plot(x, y, **kwargs)

    def plot_scatter(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        ax = figure['axes']
        return ax.scatter(x, y, **kwargs)

    def plot_bar(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        ax = figure['axes']
        return ax.bar(x, y, **kwargs)

    def plot_surface(self, figure: Any, X: np.ndarray, Y: np.ndarray, Z: np.ndarray, **kwargs) -> Any:
        from mpl_toolkits.mplot3d import Axes3D
        fig = figure['figure']
        ax = fig.add_subplot(111, projection='3d')
        return ax.plot_surface(X, Y, Z, **kwargs)

    def set_title(self, figure: Any, title: str) -> None:
        figure['axes'].set_title(title)

    def set_labels(self, figure: Any, xlabel: str, ylabel: str) -> None:
        ax = figure['axes']
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

    def show(self, figure: Any) -> None:
        import matplotlib.pyplot as plt
        plt.show()

    def save(self, figure: Any, filepath: str, dpi: int = 300) -> None:
        figure['figure'].savefig(filepath, dpi=dpi, bbox_inches='tight')


class PlotlyAdapter(BackendAdapter):
    """Adapter for plotly backend."""

    def _check_availability(self) -> bool:
        try:
            import plotly.graph_objects as go
            import plotly.offline as pyo
            return True
        except ImportError:
            return False

    def _get_capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            interactive=True,
            web_ready=True,
            export_formats=['html', 'png', 'jpg', 'pdf', 'svg'],
            supports_3d=True,
            supports_animation=True,
            supports_streaming=True,
            gpu_accelerated=False
        )

    def create_figure(self, width: int, height: int, theme: VizlyTheme) -> Any:
        """Create plotly figure with theme."""
        import plotly.graph_objects as go

        # Convert theme to plotly layout
        layout = go.Layout(
            width=width,
            height=height,
            paper_bgcolor=theme.background,
            plot_bgcolor=theme.background,
            font=dict(family=theme.font_family, color=theme.palette.get('label', '#000000'))
        )

        fig = go.Figure(layout=layout)
        return fig

    def plot_line(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        import plotly.graph_objects as go

        # Map matplotlib kwargs to plotly
        plotly_kwargs = self._map_kwargs_to_plotly(kwargs, 'line')

        trace = go.Scatter(x=x, y=y, mode='lines', **plotly_kwargs)
        figure.add_trace(trace)
        return trace

    def plot_scatter(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        import plotly.graph_objects as go

        plotly_kwargs = self._map_kwargs_to_plotly(kwargs, 'scatter')

        trace = go.Scatter(x=x, y=y, mode='markers', **plotly_kwargs)
        figure.add_trace(trace)
        return trace

    def plot_bar(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        import plotly.graph_objects as go

        plotly_kwargs = self._map_kwargs_to_plotly(kwargs, 'bar')

        trace = go.Bar(x=x, y=y, **plotly_kwargs)
        figure.add_trace(trace)
        return trace

    def plot_surface(self, figure: Any, X: np.ndarray, Y: np.ndarray, Z: np.ndarray, **kwargs) -> Any:
        import plotly.graph_objects as go

        trace = go.Surface(x=X, y=Y, z=Z)
        figure.add_trace(trace)
        return trace

    def _map_kwargs_to_plotly(self, kwargs: Dict[str, Any], plot_type: str) -> Dict[str, Any]:
        """Map matplotlib-style kwargs to plotly."""
        plotly_kwargs = {}

        # Common mappings
        if 'color' in kwargs:
            if plot_type == 'line':
                plotly_kwargs['line'] = dict(color=kwargs['color'])
            elif plot_type == 'scatter':
                plotly_kwargs['marker'] = dict(color=kwargs['color'])
            elif plot_type == 'bar':
                plotly_kwargs['marker'] = dict(color=kwargs['color'])

        if 'alpha' in kwargs:
            if 'marker' in plotly_kwargs:
                plotly_kwargs['marker']['opacity'] = kwargs['alpha']
            else:
                plotly_kwargs['opacity'] = kwargs['alpha']

        if 'label' in kwargs:
            plotly_kwargs['name'] = kwargs['label']

        if 'linewidth' in kwargs and plot_type == 'line':
            if 'line' not in plotly_kwargs:
                plotly_kwargs['line'] = {}
            plotly_kwargs['line']['width'] = kwargs['linewidth']

        return plotly_kwargs

    def set_title(self, figure: Any, title: str) -> None:
        figure.update_layout(title=title)

    def set_labels(self, figure: Any, xlabel: str, ylabel: str) -> None:
        figure.update_layout(
            xaxis_title=xlabel,
            yaxis_title=ylabel
        )

    def show(self, figure: Any) -> None:
        figure.show()

    def save(self, figure: Any, filepath: str, dpi: int = 300) -> None:
        # Determine format from filepath
        format = filepath.split('.')[-1].lower()

        if format == 'html':
            figure.write_html(filepath)
        elif format in ['png', 'jpg', 'jpeg']:
            figure.write_image(filepath, width=figure.layout.width, height=figure.layout.height)
        elif format == 'pdf':
            figure.write_image(filepath, format='pdf')
        elif format == 'svg':
            figure.write_image(filepath, format='svg')
        else:
            figure.write_html(filepath.replace(f'.{format}', '.html'))


class PureAdapter(BackendAdapter):
    """Adapter for OpenFinOps's pure Python backend."""

    def _check_availability(self) -> bool:
        try:
            from ..rendering.pure_engine import PureRenderer
            return True
        except ImportError:
            return False

    def _get_capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            interactive=False,
            web_ready=False,
            export_formats=['png', 'svg'],
            supports_3d=False,
            supports_animation=False,
            supports_streaming=False,
            gpu_accelerated=True  # OpenFinOps has GPU support
        )

    def create_figure(self, width: int, height: int, theme: VizlyTheme) -> Any:
        """Create pure Python figure."""
        from ..rendering.pure_engine import PureRenderer

        renderer = PureRenderer(width, height)
        return renderer

    def plot_line(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        # Convert to pure renderer calls
        points = [(float(x[i]), float(y[i])) for i in range(len(x))]
        figure.draw_polyline(points)
        return points

    def plot_scatter(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        size = kwargs.get('s', kwargs.get('size', 1.0))
        for i in range(len(x)):
            figure.draw_circle(float(x[i]), float(y[i]), size, fill=True)
        return list(zip(x, y))

    def plot_bar(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        width = kwargs.get('width', 0.8)
        for i in range(len(x)):
            figure.draw_rectangle(float(x[i]) - width/2, 0, width, float(y[i]), fill=True)
        return list(zip(x, y))

    def plot_surface(self, figure: Any, X: np.ndarray, Y: np.ndarray, Z: np.ndarray, **kwargs) -> Any:
        warnings.warn("3D surface plots not supported in pure backend, using contour representation")
        # Simplified contour representation
        return None

    def set_title(self, figure: Any, title: str) -> None:
        # Add title text to figure
        figure.draw_text(figure.width // 2, figure.height - 20, title)

    def set_labels(self, figure: Any, xlabel: str, ylabel: str) -> None:
        # Add axis labels
        figure.draw_text(figure.width // 2, 20, xlabel)
        figure.draw_text(20, figure.height // 2, ylabel, rotation=90)

    def show(self, figure: Any) -> None:
        print("Pure Python backend - use .save() to export")

    def save(self, figure: Any, filepath: str, dpi: int = 300) -> None:
        figure.save(filepath, dpi)


class UnifiedBackend:
    """Unified interface for multiple visualization backends."""

    def __init__(self):
        self._adapters = {
            BackendType.MATPLOTLIB: MatplotlibAdapter(),
            BackendType.PLOTLY: PlotlyAdapter(),
            BackendType.PURE: PureAdapter(),
        }

        self._current_backend = self._detect_best_backend()
        self._fallback_backend = BackendType.PURE

    def _detect_best_backend(self) -> BackendType:
        """Auto-detect the best available backend."""
        # Priority order: Plotly (interactive) -> Matplotlib (mature) -> Pure (fallback)
        for backend_type in [BackendType.PLOTLY, BackendType.MATPLOTLIB, BackendType.PURE]:
            adapter = self._adapters[backend_type]
            if adapter.available:
                return backend_type

        return BackendType.PURE

    def set_backend(self, backend: Union[BackendType, str]) -> bool:
        """Switch to a specific backend."""
        if isinstance(backend, str):
            backend = BackendType(backend.lower())

        adapter = self._adapters.get(backend)
        if not adapter or not adapter.available:
            warnings.warn(f"Backend {backend.value} not available, staying with {self._current_backend.value}")
            return False

        self._current_backend = backend
        return True

    def get_current_backend(self) -> BackendType:
        """Get the currently active backend."""
        return self._current_backend

    def get_capabilities(self) -> BackendCapabilities:
        """Get capabilities of current backend."""
        return self._adapters[self._current_backend].capabilities

    def list_available_backends(self) -> List[BackendType]:
        """List all available backends."""
        return [backend for backend, adapter in self._adapters.items() if adapter.available]

    def create_figure(self, width: int = 800, height: int = 600, theme: Optional[VizlyTheme] = None) -> Any:
        """Create a figure using the current backend."""
        if theme is None:
            from ..theme import apply_theme
            theme = apply_theme('light')

        adapter = self._adapters[self._current_backend]
        return adapter.create_figure(width, height, theme)

    def plot_line(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        """Plot line using current backend."""
        adapter = self._adapters[self._current_backend]
        return adapter.plot_line(figure, x, y, **kwargs)

    def plot_scatter(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        """Plot scatter using current backend."""
        adapter = self._adapters[self._current_backend]
        return adapter.plot_scatter(figure, x, y, **kwargs)

    def plot_bar(self, figure: Any, x: np.ndarray, y: np.ndarray, **kwargs) -> Any:
        """Plot bar using current backend."""
        adapter = self._adapters[self._current_backend]
        return adapter.plot_bar(figure, x, y, **kwargs)

    def plot_surface(self, figure: Any, X: np.ndarray, Y: np.ndarray, Z: np.ndarray, **kwargs) -> Any:
        """Plot 3D surface using current backend."""
        adapter = self._adapters[self._current_backend]
        return adapter.plot_surface(figure, X, Y, Z, **kwargs)

    def set_title(self, figure: Any, title: str) -> None:
        """Set title using current backend."""
        adapter = self._adapters[self._current_backend]
        adapter.set_title(figure, title)

    def set_labels(self, figure: Any, xlabel: str, ylabel: str) -> None:
        """Set labels using current backend."""
        adapter = self._adapters[self._current_backend]
        adapter.set_labels(figure, xlabel, ylabel)

    def show(self, figure: Any) -> None:
        """Show figure using current backend."""
        adapter = self._adapters[self._current_backend]
        adapter.show(figure)

    def save(self, figure: Any, filepath: str, dpi: int = 300) -> None:
        """Save figure using current backend."""
        adapter = self._adapters[self._current_backend]
        adapter.save(figure, filepath, dpi)


# Global unified backend instance
_unified_backend = UnifiedBackend()

def get_backend() -> UnifiedBackend:
    """Get the global unified backend instance."""
    return _unified_backend

def set_backend(backend: Union[BackendType, str]) -> bool:
    """Set the global backend."""
    return _unified_backend.set_backend(backend)

def list_backends() -> List[BackendType]:
    """List available backends."""
    return _unified_backend.list_available_backends()

def get_capabilities() -> BackendCapabilities:
    """Get current backend capabilities."""
    return _unified_backend.get_capabilities()