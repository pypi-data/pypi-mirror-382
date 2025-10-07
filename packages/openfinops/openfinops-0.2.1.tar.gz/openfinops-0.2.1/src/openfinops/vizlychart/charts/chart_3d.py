"""
3D Chart Types for OpenFinOps
=============================

Three-dimensional visualizations including surface plots, 3D scatter,
3D line plots, and volumetric visualizations.
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

from typing import List, Optional, Union, Tuple, Dict, Any, Callable
import math

import numpy as np

from .professional_charts import ProfessionalChart
from ..rendering.vizlyengine import (
    AdvancedRenderer, ColorHDR, Font, RenderQuality, LineStyle,
    MarkerStyle, Gradient, UltraPrecisionAntiAliasing, PrecisionSettings
)


class Transform3D:
    """3D transformation utilities for projection and rotation."""

    def __init__(self, eye_distance: float = 5.0, elevation: float = 30.0, azimuth: float = 45.0):
        self.eye_distance = eye_distance
        self.elevation = math.radians(elevation)
        self.azimuth = math.radians(azimuth)

    def project(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Project 3D coordinates to 2D screen coordinates with depth."""
        # Rotation matrices
        cos_el, sin_el = math.cos(self.elevation), math.sin(self.elevation)
        cos_az, sin_az = math.cos(self.azimuth), math.sin(self.azimuth)

        # Apply elevation rotation (around x-axis)
        y_rot = y * cos_el - z * sin_el
        z_rot = y * sin_el + z * cos_el

        # Apply azimuth rotation (around z-axis)
        x_final = x * cos_az - y_rot * sin_az
        y_final = x * sin_az + y_rot * cos_az
        z_final = z_rot

        # Perspective projection
        perspective_factor = self.eye_distance / (self.eye_distance - z_final)
        x_2d = x_final * perspective_factor
        y_2d = y_final * perspective_factor

        return x_2d, y_2d, z_final


