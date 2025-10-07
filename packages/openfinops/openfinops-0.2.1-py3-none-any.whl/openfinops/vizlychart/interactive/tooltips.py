"""
Tooltip and Data Inspection System
==================================

Provides hover tooltips and data inspection capabilities.
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
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.text import Text
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from ..exceptions import VizlyError


class TooltipManager:
    """Manages hover tooltips for data inspection."""

    def __init__(
        self,
        chart,
        fields: Optional[List[str]] = None,
        format_func: Optional[Callable] = None
    ):
        self.chart = chart
        self.fields = fields or ['x', 'y']
        self.format_func = format_func or self._default_formatter
        self.tooltip_box = None
        self.tooltip_text = None
        self.current_annotation = None
        self.tolerance = 0.05  # Tolerance for point detection

    def on_hover(self, event) -> None:
        """Handle hover events."""
        if not event.inaxes or event.inaxes != self.chart.axes:
            self._hide_tooltip()
            return

        # Find nearest data point
        point_info = self._find_nearest_point(event.xdata, event.ydata)

        if point_info:
            self._show_tooltip(event, point_info)
        else:
            self._hide_tooltip()

    def _find_nearest_point(self, x: float, y: float) -> Optional[Dict[str, Any]]:
        """Find the nearest data point to cursor position."""
        if not hasattr(self.chart, 'data_points') or self.chart.data_points is None:
            return None

        data = self.chart.data_points
        x_data = data.get('x', [])
        y_data = data.get('y', [])

        if len(x_data) == 0 or len(y_data) == 0:
            return None

        # Calculate distances
        distances = np.sqrt((np.array(x_data) - x)**2 + (np.array(y_data) - y)**2)
        min_idx = np.argmin(distances)

        # Check if point is within tolerance
        xlim = self.chart.axes.get_xlim()
        ylim = self.chart.axes.get_ylim()
        x_tolerance = (xlim[1] - xlim[0]) * self.tolerance
        y_tolerance = (ylim[1] - ylim[0]) * self.tolerance

        if distances[min_idx] > max(x_tolerance, y_tolerance):
            return None

        # Gather point information
        point_info = {
            'index': min_idx,
            'x': x_data[min_idx],
            'y': y_data[min_idx]
        }

        # Add additional fields
        for field in self.fields:
            if field in data:
                if isinstance(data[field], (list, np.ndarray)):
                    point_info[field] = data[field][min_idx]
                else:
                    point_info[field] = data[field]

        return point_info

    def _show_tooltip(self, event, point_info: Dict[str, Any]) -> None:
        """Display tooltip with point information."""
        if not HAS_MATPLOTLIB:
            return

        # Format tooltip text
        tooltip_text = self.format_func(point_info)

        # Position tooltip
        x_pos = event.x + 15  # Offset from cursor
        y_pos = event.y + 15

        # Remove previous tooltip
        self._hide_tooltip()

        # Create new annotation
        self.current_annotation = self.chart.axes.annotate(
            tooltip_text,
            xy=(point_info['x'], point_info['y']),
            xytext=(x_pos, y_pos),
            textcoords='figure pixels',
            bbox=dict(boxstyle='round,pad=0.5', fc='lightyellow', alpha=0.9),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
            fontsize=9,
            ha='left'
        )

        self.chart.figure.figure.canvas.draw_idle()

    def _hide_tooltip(self) -> None:
        """Hide current tooltip."""
        if self.current_annotation:
            self.current_annotation.remove()
            self.current_annotation = None
            self.chart.figure.figure.canvas.draw_idle()

    def _default_formatter(self, point_info: Dict[str, Any]) -> str:
        """Default tooltip formatting."""
        lines = []

        for field in self.fields:
            if field in point_info:
                value = point_info[field]
                if isinstance(value, (int, float)):
                    if field in ['x', 'y']:
                        lines.append(f"{field}: {value:.3f}")
                    else:
                        lines.append(f"{field}: {value}")
                else:
                    lines.append(f"{field}: {value}")

        return '\n'.join(lines)


class HoverInspector:
    """Advanced data inspection with detailed hover information."""

    def __init__(self, chart):
        self.chart = chart
        self.inspection_panel = None
        self.current_data = None

    def enable_inspection(
        self,
        panel_position: str = 'right',
        show_statistics: bool = True,
        show_neighbors: bool = True
    ) -> None:
        """Enable detailed data inspection."""
        self.show_statistics = show_statistics
        self.show_neighbors = show_neighbors
        self.panel_position = panel_position

        # Add inspection panel to figure
        self._create_inspection_panel()

        # Connect hover events
        self.chart.interaction_manager.add_callback('hover', self.on_inspect)

    def on_inspect(self, event) -> None:
        """Handle inspection events."""
        if not event.inaxes or event.inaxes != self.chart.axes:
            self._clear_inspection()
            return

        # Get detailed point information
        detailed_info = self._get_detailed_info(event.xdata, event.ydata)

        if detailed_info:
            self._update_inspection_panel(detailed_info)
        else:
            self._clear_inspection()

    def _create_inspection_panel(self) -> None:
        """Create inspection panel as subplot."""
        if not HAS_MATPLOTLIB:
            return

        # Adjust main axes to make room for panel
        current_pos = self.chart.axes.get_position()

        if self.panel_position == 'right':
            # Shrink main axes
            new_pos = [current_pos.x0, current_pos.y0,
                      current_pos.width * 0.7, current_pos.height]
            self.chart.axes.set_position(new_pos)

            # Create panel axes
            panel_pos = [current_pos.x0 + current_pos.width * 0.75, current_pos.y0,
                        current_pos.width * 0.25, current_pos.height]
            self.inspection_panel = self.chart.figure.figure.add_axes(panel_pos)

        self.inspection_panel.set_xlim(0, 1)
        self.inspection_panel.set_ylim(0, 1)
        self.inspection_panel.set_xticks([])
        self.inspection_panel.set_yticks([])
        self.inspection_panel.set_title('Data Inspection', fontsize=10)

    def _get_detailed_info(self, x: float, y: float) -> Optional[Dict[str, Any]]:
        """Get detailed information about data point."""
        if not hasattr(self.chart, 'data_points') or self.chart.data_points is None:
            return None

        data = self.chart.data_points
        x_data = np.array(data.get('x', []))
        y_data = np.array(data.get('y', []))

        if len(x_data) == 0:
            return None

        # Find nearest point
        distances = np.sqrt((x_data - x)**2 + (y_data - y)**2)
        min_idx = np.argmin(distances)

        # Check tolerance
        xlim = self.chart.axes.get_xlim()
        ylim = self.chart.axes.get_ylim()
        tolerance = max((xlim[1] - xlim[0]) * 0.05, (ylim[1] - ylim[0]) * 0.05)

        if distances[min_idx] > tolerance:
            return None

        # Gather detailed information
        info = {
            'index': min_idx,
            'x': x_data[min_idx],
            'y': y_data[min_idx],
            'distance_from_cursor': distances[min_idx]
        }

        # Add all available fields
        for field, values in data.items():
            if field not in ['x', 'y'] and isinstance(values, (list, np.ndarray)):
                info[field] = values[min_idx]

        # Add statistics if requested
        if self.show_statistics:
            info['statistics'] = {
                'x_mean': np.mean(x_data),
                'x_std': np.std(x_data),
                'y_mean': np.mean(y_data),
                'y_std': np.std(y_data)
            }

        # Add neighbor information
        if self.show_neighbors and len(x_data) > 1:
            # Find 3 nearest neighbors
            sorted_indices = np.argsort(distances)
            neighbors = []
            for i in range(1, min(4, len(sorted_indices))):
                neighbor_idx = sorted_indices[i]
                neighbors.append({
                    'index': neighbor_idx,
                    'x': x_data[neighbor_idx],
                    'y': y_data[neighbor_idx],
                    'distance': distances[neighbor_idx]
                })
            info['neighbors'] = neighbors

        return info

    def _update_inspection_panel(self, info: Dict[str, Any]) -> None:
        """Update inspection panel with detailed information."""
        if not self.inspection_panel:
            return

        # Clear previous content
        self.inspection_panel.clear()
        self.inspection_panel.set_xlim(0, 1)
        self.inspection_panel.set_ylim(0, 1)
        self.inspection_panel.set_xticks([])
        self.inspection_panel.set_yticks([])

        # Format information text
        text_lines = []
        text_lines.append(f"Point #{info['index']}")
        text_lines.append(f"X: {info['x']:.4f}")
        text_lines.append(f"Y: {info['y']:.4f}")

        # Add additional fields
        for key, value in info.items():
            if key not in ['index', 'x', 'y', 'statistics', 'neighbors', 'distance_from_cursor']:
                if isinstance(value, (int, float)):
                    text_lines.append(f"{key}: {value:.4f}")
                else:
                    text_lines.append(f"{key}: {value}")

        # Add statistics
        if 'statistics' in info:
            text_lines.append("")
            text_lines.append("Dataset Statistics:")
            stats = info['statistics']
            text_lines.append(f"X̄: {stats['x_mean']:.3f} ±{stats['x_std']:.3f}")
            text_lines.append(f"Ȳ: {stats['y_mean']:.3f} ±{stats['y_std']:.3f}")

        # Add neighbors
        if 'neighbors' in info:
            text_lines.append("")
            text_lines.append("Nearest Neighbors:")
            for i, neighbor in enumerate(info['neighbors'][:3]):
                text_lines.append(
                    f"{i+1}. #{neighbor['index']} "
                    f"({neighbor['x']:.3f}, {neighbor['y']:.3f})"
                )

        # Display text
        text_content = '\n'.join(text_lines)
        self.inspection_panel.text(
            0.05, 0.95, text_content,
            transform=self.inspection_panel.transAxes,
            fontsize=8, verticalalignment='top',
            fontfamily='monospace'
        )

        self.chart.figure.figure.canvas.draw_idle()

    def _clear_inspection(self) -> None:
        """Clear inspection panel."""
        if self.inspection_panel:
            self.inspection_panel.clear()
            self.inspection_panel.set_xlim(0, 1)
            self.inspection_panel.set_ylim(0, 1)
            self.inspection_panel.set_xticks([])
            self.inspection_panel.set_yticks([])
            self.inspection_panel.text(
                0.5, 0.5, 'Hover over data points\nfor detailed inspection',
                transform=self.inspection_panel.transAxes,
                ha='center', va='center',
                fontsize=10, alpha=0.6
            )
            self.chart.figure.figure.canvas.draw_idle()


class AdvancedTooltip:
    """Advanced tooltip with rich formatting and multiple data series."""

    def __init__(self, chart):
        self.chart = chart
        self.tooltip_style = {
            'boxstyle': 'round,pad=0.5',
            'facecolor': 'lightyellow',
            'alpha': 0.95,
            'edgecolor': 'gray'
        }
        self.arrow_style = {
            'arrowstyle': '->',
            'color': 'gray',
            'alpha': 0.7
        }

    def set_style(
        self,
        background_color: str = 'lightyellow',
        alpha: float = 0.95,
        border_color: str = 'gray',
        font_size: int = 9
    ) -> None:
        """Customize tooltip appearance."""
        self.tooltip_style.update({
            'facecolor': background_color,
            'alpha': alpha,
            'edgecolor': border_color
        })
        self.font_size = font_size

    def create_rich_tooltip(
        self,
        x: float,
        y: float,
        data: Dict[str, Any],
        template: Optional[str] = None
    ) -> str:
        """Create rich formatted tooltip."""
        if template:
            return template.format(**data)

        # Default rich formatting
        lines = []

        # Header
        if 'label' in data:
            lines.append(f"📊 {data['label']}")
        else:
            lines.append(f"📊 Data Point #{data.get('index', 'N/A')}")

        lines.append("─" * 20)

        # Coordinates
        lines.append(f"📍 Position: ({x:.3f}, {y:.3f})")

        # Additional data
        for key, value in data.items():
            if key not in ['x', 'y', 'index', 'label']:
                if isinstance(value, (int, float)):
                    if abs(value) > 1000:
                        lines.append(f"💹 {key}: {value:,.2f}")
                    else:
                        lines.append(f"📈 {key}: {value:.4f}")
                else:
                    lines.append(f"🏷️ {key}: {value}")

        return '\n'.join(lines)