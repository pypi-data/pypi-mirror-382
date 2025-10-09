"""Advanced configuration management for Vizly."""

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
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import warnings


@dataclass
class RenderingConfig:
    """Configuration for rendering performance and quality."""

    backend: str = "auto"  # 'matplotlib', 'plotly', 'bokeh', 'auto'
    dpi: int = 300
    antialiasing: bool = True
    rasterized: bool = False
    optimize_for_speed: bool = False
    gpu_acceleration: bool = False
    max_render_points: int = 100_000
    downsampling_strategy: str = "uniform"  # 'uniform', 'adaptive', 'peak_preserve'


@dataclass
class DataConfig:
    """Configuration for data handling and validation."""

    max_data_size: int = 10_000_000  # Maximum number of data points
    auto_sanitize: bool = True
    outlier_detection: bool = True
    outlier_threshold: float = 6.0  # Standard deviations
    missing_value_strategy: str = "warn"  # 'error', 'warn', 'ignore', 'interpolate'
    data_type_validation: bool = True
    memory_efficient: bool = False


@dataclass
class InteractionConfig:
    """Configuration for chart interactivity."""

    zoom_enabled: bool = True
    pan_enabled: bool = True
    selection_enabled: bool = False
    hover_tooltips: bool = False
    keyboard_shortcuts: bool = True
    mouse_sensitivity: float = 1.0
    touch_gestures: bool = True


@dataclass
class ExportConfig:
    """Configuration for data and chart export."""

    default_format: str = "png"
    supported_formats: List[str] = field(
        default_factory=lambda: ["png", "jpg", "svg", "pdf", "html"]
    )
    default_dpi: int = 300
    compression_quality: int = 95
    embed_data: bool = False
    metadata_enabled: bool = True


@dataclass
class ThemeConfig:
    """Configuration for chart appearance and styling."""

    default_theme: str = "modern"
    color_palette: str = "viridis"
    font_family: str = "sans-serif"
    font_size: int = 12
    figure_size: tuple[float, float] = (10.0, 8.0)
    grid_alpha: float = 0.3
    legend_style: str = "modern"  # 'classic', 'modern', 'minimal'


@dataclass
class PerformanceConfig:
    """Configuration for performance monitoring and optimization."""

    monitoring_enabled: bool = False
    sample_interval: float = 1.0
    history_size: int = 300
    auto_optimization: bool = True
    memory_limit_mb: int = 1024
    cpu_threshold: float = 80.0
    memory_threshold: float = 85.0


