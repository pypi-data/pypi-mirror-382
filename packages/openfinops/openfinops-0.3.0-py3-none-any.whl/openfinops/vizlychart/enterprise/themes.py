"""
Enterprise Themes & Styling
===========================

Professional themes and styling options for enterprise visualization
including corporate branding, accessibility, and presentation-ready layouts.
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

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
import warnings

try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    from cycler import cycler
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn("Matplotlib not available for enterprise themes")

from ..theme import VizlyTheme


@dataclass
class BrandingConfig:
    """Corporate branding configuration."""
    primary_color: str = "#2c5aa0"
    secondary_color: str = "#28a745"
    accent_color: str = "#ffc107"
    warning_color: str = "#fd7e14"
    danger_color: str = "#dc3545"
    logo_path: Optional[str] = None
    company_name: str = "Enterprise"
    font_family: str = "Arial"
    watermark_text: Optional[str] = None


@dataclass
class AccessibilityConfig:
    """Accessibility configuration for inclusive design."""
    colorblind_friendly: bool = True
    high_contrast: bool = False
    large_fonts: bool = False
    pattern_fills: bool = False  # Use patterns instead of colors only
    screen_reader_friendly: bool = True


class EnterpriseTheme:
    """
    Enterprise theme with professional styling, branding support,
    and accessibility features.
    """

    def __init__(self, branding: Optional[BrandingConfig] = None,
                 accessibility: Optional[AccessibilityConfig] = None):
        self.branding = branding or BrandingConfig()
        self.accessibility = accessibility or AccessibilityConfig()
        self.colors = []
        self.rcParams = {}
        self._setup_enterprise_defaults()

    def _setup_enterprise_defaults(self) -> None:
        """Setup enterprise-specific default styling."""
        if not MATPLOTLIB_AVAILABLE:
            return

        # Professional color palette
        if self.accessibility.colorblind_friendly:
            # Colorblind-friendly palette
            self.colors = [
                "#1f77b4",  # Blue
                "#ff7f0e",  # Orange
                "#2ca02c",  # Green
                "#d62728",  # Red
                "#9467bd",  # Purple
                "#8c564b",  # Brown
                "#e377c2",  # Pink
                "#7f7f7f",  # Gray
                "#bcbd22",  # Olive
                "#17becf"   # Cyan
            ]
        else:
            # Corporate colors
            self.colors = [
                self.branding.primary_color,
                self.branding.secondary_color,
                self.branding.accent_color,
                "#6c757d",  # Gray
                "#17a2b8",  # Info blue
                "#6f42c1",  # Purple
                "#e83e8c",  # Pink
                "#fd7e14",  # Orange
                "#20c997",  # Teal
                "#6610f2"   # Indigo
            ]

        # Typography
        font_size = 12 if self.accessibility.large_fonts else 10
        self.rcParams.update({
            'font.family': [self.branding.font_family],
            'font.size': font_size,
            'axes.titlesize': font_size + 2,
            'axes.labelsize': font_size,
            'xtick.labelsize': font_size - 1,
            'ytick.labelsize': font_size - 1,
            'legend.fontsize': font_size - 1,
            'figure.titlesize': font_size + 4
        })

        # Professional grid and styling
        self.rcParams.update({
            'axes.grid': True,
            'grid.alpha': 0.3,
            'grid.linewidth': 0.5,
            'axes.axisbelow': True,
            'axes.edgecolor': '#666666',
            'axes.linewidth': 0.8,
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'savefig.facecolor': 'white',
            'savefig.dpi': 300,  # High DPI for presentations
            'figure.dpi': 100
        })

        # High contrast mode
        if self.accessibility.high_contrast:
            self.rcParams.update({
                'axes.edgecolor': 'black',
                'axes.linewidth': 1.5,
                'grid.linewidth': 1.0,
                'lines.linewidth': 2.0
            })

    def apply_corporate_branding(self, fig) -> None:
        """Apply corporate branding elements to figure."""
        if not MATPLOTLIB_AVAILABLE:
            return

        # Add company logo if available
        if self.branding.logo_path:
            self._add_logo(fig)

        # Add watermark if specified
        if self.branding.watermark_text:
            self._add_watermark(fig)

        # Set color cycle
        fig.gca().set_prop_cycle(cycler('color', self.colors))

    def _add_logo(self, fig) -> None:
        """Add company logo to figure."""
        try:
            import matplotlib.image as mpimg
            logo = mpimg.imread(self.branding.logo_path)

            # Add logo in top-right corner
            logo_ax = fig.add_axes([0.85, 0.85, 0.1, 0.1])
            logo_ax.imshow(logo)
            logo_ax.axis('off')
        except Exception:
            # Silently fail if logo can't be loaded
            pass

    def _add_watermark(self, fig) -> None:
        """Add watermark text to figure."""
        fig.text(0.95, 0.02, self.branding.watermark_text,
                ha='right', va='bottom', alpha=0.3, rotation=0,
                fontsize=8, color='gray')

    def get_status_colors(self) -> Dict[str, str]:
        """Get standardized status colors for enterprise dashboards."""
        return {
            'excellent': '#28a745',
            'good': '#6abf69',
            'warning': '#ffc107',
            'critical': '#dc3545',
            'neutral': '#6c757d',
            'unknown': '#adb5bd'
        }

    def get_financial_colors(self) -> Dict[str, str]:
        """Get colors for financial data visualization."""
        return {
            'profit': '#28a745',
            'loss': '#dc3545',
            'revenue': '#007bff',
            'expense': '#fd7e14',
            'budget': '#6f42c1',
            'forecast': '#17a2b8'
        }


class PresentationTheme(EnterpriseTheme):
    """Theme optimized for presentation and executive reporting."""

    def __init__(self, branding: Optional[BrandingConfig] = None):
        accessibility = AccessibilityConfig(large_fonts=True, high_contrast=True)
        super().__init__(branding, accessibility)

        # Presentation-specific overrides
        self.rcParams.update({
            'font.size': 14,
            'axes.titlesize': 18,
            'figure.titlesize': 22,
            'lines.linewidth': 3.0,
            'lines.markersize': 8,
            'xtick.major.size': 6,
            'ytick.major.size': 6,
            'legend.frameon': True,
            'legend.fancybox': True,
            'legend.shadow': True
        })


class PrintTheme(EnterpriseTheme):
    """Theme optimized for printed reports and documentation."""

    def __init__(self, branding: Optional[BrandingConfig] = None):
        accessibility = AccessibilityConfig(
            colorblind_friendly=True,
            pattern_fills=True
        )
        super().__init__(branding, accessibility)

        # Print-specific overrides
        self.rcParams.update({
            'font.size': 9,
            'axes.titlesize': 11,
            'figure.titlesize': 14,
            'lines.linewidth': 1.0,
            'savefig.dpi': 600,  # High DPI for print
            'figure.facecolor': 'white',
            'text.color': 'black',
            'axes.labelcolor': 'black',
            'xtick.color': 'black',
            'ytick.color': 'black'
        })

        # Use patterns for better print readability
        self.use_patterns = True

    def get_print_patterns(self) -> List[str]:
        """Get patterns for print-friendly charts."""
        return ['///', '\\\\\\', '|||', '---', '+++', 'xxx', 'ooo', '...']


class DarkTheme(EnterpriseTheme):
    """Dark theme for presentations and low-light environments."""

    def __init__(self, branding: Optional[BrandingConfig] = None):
        super().__init__(branding)

        # Dark theme colors
        self.colors = [
            "#ff6b6b",  # Red
            "#4ecdc4",  # Teal
            "#45b7d1",  # Blue
            "#96ceb4",  # Green
            "#feca57",  # Yellow
            "#ff9ff3",  # Pink
            "#54a0ff",  # Light Blue
            "#5f27cd",  # Purple
            "#00d2d3",  # Cyan
            "#ff9f43"   # Orange
        ]

        # Dark background styling
        self.rcParams.update({
            'figure.facecolor': '#1e1e1e',
            'axes.facecolor': '#2d2d2d',
            'savefig.facecolor': '#1e1e1e',
            'text.color': 'white',
            'axes.labelcolor': 'white',
            'axes.edgecolor': '#666666',
            'xtick.color': 'white',
            'ytick.color': 'white',
            'grid.color': '#444444',
            'legend.facecolor': '#2d2d2d',
            'legend.edgecolor': '#666666'
        })


class ThemeManager:
    """Manager for enterprise themes and styling."""

    def __init__(self):
        self.available_themes = {
            'enterprise': EnterpriseTheme,
            'presentation': PresentationTheme,
            'print': PrintTheme,
            'dark': DarkTheme
        }
        self.current_theme: Optional[EnterpriseTheme] = None

    def apply_theme(self, theme_name: str, branding: Optional[BrandingConfig] = None,
                   accessibility: Optional[AccessibilityConfig] = None) -> None:
        """Apply enterprise theme."""
        if theme_name not in self.available_themes:
            raise ValueError(f"Unknown theme: {theme_name}")

        theme_class = self.available_themes[theme_name]

        if theme_name in ['presentation', 'print', 'dark']:
            self.current_theme = theme_class(branding)
        else:
            self.current_theme = theme_class(branding, accessibility)

        # Apply to matplotlib
        if MATPLOTLIB_AVAILABLE:
            plt.rcParams.update(self.current_theme.rcParams)

    def create_custom_branding(self, primary_color: str, company_name: str,
                             logo_path: Optional[str] = None) -> BrandingConfig:
        """Create custom branding configuration."""
        return BrandingConfig(
            primary_color=primary_color,
            company_name=company_name,
            logo_path=logo_path,
            watermark_text=f"© {company_name} - Confidential"
        )

    def get_accessibility_config(self, requirements: List[str]) -> AccessibilityConfig:
        """Get accessibility configuration based on requirements."""
        config = AccessibilityConfig()

        if 'colorblind' in requirements:
            config.colorblind_friendly = True
        if 'high_contrast' in requirements:
            config.high_contrast = True
        if 'large_fonts' in requirements:
            config.large_fonts = True
        if 'patterns' in requirements:
            config.pattern_fills = True
        if 'screen_reader' in requirements:
            config.screen_reader_friendly = True

        return config

    def export_theme_config(self) -> Dict[str, any]:
        """Export current theme configuration."""
        if not self.current_theme:
            return {}

        return {
            'branding': {
                'primary_color': self.current_theme.branding.primary_color,
                'secondary_color': self.current_theme.branding.secondary_color,
                'company_name': self.current_theme.branding.company_name,
                'font_family': self.current_theme.branding.font_family
            },
            'accessibility': {
                'colorblind_friendly': self.current_theme.accessibility.colorblind_friendly,
                'high_contrast': self.current_theme.accessibility.high_contrast,
                'large_fonts': self.current_theme.accessibility.large_fonts
            },
            'colors': self.current_theme.colors
        }

    def load_theme_config(self, config: Dict[str, any]) -> None:
        """Load theme from configuration."""
        branding_data = config.get('branding', {})
        accessibility_data = config.get('accessibility', {})

        branding = BrandingConfig(
            primary_color=branding_data.get('primary_color', '#2c5aa0'),
            secondary_color=branding_data.get('secondary_color', '#28a745'),
            company_name=branding_data.get('company_name', 'Enterprise'),
            font_family=branding_data.get('font_family', 'Arial')
        )

        accessibility = AccessibilityConfig(
            colorblind_friendly=accessibility_data.get('colorblind_friendly', True),
            high_contrast=accessibility_data.get('high_contrast', False),
            large_fonts=accessibility_data.get('large_fonts', False)
        )

        self.current_theme = EnterpriseTheme(branding, accessibility)
        if 'colors' in config:
            self.current_theme.colors = config['colors']

        # Apply to matplotlib
        if MATPLOTLIB_AVAILABLE:
            plt.rcParams.update(self.current_theme.rcParams)