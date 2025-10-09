"""
Natural Language Styling Engine
==============================

Convert natural language style descriptions into chart styling parameters.
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

import re
import colorsys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

import numpy as np


class ColorScheme(Enum):
    """Predefined color schemes."""
    PROFESSIONAL = "professional"
    VIBRANT = "vibrant"
    PASTEL = "pastel"
    MONOCHROME = "monochrome"
    WARM = "warm"
    COOL = "cool"
    EARTH = "earth"
    NEON = "neon"


class StyleTheme(Enum):
    """Overall style themes."""
    BUSINESS = "business"
    SCIENTIFIC = "scientific"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    BOLD = "bold"
    ELEGANT = "elegant"
    MODERN = "modern"
    CLASSIC = "classic"


@dataclass
class StyleConfig:
    """Complete styling configuration."""
    # Colors
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    color_scheme: Optional[ColorScheme] = None

    # Typography
    font_family: Optional[str] = None
    font_size: Optional[int] = None
    title_size: Optional[int] = None
    font_weight: Optional[str] = None

    # Layout and spacing
    figure_size: Optional[Tuple[int, int]] = None
    margins: Optional[Dict[str, float]] = None
    padding: Optional[float] = None

    # Visual elements
    line_width: Optional[float] = None
    point_size: Optional[float] = None
    transparency: Optional[float] = None
    grid_style: Optional[str] = None

    # Theme
    overall_theme: Optional[StyleTheme] = None
    background_color: Optional[str] = None

    # Special effects
    gradient: bool = False
    shadow: bool = False
    border_style: Optional[str] = None


class ColorParser:
    """Parse color-related natural language."""

    def __init__(self):
        self.color_names = {
            # Basic colors
            'red': '#FF0000', 'blue': '#0000FF', 'green': '#00FF00',
            'yellow': '#FFFF00', 'orange': '#FFA500', 'purple': '#800080',
            'pink': '#FFC0CB', 'brown': '#A52A2A', 'gray': '#808080',
            'grey': '#808080', 'black': '#000000', 'white': '#FFFFFF',

            # Extended colors
            'crimson': '#DC143C', 'navy': '#000080', 'forest': '#228B22',
            'gold': '#FFD700', 'coral': '#FF7F50', 'indigo': '#4B0082',
            'salmon': '#FA8072', 'chocolate': '#D2691E', 'silver': '#C0C0C0',
            'lime': '#00FF00', 'cyan': '#00FFFF', 'magenta': '#FF00FF',

            # Shades
            'light blue': '#ADD8E6', 'dark blue': '#00008B',
            'light green': '#90EE90', 'dark green': '#006400',
            'light gray': '#D3D3D3', 'dark gray': '#A9A9A9',
            'bright red': '#FF4500', 'deep red': '#8B0000',
        }

        self.color_schemes = {
            ColorScheme.PROFESSIONAL: ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D'],
            ColorScheme.VIBRANT: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7'],
            ColorScheme.PASTEL: ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFD3BA'],
            ColorScheme.MONOCHROME: ['#2C3E50', '#34495E', '#7F8C8D', '#95A5A6', '#BDC3C7'],
            ColorScheme.WARM: ['#FF6B35', '#F7931E', '#FFD23F', '#06FFA5', '#4D79A4'],
            ColorScheme.COOL: ['#0077BE', '#005F99', '#003D66', '#001A33', '#6FAADB'],
            ColorScheme.EARTH: ['#8D5524', '#C68642', '#E0AC69', '#F1C27D', '#FFDBAC'],
            ColorScheme.NEON: ['#FF0080', '#00FF80', '#8000FF', '#FF8000', '#0080FF']
        }

        self.intensity_modifiers = {
            'bright': 1.3, 'vivid': 1.3, 'bold': 1.2, 'vibrant': 1.2,
            'dark': 0.7, 'deep': 0.7, 'muted': 0.8, 'soft': 0.8,
            'light': 1.4, 'pale': 1.5, 'faded': 0.9
        }

    def parse_color(self, text: str) -> Optional[str]:
        """Parse a single color from text."""
        text = text.lower().strip()

        # Direct color name match
        if text in self.color_names:
            return self.color_names[text]

        # Check for hex colors
        hex_match = re.search(r'#[0-9a-f]{6}', text, re.IGNORECASE)
        if hex_match:
            return hex_match.group(0)

        # Check for RGB values
        rgb_match = re.search(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', text)
        if rgb_match:
            r, g, b = map(int, rgb_match.groups())
            return f'#{r:02x}{g:02x}{b:02x}'

        # Check for modified colors (e.g., "bright red", "dark blue")
        for modifier, factor in self.intensity_modifiers.items():
            if modifier in text:
                color_part = text.replace(modifier, '').strip()
                if color_part in self.color_names:
                    base_color = self.color_names[color_part]
                    return self._modify_color_intensity(base_color, factor)

        return None

    def parse_color_scheme(self, text: str) -> Optional[ColorScheme]:
        """Parse color scheme from text."""
        text = text.lower()

        scheme_keywords = {
            'professional': ColorScheme.PROFESSIONAL,
            'business': ColorScheme.PROFESSIONAL,
            'corporate': ColorScheme.PROFESSIONAL,
            'vibrant': ColorScheme.VIBRANT,
            'bright': ColorScheme.VIBRANT,
            'colorful': ColorScheme.VIBRANT,
            'pastel': ColorScheme.PASTEL,
            'soft': ColorScheme.PASTEL,
            'gentle': ColorScheme.PASTEL,
            'monochrome': ColorScheme.MONOCHROME,
            'grayscale': ColorScheme.MONOCHROME,
            'black and white': ColorScheme.MONOCHROME,
            'warm': ColorScheme.WARM,
            'hot': ColorScheme.WARM,
            'cool': ColorScheme.COOL,
            'cold': ColorScheme.COOL,
            'earth': ColorScheme.EARTH,
            'natural': ColorScheme.EARTH,
            'organic': ColorScheme.EARTH,
            'neon': ColorScheme.NEON,
            'electric': ColorScheme.NEON,
            'fluorescent': ColorScheme.NEON
        }

        for keyword, scheme in scheme_keywords.items():
            if keyword in text:
                return scheme

        return None

    def get_palette(self, scheme: ColorScheme, count: int = 5) -> List[str]:
        """Get color palette from scheme."""
        base_colors = self.color_schemes[scheme]

        if count <= len(base_colors):
            return base_colors[:count]

        # Generate additional colors by varying the base ones
        extended_palette = base_colors.copy()
        while len(extended_palette) < count:
            for base_color in base_colors:
                if len(extended_palette) >= count:
                    break
                # Create a slightly different variant
                variant = self._create_color_variant(base_color)
                extended_palette.append(variant)

        return extended_palette[:count]

    def _modify_color_intensity(self, hex_color: str, factor: float) -> str:
        """Modify color intensity/brightness."""
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Convert to HSV for better manipulation
        h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

        # Modify value (brightness)
        v = min(1.0, max(0.0, v * factor))

        # Convert back to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)

        return f'#{r:02x}{g:02x}{b:02x}'

    def _create_color_variant(self, hex_color: str) -> str:
        """Create a variant of the given color."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Convert to HSV
        h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

        # Slightly shift hue and saturation
        h = (h + 0.1) % 1.0  # Shift hue by 36 degrees
        s = min(1.0, max(0.3, s + 0.1))  # Adjust saturation

        # Convert back
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        r, g, b = int(r * 255), int(g * 255), int(b * 255)

        return f'#{r:02x}{g:02x}{b:02x}'


