"""
Pure Python Canvas Implementation
Replaces matplotlib backend with native drawing primitives.
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
from typing import Tuple, List, Union
from dataclasses import dataclass
import math


@dataclass
class Color:
    """RGBA color representation."""

    r: float
    g: float
    b: float
    a: float = 1.0

    @classmethod
    def from_hex(cls, hex_color: str) -> "Color":
        """Create color from hex string."""
        hex_color = hex_color.lstrip("#")
        return cls(
            r=int(hex_color[0:2], 16) / 255.0,
            g=int(hex_color[2:4], 16) / 255.0,
            b=int(hex_color[4:6], 16) / 255.0,
        )

    @classmethod
    def from_name(cls, name: str) -> "Color":
        """Create color from name."""
        colors = {
            "red": cls(1.0, 0.0, 0.0),
            "green": cls(0.0, 1.0, 0.0),
            "blue": cls(0.0, 0.0, 1.0),
            "white": cls(1.0, 1.0, 1.0),
            "black": cls(0.0, 0.0, 0.0),
            "cyan": cls(0.0, 1.0, 1.0),
            "magenta": cls(1.0, 0.0, 1.0),
            "yellow": cls(1.0, 1.0, 0.0),
            "orange": cls(1.0, 0.5, 0.0),
            "purple": cls(0.5, 0.0, 1.0),
            "gray": cls(0.5, 0.5, 0.5),
            "darkgray": cls(0.3, 0.3, 0.3),
            "lightgray": cls(0.8, 0.8, 0.8),
        }
        return colors.get(name.lower(), cls(0.0, 0.0, 0.0))

    def to_rgba_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to RGBA tuple (0-255)."""
        return (
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255),
            int(self.a * 255),
        )

    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple (0-255)."""
        return (int(self.r * 255), int(self.g * 255), int(self.b * 255))


@dataclass
class Point:
    """2D point."""

    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        """Calculate distance to another point."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class Rectangle:
    """Rectangle primitive."""

    x: float
    y: float
    width: float
    height: float

    @property
    def x2(self) -> float:
        return self.x + self.width

    @property
    def y2(self) -> float:
        return self.y + self.height

    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def contains(self, point: Point) -> bool:
        """Check if point is inside rectangle."""
        return self.x <= point.x <= self.x2 and self.y <= point.y <= self.y2


@dataclass
class Line:
    """Line primitive."""

    start: Point
    end: Point
    width: float = 1.0
    color: Color = None

    def __post_init__(self):
        if self.color is None:
            self.color = Color(0, 0, 0)

    @property
    def length(self) -> float:
        return self.start.distance_to(self.end)


