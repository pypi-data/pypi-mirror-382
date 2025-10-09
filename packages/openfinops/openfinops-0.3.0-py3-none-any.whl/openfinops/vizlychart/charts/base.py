"""Common chart scaffolding for Vizly."""

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

from dataclasses import dataclass, field
from typing import Iterable, Sequence, Union, Optional
import warnings

import numpy as np

from ..exceptions import ChartValidationError
from ..figure import VizlyFigure


def _to_numpy(sequence: Sequence[float] | Iterable[float]) -> np.ndarray:
    """Convert sequence to numpy array with improved error handling."""
    try:
        if isinstance(sequence, np.ndarray):
            return sequence.astype(float)
        return np.asarray(list(sequence), dtype=float)
    except (ValueError, TypeError) as e:
        raise ChartValidationError(f"Unable to convert data to numeric array: {e}")


def _sanitize_data(
    data: Union[Sequence[float], Iterable[float], np.ndarray], max_size: int = 1_000_000
) -> np.ndarray:
    """Sanitize and validate input data with safety checks."""
    # Convert to numpy array
    arr = _to_numpy(data)

    # Check for reasonable data size
    if arr.size > max_size:
        warnings.warn(
            f"Large dataset detected ({arr.size:,} points). "
            f"Consider using data sampling for better performance.",
            UserWarning,
        )

    # Check for suspicious patterns
    if arr.size > 0:
        # Check for all identical values (might indicate data loading issues)
        if np.all(arr == arr[0]) and arr.size > 10:
            warnings.warn(
                "All data values are identical. Please verify data source.", UserWarning
            )

        # Check for extreme outliers (values beyond 6 standard deviations)
        if arr.size > 3:  # Need at least a few points for meaningful stats
            std_dev = np.std(arr)
            mean_val = np.mean(arr)
            if std_dev > 0:
                z_scores = np.abs((arr - mean_val) / std_dev)
                extreme_outliers = np.sum(z_scores > 6)
                if extreme_outliers > 0:
                    warnings.warn(
                        f"Found {extreme_outliers} extreme outliers. "
                        f"Consider data cleaning or outlier handling.",
                        UserWarning,
                    )

    return arr


