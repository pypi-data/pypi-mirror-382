"""
Export utilities for pure Python renderer.
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
from .canvas import Canvas


class PNGExporter:
    """PNG export functionality."""

    @staticmethod
    def save(canvas: Canvas, filename: str):
        """Save canvas as PNG."""
        canvas.save_png(filename)


class SVGExporter:
    """SVG export functionality."""

    @staticmethod
    def save(canvas: Canvas, filename: str):
        """Save canvas as SVG."""
        svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{canvas.width}" height="{canvas.height}" xmlns="http://www.w3.org/2000/svg">
<rect width="100%" height="100%" fill="rgb{canvas.background.to_rgb_tuple()}"/>
</svg>"""

        with open(filename, "w") as f:
            f.write(svg_content)


class PDFExporter:
    """PDF export functionality (basic implementation)."""

    @staticmethod
    def save(canvas: Canvas, filename: str):
        """Save canvas as PDF (placeholder)."""
        # This would require a more complex PDF implementation
        # For now, save as PNG with PDF extension
        png_filename = filename.replace(".pdf", ".png")
        canvas.save_png(png_filename)
        print(f"Note: Saved as PNG instead: {png_filename}")


# Create matplotlib-compatible interface
def pyplot():
    """Create matplotlib.pyplot-like interface."""
    from .renderer import ImageRenderer, Figure

    # Global state
    _current_figure = None
    _current_renderer = None

    def figure(figsize: tuple = (8, 6), dpi: int = 100):
        """Create new figure."""
        global _current_figure, _current_renderer
        width = int(figsize[0] * dpi)
        height = int(figsize[1] * dpi)
        _current_renderer = ImageRenderer(width, height, dpi)
        _current_figure = Figure(_current_renderer)
        return _current_figure

    def subplot(rows: int = 1, cols: int = 1, index: int = 1):
        """Create subplot."""
        if _current_figure is None:
            figure()
        return _current_figure.add_subplot(rows, cols, index)

    def plot(x_data: np.ndarray, y_data: np.ndarray, *args, **kwargs):
        """Plot data."""
        if _current_figure is None:
            figure()

        ax = _current_figure.add_subplot()
        ax.plot(x_data, y_data, **kwargs)

    def scatter(x_data: np.ndarray, y_data: np.ndarray, *args, **kwargs):
        """Scatter plot."""
        if _current_figure is None:
            figure()

        ax = _current_figure.add_subplot()
        ax.scatter(x_data, y_data, **kwargs)

    def bar(x_data: np.ndarray, y_data: np.ndarray, *args, **kwargs):
        """Bar chart."""
        if _current_figure is None:
            figure()

        ax = _current_figure.add_subplot()
        ax.bar(x_data, y_data, **kwargs)

    def xlabel(label: str):
        """Set X-axis label."""
        if _current_figure and _current_figure.axes:
            _current_figure.axes[-1].set_xlabel(label)

    def ylabel(label: str):
        """Set Y-axis label."""
        if _current_figure and _current_figure.axes:
            _current_figure.axes[-1].set_ylabel(label)

    def title(title_text: str):
        """Set plot title."""
        if _current_figure and _current_figure.axes:
            _current_figure.axes[-1].set_title(title_text)

    def grid(visible: bool = True):
        """Toggle grid."""
        if _current_figure and _current_figure.axes:
            _current_figure.axes[-1].grid(visible)

    def legend():
        """Add legend."""
        if _current_figure and _current_figure.axes:
            _current_figure.axes[-1].legend()

    def savefig(filename: str, dpi: int = None):
        """Save figure."""
        if _current_figure:
            _current_figure.savefig(filename, dpi)

    def show():
        """Show figure."""
        if _current_figure:
            _current_figure.show()

    def clf():
        """Clear figure."""
        global _current_figure, _current_renderer
        if _current_renderer:
            _current_renderer.clear()

    def close():
        """Close figure."""
        global _current_figure, _current_renderer
        _current_figure = None
        _current_renderer = None

    # Return module-like object
    class PyplotModule:
        pass

    module = PyplotModule()
    module.figure = figure
    module.subplot = subplot
    module.plot = plot
    module.scatter = scatter
    module.bar = bar
    module.xlabel = xlabel
    module.ylabel = ylabel
    module.title = title
    module.grid = grid
    module.legend = legend
    module.savefig = savefig
    module.show = show
    module.clf = clf
    module.close = close

    return module
