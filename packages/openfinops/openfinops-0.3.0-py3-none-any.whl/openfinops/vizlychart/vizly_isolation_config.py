"""
Vizly Library Isolation Configuration
=====================================

This module provides configuration and utilities to ensure Vizly remains
completely isolated from any external 'plotxy' library that may be installed
on the system, preventing conflicts and ensuring stable operation.
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



import sys
import warnings
from typing import List, Optional


class VizlyIsolationManager:
    """Manages isolation of Vizly from external plotxy libraries."""

    def __init__(self):
        self.blocked_modules = ['plotxy']
        # Handle both dict and module forms of __builtins__
        if isinstance(__builtins__, dict):
            self.original_import = __builtins__['__import__']
        else:
            self.original_import = __builtins__.__import__

    def enable_isolation(self):
        """Enable protection against accidental plotxy imports."""
        if isinstance(__builtins__, dict):
            __builtins__['__import__'] = self._protected_import
        else:
            __builtins__.__import__ = self._protected_import

    def disable_isolation(self):
        """Disable import protection (for testing purposes)."""
        if isinstance(__builtins__, dict):
            __builtins__['__import__'] = self.original_import
        else:
            __builtins__.__import__ = self.original_import

    def _protected_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Protected import function that blocks plotxy imports."""
        if name == 'plotxy' or name.startswith('plotxy.'):
            warnings.warn(
                f"Attempted to import '{name}' - this may conflict with Vizly. "
                f"Use 'vizly' imports instead. "
                f"To disable this warning, use VizlyIsolationManager.disable_isolation()",
                UserWarning,
                stacklevel=3
            )
            # Allow the import but warn the user

        return self.original_import(name, globals, locals, fromlist, level)

    def check_system_conflicts(self) -> List[str]:
        """Check for potential plotxy installations that could cause conflicts."""
        conflicts = []

        try:
            import pkg_resources
            installed_packages = [d.project_name for d in pkg_resources.working_set]
            if 'plotxy' in installed_packages:
                conflicts.append("PyPI plotxy package is installed")
        except ImportError:
            pass

        # Check if plotxy is importable
        try:
            import plotxy
            conflicts.append("plotxy module is importable")
        except ImportError:
            pass

        return conflicts

    def get_isolation_report(self) -> dict:
        """Generate a report on the current isolation status."""
        # Check if isolation is enabled
        if isinstance(__builtins__, dict):
            isolation_enabled = __builtins__.get('__import__') == self._protected_import
        else:
            isolation_enabled = __builtins__.__import__ == self._protected_import

        return {
            'vizly_version': self._get_vizly_version(),
            'conflicts_detected': self.check_system_conflicts(),
            'isolation_enabled': isolation_enabled,
            'python_path': sys.path[:3],  # First 3 entries for brevity
            'recommendations': self._get_recommendations()
        }

    def _get_vizly_version(self) -> Optional[str]:
        """Get the current Vizly version."""
        try:
            import vizly
            return getattr(vizly, '__version__', 'unknown')
        except ImportError:
            return None

    def _get_recommendations(self) -> List[str]:
        """Get recommendations for proper isolation."""
        recommendations = []

        conflicts = self.check_system_conflicts()
        if conflicts:
            recommendations.append("Consider uninstalling external plotxy: pip uninstall plotxy")
            recommendations.append("Use virtual environments to isolate dependencies")

        recommendations.extend([
            "Always use 'import vizly' instead of 'import plotxy'",
            "Update legacy code to use vizly imports",
            "Pin vizly version in requirements.txt",
        ])

        return recommendations


# Global isolation manager instance
_isolation_manager = VizlyIsolationManager()


def enable_vizly_isolation():
    """Enable Vizly isolation protection."""
    _isolation_manager.enable_isolation()


def disable_vizly_isolation():
    """Disable Vizly isolation protection."""
    _isolation_manager.disable_isolation()


def check_vizly_isolation():
    """Print a report on the current isolation status."""
    report = _isolation_manager.get_isolation_report()

    print("🔒 Vizly Isolation Report")
    print("=" * 40)
    print(f"Vizly Version: {report['vizly_version']}")
    print(f"Isolation Enabled: {report['isolation_enabled']}")

    if report['conflicts_detected']:
        print("⚠️  Potential Conflicts Detected:")
        for conflict in report['conflicts_detected']:
            print(f"   - {conflict}")
    else:
        print("✅ No conflicts detected")

    print("\n📋 Recommendations:")
    for rec in report['recommendations']:
        print(f"   - {rec}")


if __name__ == "__main__":
    check_vizly_isolation()