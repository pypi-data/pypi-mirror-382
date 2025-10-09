"""
Base Interactive Chart Architecture
===================================

Core infrastructure for interactive chart capabilities.
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

import warnings
from typing import Dict, List, Optional, Callable, Any, Union
from abc import ABC, abstractmethod
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.widgets as widgets
    from matplotlib.backend_bases import Event
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import ipywidgets as ipw
    from IPython.display import display
    HAS_IPYWIDGETS = True
except ImportError:
    HAS_IPYWIDGETS = False

from ..charts.base import BaseChart
from ..exceptions import VizlyError


class InteractionManager:
    """Manages all interactive capabilities for a chart."""

    def __init__(self, chart: BaseChart):
        self.chart = chart
        self.active_interactions: Dict[str, bool] = {}
        self.callbacks: Dict[str, List[Callable]] = {
            'hover': [],
            'click': [],
            'select': [],
            'zoom': [],
            'pan': []
        }
        self._event_connections: Dict[str, Any] = {}

    def enable_interaction(self, interaction_type: str) -> None:
        """Enable a specific type of interaction."""
        if not HAS_MATPLOTLIB:
            warnings.warn("Matplotlib required for interactive features")
            return

        self.active_interactions[interaction_type] = True

        if interaction_type == 'hover':
            self._setup_hover()
        elif interaction_type == 'click':
            self._setup_click()
        elif interaction_type == 'select':
            self._setup_selection()
        elif interaction_type == 'zoom':
            self._setup_zoom()
        elif interaction_type == 'pan':
            self._setup_pan()

    def disable_interaction(self, interaction_type: str) -> None:
        """Disable a specific type of interaction."""
        if interaction_type in self.active_interactions:
            self.active_interactions[interaction_type] = False

        # Disconnect event handlers
        if interaction_type in self._event_connections:
            self.chart.figure.figure.canvas.mpl_disconnect(
                self._event_connections[interaction_type]
            )
            del self._event_connections[interaction_type]

    def add_callback(self, event_type: str, callback: Callable) -> None:
        """Add a callback function for an event type."""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)

    def _setup_hover(self) -> None:
        """Setup hover interaction."""
        def on_hover(event):
            if event.inaxes == self.chart.axes:
                for callback in self.callbacks['hover']:
                    callback(event)

        cid = self.chart.figure.figure.canvas.mpl_connect('motion_notify_event', on_hover)
        self._event_connections['hover'] = cid

    def _setup_click(self) -> None:
        """Setup click interaction."""
        def on_click(event):
            if event.inaxes == self.chart.axes:
                for callback in self.callbacks['click']:
                    callback(event)

        cid = self.chart.figure.figure.canvas.mpl_connect('button_press_event', on_click)
        self._event_connections['click'] = cid

    def _setup_selection(self) -> None:
        """Setup selection interaction."""
        from matplotlib.widgets import RectangleSelector

        def on_select(eclick, erelease):
            for callback in self.callbacks['select']:
                callback(eclick, erelease)

        selector = RectangleSelector(
            self.chart.axes, on_select,
            useblit=True, button=[1], minspanx=5, minspany=5,
            spancoords='pixels', interactive=True
        )
        self._event_connections['select'] = selector

    def _setup_zoom(self) -> None:
        """Setup zoom interaction."""
        def on_scroll(event):
            if event.inaxes == self.chart.axes:
                base_scale = 1.1
                if event.button == 'up':
                    scale_factor = 1 / base_scale
                elif event.button == 'down':
                    scale_factor = base_scale
                else:
                    return

                xlim = self.chart.axes.get_xlim()
                ylim = self.chart.axes.get_ylim()

                # Get cursor position
                xdata, ydata = event.xdata, event.ydata

                # Calculate new limits
                x_left = xdata - (xdata - xlim[0]) * scale_factor
                x_right = xdata + (xlim[1] - xdata) * scale_factor
                y_bottom = ydata - (ydata - ylim[0]) * scale_factor
                y_top = ydata + (ylim[1] - ydata) * scale_factor

                self.chart.axes.set_xlim([x_left, x_right])
                self.chart.axes.set_ylim([y_bottom, y_top])
                self.chart.figure.figure.canvas.draw()

                for callback in self.callbacks['zoom']:
                    callback(event)

        cid = self.chart.figure.figure.canvas.mpl_connect('scroll_event', on_scroll)
        self._event_connections['zoom'] = cid

    def _setup_pan(self) -> None:
        """Setup pan interaction."""
        self.pan_start = None

        def on_press(event):
            if event.inaxes == self.chart.axes and event.button == 2:  # Middle mouse
                self.pan_start = (event.xdata, event.ydata)

        def on_motion(event):
            if (self.pan_start and event.inaxes == self.chart.axes and
                event.xdata and event.ydata):

                dx = self.pan_start[0] - event.xdata
                dy = self.pan_start[1] - event.ydata

                xlim = self.chart.axes.get_xlim()
                ylim = self.chart.axes.get_ylim()

                self.chart.axes.set_xlim([xlim[0] + dx, xlim[1] + dx])
                self.chart.axes.set_ylim([ylim[0] + dy, ylim[1] + dy])
                self.chart.figure.figure.canvas.draw()

        def on_release(event):
            if event.button == 2:
                self.pan_start = None
                for callback in self.callbacks['pan']:
                    callback(event)

        cid1 = self.chart.figure.figure.canvas.mpl_connect('button_press_event', on_press)
        cid2 = self.chart.figure.figure.canvas.mpl_connect('motion_notify_event', on_motion)
        cid3 = self.chart.figure.figure.canvas.mpl_connect('button_release_event', on_release)

        self._event_connections['pan'] = [cid1, cid2, cid3]


class InteractiveChart(BaseChart):
    """Enhanced chart class with interactive capabilities."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interaction_manager = InteractionManager(self)
        self.tooltip_manager = None
        self.selection_manager = None
        self._interactive_elements: Dict[str, Any] = {}

    def enable_tooltips(
        self,
        fields: Optional[List[str]] = None,
        format_func: Optional[Callable] = None
    ) -> 'InteractiveChart':
        """Enable hover tooltips for data inspection."""
        from .tooltips import TooltipManager

        self.tooltip_manager = TooltipManager(self, fields, format_func)
        self.interaction_manager.enable_interaction('hover')
        self.interaction_manager.add_callback('hover', self.tooltip_manager.on_hover)

        return self

    def enable_zoom_pan(self) -> 'InteractiveChart':
        """Enable zoom (scroll) and pan (middle-click drag) interactions."""
        self.interaction_manager.enable_interaction('zoom')
        self.interaction_manager.enable_interaction('pan')

        return self

    def enable_selection(
        self,
        callback: Optional[Callable] = None
    ) -> 'InteractiveChart':
        """Enable rectangular selection tool."""
        from .controls import SelectionManager

        self.selection_manager = SelectionManager(self, callback)
        self.interaction_manager.enable_interaction('select')
        self.interaction_manager.add_callback('select', self.selection_manager.on_select)

        return self

    def add_control_panel(self) -> 'InteractiveChart':
        """Add interactive control panel (requires Jupyter)."""
        if not HAS_IPYWIDGETS:
            warnings.warn("ipywidgets required for control panels")
            return self

        from .controls import ControlPanel

        self.control_panel = ControlPanel(self)
        self.control_panel.create_widgets()

        return self

    def enable_crossfilter(
        self,
        linked_charts: List['InteractiveChart']
    ) -> 'InteractiveChart':
        """Enable crossfilter-style interactions with other charts."""
        def on_selection(eclick, erelease):
            # Get selection bounds
            x1, x2 = sorted([eclick.xdata, erelease.xdata])
            y1, y2 = sorted([eclick.ydata, erelease.ydata])

            # Apply filter to linked charts
            for chart in linked_charts:
                if hasattr(chart, 'apply_filter'):
                    chart.apply_filter(x1, x2, y1, y2)

        self.interaction_manager.enable_interaction('select')
        self.interaction_manager.add_callback('select', on_selection)

        return self

    def show_interactive(self, backend: str = 'auto') -> None:
        """Display chart with interactive backend."""
        if backend == 'auto':
            try:
                # Try to use widget backend in Jupyter
                plt.switch_backend('widget')
            except:
                try:
                    # Fall back to TkAgg for desktop
                    plt.switch_backend('TkAgg')
                except:
                    warnings.warn("No interactive backend available")
        else:
            plt.switch_backend(backend)

        self.show()


