"""
Vizly VR/AR Visualization Module
===============================

Advanced virtual and augmented reality visualization capabilities for Vizly.
Supports WebXR, OpenXR, and immersive spatial visualization.

Basic Usage:
    >>> import vizly.vr as vr
    >>> # WebXR session
    >>> session = vr.WebXRSession("immersive-vr")
    >>> session.add_chart({'type': 'scatter', 'data': data})
    >>> await session.request_session()

    >>> # VR scene
    >>> scene = vr.VRScene()
    >>> chart = vizly.SurfaceChart()
    >>> vr_chart = scene.add_chart(chart)
    >>> scene.start_vr_session()

Supported Platforms:
    - WebXR (browser-based VR/AR)
    - Native VR/AR applications
    - Spatial computing environments
    - Immersive visualization displays
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



from .core import VRScene, ARScene, XREnvironment, VRChart, ARChart
from .webxr import WebXRSession, WebXRServer
from .spatial import SpatialRenderer, VRCanvas, ARCanvas, SpatialObject
from .immersive_charts import (
    ImmersiveChart, VRScatterChart, VRSurfaceChart, VRLineChart,
    AROverlayChart, ImmersiveChartRenderer
)

__version__ = "0.5.0"
__all__ = [
    # Core VR/AR
    "VRScene", "ARScene", "XREnvironment", "VRChart", "ARChart",
    # WebXR
    "WebXRSession", "WebXRServer",
    # Spatial rendering
    "SpatialRenderer", "VRCanvas", "ARCanvas", "SpatialObject",
    # Immersive charts
    "ImmersiveChart", "VRScatterChart", "VRSurfaceChart", "VRLineChart",
    "AROverlayChart", "ImmersiveChartRenderer",
]