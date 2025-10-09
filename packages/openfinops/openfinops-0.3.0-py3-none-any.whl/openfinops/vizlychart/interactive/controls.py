"""
Interactive Controls and Selection Tools
=======================================

Provides zoom, pan, selection, and control panel functionality.
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
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.widgets as widgets
    from matplotlib.patches import Rectangle
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import ipywidgets as ipw
    from IPython.display import display
    HAS_IPYWIDGETS = True
except ImportError:
    HAS_IPYWIDGETS = False

from ..exceptions import VizlyError


class ZoomPanManager:
    """Advanced zoom and pan functionality."""

    def __init__(self, chart):
        self.chart = chart
        self.zoom_history = []
        self.current_zoom_level = 0
        self.zoom_factor = 1.2
        self.pan_sensitivity = 1.0

    def enable_zoom_box(self) -> None:
        """Enable zoom box selection."""
        if not HAS_MATPLOTLIB:
            warnings.warn("Matplotlib required for zoom box")
            return

        def on_zoom_select(eclick, erelease):
            x1, x2 = sorted([eclick.xdata, erelease.xdata])
            y1, y2 = sorted([eclick.ydata, erelease.ydata])

            # Store current view in history
            current_xlim = self.chart.axes.get_xlim()
            current_ylim = self.chart.axes.get_ylim()
            self.zoom_history.append((current_xlim, current_ylim))

            # Apply zoom
            self.chart.axes.set_xlim([x1, x2])
            self.chart.axes.set_ylim([y1, y2])
            self.chart.figure.figure.canvas.draw()

        self.zoom_selector = widgets.RectangleSelector(
            self.chart.axes, on_zoom_select,
            useblit=True, button=[1], minspanx=5, minspany=5,
            spancoords='pixels', interactive=True
        )

    def zoom_to_fit(self) -> None:
        """Zoom to fit all data."""
        if not hasattr(self.chart, 'data_points') or not self.chart.data_points:
            return

        data = self.chart.data_points
        x_data = data.get('x', [])
        y_data = data.get('y', [])

        if len(x_data) == 0 or len(y_data) == 0:
            return

        # Calculate bounds with margin
        margin = 0.05
        x_min, x_max = np.min(x_data), np.max(x_data)
        y_min, y_max = np.min(y_data), np.max(y_data)

        x_margin = (x_max - x_min) * margin
        y_margin = (y_max - y_min) * margin

        self.chart.axes.set_xlim([x_min - x_margin, x_max + x_margin])
        self.chart.axes.set_ylim([y_min - y_margin, y_max + y_margin])
        self.chart.figure.figure.canvas.draw()

    def zoom_reset(self) -> None:
        """Reset zoom to original view."""
        if self.zoom_history:
            original_xlim, original_ylim = self.zoom_history[0]
            self.chart.axes.set_xlim(original_xlim)
            self.chart.axes.set_ylim(original_ylim)
            self.chart.figure.figure.canvas.draw()

    def zoom_previous(self) -> None:
        """Go back to previous zoom level."""
        if len(self.zoom_history) > 1:
            self.zoom_history.pop()  # Remove current
            prev_xlim, prev_ylim = self.zoom_history[-1]
            self.chart.axes.set_xlim(prev_xlim)
            self.chart.axes.set_ylim(prev_ylim)
            self.chart.figure.figure.canvas.draw()


class SelectionManager:
    """Advanced selection and brushing tools."""

    def __init__(self, chart, callback: Optional[Callable] = None):
        self.chart = chart
        self.callback = callback
        self.selection_patches = []
        self.selected_points = []
        self.selection_mode = 'replace'  # 'replace', 'add', 'subtract'

    def on_select(self, eclick, erelease) -> None:
        """Handle selection events."""
        x1, x2 = sorted([eclick.xdata, erelease.xdata])
        y1, y2 = sorted([eclick.ydata, erelease.ydata])

        # Find points in selection
        selected_indices = self._find_points_in_selection(x1, x2, y1, y2)

        # Update selection based on mode
        if self.selection_mode == 'replace':
            self.selected_points = selected_indices
        elif self.selection_mode == 'add':
            self.selected_points.extend(selected_indices)
            self.selected_points = list(set(self.selected_points))  # Remove duplicates
        elif self.selection_mode == 'subtract':
            self.selected_points = [idx for idx in self.selected_points
                                  if idx not in selected_indices]

        # Visual feedback
        self._update_selection_visual()

        # Call user callback
        if self.callback:
            self.callback(self.selected_points, x1, x2, y1, y2)

    def _find_points_in_selection(
        self,
        x1: float, x2: float,
        y1: float, y2: float
    ) -> List[int]:
        """Find data points within selection bounds."""
        if not hasattr(self.chart, 'data_points') or not self.chart.data_points:
            return []

        data = self.chart.data_points
        x_data = np.array(data.get('x', []))
        y_data = np.array(data.get('y', []))

        if len(x_data) == 0:
            return []

        # Find points in rectangle
        mask = ((x_data >= x1) & (x_data <= x2) &
                (y_data >= y1) & (y_data <= y2))

        return np.where(mask)[0].tolist()

    def _update_selection_visual(self) -> None:
        """Update visual representation of selection."""
        if not hasattr(self.chart, '_interactive_elements'):
            return

        scatter = self.chart._interactive_elements.get('scatter')
        if scatter and hasattr(self.chart, 'data_points'):
            data = self.chart.data_points
            n_points = len(data.get('x', []))

            # Create color array
            colors = np.full(n_points, 'blue', dtype=object)
            colors[self.selected_points] = 'red'

            # Update scatter plot colors
            scatter.set_color(colors)
            self.chart.figure.figure.canvas.draw()

    def set_selection_mode(self, mode: str) -> None:
        """Set selection mode: 'replace', 'add', 'subtract'."""
        if mode in ['replace', 'add', 'subtract']:
            self.selection_mode = mode
        else:
            raise ValueError(f"Invalid selection mode: {mode}")

    def clear_selection(self) -> None:
        """Clear current selection."""
        self.selected_points = []
        self._update_selection_visual()

    def select_all(self) -> None:
        """Select all data points."""
        if hasattr(self.chart, 'data_points') and self.chart.data_points:
            n_points = len(self.chart.data_points.get('x', []))
            self.selected_points = list(range(n_points))
            self._update_selection_visual()

    def invert_selection(self) -> None:
        """Invert current selection."""
        if hasattr(self.chart, 'data_points') and self.chart.data_points:
            n_points = len(self.chart.data_points.get('x', []))
            all_indices = set(range(n_points))
            selected_set = set(self.selected_points)
            self.selected_points = list(all_indices - selected_set)
            self._update_selection_visual()


class ControlPanel:
    """Interactive control panel for Jupyter environments."""

    def __init__(self, chart):
        self.chart = chart
        self.widgets = {}
        self.panel = None

    def create_widgets(self) -> None:
        """Create interactive widget controls."""
        if not HAS_IPYWIDGETS:
            warnings.warn("ipywidgets required for control panels")
            return

        # Zoom controls
        zoom_in_btn = ipw.Button(description="🔍 Zoom In", button_style='info')
        zoom_out_btn = ipw.Button(description="🔍 Zoom Out", button_style='info')
        zoom_fit_btn = ipw.Button(description="📐 Fit All", button_style='success')
        zoom_reset_btn = ipw.Button(description="🔄 Reset", button_style='warning')

        # Selection controls
        select_all_btn = ipw.Button(description="☑️ Select All", button_style='')
        clear_selection_btn = ipw.Button(description="❌ Clear", button_style='danger')
        invert_selection_btn = ipw.Button(description="🔄 Invert", button_style='')

        # Mode selection
        selection_mode = ipw.Dropdown(
            options=['replace', 'add', 'subtract'],
            value='replace',
            description='Mode:'
        )

        # Display controls
        if hasattr(self.chart, 'data_points') and self.chart.data_points:
            # Point size slider
            point_size_slider = ipw.IntSlider(
                value=20, min=1, max=100,
                description='Point Size:'
            )

            # Alpha slider
            alpha_slider = ipw.FloatSlider(
                value=0.7, min=0.1, max=1.0, step=0.1,
                description='Transparency:'
            )

            self.widgets.update({
                'point_size': point_size_slider,
                'alpha': alpha_slider
            })

        # Store widgets
        self.widgets.update({
            'zoom_in': zoom_in_btn,
            'zoom_out': zoom_out_btn,
            'zoom_fit': zoom_fit_btn,
            'zoom_reset': zoom_reset_btn,
            'select_all': select_all_btn,
            'clear_selection': clear_selection_btn,
            'invert_selection': invert_selection_btn,
            'selection_mode': selection_mode
        })

        # Connect event handlers
        self._connect_widget_events()

        # Create panel layout
        zoom_box = ipw.HBox([zoom_in_btn, zoom_out_btn, zoom_fit_btn, zoom_reset_btn])
        selection_box = ipw.HBox([select_all_btn, clear_selection_btn, invert_selection_btn])
        mode_box = ipw.HBox([selection_mode])

        panel_items = [
            ipw.HTML("<b>🎛️ Interactive Controls</b>"),
            ipw.HTML("<b>Zoom:</b>"),
            zoom_box,
            ipw.HTML("<b>Selection:</b>"),
            selection_box,
            mode_box
        ]

        # Add display controls if available
        if 'point_size' in self.widgets:
            display_box = ipw.VBox([
                self.widgets['point_size'],
                self.widgets['alpha']
            ])
            panel_items.extend([
                ipw.HTML("<b>Display:</b>"),
                display_box
            ])

        self.panel = ipw.VBox(panel_items)

    def _connect_widget_events(self) -> None:
        """Connect widget events to chart functions."""
        # Zoom controls
        self.widgets['zoom_in'].on_click(lambda b: self._zoom_in())
        self.widgets['zoom_out'].on_click(lambda b: self._zoom_out())
        self.widgets['zoom_fit'].on_click(lambda b: self._zoom_fit())
        self.widgets['zoom_reset'].on_click(lambda b: self._zoom_reset())

        # Selection controls
        self.widgets['select_all'].on_click(lambda b: self._select_all())
        self.widgets['clear_selection'].on_click(lambda b: self._clear_selection())
        self.widgets['invert_selection'].on_click(lambda b: self._invert_selection())

        # Mode selection
        self.widgets['selection_mode'].observe(self._on_mode_change, names='value')

        # Display controls
        if 'point_size' in self.widgets:
            self.widgets['point_size'].observe(self._on_point_size_change, names='value')
            self.widgets['alpha'].observe(self._on_alpha_change, names='value')

    def _zoom_in(self) -> None:
        """Zoom in by fixed factor."""
        xlim = self.chart.axes.get_xlim()
        ylim = self.chart.axes.get_ylim()

        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        x_range = (xlim[1] - xlim[0]) / 1.5
        y_range = (ylim[1] - ylim[0]) / 1.5

        self.chart.axes.set_xlim([x_center - x_range/2, x_center + x_range/2])
        self.chart.axes.set_ylim([y_center - y_range/2, y_center + y_range/2])
        self.chart.figure.figure.canvas.draw()

    def _zoom_out(self) -> None:
        """Zoom out by fixed factor."""
        xlim = self.chart.axes.get_xlim()
        ylim = self.chart.axes.get_ylim()

        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2

        x_range = (xlim[1] - xlim[0]) * 1.5
        y_range = (ylim[1] - ylim[0]) * 1.5

        self.chart.axes.set_xlim([x_center - x_range/2, x_center + x_range/2])
        self.chart.axes.set_ylim([y_center - y_range/2, y_center + y_range/2])
        self.chart.figure.figure.canvas.draw()

    def _zoom_fit(self) -> None:
        """Zoom to fit all data."""
        if hasattr(self.chart, 'zoom_pan_manager'):
            self.chart.zoom_pan_manager.zoom_to_fit()

    def _zoom_reset(self) -> None:
        """Reset zoom."""
        if hasattr(self.chart, 'zoom_pan_manager'):
            self.chart.zoom_pan_manager.zoom_reset()

    def _select_all(self) -> None:
        """Select all points."""
        if hasattr(self.chart, 'selection_manager'):
            self.chart.selection_manager.select_all()

    def _clear_selection(self) -> None:
        """Clear selection."""
        if hasattr(self.chart, 'selection_manager'):
            self.chart.selection_manager.clear_selection()

    def _invert_selection(self) -> None:
        """Invert selection."""
        if hasattr(self.chart, 'selection_manager'):
            self.chart.selection_manager.invert_selection()

    def _on_mode_change(self, change) -> None:
        """Handle selection mode change."""
        if hasattr(self.chart, 'selection_manager'):
            self.chart.selection_manager.set_selection_mode(change['new'])

    def _on_point_size_change(self, change) -> None:
        """Handle point size change."""
        if hasattr(self.chart, '_interactive_elements'):
            scatter = self.chart._interactive_elements.get('scatter')
            if scatter:
                scatter.set_sizes([change['new']] * len(scatter.get_offsets()))
                self.chart.figure.figure.canvas.draw()

    def _on_alpha_change(self, change) -> None:
        """Handle alpha change."""
        if hasattr(self.chart, '_interactive_elements'):
            scatter = self.chart._interactive_elements.get('scatter')
            if scatter:
                scatter.set_alpha(change['new'])
                self.chart.figure.figure.canvas.draw()

    def display(self) -> None:
        """Display the control panel."""
        if self.panel and HAS_IPYWIDGETS:
            display(self.panel)
        else:
            print("Control panel not available (requires ipywidgets)")


class CrossfilterManager:
    """Crossfilter-style interactions between multiple charts."""

    def __init__(self):
        self.charts = {}
        self.filters = {}
        self.linked_selections = True

    def add_chart(self, name: str, chart, data_key: str = 'default') -> None:
        """Add chart to crossfilter system."""
        self.charts[name] = {
            'chart': chart,
            'data_key': data_key,
            'original_data': chart.data_points.copy() if hasattr(chart, 'data_points') else None
        }

        # Connect selection events
        if hasattr(chart, 'selection_manager'):
            chart.selection_manager.callback = lambda selected, x1, x2, y1, y2: \
                self._on_chart_selection(name, selected, x1, x2, y1, y2)

    def _on_chart_selection(
        self,
        source_chart: str,
        selected_indices: List[int],
        x1: float, x2: float,
        y1: float, y2: float
    ) -> None:
        """Handle selection in one chart and update others."""
        if not self.linked_selections:
            return

        # Store filter for source chart
        self.filters[source_chart] = {
            'indices': selected_indices,
            'bounds': (x1, x2, y1, y2)
        }

        # Update other charts
        for chart_name, chart_info in self.charts.items():
            if chart_name != source_chart:
                self._apply_filter_to_chart(chart_name, selected_indices)

    def _apply_filter_to_chart(self, chart_name: str, filtered_indices: List[int]) -> None:
        """Apply filter to a specific chart."""
        chart_info = self.charts[chart_name]
        chart = chart_info['chart']

        if hasattr(chart, 'apply_crossfilter'):
            chart.apply_crossfilter(filtered_indices)

    def clear_all_filters(self) -> None:
        """Clear all active filters."""
        self.filters = {}

        for chart_name, chart_info in self.charts.items():
            chart = chart_info['chart']
            if hasattr(chart, 'clear_crossfilter'):
                chart.clear_crossfilter()

    def toggle_linked_selections(self) -> None:
        """Toggle linked selections on/off."""
        self.linked_selections = not self.linked_selections