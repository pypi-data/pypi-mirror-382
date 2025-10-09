"""
Core Animation System
====================

Fundamental animation classes and utilities for creating dynamic visualizations.
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
from dataclasses import dataclass
import math
import time

import numpy as np

from ..charts.professional_charts import ProfessionalChart
from ..rendering.vizlyengine import ColorHDR


@dataclass
class AnimationFrame:
    """Single frame in an animation sequence."""
    data: Dict[str, Any]
    timestamp: float
    duration: float = 1.0  # Duration to display this frame
    easing: str = "linear"  # Easing function: linear, ease_in, ease_out, ease_in_out


class Animation:
    """Core animation system for OpenFinOps."""

    def __init__(self, chart: ProfessionalChart):
        self.chart = chart
        self.frames = []
        self.current_frame = 0
        self.fps = 30
        self.loop = False
        self.interpolation = "linear"

    def add_frame(self, data: Dict[str, Any], duration: float = 1.0,
                  easing: str = "linear") -> 'Animation':
        """Add a frame to the animation sequence."""
        timestamp = len(self.frames) * duration
        frame = AnimationFrame(data=data, timestamp=timestamp, duration=duration, easing=easing)
        self.frames.append(frame)
        return self

    def set_fps(self, fps: int) -> 'Animation':
        """Set animation frame rate."""
        self.fps = fps
        return self

    def set_loop(self, loop: bool) -> 'Animation':
        """Enable or disable animation looping."""
        self.loop = loop
        return self

    def interpolate_frames(self, frame1: AnimationFrame, frame2: AnimationFrame,
                          progress: float) -> Dict[str, Any]:
        """Interpolate between two animation frames."""
        progress = self._apply_easing(progress, frame2.easing)
        interpolated_data = {}

        for key in frame1.data:
            if key in frame2.data:
                val1, val2 = frame1.data[key], frame2.data[key]

                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    # Numeric interpolation
                    interpolated_data[key] = val1 + (val2 - val1) * progress
                elif isinstance(val1, np.ndarray) and isinstance(val2, np.ndarray):
                    # Array interpolation
                    interpolated_data[key] = val1 + (val2 - val1) * progress
                elif isinstance(val1, ColorHDR) and isinstance(val2, ColorHDR):
                    # Color interpolation
                    r = val1.r + (val2.r - val1.r) * progress
                    g = val1.g + (val2.g - val1.g) * progress
                    b = val1.b + (val2.b - val1.b) * progress
                    a = val1.a + (val2.a - val1.a) * progress
                    interpolated_data[key] = ColorHDR(r, g, b, a)
                else:
                    # No interpolation, use discrete transition
                    interpolated_data[key] = val2 if progress > 0.5 else val1
            else:
                interpolated_data[key] = frame1.data[key]

        return interpolated_data

    def _apply_easing(self, t: float, easing: str) -> float:
        """Apply easing function to progress value."""
        t = max(0, min(1, t))  # Clamp to [0, 1]

        if easing == "ease_in":
            return t * t
        elif easing == "ease_out":
            return 1 - (1 - t) * (1 - t)
        elif easing == "ease_in_out":
            return 3 * t * t - 2 * t * t * t
        elif easing == "bounce":
            if t < 0.5:
                return 2 * t * t
            else:
                return 1 - 2 * (1 - t) * (1 - t)
        else:  # linear
            return t

    def render_frame(self, frame_index: int) -> ProfessionalChart:
        """Render a specific frame of the animation."""
        if frame_index >= len(self.frames):
            if self.loop:
                frame_index = frame_index % len(self.frames)
            else:
                frame_index = len(self.frames) - 1

        if frame_index < 0:
            frame_index = 0

        frame = self.frames[frame_index]

        # Update chart with frame data
        self._update_chart_with_data(frame.data)

        return self.chart

    def _update_chart_with_data(self, data: Dict[str, Any]):
        """Update chart properties with animation data."""
        # This is a simplified implementation - would need to be expanded
        # based on specific chart types and properties

        if 'title' in data:
            self.chart.set_title(data['title'])

        if 'x_data' in data and 'y_data' in data:
            # Clear and re-plot data (simplified)
            self.chart.data_series = []
            self.chart.plot(data['x_data'], data['y_data'])

        # Add more property updates as needed

    def save_gif(self, filename: str, duration_per_frame: float = 0.5):
        """Save animation as GIF file."""
        try:
            from PIL import Image
            import io
        except ImportError:
            raise ImportError("PIL (Pillow) is required for GIF export. Install with: pip install Pillow")

        frames = []
        for i in range(len(self.frames)):
            chart = self.render_frame(i)

            # Convert chart to image (this would need proper implementation)
            # For now, this is a placeholder
            svg_content = chart.to_svg()

            # Convert SVG to PIL Image (simplified - would need proper SVG to image conversion)
            # This is a placeholder implementation
            img = self._svg_to_image(svg_content)
            frames.append(img)

        if frames:
            frames[0].save(
                filename,
                save_all=True,
                append_images=frames[1:],
                duration=int(duration_per_frame * 1000),
                loop=0 if self.loop else 1
            )

    def _svg_to_image(self, svg_content: str):
        """Convert SVG to PIL Image."""
        try:
            from PIL import Image
            import io

            # Try using cairosvg if available
            try:
                import cairosvg
                png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
                return Image.open(io.BytesIO(png_data))
            except ImportError:
                # Fallback: Try using wand (ImageMagick)
                try:
                    from wand.image import Image as WandImage
                    from wand.color import Color

                    with WandImage() as img:
                        img.read(blob=svg_content.encode('utf-8'))
                        img.format = 'png'

                        # Convert to PIL Image
                        png_blob = img.make_blob('png')
                        return Image.open(io.BytesIO(png_blob))
                except ImportError:
                    # Final fallback: Create simple colored image with text
                    img = Image.new('RGB', (self.chart.width, self.chart.height), color='white')

                    try:
                        from PIL import ImageDraw, ImageFont
                        draw = ImageDraw.Draw(img)

                        # Try to load a basic font
                        try:
                            font = ImageFont.load_default()
                        except:
                            font = None

                        # Draw simple text indicating this is a chart frame
                        text = "Chart Frame"
                        if hasattr(self.chart, 'title') and self.chart.title:
                            text = self.chart.title

                        text_bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]

                        x = (self.chart.width - text_width) // 2
                        y = (self.chart.height - text_height) // 2

                        draw.text((x, y), text, fill='black', font=font)
                    except:
                        # If even text drawing fails, just return the white image
                        pass

                    return img

        except ImportError:
            # If PIL is not available, return None
            return None

    def get_info(self) -> Dict[str, Any]:
        """Get animation metadata and information."""
        total_duration = sum(frame.duration for frame in self.frames)
        return {
            'frame_count': len(self.frames),
            'fps': self.fps,
            'loop': self.loop,
            'interpolation': self.interpolation,
            'total_duration': total_duration,
            'frames_per_second': self.fps
        }

    def play(self, interval: float = None):
        """Play animation in real-time (for interactive environments)."""
        if interval is None:
            interval = 1.0 / self.fps

        import time

        frame_count = len(self.frames)
        start_time = time.time()

        while True:
            current_time = time.time() - start_time
            frame_index = int(current_time / interval) % frame_count if self.loop else min(int(current_time / interval), frame_count - 1)

            self.render_frame(frame_index)

            if not self.loop and frame_index >= frame_count - 1:
                break

            time.sleep(interval)


def animate_chart(chart: ProfessionalChart) -> Animation:
    """Create an animation from a chart."""
    return Animation(chart)


def create_gif_animation(charts: List[ProfessionalChart], filename: str,
                        duration_per_frame: float = 0.5, loop: bool = True):
    """Create GIF animation from a list of charts."""
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("PIL (Pillow) is required for GIF export. Install with: pip install Pillow")

    frames = []
    animation = Animation(charts[0])  # Create temporary animation for image conversion

    for i, chart in enumerate(charts):
        try:
            svg_content = chart.to_svg() if hasattr(chart, 'to_svg') else chart.render()
            img = animation._svg_to_image(svg_content)

            if img is None:
                # Fallback: create a simple frame with chart information
                img = Image.new('RGB', (chart.width, chart.height), color='white')

                try:
                    from PIL import ImageDraw, ImageFont
                    draw = ImageDraw.Draw(img)
                    font = ImageFont.load_default()

                    text = f"Frame {i+1}"
                    if hasattr(chart, 'title') and chart.title:
                        text = f"{chart.title} - Frame {i+1}"

                    text_bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]

                    x = (chart.width - text_width) // 2
                    y = (chart.height - text_height) // 2

                    draw.text((x, y), text, fill='black', font=font)
                except:
                    pass

            frames.append(img)
        except Exception as e:
            # If chart conversion fails, create error frame
            img = Image.new('RGB', (800, 600), color='lightgray')
            try:
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.text((10, 10), f"Error in frame {i+1}: {str(e)[:50]}...", fill='red')
            except:
                pass
            frames.append(img)

    if frames:
        frames[0].save(
            filename,
            save_all=True,
            append_images=frames[1:],
            duration=int(duration_per_frame * 1000),
            loop=0 if loop else 1
        )