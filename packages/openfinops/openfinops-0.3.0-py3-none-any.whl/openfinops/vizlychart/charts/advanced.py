"""Advanced chart types for specialized visualization needs."""

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
from typing import Dict, List, Optional, Tuple
import warnings

import numpy as np
from scipy.signal import spectrogram
from scipy.spatial import ConvexHull

from .base import BaseChart

try:
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    from matplotlib.collections import LineCollection, PolyCollection
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
except ImportError:
    warnings.warn("Matplotlib not available for advanced charts")

try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


logger = logging.getLogger(__name__)


class HeatmapChart(BaseChart):
    """2D heatmap visualization."""

    def plot(
        self,
        data: np.ndarray,
        x_labels: Optional[List[str]] = None,
        y_labels: Optional[List[str]] = None,
        colormap: str = "viridis",
        interpolation: str = "nearest",
        show_values: bool = False,
        value_format: str = ".2f",
        title: Optional[str] = None,
    ) -> None:
        """Plot 2D heatmap."""

        if data.ndim != 2:
            raise ValueError("Data must be 2D array for heatmap")

        # Create heatmap
        im = self.axes.imshow(
            data,
            cmap=colormap,
            interpolation=interpolation,
            aspect="auto",
            origin="lower",
        )

        # Set labels
        if x_labels:
            self.axes.set_xticks(range(len(x_labels)))
            self.axes.set_xticklabels(x_labels, rotation=45, ha="right")

        if y_labels:
            self.axes.set_yticks(range(len(y_labels)))
            self.axes.set_yticklabels(y_labels)

        # Add colorbar
        cbar = self.figure.figure.colorbar(im, ax=self.axes)

        # Show values in cells
        if show_values:
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    text = self.axes.text(
                        j,
                        i,
                        format(data[i, j], value_format),
                        ha="center",
                        va="center",
                        color="white",
                    )

        if title:
            self.axes.set_title(title)

    def heatmap(
        self,
        data: np.ndarray,
        x_labels: Optional[List[str]] = None,
        y_labels: Optional[List[str]] = None,
        cmap: str = "viridis",
        interpolation: str = "nearest",
        annot: bool = False,
        fmt: str = ".2f",
        title: Optional[str] = None,
        cbar: bool = True,
        **kwargs
    ) -> None:
        """
        Create a heatmap visualization.

        This is an alias for plot() with seaborn-compatible parameter names.

        Parameters:
            data: 2D array for heatmap
            x_labels: Labels for x-axis
            y_labels: Labels for y-axis
            cmap: Colormap name (alias for colormap)
            interpolation: Interpolation method
            annot: Show values in cells (alias for show_values)
            fmt: Format string for values (alias for value_format)
            title: Chart title
            cbar: Whether to show colorbar
            **kwargs: Additional matplotlib imshow parameters
        """
        # Map seaborn-style parameters to our internal method
        self.plot(
            data=data,
            x_labels=x_labels,
            y_labels=y_labels,
            colormap=cmap,
            interpolation=interpolation,
            show_values=annot,
            value_format=fmt,
            title=title,
        )


class ViolinChart(BaseChart):
    """Violin plot for distribution visualization."""

    def plot(
        self,
        datasets: List[np.ndarray],
        labels: Optional[List[str]] = None,
        positions: Optional[List[float]] = None,
        width: float = 0.8,
        show_means: bool = True,
        show_medians: bool = True,
        show_extrema: bool = True,
    ) -> None:
        """Plot violin charts."""

        if not datasets:
            raise ValueError("At least one dataset required")

        if positions is None:
            positions = list(range(1, len(datasets) + 1))

        # Create violin plots
        parts = self.axes.violinplot(
            datasets,
            positions=positions,
            widths=[width] * len(datasets),
            showmeans=show_means,
            showmedians=show_medians,
            showextrema=show_extrema,
        )

        # Customize appearance
        for pc in parts["bodies"]:
            pc.set_facecolor("lightblue")
            pc.set_alpha(0.7)

        # Set labels
        if labels:
            self.axes.set_xticks(positions)
            self.axes.set_xticklabels(labels)

        self.axes.set_ylabel("Value")


