"""
Pure Python Renderer
Replaces matplotlib with native rendering capabilities.
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



import numpy as np
from typing import Union
from .canvas import Canvas, Color, Point, Rectangle


class PureRenderer:
    """Pure Python renderer replacing matplotlib backend."""

    def __init__(self, width: int = 800, height: int = 600, dpi: int = 100):
        self.width = width
        self.height = height
        self.dpi = dpi

        # Create canvas
        self.canvas = Canvas(width, height)

        # Plot area (with margins)
        self.margin_left = 80
        self.margin_right = 20
        self.margin_top = 20
        self.margin_bottom = 60

        self.plot_area = Rectangle(
            self.margin_left,
            self.margin_top,
            self.width - self.margin_left - self.margin_right,
            self.height - self.margin_top - self.margin_bottom,
        )

        # Data ranges
        self.x_min = 0.0
        self.x_max = 1.0
        self.y_min = 0.0
        self.y_max = 1.0

        # Style settings
        self.grid_color = Color(0.9, 0.9, 0.9)
        self.axis_color = Color(0.0, 0.0, 0.0)
        self.text_color = Color(0.0, 0.0, 0.0)

    def set_xlim(self, x_min: float, x_max: float):
        """Set X-axis limits."""
        self.x_min = x_min
        self.x_max = x_max

    def set_ylim(self, y_min: float, y_max: float):
        """Set Y-axis limits."""
        self.y_min = y_min
        self.y_max = y_max

    def data_to_pixel(self, x: float, y: float) -> Point:
        """Convert data coordinates to pixel coordinates."""
        # Normalize to [0, 1]
        x_norm = (x - self.x_min) / (self.x_max - self.x_min)
        y_norm = (y - self.y_min) / (self.y_max - self.y_min)

        # Convert to plot area pixels
        pixel_x = self.plot_area.x + x_norm * self.plot_area.width
        pixel_y = (
            self.plot_area.y + self.plot_area.height - y_norm * self.plot_area.height
        )

        return Point(pixel_x, pixel_y)

    def draw_grid(self, x_ticks: int = 10, y_ticks: int = 10):
        """Draw grid lines."""
        # Vertical grid lines
        for i in range(x_ticks + 1):
            x = self.x_min + i * (self.x_max - self.x_min) / x_ticks
            pixel_point = self.data_to_pixel(x, self.y_min)
            pixel_point_top = self.data_to_pixel(x, self.y_max)

            self.canvas.draw_line(
                Point(pixel_point.x, pixel_point.y),
                Point(pixel_point_top.x, pixel_point_top.y),
                self.grid_color,
                1.0,
            )

        # Horizontal grid lines
        for i in range(y_ticks + 1):
            y = self.y_min + i * (self.y_max - self.y_min) / y_ticks
            pixel_point = self.data_to_pixel(self.x_min, y)
            pixel_point_right = self.data_to_pixel(self.x_max, y)

            self.canvas.draw_line(
                Point(pixel_point.x, pixel_point.y),
                Point(pixel_point_right.x, pixel_point_right.y),
                self.grid_color,
                1.0,
            )

    def draw_axes(self):
        """Draw X and Y axes."""
        # X-axis
        x_start = self.data_to_pixel(self.x_min, 0)
        x_end = self.data_to_pixel(self.x_max, 0)

        # Check if y=0 is in range
        if self.y_min <= 0 <= self.y_max:
            self.canvas.draw_line(x_start, x_end, self.axis_color, 2.0)

        # Y-axis
        y_start = self.data_to_pixel(0, self.y_min)
        y_end = self.data_to_pixel(0, self.y_max)

        # Check if x=0 is in range
        if self.x_min <= 0 <= self.x_max:
            self.canvas.draw_line(y_start, y_end, self.axis_color, 2.0)

        # Frame around plot area
        self.canvas.draw_rectangle(
            self.plot_area, border_color=self.axis_color, border_width=1.0
        )

    def draw_line_plot(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        color: Union[Color, str] = None,
        line_width: float = 2.0,
        label: str = None,
    ):
        """Draw line plot."""
        if isinstance(color, str):
            color = Color.from_name(color)
        elif color is None:
            color = Color(0.0, 0.0, 1.0)  # Default blue

        points = []
        for x, y in zip(x_data, y_data):
            if not (np.isnan(x) or np.isnan(y)):
                points.append(self.data_to_pixel(float(x), float(y)))

        # Draw connected line segments
        for i in range(len(points) - 1):
            self.canvas.draw_line(points[i], points[i + 1], color, line_width)

    def draw_scatter_plot(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        colors: np.ndarray = None,
        sizes: np.ndarray = None,
        marker: str = "o",
    ):
        """Draw scatter plot."""
        default_size = 3.0
        default_color = Color(1.0, 0.0, 0.0)  # Red

        for i, (x, y) in enumerate(zip(x_data, y_data)):
            if np.isnan(x) or np.isnan(y):
                continue

            pixel_point = self.data_to_pixel(float(x), float(y))

            # Determine size
            size = default_size
            if sizes is not None and i < len(sizes):
                size = float(sizes[i])

            # Determine color
            color = default_color
            if colors is not None:
                if len(colors.shape) == 1:  # Color map values
                    if i < len(colors):
                        # Map value to color (simple implementation)
                        val = float(colors[i])
                        color = Color(val, 1.0 - val, 0.5)
                elif len(colors.shape) == 2:  # RGB values
                    if i < len(colors):
                        rgb = colors[i]
                        color = Color(float(rgb[0]), float(rgb[1]), float(rgb[2]))

            # Draw marker
            if marker == "o":
                self.canvas.draw_circle(pixel_point, size, fill_color=color)
            elif marker == "s":
                from .canvas import Rectangle

                rect = Rectangle(
                    pixel_point.x - size, pixel_point.y - size, size * 2, size * 2
                )
                self.canvas.draw_rectangle(rect, fill_color=color)

    def draw_bar_chart(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        width: float = 0.8,
        color: Union[Color, str] = None,
    ):
        """Draw bar chart."""
        if isinstance(color, str):
            color = Color.from_name(color)
        elif color is None:
            color = Color(0.0, 0.5, 1.0)  # Default blue

        # Calculate bar width in pixels
        data_width = (self.x_max - self.x_min) / len(x_data) * width
        pixel_width = data_width * self.plot_area.width / (self.x_max - self.x_min)

        for x, y in zip(x_data, y_data):
            if np.isnan(x) or np.isnan(y):
                continue

            # Bar bottom
            bottom_point = self.data_to_pixel(float(x), 0)
            top_point = self.data_to_pixel(float(x), float(y))

            # Create rectangle for bar
            from .canvas import Rectangle

            bar_rect = Rectangle(
                bottom_point.x - pixel_width / 2,
                min(bottom_point.y, top_point.y),
                pixel_width,
                abs(top_point.y - bottom_point.y),
            )

            self.canvas.draw_rectangle(
                bar_rect,
                fill_color=color,
                border_color=Color(0, 0, 0),
                border_width=1.0,
            )

    def draw_labels(self, title: str = None, xlabel: str = None, ylabel: str = None):
        """Draw plot labels."""
        font_size = 14

        # Title
        if title:
            title_pos = Point(self.width // 2, 15)
            self.canvas.draw_text(title, title_pos, self.text_color, font_size + 2)

        # X-label
        if xlabel:
            xlabel_pos = Point(
                self.plot_area.x + self.plot_area.width // 2, self.height - 20
            )
            self.canvas.draw_text(xlabel, xlabel_pos, self.text_color, font_size)

        # Y-label (rotated)
        if ylabel:
            ylabel_pos = Point(15, self.plot_area.y + self.plot_area.height // 2)
            # Note: Text rotation would need more complex implementation
            self.canvas.draw_text(ylabel, ylabel_pos, self.text_color, font_size)

    def draw_ticks(self, x_ticks: int = 5, y_ticks: int = 5):
        """Draw axis tick marks and labels."""
        tick_size = 5
        font_size = 10

        # X-axis ticks
        for i in range(x_ticks + 1):
            x_val = self.x_min + i * (self.x_max - self.x_min) / x_ticks
            pixel_point = self.data_to_pixel(x_val, self.y_min)

            # Tick mark
            self.canvas.draw_line(
                Point(pixel_point.x, pixel_point.y),
                Point(pixel_point.x, pixel_point.y + tick_size),
                self.axis_color,
                1.0,
            )

            # Tick label
            label = f"{x_val:.1f}"
            label_pos = Point(pixel_point.x - 10, pixel_point.y + 15)
            self.canvas.draw_text(label, label_pos, self.text_color, font_size)

        # Y-axis ticks
        for i in range(y_ticks + 1):
            y_val = self.y_min + i * (self.y_max - self.y_min) / y_ticks
            pixel_point = self.data_to_pixel(self.x_min, y_val)

            # Tick mark
            self.canvas.draw_line(
                Point(pixel_point.x - tick_size, pixel_point.y),
                Point(pixel_point.x, pixel_point.y),
                self.axis_color,
                1.0,
            )

            # Tick label
            label = f"{y_val:.1f}"
            label_pos = Point(pixel_point.x - 30, pixel_point.y)
            self.canvas.draw_text(label, label_pos, self.text_color, font_size)

    def save(self, filename: str):
        """Save the plot to file."""
        self.canvas.save_png(filename)

    def clear(self):
        """Clear the canvas."""
        self.canvas.clear()


class ImageRenderer(PureRenderer):
    """Image-focused renderer for static output."""

    def __init__(self, width: int = 800, height: int = 600, dpi: int = 100):
        super().__init__(width, height, dpi)

    def create_figure(self) -> "Figure":
        """Create a matplotlib-like figure interface."""
        return Figure(self)


class Figure:
    """Matplotlib-like figure interface."""

    def __init__(self, renderer: PureRenderer):
        self.renderer = renderer
        self.axes = []

    def add_subplot(self, rows: int = 1, cols: int = 1, index: int = 1) -> "Axes":
        """Add subplot (simplified implementation)."""
        # For now, just return single axes
        axes = Axes(self.renderer)
        self.axes.append(axes)
        return axes

    def savefig(self, filename: str, dpi: int = None):
        """Save figure to file."""
        self.renderer.save(filename)

    def show(self):
        """Display figure (placeholder)."""
        print("Figure would be displayed here")


class Axes:
    """Matplotlib-like axes interface."""

    def __init__(self, renderer: PureRenderer):
        self.renderer = renderer

    def plot(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        color: str = None,
        linewidth: float = 2.0,
        label: str = None,
    ):
        """Plot line."""
        # Auto-scale data
        if hasattr(self.renderer, "_auto_scale"):
            self.renderer._auto_scale = True
        else:
            self.renderer.set_xlim(float(np.min(x_data)), float(np.max(x_data)))
            self.renderer.set_ylim(float(np.min(y_data)), float(np.max(y_data)))

        self.renderer.draw_grid()
        self.renderer.draw_axes()
        self.renderer.draw_line_plot(x_data, y_data, color, linewidth, label)
        self.renderer.draw_ticks()

    def scatter(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        c: np.ndarray = None,
        s: np.ndarray = None,
        marker: str = "o",
    ):
        """Scatter plot."""
        # Auto-scale data
        self.renderer.set_xlim(float(np.min(x_data)), float(np.max(x_data)))
        self.renderer.set_ylim(float(np.min(y_data)), float(np.max(y_data)))

        self.renderer.draw_grid()
        self.renderer.draw_axes()
        self.renderer.draw_scatter_plot(x_data, y_data, c, s, marker)
        self.renderer.draw_ticks()

    def bar(
        self,
        x_data: np.ndarray,
        y_data: np.ndarray,
        color: str = None,
        width: float = 0.8,
    ):
        """Bar chart."""
        # Auto-scale data
        self.renderer.set_xlim(float(np.min(x_data)) - 0.5, float(np.max(x_data)) + 0.5)
        self.renderer.set_ylim(0, float(np.max(y_data)) * 1.1)

        self.renderer.draw_grid()
        self.renderer.draw_axes()
        self.renderer.draw_bar_chart(x_data, y_data, width, color)
        self.renderer.draw_ticks()

    def set_xlabel(self, label: str):
        """Set X-axis label."""
        # Store for later rendering
        self._xlabel = label

    def set_ylabel(self, label: str):
        """Set Y-axis label."""
        # Store for later rendering
        self._ylabel = label

    def set_title(self, title: str):
        """Set plot title."""
        # Store for later rendering
        self._title = title

    def grid(self, visible: bool = True):
        """Toggle grid visibility."""
        if visible:
            self.renderer.draw_grid()

    def legend(self):
        """Add legend (placeholder)."""
        pass
