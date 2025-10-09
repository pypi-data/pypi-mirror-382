"""Dashboard Plugin Base Class"""

from abc import abstractmethod
from typing import Any
from .base import PluginBase


class DashboardPlugin(PluginBase):
    """
    Base class for dashboard widget plugins.

    Dashboard plugins create custom visualizations and widgets.
    """

    @abstractmethod
    def render(self, **kwargs) -> Any:
        """
        Render the dashboard widget.

        Returns:
            Rendered widget (format depends on implementation)
        """
        pass

    def get_widget_config(self):
        """Get widget configuration."""
        return {
            "title": self.get_config_value("title", "Custom Widget"),
            "width": self.get_config_value("width", 12),
            "height": self.get_config_value("height", 6),
        }