class RadarChart(BaseChart):
    """Radar/spider chart for multivariate data."""

    def plot(
        self,
        values: np.ndarray,
        labels: List[str],
        series_names: Optional[List[str]] = None,
        colors: Optional[List[str]] = None,
        fill_alpha: float = 0.25,
        line_width: float = 2.0,
    ) -> None:
        """Plot radar chart."""

        if values.ndim == 1:
            values = values.reshape(1, -1)

        n_vars = len(labels)
        n_series = values.shape[0]

        # Compute angles for each variable
        angles = np.linspace(0, 2 * np.pi, n_vars, endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle

        # Clear axes and set up polar projection
        self.axes.clear()
        polar_axes = self.figure.figure.add_subplot(111, projection="polar")
        self.bind_axes(polar_axes)

        # Plot each series
        for i in range(n_series):
            series_values = values[i].tolist()
            series_values += series_values[:1]  # Complete the circle

            color = colors[i] if colors and i < len(colors) else None
            series_name = (
                series_names[i]
                if series_names and i < len(series_names)
                else f"Series {i+1}"
            )

            # Plot line
            self.axes.plot(
                angles,
                series_values,
                "o-",
                linewidth=line_width,
                label=series_name,
                color=color,
            )

            # Fill area
            self.axes.fill(angles, series_values, alpha=fill_alpha, color=color)

        # Set labels
        self.axes.set_xticks(angles[:-1])
        self.axes.set_xticklabels(labels)

        # Add legend
        if series_names:
            self.axes.legend(loc="upper right", bbox_to_anchor=(1.2, 1.0))


class TreemapChart(BaseChart):
    """Treemap for hierarchical data visualization."""

    def plot(
        self,
        sizes: List[float],
        labels: List[str],
        colors: Optional[List[str]] = None,
        title: Optional[str] = None,
    ) -> None:
        """Plot treemap."""

        if len(sizes) != len(labels):
            raise ValueError("Sizes and labels must have same length")

        # Normalize sizes
        total_size = sum(sizes)
        normalized_sizes = [s / total_size for s in sizes]

        # Calculate rectangles using squarified algorithm
        rectangles = self._squarify(normalized_sizes, 0, 0, 1, 1)

        # Clear axes
        self.axes.clear()

        # Plot rectangles
        for i, (x, y, w, h) in enumerate(rectangles):
            color = colors[i] if colors and i < len(colors) else plt.cm.Set3(i)

            # Draw rectangle
            rect = plt.Rectangle(
                (x, y), w, h, facecolor=color, edgecolor="white", linewidth=2
            )
            self.axes.add_patch(rect)

            # Add label
            if w * h > 0.01:  # Only show labels for large enough rectangles
                self.axes.text(
                    x + w / 2,
                    y + h / 2,
                    labels[i],
                    ha="center",
                    va="center",
                    fontsize=8,
                    weight="bold",
                )

        self.axes.set_xlim(0, 1)
        self.axes.set_ylim(0, 1)
        self.axes.set_aspect("equal")
        self.axes.axis("off")

        if title:
            self.axes.set_title(title, pad=20)

    def _squarify(
        self, sizes: List[float], x: float, y: float, w: float, h: float
    ) -> List[Tuple[float, float, float, float]]:
        """Squarified treemap algorithm."""
        if not sizes:
            return []

        if len(sizes) == 1:
            return [(x, y, w, h)]

        # Find best split
        total_size = sum(sizes)
        best_ratio = float("inf")
        best_split = 1

        for i in range(1, len(sizes)):
            left_size = sum(sizes[:i])
            right_size = sum(sizes[i:])

            if w >= h:  # Split vertically
                left_width = w * left_size / total_size
                ratio = max(left_width / h, h / left_width)
            else:  # Split horizontally
                left_height = h * left_size / total_size
                ratio = max(w / left_height, left_height / w)

            if ratio < best_ratio:
                best_ratio = ratio
                best_split = i

        # Recursive split
        left_sizes = sizes[:best_split]
        right_sizes = sizes[best_split:]

        left_total = sum(left_sizes)
        right_total = sum(right_sizes)

        if w >= h:  # Split vertically
            left_width = w * left_total / total_size
            left_rects = self._squarify(left_sizes, x, y, left_width, h)
            right_rects = self._squarify(
                right_sizes, x + left_width, y, w - left_width, h
            )
        else:  # Split horizontally
            left_height = h * left_total / total_size
            left_rects = self._squarify(left_sizes, x, y, w, left_height)
            right_rects = self._squarify(
                right_sizes, x, y + left_height, w, h - left_height
            )

        return left_rects + right_rects


class SankeyChart(BaseChart):
    """Sankey diagram for flow visualization."""

    def plot(
        self,
        flows: List[Tuple[str, str, float]],
        node_colors: Optional[Dict[str, str]] = None,
        title: Optional[str] = None,
    ) -> None:
        """Plot Sankey diagram."""

        # Extract unique nodes
        nodes = set()
        for source, target, _ in flows:
            nodes.add(source)
            nodes.add(target)

        nodes = list(nodes)
        node_positions = self._calculate_node_positions(flows, nodes)

        # Clear axes
        self.axes.clear()

        # Draw flows
        for source, target, weight in flows:
            src_pos = node_positions[source]
            tgt_pos = node_positions[target]

            # Create curved flow
            self._draw_flow(src_pos, tgt_pos, weight)

        # Draw nodes
        for node in nodes:
            pos = node_positions[node]
            color = node_colors.get(node, "lightblue") if node_colors else "lightblue"

            # Draw node rectangle
            rect = plt.Rectangle(
                (pos[0] - 0.05, pos[1] - 0.02),
                0.1,
                0.04,
                facecolor=color,
                edgecolor="black",
            )
            self.axes.add_patch(rect)

            # Add label
            self.axes.text(pos[0], pos[1], node, ha="center", va="center", fontsize=8)

        self.axes.set_xlim(-0.2, 1.2)
        self.axes.set_ylim(-0.2, 1.2)
        self.axes.set_aspect("equal")
        self.axes.axis("off")

        if title:
            self.axes.set_title(title)

    def _calculate_node_positions(
        self, flows: List[Tuple[str, str, float]], nodes: List[str]
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate optimal node positions."""
        # Simple layout: sources on left, targets on right
        sources = set(flow[0] for flow in flows)
        targets = set(flow[1] for flow in flows)

        positions = {}
        y_pos = 0.1

        # Position sources
        for node in nodes:
            if node in sources:
                positions[node] = (0.2, y_pos)
                y_pos += 0.8 / len(sources)

        y_pos = 0.1
        # Position targets
        for node in nodes:
            if node in targets and node not in positions:
                positions[node] = (0.8, y_pos)
                y_pos += 0.8 / len(targets)

        return positions

    def _draw_flow(
        self, src_pos: Tuple[float, float], tgt_pos: Tuple[float, float], weight: float
    ) -> None:
        """Draw a curved flow between nodes."""
        x1, y1 = src_pos
        x2, y2 = tgt_pos

        # Create Bezier curve
        mid_x = (x1 + x2) / 2
        control1 = (mid_x, y1)
        control2 = (mid_x, y2)

        # Generate curve points
        t = np.linspace(0, 1, 100)
        curve_x = (
            (1 - t) ** 3 * x1
            + 3 * (1 - t) ** 2 * t * control1[0]
            + 3 * (1 - t) * t**2 * control2[0]
            + t**3 * x2
        )
        curve_y = (
            (1 - t) ** 3 * y1
            + 3 * (1 - t) ** 2 * t * control1[1]
            + 3 * (1 - t) * t**2 * control2[1]
            + t**3 * y2
        )

        # Draw flow with width proportional to weight
        line_width = max(1, weight * 10)
        self.axes.plot(
            curve_x, curve_y, linewidth=line_width, alpha=0.6, color="steelblue"
        )


class SpectrogramChart(BaseChart):
    """Spectrogram for time-frequency analysis."""

    def plot(
        self,
        signal: np.ndarray,
        sample_rate: float,
        window: str = "hann",
        nperseg: Optional[int] = None,
        noverlap: Optional[int] = None,
        colormap: str = "viridis",
        title: Optional[str] = None,
    ) -> None:
        """Plot spectrogram."""

        # Compute spectrogram
        frequencies, times, Sxx = spectrogram(
            signal, fs=sample_rate, window=window, nperseg=nperseg, noverlap=noverlap
        )

        # Convert to dB
        Sxx_dB = 10 * np.log10(Sxx + 1e-10)

        # Plot
        im = self.axes.pcolormesh(
            times, frequencies, Sxx_dB, cmap=colormap, shading="gouraud"
        )

        # Labels and colorbar
        self.axes.set_ylabel("Frequency [Hz]")
        self.axes.set_xlabel("Time [s]")

        cbar = self.figure.figure.colorbar(im, ax=self.axes)
        cbar.set_label("Power Spectral Density [dB]")

        if title:
            self.axes.set_title(title)


class ClusterChart(BaseChart):
    """Clustering visualization with multiple algorithms."""

    def plot(
        self,
        data: np.ndarray,
        algorithm: str = "kmeans",
        n_clusters: Optional[int] = None,
        labels: Optional[np.ndarray] = None,
        title: Optional[str] = None,
        **algorithm_params,
    ) -> np.ndarray:
        """Plot clustering results."""

        if not HAS_SKLEARN:
            raise ImportError("scikit-learn required for clustering")

        if data.shape[1] > 2:
            # Reduce dimensionality for visualization
            if data.shape[1] > 50:
                # Use PCA first to reduce to 50 dimensions, then t-SNE
                pca = PCA(n_components=50)
                data_reduced = pca.fit_transform(data)
                tsne = TSNE(n_components=2, random_state=42)
                data_2d = tsne.fit_transform(data_reduced)
            else:
                # Use t-SNE directly
                tsne = TSNE(n_components=2, random_state=42)
                data_2d = tsne.fit_transform(data)
        else:
            data_2d = data

        # Perform clustering if labels not provided
        if labels is None:
            if algorithm.lower() == "kmeans":
                if n_clusters is None:
                    n_clusters = 3
                clusterer = KMeans(n_clusters=n_clusters, **algorithm_params)
            elif algorithm.lower() == "dbscan":
                clusterer = DBSCAN(**algorithm_params)
            else:
                raise ValueError(f"Unknown clustering algorithm: {algorithm}")

            labels = clusterer.fit_predict(data)

        # Plot clusters
        unique_labels = np.unique(labels)
        colors = plt.cm.Set1(np.linspace(0, 1, len(unique_labels)))

        for label, color in zip(unique_labels, colors):
            if label == -1:  # Noise points in DBSCAN
                color = "black"

            mask = labels == label
            self.axes.scatter(
                data_2d[mask, 0],
                data_2d[mask, 1],
                c=[color],
                label=f"Cluster {label}",
                alpha=0.7,
            )

        self.axes.legend()
        self.axes.set_xlabel("Dimension 1")
        self.axes.set_ylabel("Dimension 2")

        if title:
            self.axes.set_title(title)

        return labels


class ParallelCoordinatesChart(BaseChart):
    """Parallel coordinates plot for multivariate data."""

    def plot(
        self,
        data: np.ndarray,
        feature_names: Optional[List[str]] = None,
        class_labels: Optional[np.ndarray] = None,
        normalize: bool = True,
        alpha: float = 0.7,
    ) -> None:
        """Plot parallel coordinates."""

        if data.ndim != 2:
            raise ValueError("Data must be 2D array")

        n_samples, n_features = data.shape

        # Normalize data to [0, 1] range
        if normalize:
            data_norm = (data - data.min(axis=0)) / (
                data.max(axis=0) - data.min(axis=0)
            )
        else:
            data_norm = data

        # Set up x-coordinates for features
        x_coords = np.arange(n_features)

        # Plot lines
        if class_labels is not None:
            unique_classes = np.unique(class_labels)
            colors = plt.cm.Set1(np.linspace(0, 1, len(unique_classes)))

            for class_val, color in zip(unique_classes, colors):
                mask = class_labels == class_val
                class_data = data_norm[mask]

                for i in range(class_data.shape[0]):
                    self.axes.plot(x_coords, class_data[i], color=color, alpha=alpha)

                # Add dummy line for legend
                self.axes.plot([], [], color=color, label=f"Class {class_val}")

            self.axes.legend()
        else:
            # Single color for all lines
            for i in range(n_samples):
                self.axes.plot(x_coords, data_norm[i], color="steelblue", alpha=alpha)

        # Set labels
        self.axes.set_xticks(x_coords)
        if feature_names:
            self.axes.set_xticklabels(feature_names, rotation=45, ha="right")
        else:
            self.axes.set_xticklabels(
                [f"Feature {i}" for i in range(n_features)], rotation=45, ha="right"
            )

        self.axes.set_ylabel("Normalized Value")
        self.axes.grid(True, alpha=0.3)


class ConvexHullChart(BaseChart):
    """Convex hull visualization for 2D/3D point sets."""

    def plot(
        self,
        points: np.ndarray,
        show_points: bool = True,
        show_hull: bool = True,
        fill_hull: bool = False,
        hull_color: str = "red",
        point_color: str = "blue",
        alpha: float = 0.7,
    ) -> None:
        """Plot convex hull."""

        if points.shape[1] not in [2, 3]:
            raise ValueError("Points must be 2D or 3D")

        # Compute convex hull
        hull = ConvexHull(points)

        if points.shape[1] == 2:
            # 2D plot
            if show_points:
                self.axes.scatter(
                    points[:, 0], points[:, 1], c=point_color, alpha=alpha
                )

            if show_hull:
                # Plot hull edges
                for simplex in hull.simplices:
                    self.axes.plot(
                        points[simplex, 0],
                        points[simplex, 1],
                        color=hull_color,
                        linewidth=2,
                    )

            if fill_hull:
                # Fill hull area
                hull_points = points[hull.vertices]
                polygon = Polygon(hull_points, facecolor=hull_color, alpha=0.3)
                self.axes.add_patch(polygon)

        else:
            # 3D plot
            if not hasattr(self.axes, "scatter3D"):
                self.axes = self.figure.figure.add_subplot(111, projection="3d")

            if show_points:
                self.axes.scatter3D(
                    points[:, 0], points[:, 1], points[:, 2], c=point_color, alpha=alpha
                )

            if show_hull:
                # Plot hull faces
                for simplex in hull.simplices:
                    triangle = points[simplex]
                    self.axes.plot3D(
                        triangle[:, 0], triangle[:, 1], triangle[:, 2], color=hull_color
                    )

            if fill_hull:
                # Fill hull faces
                poly3d = [
                    [points[j] for j in hull.simplices[i]]
                    for i in range(len(hull.simplices))
                ]
                self.axes.add_collection3d(
                    Poly3DCollection(poly3d, facecolors=hull_color, alpha=0.3)
                )

        self.axes.set_xlabel("X")
        self.axes.set_ylabel("Y")
        if points.shape[1] == 3:
            self.axes.set_zlabel("Z")
