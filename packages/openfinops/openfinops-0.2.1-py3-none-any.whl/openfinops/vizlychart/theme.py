"""Styling primitives and theme registry for Vizly."""

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
from typing import Dict, Literal, Mapping
from matplotlib import font_manager

from matplotlib import pyplot as plt

from .exceptions import ThemeNotFoundError

StyleName = Literal["light", "dark", "engineering", "extraordinary"]


@dataclass(frozen=True)
class VizlyTheme:
    """Encapsulates matplotlib style parameters used by Vizly."""

    name: StyleName
    palette: Dict[str, str]
    background: str
    grid: Dict[str, object] = field(default_factory=dict)
    font_family: str = "DejaVu Sans"

    def apply(self) -> None:
        """Apply the theme to Matplotlib's global rcParams."""
        import pathlib

        # Get the absolute path to the font file
        current_dir = pathlib.Path(__file__).parent.parent.parent
        font_path = current_dir / "orbitron" / "Orbitron Medium.ttf"

        # Only try to load the font if it exists
        if font_path.exists():
            try:
                font_manager.fontManager.addfont(str(font_path))
                prop = font_manager.FontProperties(fname=str(font_path))
                font_name = prop.get_name()
            except Exception:
                # Fall back to default font if loading fails
                font_name = self.font_family
        else:
            # Use default font family if font file doesn't exist
            font_name = self.font_family
        plt.style.use("default")
        plt.rcParams["figure.facecolor"] = self.background
        plt.rcParams["axes.facecolor"] = self.background
        plt.rcParams["axes.edgecolor"] = self.palette.get("axes", "#222222")
        plt.rcParams["axes.labelcolor"] = self.palette.get("label", "#111111")
        plt.rcParams["xtick.color"] = self.palette.get("tick", "#111111")
        plt.rcParams["ytick.color"] = self.palette.get("tick", "#111111")
        plt.rcParams["grid.color"] = self.grid.get("color", "#CCCCCC")
        plt.rcParams["grid.linestyle"] = self.grid.get("linestyle", "--")
        plt.rcParams["font.family"] = font_name


THEMES: Mapping[str, VizlyTheme] = {
    "light": VizlyTheme(
        name="light",
        palette={"axes": "#1f2933", "label": "#111827", "tick": "#4b5563"},
        background="#ffffff",
        grid={"color": "#d1d5db", "linestyle": "--"},
    ),
    "dark": VizlyTheme(
        name="dark",
        palette={"axes": "#f3f4f6", "label": "#f9fafb", "tick": "#d1d5db"},
        background="#111827",
        grid={"color": "#374151", "linestyle": ":"},
        font_family="DejaVu Sans",
    ),
    "engineering": VizlyTheme(
        name="engineering",
        palette={"axes": "#2d3748", "label": "#1a202c", "tick": "#2d3748"},
        background="#f7fafc",
        grid={"color": "#cbd5e0", "linestyle": "-"},
        font_family="DejaVu Sans Mono",
    ),
    "extraordinary": VizlyTheme(
        name="extraordinary",
        palette={
            "axes": "#c026d3",
            "label": "#be185d",
            "tick": "#db2777",
        },
        background="#000000",
        grid={"color": "#4f46e5", "linestyle": "-."},
        font_family="Orbitron",
    ),
}

ALIASES = {"eng": "engineering", "default": "light"}


def _normalize_style(style: StyleName | str) -> str:
    key = style.lower() if isinstance(style, str) else style
    return ALIASES.get(key, key)


def get_theme(style: StyleName | str) -> VizlyTheme:
    """Retrieve a theme by key and raise if not found."""
    key = _normalize_style(style)
    if key not in THEMES:
        raise ThemeNotFoundError(
            f"Unknown theme '{style}'. Available: {', '.join(sorted(THEMES))}"
        )
    return THEMES[key]


def apply_theme(style: StyleName | str) -> VizlyTheme:
    """Load a theme by name and apply it globally."""
    theme = get_theme(style)
    theme.apply()
    return theme
