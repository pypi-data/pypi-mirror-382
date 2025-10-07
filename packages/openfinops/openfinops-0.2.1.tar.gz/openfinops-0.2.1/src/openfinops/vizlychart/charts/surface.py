"""Surface and mesh plotting utilities."""

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
from typing import Iterable, Optional

import numpy as np

from .base import BaseChart
from ..exceptions import VizlyError


class _Axes3DInteractor:
    """Lightweight mouse/scroll interactor for Matplotlib 3D axes."""

    def __init__(self, axes) -> None:  # pragma: no cover - UI glue
        self.axes = axes
        self.canvas = axes.figure.canvas
        self._drag_button: Optional[int] = None
        self._last_xy: Optional[tuple[float, float]] = None
        self._cids: list[int] = []
        self._register_events()

    def _register_events(self) -> None:  # pragma: no cover - UI glue
        self._cids.extend(
            [
                self.canvas.mpl_connect("button_press_event", self._on_press),
                self.canvas.mpl_connect("button_release_event", self._on_release),
                self.canvas.mpl_connect("motion_notify_event", self._on_motion),
                self.canvas.mpl_connect("scroll_event", self._on_scroll),
            ]
        )

    def disconnect(self) -> None:  # pragma: no cover - UI glue
        for cid in self._cids:
            self.canvas.mpl_disconnect(cid)
        self._cids.clear()

    def _on_press(self, event) -> None:  # pragma: no cover - UI glue
        if event.inaxes is not self.axes:
            return
        self._drag_button = event.button
        self._last_xy = (event.x, event.y)

    def _on_release(self, event) -> None:  # pragma: no cover - UI glue
        if event.button == self._drag_button:
            self._drag_button = None
            self._last_xy = None

    def _on_motion(self, event) -> None:  # pragma: no cover - UI glue
        if self._drag_button is None or self._last_xy is None:
            return
        if event.inaxes is not self.axes:
            return
        dx = event.x - self._last_xy[0]
        dy = event.y - self._last_xy[1]
        if self._drag_button == 1:
            self._rotate(dx, dy)
        elif self._drag_button in {2, 3}:
            self._pan(dx, dy)
        self._last_xy = (event.x, event.y)
        self.canvas.draw_idle()

    def _rotate(self, dx: float, dy: float) -> None:  # pragma: no cover - UI glue
        azim = (self.axes.azim - dx * 0.4) % 360
        elev = np.clip(self.axes.elev - dy * 0.3, -170, 170)
        self.axes.view_init(elev=elev, azim=azim)

    def _pan(self, dx: float, dy: float) -> None:  # pragma: no cover - UI glue
        width, height = self.canvas.get_width_height()
        if width == 0 or height == 0:
            return
        scale_x = dx / width
        scale_y = dy / height
        for getter, setter in (
            (self.axes.get_xlim3d, self.axes.set_xlim3d),
            (self.axes.get_ylim3d, self.axes.set_ylim3d),
        ):
            lower, upper = getter()
            span = upper - lower
            if getter is self.axes.get_xlim3d:
                delta = -scale_x * span
            else:
                delta = scale_y * span
            setter((lower + delta, upper + delta))

    def _on_scroll(self, event) -> None:  # pragma: no cover - UI glue
        if event.inaxes is not self.axes:
            return
        direction = -1 if getattr(event, "button", "up") == "up" else 1
        factor = 0.9 if direction < 0 else 1.1
        for getter, setter in (
            (self.axes.get_xlim3d, self.axes.set_xlim3d),
            (self.axes.get_ylim3d, self.axes.set_ylim3d),
            (self.axes.get_zlim3d, self.axes.set_zlim3d),
        ):
            lower, upper = getter()
            center = (lower + upper) / 2
            half_range = (upper - lower) * factor / 2
            setter((center - half_range, center + half_range))
        self.canvas.draw_idle()