class StyleParser:
    """Parse natural language style descriptions."""

    def __init__(self):
        self.color_parser = ColorParser()
        self.font_families = {
            'serif': ['Times New Roman', 'Georgia', 'serif'],
            'sans-serif': ['Arial', 'Helvetica', 'sans-serif'],
            'monospace': ['Courier New', 'Monaco', 'monospace'],
            'modern': ['Roboto', 'Open Sans', 'sans-serif'],
            'elegant': ['Georgia', 'Playfair Display', 'serif'],
            'technical': ['DejaVu Sans Mono', 'Consolas', 'monospace'],
            'professional': ['Calibri', 'Tahoma', 'sans-serif']
        }

        self.theme_configs = {
            StyleTheme.BUSINESS: {
                'color_scheme': ColorScheme.PROFESSIONAL,
                'font_family': 'professional',
                'background_color': '#FFFFFF',
                'grid_style': 'solid'
            },
            StyleTheme.SCIENTIFIC: {
                'color_scheme': ColorScheme.MONOCHROME,
                'font_family': 'serif',
                'background_color': '#FAFAFA',
                'grid_style': 'dashed'
            },
            StyleTheme.CREATIVE: {
                'color_scheme': ColorScheme.VIBRANT,
                'font_family': 'modern',
                'background_color': '#F8F9FA',
                'gradient': True
            },
            StyleTheme.MINIMAL: {
                'color_scheme': ColorScheme.MONOCHROME,
                'font_family': 'sans-serif',
                'background_color': '#FFFFFF',
                'grid_style': None
            },
            StyleTheme.BOLD: {
                'color_scheme': ColorScheme.VIBRANT,
                'font_family': 'sans-serif',
                'font_weight': 'bold',
                'line_width': 3.0
            },
            StyleTheme.ELEGANT: {
                'color_scheme': ColorScheme.PASTEL,
                'font_family': 'elegant',
                'background_color': '#FEFEFE',
                'shadow': True
            }
        }

    def parse(self, description: str) -> StyleConfig:
        """Parse natural language style description into StyleConfig."""
        config = StyleConfig()
        description = description.lower()

        # Parse theme first (affects other defaults)
        theme = self._parse_theme(description)
        if theme:
            config.overall_theme = theme
            # Apply theme defaults
            theme_config = self.theme_configs[theme]
            for key, value in theme_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        # Parse colors
        config.primary_color = self._parse_primary_color(description)
        config.secondary_color = self._parse_secondary_color(description)
        config.color_scheme = self._parse_color_scheme(description)
        config.background_color = self._parse_background_color(description)

        # Parse typography
        config.font_family = self._parse_font_family(description)
        config.font_size = self._parse_font_size(description)
        config.font_weight = self._parse_font_weight(description)

        # Parse sizes and dimensions
        config.figure_size = self._parse_figure_size(description)
        config.line_width = self._parse_line_width(description)
        config.point_size = self._parse_point_size(description)

        # Parse visual effects
        config.transparency = self._parse_transparency(description)
        config.grid_style = self._parse_grid_style(description)
        config.gradient = self._parse_boolean_feature(description, 'gradient')
        config.shadow = self._parse_boolean_feature(description, 'shadow')

        return config

    def _parse_theme(self, text: str) -> Optional[StyleTheme]:
        """Parse overall theme."""
        theme_keywords = {
            'business': StyleTheme.BUSINESS,
            'professional': StyleTheme.BUSINESS,
            'corporate': StyleTheme.BUSINESS,
            'scientific': StyleTheme.SCIENTIFIC,
            'academic': StyleTheme.SCIENTIFIC,
            'research': StyleTheme.SCIENTIFIC,
            'creative': StyleTheme.CREATIVE,
            'artistic': StyleTheme.CREATIVE,
            'minimal': StyleTheme.MINIMAL,
            'minimalist': StyleTheme.MINIMAL,
            'clean': StyleTheme.MINIMAL,
            'simple': StyleTheme.MINIMAL,
            'bold': StyleTheme.BOLD,
            'strong': StyleTheme.BOLD,
            'striking': StyleTheme.BOLD,
            'elegant': StyleTheme.ELEGANT,
            'sophisticated': StyleTheme.ELEGANT,
            'refined': StyleTheme.ELEGANT,
            'modern': StyleTheme.MODERN,
            'contemporary': StyleTheme.MODERN,
            'classic': StyleTheme.CLASSIC,
            'traditional': StyleTheme.CLASSIC,
            'timeless': StyleTheme.CLASSIC
        }

        for keyword, theme in theme_keywords.items():
            if keyword in text:
                return theme

        return None

    def _parse_primary_color(self, text: str) -> Optional[str]:
        """Parse primary color."""
        # Look for explicit primary color
        primary_match = re.search(r'primary color?\s*:?\s*([a-z\s#0-9]+)', text)
        if primary_match:
            return self.color_parser.parse_color(primary_match.group(1))

        # Look for main color
        main_match = re.search(r'main color?\s*:?\s*([a-z\s#0-9]+)', text)
        if main_match:
            return self.color_parser.parse_color(main_match.group(1))

        # Look for first mentioned color
        color_words = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'gray', 'black']
        for color in color_words:
            if color in text:
                return self.color_parser.parse_color(color)

        return None

    def _parse_secondary_color(self, text: str) -> Optional[str]:
        """Parse secondary color."""
        secondary_match = re.search(r'secondary color?\s*:?\s*([a-z\s#0-9]+)', text)
        if secondary_match:
            return self.color_parser.parse_color(secondary_match.group(1))

        return None

    def _parse_color_scheme(self, text: str) -> Optional[ColorScheme]:
        """Parse color scheme."""
        return self.color_parser.parse_color_scheme(text)

    def _parse_background_color(self, text: str) -> Optional[str]:
        """Parse background color."""
        bg_match = re.search(r'background\s*:?\s*([a-z\s#0-9]+)', text)
        if bg_match:
            return self.color_parser.parse_color(bg_match.group(1))

        # Common background descriptions
        if 'white background' in text or 'light background' in text:
            return '#FFFFFF'
        elif 'dark background' in text or 'black background' in text:
            return '#2C3E50'
        elif 'transparent background' in text:
            return 'transparent'

        return None

    def _parse_font_family(self, text: str) -> Optional[str]:
        """Parse font family."""
        font_match = re.search(r'font\s*:?\s*([a-z\s-]+)', text)
        if font_match:
            font_desc = font_match.group(1).strip()
            if font_desc in self.font_families:
                return self.font_families[font_desc][0]  # Return primary font

        # Check for font type keywords
        if any(word in text for word in ['serif', 'times']):
            return self.font_families['serif'][0]
        elif any(word in text for word in ['sans-serif', 'arial', 'helvetica']):
            return self.font_families['sans-serif'][0]
        elif any(word in text for word in ['monospace', 'courier']):
            return self.font_families['monospace'][0]

        return None

    def _parse_font_size(self, text: str) -> Optional[int]:
        """Parse font size."""
        # Look for explicit size
        size_match = re.search(r'font size\s*:?\s*(\d+)', text)
        if size_match:
            return int(size_match.group(1))

        # Size descriptors
        if any(word in text for word in ['large font', 'big font', 'huge font']):
            return 14
        elif any(word in text for word in ['small font', 'tiny font']):
            return 10
        elif 'medium font' in text:
            return 12

        return None

    def _parse_font_weight(self, text: str) -> Optional[str]:
        """Parse font weight."""
        if any(word in text for word in ['bold', 'thick', 'heavy']):
            return 'bold'
        elif any(word in text for word in ['light', 'thin']):
            return 'light'
        elif 'normal' in text:
            return 'normal'

        return None

    def _parse_figure_size(self, text: str) -> Optional[Tuple[int, int]]:
        """Parse figure size."""
        # Look for explicit dimensions
        size_match = re.search(r'(\d+)\s*x\s*(\d+)', text)
        if size_match:
            return (int(size_match.group(1)), int(size_match.group(2)))

        # Size descriptors
        if any(word in text for word in ['large chart', 'big chart', 'huge chart']):
            return (1200, 800)
        elif any(word in text for word in ['small chart', 'tiny chart']):
            return (600, 400)
        elif 'wide chart' in text:
            return (1000, 600)
        elif 'tall chart' in text:
            return (600, 900)

        return None

    def _parse_line_width(self, text: str) -> Optional[float]:
        """Parse line width."""
        # Look for explicit width
        width_match = re.search(r'line width\s*:?\s*([\d.]+)', text)
        if width_match:
            return float(width_match.group(1))

        # Width descriptors
        if any(word in text for word in ['thick lines', 'bold lines', 'heavy lines']):
            return 3.0
        elif any(word in text for word in ['thin lines', 'fine lines', 'light lines']):
            return 1.0
        elif any(word in text for word in ['medium lines', 'normal lines']):
            return 2.0

        return None

    def _parse_point_size(self, text: str) -> Optional[float]:
        """Parse point/marker size."""
        if any(word in text for word in ['large points', 'big points', 'huge points']):
            return 8.0
        elif any(word in text for word in ['small points', 'tiny points']):
            return 3.0
        elif any(word in text for word in ['medium points', 'normal points']):
            return 5.0

        return None

    def _parse_transparency(self, text: str) -> Optional[float]:
        """Parse transparency/alpha."""
        # Look for explicit alpha
        alpha_match = re.search(r'alpha\s*:?\s*([\d.]+)', text)
        if alpha_match:
            return float(alpha_match.group(1))

        # Transparency descriptors
        if any(word in text for word in ['transparent', 'see-through']):
            return 0.7
        elif any(word in text for word in ['semi-transparent', 'translucent']):
            return 0.8
        elif 'opaque' in text:
            return 1.0

        return None

    def _parse_grid_style(self, text: str) -> Optional[str]:
        """Parse grid style."""
        if 'dotted grid' in text:
            return 'dotted'
        elif 'dashed grid' in text:
            return 'dashed'
        elif 'solid grid' in text:
            return 'solid'
        elif 'no grid' in text:
            return None

        return None

    def _parse_boolean_feature(self, text: str, feature: str) -> bool:
        """Parse boolean features like gradient, shadow."""
        positive_patterns = [f'with {feature}', f'{feature}', f'add {feature}']
        negative_patterns = [f'no {feature}', f'without {feature}', f'remove {feature}']

        for pattern in positive_patterns:
            if pattern in text:
                return True

        for pattern in negative_patterns:
            if pattern in text:
                return False

        return False


