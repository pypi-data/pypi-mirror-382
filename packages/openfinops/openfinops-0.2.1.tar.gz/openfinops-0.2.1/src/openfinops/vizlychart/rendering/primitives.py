"""
Basic rendering primitives for pure Python renderer.
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



from typing import List
from .canvas import Point, Color


class Shape:
    """Base class for all drawable shapes."""

    def __init__(self, color: Color = None):
        self.color = color or Color(0, 0, 0)


class Path(Shape):
    """Path primitive for complex shapes."""

    def __init__(self, points: List[Point], color: Color = None):
        super().__init__(color)
        self.points = points


class Text(Shape):
    """Text primitive."""

    def __init__(
        self, text: str, position: Point, font_size: int = 12, color: Color = None
    ):
        super().__init__(color)
        self.text = text
        self.position = position
        self.font_size = font_size


class Image(Shape):
    """Image primitive."""

    def __init__(self, data, position: Point, width: int, height: int):
        super().__init__()
        self.data = data
        self.position = position
        self.width = width
        self.height = height