@dataclass
class SurfaceChart(BaseChart):
    """Render 3D surfaces using Matplotlib's mplot3d toolkit."""

    def __post_init__(self) -> None:
        super().__post_init__()
        if not hasattr(self.axes, "plot_surface"):
            axes = self.figure.add_subplot(111, projection="3d")
            self.bind_axes(axes)

    def plot(
        self,
        x_grid: Iterable[Iterable[float]] | np.ndarray,
        y_grid: Iterable[Iterable[float]] | np.ndarray,
        z_grid: Iterable[Iterable[float]] | np.ndarray,
        *,
        cmap: str = "viridis",
        linewidth: float = 0.0,
        antialiased: bool = True,
    ) -> None:
        x = np.array(x_grid, dtype=float)
        y = np.array(y_grid, dtype=float)
        z = np.array(z_grid, dtype=float)
        if x.shape != y.shape or x.shape != z.shape:
            raise ValueError("x, y, and z grids must have equal dimensions")
        self.axes.plot_surface(
            x, y, z, cmap=cmap, linewidth=linewidth, antialiased=antialiased
        )
        self.axes.set_xlabel("X")
        self.axes.set_ylabel("Y")
        self.axes.set_zlabel("Z")

    def plot_surface(
        self,
        x_grid: Iterable[Iterable[float]] | np.ndarray,
        y_grid: Iterable[Iterable[float]] | np.ndarray,
        z_grid: Iterable[Iterable[float]] | np.ndarray,
        *,
        cmap: str = "viridis",
        linewidth: float = 0.0,
        antialiased: bool = True,
        alpha: float = 1.0,
        lighting: bool = True,
        **kwargs
    ) -> None:
        """
        Create a 3D surface plot.

        This is an alias for plot() with additional matplotlib-compatible parameters.

        Parameters:
            x_grid: X coordinates of the surface grid
            y_grid: Y coordinates of the surface grid
            z_grid: Z coordinates of the surface grid
            cmap: Colormap name
            linewidth: Width of surface grid lines
            antialiased: Enable antialiasing
            alpha: Surface transparency (0-1)
            lighting: Enable 3D lighting effects
            **kwargs: Additional matplotlib plot_surface parameters
        """
        # Convert inputs to numpy arrays
        x = np.array(x_grid, dtype=float)
        y = np.array(y_grid, dtype=float)
        z = np.array(z_grid, dtype=float)

        if x.shape != y.shape or x.shape != z.shape:
            raise ValueError("x, y, and z grids must have equal dimensions")

        # Apply additional styling parameters
        surface_kwargs = {
            'cmap': cmap,
            'linewidth': linewidth,
            'antialiased': antialiased,
            'alpha': alpha,
            **kwargs
        }

        # Create the surface plot
        surface = self.axes.plot_surface(x, y, z, **surface_kwargs)

        # Apply lighting if requested
        if lighting:
            self.axes.view_init(elev=30, azim=45)

        # Set axis labels
        self.axes.set_xlabel("X")
        self.axes.set_ylabel("Y")
        self.axes.set_zlabel("Z")

        return surface


@dataclass
class InteractiveSurfaceChart(SurfaceChart):
    """Render 3D surfaces with lightweight mouse interaction support."""

    _interactor: Optional[_Axes3DInteractor] = field(
        default=None, init=False, repr=False
    )
    _mesh_cache: Optional[dict[str, object]] = field(
        default=None, init=False, repr=False
    )

    def plot(
        self,
        x_grid: Iterable[Iterable[float]] | np.ndarray,
        y_grid: Iterable[Iterable[float]] | np.ndarray,
        z_grid: Iterable[Iterable[float]] | np.ndarray,
        *,
        cmap: str = "viridis",
        linewidth: float = 0.0,
        antialiased: bool = True,
        enable_interaction: bool = True,
        capture_mesh: bool = True,
    ) -> None:
        super().plot(
            x_grid,
            y_grid,
            z_grid,
            cmap=cmap,
            linewidth=linewidth,
            antialiased=antialiased,
        )
        if capture_mesh:
            x = np.array(x_grid, dtype=float)
            y = np.array(y_grid, dtype=float)
            z = np.array(z_grid, dtype=float)
            self._mesh_cache = {
                "rows": int(x.shape[0]),
                "cols": int(x.shape[1]),
                "x": x.ravel().tolist(),
                "y": y.ravel().tolist(),
                "z": z.ravel().tolist(),
                "zmin": float(z.min()),
                "zmax": float(z.max()),
                "cmap": cmap,
            }
        if enable_interaction:
            self.enable_interaction()

    def enable_interaction(self) -> None:  # pragma: no cover - UI glue
        if self._interactor is not None:
            return
        canvas = getattr(self.figure.figure, "canvas", None)
        if canvas is None:  # headless backend
            return
        self._interactor = _Axes3DInteractor(self.axes)

    def disable_interaction(self) -> None:  # pragma: no cover - UI glue
        if self._interactor is None:
            return
        self._interactor.disconnect()
        self._interactor = None

    def export_mesh(self) -> dict[str, object]:
        if self._mesh_cache is None:
            raise VizlyError(
                "Interactive surface has no mesh cache. Call plot() first."
            )
        return self._mesh_cache