@dataclass
class BaseChart:
    """Base class for all Vizly charts."""

    figure: VizlyFigure | int | None = None
    label: str | None = None
    autoset_labels: bool = True
    width: float | int | None = None
    height: float | int | None = None
    _axes: object = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # Handle different initialization patterns
        if isinstance(self.figure, int):
            # Called with BaseChart(width, height) pattern
            self.width = self.figure
            self.height = self.width if self.width is None else getattr(self, '_second_param', self.width)
            self.figure = None

        if self.figure is None:
            # Create figure with specified dimensions if provided
            if self.width is not None or self.height is not None:
                # Convert pixel values to inches (assuming 100 DPI)
                width_inches = (self.width / 100) if self.width else 10.0
                height_inches = (self.height / 100) if self.height else 8.0
                self.figure = VizlyFigure(width=width_inches, height=height_inches)
            else:
                self.figure = VizlyFigure()
        self._axes = self.figure.axes

    @property
    def axes(self):  # type: ignore[override]
        return self._axes

    def _validate_xy(
        self,
        x_values: Sequence[float] | Iterable[float],
        y_values: Sequence[float] | Iterable[float],
        sanitize: bool = True,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Enhanced validation with data sanitization and safety checks."""
        if sanitize:
            x = _sanitize_data(x_values)
            y = _sanitize_data(y_values)
        else:
            x = _to_numpy(x_values)
            y = _to_numpy(y_values)

        if x.size != y.size:
            raise ChartValidationError(
                f"x and y must be the same length (got {x.size} and {y.size})"
            )

        if x.size == 0:
            raise ChartValidationError("Cannot plot empty datasets")

        # Check for finite values
        x_finite = np.isfinite(x)
        y_finite = np.isfinite(y)

        if not np.all(x_finite):
            invalid_count = np.sum(~x_finite)
            if invalid_count == x.size:
                raise ChartValidationError("All x values are invalid (inf/nan)")
            warnings.warn(
                f"Found {invalid_count} invalid x values (inf/nan). These will be excluded.",
                UserWarning,
            )

        if not np.all(y_finite):
            invalid_count = np.sum(~y_finite)
            if invalid_count == y.size:
                raise ChartValidationError("All y values are invalid (inf/nan)")
            warnings.warn(
                f"Found {invalid_count} invalid y values (inf/nan). These will be excluded.",
                UserWarning,
            )

        # Filter out invalid values
        valid_mask = x_finite & y_finite
        if np.sum(valid_mask) < x.size:
            x = x[valid_mask]
            y = y[valid_mask]

        if x.size == 0:
            raise ChartValidationError("No valid data points remaining after filtering")

        return x, y

    def _maybe_set_labels(self, xlabel: str | None, ylabel: str | None) -> None:
        if not self.autoset_labels:
            return
        if xlabel:
            self.axes.set_xlabel(xlabel)
        if ylabel:
            self.axes.set_ylabel(ylabel)

    def bind_axes(self, axes) -> None:
        """Bind operations to a different axes instance."""
        self._axes = axes

    def set_title(
        self, title: str, fontsize: int = 14, fontweight: str = "bold"
    ) -> None:
        """Set the chart title."""
        self.axes.set_title(title, fontsize=fontsize, fontweight=fontweight)

    def set_labels(self, xlabel: str | None = None, ylabel: str | None = None) -> None:
        """Set the x and y axis labels."""
        if xlabel:
            self.axes.set_xlabel(xlabel)
        if ylabel:
            self.axes.set_ylabel(ylabel)

    def add_legend(self, location: str = "best") -> None:
        """Add a legend to the chart."""
        self.axes.legend(loc=location)

    def add_grid(
        self,
        visible: bool = True,
        alpha: float = 0.3,
        linestyle: str = "--",
        axis: str = "both",
        color: str | None = None,
    ) -> None:
        """Add a grid to the chart."""
        grid_kwargs = {"alpha": alpha, "linestyle": linestyle, "axis": axis}
        if color is not None:
            grid_kwargs["color"] = color

        self.axes.grid(visible, **grid_kwargs)

    def save(
        self,
        filename: str,
        dpi: int = 300,
        bbox_inches: str = "tight",
        format: str | None = None,
        transparent: bool = False,
        facecolor: str | None = None,
        edgecolor: str | None = None,
        **kwargs
    ) -> None:
        """
        Save the chart to a file with support for multiple formats.

        Parameters:
            filename: Output filename (format inferred from extension if not specified)
            dpi: Resolution for raster formats (PNG, JPG)
            bbox_inches: Bounding box layout
            format: Output format (png, svg, pdf, eps, ps). If None, inferred from filename
            transparent: Whether to use transparent background
            facecolor: Background color
            edgecolor: Edge color
            **kwargs: Additional matplotlib savefig parameters
        """
        # Auto-detect format from filename if not specified
        if format is None:
            import os
            _, ext = os.path.splitext(filename.lower())
            format_map = {
                '.png': 'png',
                '.svg': 'svg',
                '.pdf': 'pdf',
                '.eps': 'eps',
                '.ps': 'ps',
                '.jpg': 'jpeg',
                '.jpeg': 'jpeg'
            }
            format = format_map.get(ext, 'png')

        # Prepare save arguments
        save_kwargs = {
            'dpi': dpi,
            'bbox_inches': bbox_inches,
            'format': format,
            'transparent': transparent,
            **kwargs
        }

        # Handle format-specific options
        if format == 'svg':
            # SVG-specific optimizations
            save_kwargs.update({
                'dpi': 72,  # SVG doesn't need high DPI
                'metadata': {
                    'Creator': 'Vizly Visualization Library',
                    'Title': getattr(self.axes, 'get_title', lambda: 'Vizly Chart')(),
                }
            })
        elif format == 'pdf':
            # PDF-specific optimizations
            save_kwargs.update({
                'metadata': {
                    'Creator': 'Vizly Visualization Library',
                    'Title': getattr(self.axes, 'get_title', lambda: 'Vizly Chart')(),
                }
            })

        # Apply colors if specified
        if facecolor is not None:
            save_kwargs['facecolor'] = facecolor
        if edgecolor is not None:
            save_kwargs['edgecolor'] = edgecolor

        # Save the figure
        if self.figure and hasattr(self.figure, "savefig"):
            self.figure.savefig(filename, **save_kwargs)
        else:
            # Fallback for when figure doesn't have savefig
            import matplotlib.pyplot as plt
            plt.savefig(filename, **save_kwargs)

    def export_svg(
        self,
        filename: str,
        width: str = "800px",
        height: str = "600px",
        embed_fonts: bool = True
    ) -> None:
        """
        Export chart as SVG with enhanced options.

        Parameters:
            filename: Output SVG filename
            width: SVG width (CSS units)
            height: SVG height (CSS units)
            embed_fonts: Whether to embed fonts in SVG
        """
        # Configure matplotlib for SVG output
        import matplotlib
        original_backend = matplotlib.get_backend()

        try:
            # Set SVG-optimized parameters
            import matplotlib.pyplot as plt
            with plt.style.context('default'):
                # Configure SVG settings
                plt.rcParams['svg.fonttype'] = 'none' if embed_fonts else 'path'
                plt.rcParams['font.size'] = 12

                # Save as SVG
                self.save(
                    filename,
                    format='svg',
                    transparent=True,
                    bbox_inches='tight'
                )

        finally:
            # Restore original backend if needed
            pass

    def export_formats(self, base_filename: str, formats: list[str] = None) -> dict[str, str]:
        """
        Export chart in multiple formats.

        Parameters:
            base_filename: Base filename (without extension)
            formats: List of formats to export (default: ['png', 'svg', 'pdf'])

        Returns:
            Dictionary mapping format to actual filename
        """
        if formats is None:
            formats = ['png', 'svg', 'pdf']

        exported_files = {}

        for fmt in formats:
            filename = f"{base_filename}.{fmt}"
            try:
                if fmt == 'svg':
                    self.export_svg(filename)
                else:
                    self.save(filename, format=fmt)
                exported_files[fmt] = filename
            except Exception as e:
                import warnings
                warnings.warn(f"Failed to export {fmt}: {e}", UserWarning)

        return exported_files

    def show(self) -> None:
        """Display the chart."""
        if self.figure and hasattr(self.figure, "show"):
            self.figure.show()
        else:
            # Fallback to matplotlib
            import matplotlib.pyplot as plt

            plt.show()

    def render(self) -> str:
        """Render the chart to SVG string."""
        import io

        # Create a string buffer to capture SVG output
        svg_buffer = io.StringIO()

        try:
            # Save the figure as SVG to buffer
            if self.figure and hasattr(self.figure, "savefig"):
                self.figure.savefig(svg_buffer, format='svg', bbox_inches='tight')
            else:
                # Fallback to matplotlib
                import matplotlib.pyplot as plt
                plt.savefig(svg_buffer, format='svg', bbox_inches='tight')

            # Get SVG content
            svg_content = svg_buffer.getvalue()
            svg_buffer.close()

            return svg_content

        except Exception as e:
            # Return error message in SVG format
            return f'<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg"><text x="200" y="150" text-anchor="middle" fill="red">Render Error: {str(e)}</text></svg>'

    def set_limits(self, xlim: tuple | None = None, ylim: tuple | None = None) -> None:
        """Set axis limits."""
        if xlim:
            self.axes.set_xlim(xlim)
        if ylim:
            self.axes.set_ylim(ylim)

    def set_theme(self, theme_name: str) -> None:
        """Set the chart theme."""
        # For now, just store the theme name
        self._theme = theme_name

    def set_background_color(self, color: str) -> None:
        """Set the background color."""
        if self.figure and hasattr(self.figure, "patch"):
            self.figure.patch.set_facecolor(color)
        self.axes.set_facecolor(color)

    def enable_zoom_pan(self, enabled: bool = True) -> None:
        """Enable or disable zoom and pan functionality."""
        try:
            if enabled:
                # Enable matplotlib's navigation toolbar functionality
                if hasattr(self.axes, "figure") and hasattr(self.axes.figure, "canvas"):
                    self.axes.figure.canvas.toolbar_visible = True
                self._zoom_pan_enabled = True
            else:
                self._zoom_pan_enabled = False
        except Exception:
            warnings.warn(
                "Zoom/pan functionality not available in current backend", UserWarning
            )

    def enable_selection(self, callback: Optional[callable] = None) -> None:
        """Enable data point selection with optional callback."""
        try:
            if callback:
                self._selection_callback = callback
            self._selection_enabled = True
            # Store reference for potential matplotlib event handling
            self._selection_handler = None
        except Exception:
            warnings.warn(
                "Selection functionality not available in current backend", UserWarning
            )

    def enable_hover_tooltips(self, enabled: bool = True) -> None:
        """Enable hover tooltips showing data values."""
        try:
            self._tooltips_enabled = enabled
            if enabled and hasattr(self.axes, "figure"):
                # Placeholder for tooltip implementation
                self._tooltip_handler = None
        except Exception:
            warnings.warn(
                "Tooltip functionality not available in current backend", UserWarning
            )

    def enable_data_sampling(
        self, max_points: int = 5000, strategy: str = "uniform"
    ) -> None:
        """Enable intelligent data sampling for performance."""
        if max_points <= 0:
            raise ValueError("max_points must be positive")
        if strategy not in ["uniform", "adaptive", "peak_preserve"]:
            raise ValueError(
                "strategy must be one of: uniform, adaptive, peak_preserve"
            )

        self._max_points = max_points
        self._sampling_strategy = strategy
        self._sampling_enabled = True

    def enable_fast_rendering(self, enabled: bool = True) -> None:
        """Enable fast rendering optimizations."""
        self._fast_rendering = enabled
        if enabled:
            # Set rendering optimizations
            self._render_config = {
                "rasterized": True,
                "antialiased": False,
                "snap": True,
            }
        else:
            self._render_config = {}

    def add_annotation(
        self,
        text: str,
        xy: tuple,
        xytext: Optional[tuple] = None,
        fontsize: int = 10,
        color: str = "black",
        arrow_props: Optional[dict] = None,
    ) -> None:
        """Add text annotation to the chart."""
        try:
            if xytext is None:
                xytext = xy

            if arrow_props is None and xytext != xy:
                arrow_props = dict(arrowstyle="->", connectionstyle="arc3,rad=0")

            self.axes.annotate(
                text,
                xy=xy,
                xytext=xytext,
                fontsize=fontsize,
                color=color,
                arrowprops=arrow_props,
            )
        except Exception as e:
            warnings.warn(f"Failed to add annotation: {e}", UserWarning)

    def add_threshold_line(
        self,
        value: float,
        axis: str = "y",
        color: str = "red",
        linestyle: str = "--",
        alpha: float = 0.7,
        label: Optional[str] = None,
    ) -> None:
        """Add horizontal or vertical threshold line."""
        try:
            if axis.lower() == "y":
                self.axes.axhline(
                    y=value, color=color, linestyle=linestyle, alpha=alpha, label=label
                )
            elif axis.lower() == "x":
                self.axes.axvline(
                    x=value, color=color, linestyle=linestyle, alpha=alpha, label=label
                )
            else:
                raise ValueError("axis must be 'x' or 'y'")
        except Exception as e:
            warnings.warn(f"Failed to add threshold line: {e}", UserWarning)

    def set_style(self, style_dict: dict) -> None:
        """Apply custom styling to the chart."""
        try:
            # Apply matplotlib rcParams style updates
            import matplotlib.pyplot as plt

            with plt.style.context(style_dict):
                # Refresh the current plot
                if hasattr(self.axes, "figure"):
                    self.axes.figure.canvas.draw_idle()
        except Exception as e:
            warnings.warn(f"Failed to apply style: {e}", UserWarning)

    def export_data(self, filename: str, format: str = "csv") -> bool:
        """Export chart data to file."""
        try:
            if not hasattr(self, "_plot_data"):
                warnings.warn("No plot data available for export", UserWarning)
                return False

            if format.lower() == "csv":
                import csv

                with open(filename, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["x", "y"])  # Header
                    for x, y in zip(self._plot_data["x"], self._plot_data["y"]):
                        writer.writerow([x, y])
                return True
            else:
                warnings.warn(f"Export format '{format}' not supported", UserWarning)
                return False
        except Exception as e:
            warnings.warn(f"Failed to export data: {e}", UserWarning)
            return False

    def _sample_data(
        self, x: np.ndarray, y: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Apply data sampling based on configured strategy."""
        if not getattr(self, "_sampling_enabled", False) or len(x) <= self._max_points:
            return x, y

        strategy = getattr(self, "_sampling_strategy", "uniform")

        if strategy == "uniform":
            # Simple uniform sampling
            indices = np.linspace(0, len(x) - 1, self._max_points, dtype=int)
            return x[indices], y[indices]

        elif strategy == "adaptive":
            # Sample more densely where data changes rapidly
            if len(x) < 3:
                return x, y

            # Calculate local variation
            dy = np.abs(np.diff(y))
            # Add small epsilon to avoid division by zero
            weights = dy / (np.max(dy) + 1e-10)

            # Include first and last points
            indices = [0]
            cumulative_weight = 0
            target_weight = np.sum(weights) / (self._max_points - 2)

            for i in range(1, len(weights)):
                cumulative_weight += weights[i - 1]
                if cumulative_weight >= target_weight:
                    indices.append(i)
                    cumulative_weight = 0

            indices.append(len(x) - 1)
            indices = np.unique(indices)

            return x[indices], y[indices]

        elif strategy == "peak_preserve":
            # Preserve local maxima and minima
            if len(x) < 5:
                return x, y

            # Find local extrema
            from scipy.signal import find_peaks

            peaks, _ = find_peaks(y)
            valleys, _ = find_peaks(-y)

            # Combine extrema with uniform sampling
            extrema = np.concatenate([peaks, valleys, [0, len(x) - 1]])
            extrema = np.unique(extrema)

            # If we have too many extrema, subsample them
            if len(extrema) > self._max_points:
                step = len(extrema) // self._max_points
                extrema = extrema[::step]

            # Fill remaining spots with uniform sampling
            remaining_points = self._max_points - len(extrema)
            if remaining_points > 0:
                all_indices = set(range(len(x)))
                available_indices = all_indices - set(extrema)
                if available_indices:
                    uniform_indices = np.linspace(
                        0, len(x) - 1, remaining_points + len(extrema), dtype=int
                    )
                    additional = [i for i in uniform_indices if i not in extrema][
                        :remaining_points
                    ]
                    extrema = np.concatenate([extrema, additional])

            extrema = np.unique(extrema)
            return x[extrema], y[extrema]

        return x, y