@dataclass
class VizlyConfig:
    """Main configuration container for Vizly."""

    rendering: RenderingConfig = field(default_factory=RenderingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    interaction: InteractionConfig = field(default_factory=InteractionConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

    # Global settings
    debug_mode: bool = False
    verbose_warnings: bool = True
    auto_show: bool = False
    figure_backend: str = "auto"


class ConfigManager:
    """Manages Vizly configuration with file persistence and validation."""

    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        self.config = VizlyConfig()
        self._config_file = self._resolve_config_file(config_file)
        self._load_config()

    def _resolve_config_file(self, config_file: Optional[Union[str, Path]]) -> Path:
        """Resolve configuration file path."""
        if config_file:
            return Path(config_file)

        # Try common locations
        candidates = [
            Path.cwd() / "vizly_config.json",
            Path.home() / ".vizly" / "config.json",
            Path.home() / ".config" / "vizly" / "config.json",
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        # Default to user config directory
        default_path = Path.home() / ".vizly" / "config.json"
        default_path.parent.mkdir(parents=True, exist_ok=True)
        return default_path

    def _load_config(self) -> None:
        """Load configuration from file."""
        if not self._config_file.exists():
            self._save_config()  # Create default config
            return

        try:
            with open(self._config_file, "r") as f:
                data = json.load(f)

            # Update config with loaded data
            self._update_config_from_dict(data)

        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            warnings.warn(
                f"Failed to load config from {self._config_file}: {e}", UserWarning
            )

    def _update_config_from_dict(self, data: dict) -> None:
        """Update configuration from dictionary."""
        for section_name, section_data in data.items():
            if hasattr(self.config, section_name):
                section = getattr(self.config, section_name)
                if hasattr(section, "__dict__"):
                    # Update dataclass fields
                    for key, value in section_data.items():
                        if hasattr(section, key):
                            setattr(section, key, value)
                else:
                    # Direct attribute
                    setattr(self.config, section_name, section_data)

    def _save_config(self) -> None:
        """Save current configuration to file."""
        try:
            data = asdict(self.config)
            with open(self._config_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except (PermissionError, OSError) as e:
            warnings.warn(
                f"Failed to save config to {self._config_file}: {e}", UserWarning
            )

    def get(self, path: str) -> Any:
        """Get configuration value by dot-separated path."""
        parts = path.split(".")
        value = self.config

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                raise KeyError(f"Configuration path '{path}' not found")

        return value

    def set(self, path: str, value: Any, save: bool = True) -> None:
        """Set configuration value by dot-separated path."""
        parts = path.split(".")
        obj = self.config

        # Navigate to parent object
        for part in parts[:-1]:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                raise KeyError(f"Configuration path '{'.'.join(parts[:-1])}' not found")

        # Set the final value
        final_key = parts[-1]
        if hasattr(obj, final_key):
            setattr(obj, final_key, value)
            if save:
                self._save_config()
        else:
            raise KeyError(f"Configuration key '{final_key}' not found")

    def reset_section(self, section: str) -> None:
        """Reset a configuration section to defaults."""
        if section == "rendering":
            self.config.rendering = RenderingConfig()
        elif section == "data":
            self.config.data = DataConfig()
        elif section == "interaction":
            self.config.interaction = InteractionConfig()
        elif section == "export":
            self.config.export = ExportConfig()
        elif section == "theme":
            self.config.theme = ThemeConfig()
        elif section == "performance":
            self.config.performance = PerformanceConfig()
        else:
            raise ValueError(f"Unknown configuration section: {section}")

        self._save_config()

    def reset_all(self) -> None:
        """Reset all configuration to defaults."""
        self.config = VizlyConfig()
        self._save_config()

    def validate_config(self) -> List[str]:
        """Validate current configuration and return list of issues."""
        issues = []

        # Validate rendering config
        if self.config.rendering.dpi < 50 or self.config.rendering.dpi > 1200:
            issues.append("DPI should be between 50 and 1200")

        if self.config.rendering.max_render_points < 100:
            issues.append("max_render_points should be at least 100")

        # Validate data config
        if self.config.data.max_data_size < 1000:
            issues.append("max_data_size should be at least 1000")

        if (
            self.config.data.outlier_threshold < 1.0
            or self.config.data.outlier_threshold > 10.0
        ):
            issues.append("outlier_threshold should be between 1.0 and 10.0")

        # Validate performance config
        if (
            self.config.performance.sample_interval < 0.1
            or self.config.performance.sample_interval > 60.0
        ):
            issues.append(
                "performance sample_interval should be between 0.1 and 60.0 seconds"
            )

        if self.config.performance.memory_limit_mb < 64:
            issues.append("memory_limit_mb should be at least 64 MB")

        return issues

    def get_optimized_config(
        self, data_size: int, complexity: str = "medium"
    ) -> Dict[str, Any]:
        """Get optimized configuration based on data characteristics."""
        optimizations = {}

        # Optimize based on data size
        if data_size > 1_000_000:
            optimizations.update(
                {
                    "rendering.rasterized": True,
                    "rendering.optimize_for_speed": True,
                    "rendering.max_render_points": 50_000,
                    "data.memory_efficient": True,
                    "performance.monitoring_enabled": True,
                }
            )
        elif data_size > 100_000:
            optimizations.update(
                {
                    "rendering.max_render_points": data_size // 2,
                    "data.memory_efficient": True,
                }
            )

        # Optimize based on complexity
        if complexity == "high":
            optimizations.update(
                {
                    "rendering.antialiasing": False,
                    "performance.auto_optimization": True,
                    "performance.monitoring_enabled": True,
                }
            )
        elif complexity == "low":
            optimizations.update(
                {
                    "rendering.antialiasing": True,
                    "rendering.dpi": 300,
                }
            )

        return optimizations

    def apply_optimizations(self, optimizations: Dict[str, Any]) -> None:
        """Apply a set of optimizations to the configuration."""
        for path, value in optimizations.items():
            try:
                self.set(path, value, save=False)
            except KeyError:
                warnings.warn(f"Unknown optimization path: {path}", UserWarning)

        self._save_config()

    def export_config(self, file_path: Union[str, Path]) -> None:
        """Export configuration to a file."""
        file_path = Path(file_path)
        try:
            data = asdict(self.config)
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except (PermissionError, OSError) as e:
            raise RuntimeError(f"Failed to export config to {file_path}: {e}")

    def import_config(self, file_path: Union[str, Path]) -> None:
        """Import configuration from a file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            self._update_config_from_dict(data)
            self._save_config()

        except (json.JSONDecodeError, PermissionError, OSError) as e:
            raise RuntimeError(f"Failed to import config from {file_path}: {e}")

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration."""
        return {
            "config_file": str(self._config_file),
            "rendering": {
                "backend": self.config.rendering.backend,
                "dpi": self.config.rendering.dpi,
                "optimization": self.config.rendering.optimize_for_speed,
            },
            "data": {
                "max_size": self.config.data.max_data_size,
                "sanitization": self.config.data.auto_sanitize,
                "outlier_detection": self.config.data.outlier_detection,
            },
            "performance": {
                "monitoring": self.config.performance.monitoring_enabled,
                "auto_optimization": self.config.performance.auto_optimization,
            },
            "validation_issues": self.validate_config(),
        }


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> VizlyConfig:
    """Get the current configuration."""
    return get_config_manager().config


def set_config(path: str, value: Any) -> None:
    """Set a configuration value."""
    get_config_manager().set(path, value)


def reset_config(section: Optional[str] = None) -> None:
    """Reset configuration section or all configuration."""
    manager = get_config_manager()
    if section:
        manager.reset_section(section)
    else:
        manager.reset_all()


def configure_for_performance(data_size: int, enable_monitoring: bool = True) -> None:
    """Quick configuration for performance scenarios."""
    manager = get_config_manager()
    optimizations = manager.get_optimized_config(data_size, "high")

    if enable_monitoring:
        optimizations["performance.monitoring_enabled"] = True

    manager.apply_optimizations(optimizations)


def configure_for_quality(high_dpi: bool = True) -> None:
    """Quick configuration for high-quality output."""
    manager = get_config_manager()
    optimizations = {
        "rendering.antialiasing": True,
        "rendering.rasterized": False,
        "rendering.optimize_for_speed": False,
    }

    if high_dpi:
        optimizations["rendering.dpi"] = 600

    manager.apply_optimizations(optimizations)