class Canvas:
    """Pure Python canvas for drawing operations."""

    def __init__(self, width: int, height: int, background: Color = None):
        self.width = width
        self.height = height
        self.background = background or Color(1.0, 1.0, 1.0)

        # Create pixel buffer (RGBA)
        self.pixels = np.full((height, width, 4), 255, dtype=np.uint8)
        self._clear_background()

        # Drawing state
        self.current_color = Color(0, 0, 0)
        self.current_line_width = 1.0
        self.current_font_size = 12

    def _clear_background(self):
        """Clear canvas with background color."""
        bg_rgba = self.background.to_rgba_tuple()
        self.pixels[:, :] = bg_rgba

    def clear(self):
        """Clear the canvas."""
        self._clear_background()

    def set_color(self, color: Union[Color, str]):
        """Set current drawing color."""
        if isinstance(color, str):
            self.current_color = Color.from_name(color)
        else:
            self.current_color = color

    def set_line_width(self, width: float):
        """Set current line width."""
        self.current_line_width = width

    def draw_pixel(self, x: int, y: int, color: Color = None):
        """Draw a single pixel."""
        if 0 <= x < self.width and 0 <= y < self.height:
            color = color or self.current_color
            self.pixels[y, x] = color.to_rgba_tuple()

    def draw_line(
        self, start: Point, end: Point, color: Color = None, width: float = None
    ):
        """Draw a line using Bresenham's algorithm."""
        color = color or self.current_color
        width = width or self.current_line_width

        x0, y0 = int(start.x), int(start.y)
        x1, y1 = int(end.x), int(end.y)

        # Bresenham's line algorithm
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        x, y = x0, y0

        while True:
            # Draw pixel with line width
            for i in range(int(width)):
                for j in range(int(width)):
                    px = x + i - int(width // 2)
                    py = y + j - int(width // 2)
                    self.draw_pixel(px, py, color)

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def draw_rectangle(
        self,
        rect: Rectangle,
        fill_color: Color = None,
        border_color: Color = None,
        border_width: float = 1.0,
    ):
        """Draw a rectangle."""
        x, y = int(rect.x), int(rect.y)
        w, h = int(rect.width), int(rect.height)

        # Fill rectangle
        if fill_color:
            for py in range(y, y + h):
                for px in range(x, x + w):
                    self.draw_pixel(px, py, fill_color)

        # Draw border
        if border_color:
            # Top and bottom
            for px in range(x, x + w):
                for i in range(int(border_width)):
                    self.draw_pixel(px, y + i, border_color)
                    self.draw_pixel(px, y + h - 1 - i, border_color)

            # Left and right
            for py in range(y, y + h):
                for i in range(int(border_width)):
                    self.draw_pixel(x + i, py, border_color)
                    self.draw_pixel(x + w - 1 - i, py, border_color)

    def draw_circle(
        self,
        center: Point,
        radius: float,
        fill_color: Color = None,
        border_color: Color = None,
        border_width: float = 1.0,
    ):
        """Draw a circle using midpoint algorithm."""
        cx, cy = int(center.x), int(center.y)
        r = int(radius)

        # Fill circle
        if fill_color:
            for y in range(cy - r, cy + r + 1):
                for x in range(cx - r, cx + r + 1):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r**2:
                        self.draw_pixel(x, y, fill_color)

        # Draw border using midpoint circle algorithm
        if border_color:
            x = 0
            y = r
            d = 1 - r

            def draw_circle_points(cx, cy, x, y, color, width):
                """Draw 8 symmetric points of circle."""
                for i in range(int(width)):
                    self.draw_pixel(cx + x, cy + y + i, color)
                    self.draw_pixel(cx - x, cy + y + i, color)
                    self.draw_pixel(cx + x, cy - y - i, color)
                    self.draw_pixel(cx - x, cy - y - i, color)
                    self.draw_pixel(cx + y, cy + x + i, color)
                    self.draw_pixel(cx - y, cy + x + i, color)
                    self.draw_pixel(cx + y, cy - x - i, color)
                    self.draw_pixel(cx - y, cy - x - i, color)

            while x <= y:
                draw_circle_points(cx, cy, x, y, border_color, border_width)

                if d < 0:
                    d += 2 * x + 3
                else:
                    d += 2 * (x - y) + 5
                    y -= 1
                x += 1

    def draw_polygon(
        self,
        points: List[Point],
        fill_color: Color = None,
        border_color: Color = None,
        border_width: float = 1.0,
    ):
        """Draw a polygon."""
        if len(points) < 3:
            return

        # Draw border
        if border_color:
            for i in range(len(points)):
                start = points[i]
                end = points[(i + 1) % len(points)]
                self.draw_line(start, end, border_color, border_width)

        # Fill polygon using scanline algorithm
        if fill_color:
            self._fill_polygon(points, fill_color)

    def _fill_polygon(self, points: List[Point], color: Color):
        """Fill polygon using scanline algorithm."""
        if len(points) < 3:
            return

        # Find bounding box
        min_y = max(0, int(min(p.y for p in points)))
        max_y = min(self.height - 1, int(max(p.y for p in points)))

        # For each scanline
        for y in range(min_y, max_y + 1):
            intersections = []

            # Find intersections with polygon edges
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]

                if p1.y <= y < p2.y or p2.y <= y < p1.y:
                    # Calculate intersection x-coordinate
                    if p2.y != p1.y:
                        x = p1.x + (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y)
                        intersections.append(int(x))

            # Sort intersections and fill pairs
            intersections.sort()
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    x1, x2 = intersections[i], intersections[i + 1]
                    for x in range(max(0, x1), min(self.width, x2 + 1)):
                        self.draw_pixel(x, y, color)

    def draw_text(
        self, text: str, position: Point, color: Color = None, font_size: int = None
    ):
        """Draw text (simplified bitmap font)."""
        color = color or self.current_color
        font_size = font_size or self.current_font_size

        # Simple bitmap font simulation
        char_width = font_size // 2
        char_height = font_size

        x, y = int(position.x), int(position.y)

        for i, char in enumerate(text):
            char_x = x + i * char_width

            # Draw a simple rectangle for each character (placeholder)
            self.draw_rectangle(
                Rectangle(char_x, y, char_width - 1, char_height),
                border_color=color,
                border_width=1.0,
            )

    def get_pixel_data(self) -> np.ndarray:
        """Get raw pixel data as numpy array."""
        return self.pixels.copy()

    def save_png(self, filename: str):
        """Save canvas as PNG file."""
        try:
            from PIL import Image

            # Convert RGBA to RGB if needed
            if self.pixels.shape[2] == 4:
                # Handle alpha channel
                rgb_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                alpha = self.pixels[:, :, 3] / 255.0

                for c in range(3):
                    rgb_array[:, :, c] = (
                        self.pixels[:, :, c] * alpha
                        + 255 * (1 - alpha)  # White background
                    ).astype(np.uint8)

                image = Image.fromarray(rgb_array, "RGB")
            else:
                image = Image.fromarray(self.pixels, "RGB")

            image.save(filename)

        except ImportError:
            # Fallback: simple PPM format
            self._save_ppm(filename.replace(".png", ".ppm"))

    def _save_ppm(self, filename: str):
        """Save as PPM format (fallback when PIL not available)."""
        with open(filename, "w") as f:
            f.write(f"P3\n{self.width} {self.height}\n255\n")

            for y in range(self.height):
                for x in range(self.width):
                    r, g, b = self.pixels[y, x, :3]
                    f.write(f"{r} {g} {b} ")
                f.write("\n")