class Chart3D(ProfessionalChart):
    """Base class for 3D charts."""

    def __init__(self, width: int = 800, height: int = 600,
                 dpi: float = 96.0, quality: RenderQuality = RenderQuality.SVG_ONLY):
        super().__init__(width, height, dpi, quality)
        self.transform = Transform3D()
        self.show_axes = True
        self.grid_3d = True
        self.axis_labels = ["X", "Y", "Z"]

    def set_view(self, elevation: float = 25.0, azimuth: float = 45.0, distance: float = 4.0) -> 'Chart3D':
        """Set 3D viewing parameters for enhanced perspective."""
        # Store viewing parameters for enhanced projection
        self.elevation = math.radians(elevation)
        self.azimuth = math.radians(azimuth)
        self.distance = distance

        # Also update legacy transform for compatibility
        self.transform = Transform3D(distance, elevation, azimuth)
        return self

    def _project_3d(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Project 3D point to 2D screen coordinates."""
        # Normalize to unit cube first
        x_norm = (x - self.x_min) / (self.x_max - self.x_min) * 2 - 1
        y_norm = (y - self.y_min) / (self.y_max - self.y_min) * 2 - 1
        z_norm = (z - self.z_min) / (self.z_max - self.z_min) * 2 - 1

        # Project to 2D
        x_2d, y_2d, depth = self.transform.project(x_norm, y_norm, z_norm)

        # Convert to screen coordinates
        center_x = self.width / 2
        center_y = self.height / 2
        scale = min(self.width, self.height) / 4

        screen_x = center_x + x_2d * scale
        screen_y = center_y - y_2d * scale  # Flip Y for screen coordinates

        return screen_x, screen_y, depth

    def _set_3d_bounds(self, x_data: np.ndarray, y_data: np.ndarray, z_data: np.ndarray):
        """Set 3D data bounds."""
        self.x_min, self.x_max = x_data.min(), x_data.max()
        self.y_min, self.y_max = y_data.min(), y_data.max()
        self.z_min, self.z_max = z_data.min(), z_data.max()

    def _draw_3d_axes(self):
        """Draw 3D coordinate axes."""
        if not self.show_axes:
            return

        axis_color = ColorHDR(0.3, 0.3, 0.3, 1.0)

        # Draw main axes
        origin = self._project_3d(0, 0, 0)
        x_end = self._project_3d(self.x_max, 0, 0)
        y_end = self._project_3d(0, self.y_max, 0)
        z_end = self._project_3d(0, 0, self.z_max)

        # X axis (red)
        self.renderer.canvas.draw_ultra_precision_line(
            origin[0], origin[1], x_end[0], x_end[1], ColorHDR(0.8, 0.2, 0.2, 1.0), 2.0)

        # Y axis (green)
        self.renderer.canvas.draw_ultra_precision_line(
            origin[0], origin[1], y_end[0], y_end[1], ColorHDR(0.2, 0.8, 0.2, 1.0), 2.0)

        # Z axis (blue)
        self.renderer.canvas.draw_ultra_precision_line(
            origin[0], origin[1], z_end[0], z_end[1], ColorHDR(0.2, 0.2, 0.8, 1.0), 2.0)

        # Add axis labels
        font = Font(size=14, weight="bold")
        self.renderer.canvas.draw_text_advanced(
            self.axis_labels[0], x_end[0] + 10, x_end[1], font, self.text_color)
        self.renderer.canvas.draw_text_advanced(
            self.axis_labels[1], y_end[0] + 10, y_end[1], font, self.text_color)
        self.renderer.canvas.draw_text_advanced(
            self.axis_labels[2], z_end[0] + 10, z_end[1], font, self.text_color)

    def render(self):
        """Render the 3D chart to SVG."""
        # Start SVG document
        svg_content = f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Add background
        svg_content += f'<rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/>\n'

        # Add title if present
        if self.title:
            svg_content += f'<text x="{self.width//2}" y="30" text-anchor="middle" font-size="16" font-weight="bold">{self.title}</text>\n'

        # Draw 3D coordinate system
        svg_content += '<g id="3d-axes">\n'

        # Draw axis lines (simplified 3D perspective)
        center_x, center_y = self.width // 2, self.height // 2

        # X-axis (horizontal)
        svg_content += f'<line x1="{center_x - 100}" y1="{center_y}" x2="{center_x + 100}" y2="{center_y}" stroke="black" stroke-width="2"/>\n'
        svg_content += f'<text x="{center_x + 110}" y="{center_y + 5}" font-size="12">{self.axis_labels[0]}</text>\n'

        # Y-axis (vertical)
        svg_content += f'<line x1="{center_x}" y1="{center_y - 100}" x2="{center_x}" y2="{center_y + 100}" stroke="black" stroke-width="2"/>\n'
        svg_content += f'<text x="{center_x + 10}" y="{center_y - 110}" font-size="12">{self.axis_labels[1]}</text>\n'

        # Z-axis (perspective diagonal)
        svg_content += f'<line x1="{center_x}" y1="{center_y}" x2="{center_x - 70}" y2="{center_y - 70}" stroke="black" stroke-width="2"/>\n'
        svg_content += f'<text x="{center_x - 90}" y="{center_y - 80}" font-size="12">{self.axis_labels[2]}</text>\n'

        svg_content += '</g>\n'

        # Placeholder for 3D data
        svg_content += '<g id="3d-data">\n'
        svg_content += '<!-- 3D data would be rendered here -->\n'
        svg_content += '</g>\n'

        svg_content += '</svg>'
        return svg_content


class Surface3D(Chart3D):
    """3D surface plot implementation."""

    def __init__(self, width: int = 800, height: int = 600,
                 dpi: float = 96.0, quality: RenderQuality = RenderQuality.SVG_ONLY):
        super().__init__(width, height, dpi, quality)
        self.wireframe = False
        self.colormap = "viridis"
        self.alpha = 1.0

    def plot_surface(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray,
                     wireframe: bool = False, colormap: str = "viridis",
                     alpha: float = 1.0) -> 'Surface3D':
        """Create 3D surface plot."""
        self.wireframe = wireframe
        self.colormap = colormap
        self.alpha = alpha

        # Set 3D bounds
        self._set_3d_bounds(X.flatten(), Y.flatten(), Z.flatten())

        # Create triangular faces for the surface
        rows, cols = Z.shape
        faces = []

        for i in range(rows - 1):
            for j in range(cols - 1):
                # Create two triangles for each quad
                p1 = (X[i, j], Y[i, j], Z[i, j])
                p2 = (X[i+1, j], Y[i+1, j], Z[i+1, j])
                p3 = (X[i, j+1], Y[i, j+1], Z[i, j+1])
                p4 = (X[i+1, j+1], Y[i+1, j+1], Z[i+1, j+1])

                faces.extend([(p1, p2, p3), (p2, p4, p3)])

        # Sort faces by depth (painter's algorithm)
        face_depths = []
        for face in faces:
            depths = [self._project_3d(p[0], p[1], p[2])[2] for p in face]
            avg_depth = sum(depths) / len(depths)
            face_depths.append((avg_depth, face))

        face_depths.sort(key=lambda x: x[0], reverse=True)

        # Draw faces
        z_min, z_max = Z.min(), Z.max()
        for depth, face in face_depths:
            # Calculate face color based on average Z value
            avg_z = sum(p[2] for p in face) / len(face)
            color_intensity = (avg_z - z_min) / (z_max - z_min) if z_max != z_min else 0.5
            color = self._map_to_colormap(color_intensity, colormap)
            color = ColorHDR(color.r, color.g, color.b, alpha)

            # Project face points to 2D
            projected_points = [self._project_3d(p[0], p[1], p[2]) for p in face]

            if wireframe:
                self._draw_wireframe_triangle(projected_points, color)
            else:
                self._draw_filled_triangle(projected_points, color)

        # Draw axes
        self._draw_3d_axes()

        return self

    def _map_to_colormap(self, value: float, colormap: str) -> ColorHDR:
        """Map value to color using specified colormap."""
        value = max(0, min(1, value))  # Clamp to [0, 1]

        if colormap == "viridis":
            r = 0.267004 + value * (0.993248 - 0.267004)
            g = 0.004874 + value * (0.906157 - 0.004874)
            b = 0.329415 + value * (0.143936 - 0.329415)
        elif colormap == "plasma":
            r = 0.050383 + value * (0.940015 - 0.050383)
            g = 0.029803 + value * (0.975158 - 0.029803)
            b = 0.527975 + value * (0.131326 - 0.527975)
        elif colormap == "coolwarm":
            r = 0.230 + value * (0.706 - 0.230)
            g = 0.299 + value * (0.016 - 0.299)
            b = 0.754 + value * (0.150 - 0.754)
        else:  # Default rainbow
            r = 0.5 * (1 + math.cos(2 * math.pi * value))
            g = 0.5 * (1 + math.cos(2 * math.pi * value + 2 * math.pi / 3))
            b = 0.5 * (1 + math.cos(2 * math.pi * value + 4 * math.pi / 3))

        return ColorHDR(r, g, b, 1.0)

    def _draw_filled_triangle(self, points: List[Tuple[float, float, float]], color: ColorHDR):
        """Draw a filled triangle (simplified as wireframe for SVG)."""
        # For SVG output, draw as wireframe since filling is complex
        self._draw_wireframe_triangle(points, color)

    def _draw_wireframe_triangle(self, points: List[Tuple[float, float, float]], color: ColorHDR):
        """Draw triangle wireframe."""
        for i in range(3):
            x1, y1, _ = points[i]
            x2, y2, _ = points[(i + 1) % 3]
            self.renderer.canvas.draw_ultra_precision_line(x1, y1, x2, y2, color, 1.0)


class Scatter3D(Chart3D):
    """3D scatter plot implementation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scatter_data = []

    def scatter(self, x: Union[np.ndarray, list], y: Union[np.ndarray, list], z: Union[np.ndarray, list],
                color: Optional[ColorHDR] = None, size: float = 5.0,
                colors: Optional[np.ndarray] = None, sizes: Optional[np.ndarray] = None,
                c: Optional[np.ndarray] = None,  # Alias for colors (matplotlib compatibility)
                colormap: str = "viridis", alpha: float = 1.0) -> 'Scatter3D':
        """Create 3D scatter plot (main API method)."""
        # Handle c as alias for colors (matplotlib compatibility)
        if c is not None and colors is None:
            colors = c

        # Convert to numpy arrays
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)
        if not isinstance(z, np.ndarray):
            z = np.array(z)

        # Handle single color vs array of colors
        if color is not None and colors is None:
            colors = np.full(len(x), color)
        elif colors is None:
            colors = np.full(len(x), self.default_colors[0])

        # Handle single size vs array of sizes
        if sizes is None:
            sizes = np.full(len(x), size)

        # Store data for rendering
        self.scatter_data.append({
            'x': x, 'y': y, 'z': z,
            'colors': colors, 'sizes': sizes,
            'colormap': colormap, 'alpha': alpha
        })

        return self

    def scatter_3d(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                   colors: Optional[np.ndarray] = None, sizes: Optional[np.ndarray] = None,
                   colormap: str = "viridis", alpha: float = 1.0) -> 'Scatter3D':
        """Create 3D scatter plot (legacy method)."""
        return self.scatter(x, y, z, colors=colors, sizes=sizes, colormap=colormap, alpha=alpha)

    def render(self):
        """Render 3D scatter plot to SVG."""
        if not self.scatter_data:
            return f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg"><rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/><text x="{self.width//2}" y="{self.height//2}" text-anchor="middle" font-size="14" fill="gray">No 3D data to display</text></svg>'

        # Start SVG document
        svg_content = f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n'

        # Add background
        svg_content += f'<rect width="{self.width}" height="{self.height}" fill="rgb(255,255,255)"/>\n'

        # Add title if present
        if self.title:
            svg_content += f'<text x="{self.width//2}" y="30" text-anchor="middle" font-size="16" font-weight="bold">{self.title}</text>\n'

        # Process all scatter data
        all_points_with_depth = []

        for data in self.scatter_data:
            x, y, z = data['x'], data['y'], data['z']
            colors = data['colors']
            sizes = data['sizes']
            alpha = data['alpha']

            # Set 3D bounds from first dataset (simplified)
            if not hasattr(self, 'x_min'):
                self.x_min, self.x_max = x.min(), x.max()
                self.y_min, self.y_max = y.min(), y.max()
                self.z_min, self.z_max = z.min(), z.max()

            # Project points and collect for depth sorting with enhanced 3D
            for i in range(len(x)):
                screen_x, screen_y, depth, depth_norm = self._project_3d_enhanced(x[i], y[i], z[i])

                # Handle color
                if isinstance(colors[i], ColorHDR):
                    color = colors[i]
                else:
                    color = self.default_colors[0]

                # Apply depth-based size and alpha variations for 3D effect
                base_size = sizes[i]
                depth_size = base_size * (0.3 + 1.4 * depth_norm)  # Size varies from 30% to 170% based on depth
                depth_alpha = alpha * (0.4 + 0.6 * depth_norm)     # Alpha varies from 40% to 100% based on depth

                all_points_with_depth.append((depth, screen_x, screen_y, color, depth_size, depth_alpha, depth_norm))

        # Sort by depth (back to front for proper layering)
        all_points_with_depth.sort(key=lambda p: p[0])  # Sort front to back (smaller depth first)

        # Draw enhanced 3D coordinate system with perspective
        center_x, center_y = self.width // 2, self.height // 2
        svg_content += f'<g id="3d-axes">\n'

        # Draw 3D axes with proper perspective using the enhanced projection
        axis_length = 1.2  # In normalized coordinates

        # X-axis (red) - from origin to positive X
        origin_x, origin_y, _, _ = self._project_3d_enhanced(0, 0, 0)
        x_end_x, x_end_y, _, _ = self._project_3d_enhanced(axis_length, 0, 0)
        svg_content += f'<line x1="{origin_x}" y1="{origin_y}" x2="{x_end_x}" y2="{x_end_y}" stroke="rgb(220,50,50)" stroke-width="3" opacity="0.8"/>\n'
        svg_content += f'<text x="{x_end_x + 15}" y="{x_end_y + 5}" font-size="14" font-weight="bold" fill="rgb(180,50,50)">X</text>\n'

        # Y-axis (green) - from origin to positive Y
        y_end_x, y_end_y, _, _ = self._project_3d_enhanced(0, axis_length, 0)
        svg_content += f'<line x1="{origin_x}" y1="{origin_y}" x2="{y_end_x}" y2="{y_end_y}" stroke="rgb(50,220,50)" stroke-width="3" opacity="0.8"/>\n'
        svg_content += f'<text x="{y_end_x + 5}" y="{y_end_y - 10}" font-size="14" font-weight="bold" fill="rgb(50,180,50)">Y</text>\n'

        # Z-axis (blue) - from origin to positive Z
        z_end_x, z_end_y, _, _ = self._project_3d_enhanced(0, 0, axis_length)
        svg_content += f'<line x1="{origin_x}" y1="{origin_y}" x2="{z_end_x}" y2="{z_end_y}" stroke="rgb(50,50,220)" stroke-width="3" opacity="0.8"/>\n'
        svg_content += f'<text x="{z_end_x - 5}" y="{z_end_y - 10}" font-size="14" font-weight="bold" fill="rgb(50,50,180)">Z</text>\n'

        # Add grid lines for better 3D reference
        grid_steps = 5
        grid_alpha = 0.15
        for i in range(-grid_steps, grid_steps + 1):
            step = i / grid_steps
            if step != 0:  # Skip the main axes
                # X-direction grid lines
                gx1, gy1, _, _ = self._project_3d_enhanced(step, -1, 0)
                gx2, gy2, _, _ = self._project_3d_enhanced(step, 1, 0)
                svg_content += f'<line x1="{gx1}" y1="{gy1}" x2="{gx2}" y2="{gy2}" stroke="rgb(150,150,150)" stroke-width="1" opacity="{grid_alpha}"/>\n'

                # Y-direction grid lines
                gx1, gy1, _, _ = self._project_3d_enhanced(-1, step, 0)
                gx2, gy2, _, _ = self._project_3d_enhanced(1, step, 0)
                svg_content += f'<line x1="{gx1}" y1="{gy1}" x2="{gx2}" y2="{gy2}" stroke="rgb(150,150,150)" stroke-width="1" opacity="{grid_alpha}"/>\n'

        svg_content += f'</g>\n'

        # Draw scatter points with enhanced 3D effect
        svg_content += f'<g id="3d-scatter-points">\n'
        for depth, screen_x, screen_y, color, size, alpha, depth_norm in all_points_with_depth:
            # Convert color to RGB string
            color_str = f"rgb({int(color.r * 255)},{int(color.g * 255)},{int(color.b * 255)})"

            # Add subtle gradient effect based on depth
            if depth_norm > 0.5:  # Points closer to viewer
                # Add a subtle highlight
                svg_content += f'<circle cx="{screen_x}" cy="{screen_y}" r="{size + 1}" fill="rgba(255,255,255,0.3)" opacity="{alpha * 0.5}"/>\n'

            # Draw main scatter point with depth-adjusted properties
            svg_content += f'<circle cx="{screen_x}" cy="{screen_y}" r="{size}" fill="{color_str}" opacity="{alpha}"/>\n'

            # Add depth shadow for points further back
            if depth_norm < 0.3:
                shadow_offset = 2
                svg_content += f'<circle cx="{screen_x + shadow_offset}" cy="{screen_y + shadow_offset}" r="{size * 0.8}" fill="rgba(0,0,0,0.2)" opacity="{alpha * 0.3}"/>\n'

        svg_content += f'</g>\n'

        # Close SVG document
        svg_content += '</svg>'
        return svg_content

    def _project_3d_enhanced(self, x: float, y: float, z: float) -> Tuple[float, float, float, float]:
        """Enhanced 3D projection with proper perspective and depth."""
        # Normalize coordinates to [-1, 1] range for better perspective
        if hasattr(self, 'x_min'):
            x_norm = 2 * (x - self.x_min) / (self.x_max - self.x_min) - 1 if self.x_max != self.x_min else 0
            y_norm = 2 * (y - self.y_min) / (self.y_max - self.y_min) - 1 if self.y_max != self.y_min else 0
            z_norm = 2 * (z - self.z_min) / (self.z_max - self.z_min) - 1 if self.z_max != self.z_min else 0
        else:
            x_norm = y_norm = z_norm = 0

        # Enhanced viewing parameters for better 3D effect (customizable via set_view)
        elevation = getattr(self, 'elevation', math.radians(25))   # 25 degrees elevation (default)
        azimuth = getattr(self, 'azimuth', math.radians(45))       # 45 degrees azimuth rotation (default)
        distance = getattr(self, 'distance', 4.0)                 # Camera distance for perspective (default)

        # Apply rotation transformations
        # First rotate around Z axis (azimuth)
        cos_az = math.cos(azimuth)
        sin_az = math.sin(azimuth)
        x1 = x_norm * cos_az - y_norm * sin_az
        y1 = x_norm * sin_az + y_norm * cos_az
        z1 = z_norm

        # Then rotate around X axis (elevation)
        cos_el = math.cos(elevation)
        sin_el = math.sin(elevation)
        x2 = x1
        y2 = y1 * cos_el - z1 * sin_el
        z2 = y1 * sin_el + z1 * cos_el

        # Apply perspective projection
        # Move camera back and apply perspective divide
        z_camera = z2 + distance
        perspective_factor = distance / z_camera if z_camera > 0.1 else 1.0

        # Project to screen with perspective
        center_x = self.width / 2
        center_y = self.height / 2
        scale = min(self.width, self.height) / 5  # Slightly larger scale

        screen_x = center_x + x2 * perspective_factor * scale
        screen_y = center_y - y2 * perspective_factor * scale  # Flip Y for screen coords

        # Calculate depth for size/alpha variation
        depth_normalized = (z2 + 1) / 2  # Convert from [-1,1] to [0,1]

        return screen_x, screen_y, z2, depth_normalized

    def _project_3d_simple(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Backward compatibility wrapper."""
        screen_x, screen_y, depth, _ = self._project_3d_enhanced(x, y, z)
        return screen_x, screen_y, depth

    def _map_to_colormap(self, value: float, colormap: str) -> ColorHDR:
        """Map value to color using specified colormap."""
        value = max(0, min(1, value))

        if colormap == "viridis":
            r = 0.267004 + value * (0.993248 - 0.267004)
            g = 0.004874 + value * (0.906157 - 0.004874)
            b = 0.329415 + value * (0.143936 - 0.329415)
        else:
            r = g = b = value

        return ColorHDR(r, g, b, 1.0)


class Line3D(Chart3D):
    """3D line plot implementation."""

    def plot_3d(self, x: np.ndarray, y: np.ndarray, z: np.ndarray,
                color: Optional[ColorHDR] = None, line_width: float = 2.0,
                label: str = "") -> 'Line3D':
        """Create 3D line plot."""
        self._set_3d_bounds(x, y, z)

        if color is None:
            color = self.default_colors[0]

        # Project all points to 2D
        projected_points = []
        for i in range(len(x)):
            screen_x, screen_y, depth = self._project_3d(x[i], y[i], z[i])
            projected_points.append((screen_x, screen_y, depth))

        # Draw line segments
        for i in range(len(projected_points) - 1):
            x1, y1, _ = projected_points[i]
            x2, y2, _ = projected_points[i + 1]
            self.renderer.canvas.draw_ultra_precision_line(x1, y1, x2, y2, color, line_width)

        # Draw axes
        self._draw_3d_axes()

        return self