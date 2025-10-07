"""Export utilities for web components."""

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

import json
import logging
from abc import ABC, abstractmethod

from .components import BaseWebComponent

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Abstract base class for exporters."""

    @abstractmethod
    def export(self, component: BaseWebComponent) -> str:
        """Export component to string format."""
        ...


class HTMLExporter(BaseExporter):
    """Export components to HTML."""

    def export(self, component: BaseWebComponent) -> str:
        """Export component to HTML."""
        return component.to_html()


class JSONExporter(BaseExporter):
    """Export components to JSON."""

    def export(self, component: BaseWebComponent) -> str:
        """Export component to JSON."""
        return json.dumps(component.to_json(), indent=2)


class WebComponentExporter(BaseExporter):
    """Export components as web components."""

    def export(self, component: BaseWebComponent) -> str:
        """Export as web component."""
        html = component.to_html()
        json_data = json.dumps(component.to_json())

        return f"""
        <script>
        class VizlyComponent extends HTMLElement {{
            constructor() {{
                super();
                this.attachShadow({{ mode: 'open' }});
                this.data = {json_data};
            }}

            connectedCallback() {{
                this.shadowRoot.innerHTML = `{html}`;
            }}
        }}

        customElements.define('vizly-component', VizlyComponent);
        </script>
        """