class InteractiveScatterChart(InteractiveChart):
    """Interactive scatter chart with enhanced selection and filtering."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_points = None
        self.selected_indices = []

    def plot(
        self,
        x: np.ndarray,
        y: np.ndarray,
        *,
        color=None,
        size=None,
        labels: Optional[List[str]] = None,
        interactive: bool = True,
        **kwargs
    ) -> 'InteractiveScatterChart':
        """Plot interactive scatter chart."""
        # Store data for interaction
        self.data_points = {
            'x': np.array(x),
            'y': np.array(y),
            'labels': labels or [f"Point {i}" for i in range(len(x))]
        }

        if color is not None:
            self.data_points['color'] = np.array(color)
        if size is not None:
            self.data_points['size'] = np.array(size)

        # Create scatter plot
        scatter = self.axes.scatter(x, y, c=color, s=size, **kwargs)
        self._interactive_elements['scatter'] = scatter

        if interactive:
            self.enable_tooltips(['x', 'y', 'labels'])
            self.enable_zoom_pan()
            self.enable_selection()

        return self

    def apply_filter(self, x1: float, x2: float, y1: float, y2: float) -> None:
        """Apply rectangular filter to highlight points."""
        if self.data_points is None:
            return

        x_data = self.data_points['x']
        y_data = self.data_points['y']

        # Find points in selection
        mask = ((x_data >= x1) & (x_data <= x2) &
                (y_data >= y1) & (y_data <= y2))

        self.selected_indices = np.where(mask)[0].tolist()

        # Update visualization to highlight selected points
        scatter = self._interactive_elements.get('scatter')
        if scatter:
            # Reset all point colors
            colors = np.full(len(x_data), 'blue')
            colors[mask] = 'red'  # Highlight selected

            scatter.set_color(colors)
            self.figure.figure.canvas.draw()


class InteractiveLineChart(InteractiveChart):
    """Interactive line chart with data point inspection."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.line_data = None

    def plot(
        self,
        x: np.ndarray,
        y: np.ndarray,
        *,
        interactive: bool = True,
        **kwargs
    ) -> 'InteractiveLineChart':
        """Plot interactive line chart."""
        # Store data for interaction
        self.line_data = {
            'x': np.array(x),
            'y': np.array(y)
        }

        # Create line plot
        line = self.axes.plot(x, y, **kwargs)[0]
        self._interactive_elements['line'] = line

        if interactive:
            self.enable_tooltips(['x', 'y'])
            self.enable_zoom_pan()

        return self

    def add_data_markers(self, indices: List[int], **marker_kwargs) -> None:
        """Add interactive markers at specific data points."""
        if self.line_data is None:
            return

        x_points = self.line_data['x'][indices]
        y_points = self.line_data['y'][indices]

        markers = self.axes.scatter(
            x_points, y_points,
            zorder=5, **marker_kwargs
        )

        self._interactive_elements['markers'] = markers