class NaturalLanguageStylist:
    """Main class for converting natural language to chart styles."""

    def __init__(self):
        self.parser = StyleParser()

    def style_from_text(self, description: str) -> StyleConfig:
        """Convert natural language description to style configuration."""
        return self.parser.parse(description)

    def apply_to_chart(self, chart, style_config: StyleConfig):
        """Apply style configuration to a chart object."""
        # Apply colors
        if style_config.primary_color:
            self._set_chart_color(chart, style_config.primary_color)

        if style_config.color_scheme:
            palette = self.parser.color_parser.get_palette(style_config.color_scheme)
            self._set_chart_palette(chart, palette)

        if style_config.background_color:
            self._set_background_color(chart, style_config.background_color)

        # Apply typography
        if style_config.font_family:
            self._set_font_family(chart, style_config.font_family)

        if style_config.font_size:
            self._set_font_size(chart, style_config.font_size)

        # Apply sizes
        if style_config.figure_size:
            self._set_figure_size(chart, style_config.figure_size)

        if style_config.line_width:
            self._set_line_width(chart, style_config.line_width)

        if style_config.point_size:
            self._set_point_size(chart, style_config.point_size)

        # Apply visual effects
        if style_config.transparency:
            self._set_transparency(chart, style_config.transparency)

        if style_config.grid_style is not None:
            self._set_grid_style(chart, style_config.grid_style)

    def _set_chart_color(self, chart, color: str):
        """Set primary chart color."""
        if hasattr(chart, 'set_color'):
            chart.set_color(color)
        elif hasattr(chart, 'color'):
            chart.color = color

    def _set_chart_palette(self, chart, palette: List[str]):
        """Set chart color palette."""
        if hasattr(chart, 'set_palette'):
            chart.set_palette(palette)
        elif hasattr(chart, 'colors'):
            chart.colors = palette

    def _set_background_color(self, chart, color: str):
        """Set background color."""
        if hasattr(chart, 'set_background'):
            chart.set_background(color)
        elif hasattr(chart, 'figure') and hasattr(chart.figure, 'patch'):
            chart.figure.patch.set_facecolor(color)

    def _set_font_family(self, chart, font_family: str):
        """Set font family."""
        if hasattr(chart, 'set_font'):
            chart.set_font(font_family)
        # Implementation depends on chart type and backend

    def _set_font_size(self, chart, font_size: int):
        """Set font size."""
        if hasattr(chart, 'set_font_size'):
            chart.set_font_size(font_size)

    def _set_figure_size(self, chart, size: Tuple[int, int]):
        """Set figure size."""
        if hasattr(chart, 'set_size'):
            chart.set_size(size[0], size[1])
        elif hasattr(chart, 'figure'):
            chart.figure.set_size_inches(size[0]/100, size[1]/100)

    def _set_line_width(self, chart, width: float):
        """Set line width."""
        if hasattr(chart, 'set_line_width'):
            chart.set_line_width(width)

    def _set_point_size(self, chart, size: float):
        """Set point/marker size."""
        if hasattr(chart, 'set_point_size'):
            chart.set_point_size(size)

    def _set_transparency(self, chart, alpha: float):
        """Set transparency."""
        if hasattr(chart, 'set_alpha'):
            chart.set_alpha(alpha)

    def _set_grid_style(self, chart, style: Optional[str]):
        """Set grid style."""
        if hasattr(chart, 'set_grid'):
            chart.set_grid(style is not None, style=style if style else 'solid')

    def generate_style_suggestions(self, chart_type: str, data_context: str = "") -> List[str]:
        """Generate style suggestions based on chart type and context."""
        suggestions = []

        base_suggestions = [
            "Use a professional business theme with blue and gray colors",
            "Apply a vibrant color scheme with bold fonts",
            "Create a minimal design with clean lines and white background",
            "Use an elegant style with soft pastel colors and shadows"
        ]

        chart_specific = {
            'line': [
                "Use thick lines with gradient background",
                "Apply a scientific theme with monospace font and grid",
                "Create a time series look with date formatting"
            ],
            'scatter': [
                "Use large semi-transparent points with vibrant colors",
                "Apply a correlation theme with cool color scheme",
                "Create bubble chart effect with varying point sizes"
            ],
            'bar': [
                "Use horizontal bars with professional colors",
                "Apply gradient fills with shadow effects",
                "Create a comparison theme with contrasting colors"
            ]
        }

        suggestions.extend(base_suggestions)
        if chart_type in chart_specific:
            suggestions.extend(chart_specific[chart_type])

        return suggestions


# Convenient functions
def style_chart(chart, description: str):
    """Apply natural language styling to a chart."""
    stylist = NaturalLanguageStylist()
    config = stylist.style_from_text(description)
    stylist.apply_to_chart(chart, config)
    return chart

def parse_style(description: str) -> StyleConfig:
    """Parse natural language style description."""
    parser = StyleParser()
    return parser.parse(description)