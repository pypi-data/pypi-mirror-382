"""
IAM Configuration Loader for OpenFinOps
========================================

Loads and manages IAM configurations from YAML/JSON files.
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



import os
import yaml
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class IAMConfig:
    """Complete IAM configuration."""
    security_settings: Dict[str, Any] = field(default_factory=dict)
    data_classifications: Dict[str, int] = field(default_factory=dict)
    dashboard_types: List[str] = field(default_factory=list)
    roles: Dict[str, Any] = field(default_factory=dict)
    personas: Dict[str, Any] = field(default_factory=dict)
    role_templates: Dict[str, Any] = field(default_factory=dict)


class IAMConfigLoader:
    """Load and validate IAM configurations."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize config loader.

        Args:
            config_path: Path to custom config file. If None, uses default.
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Optional[IAMConfig] = None

    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        return os.path.join(
            os.path.dirname(__file__),
            'iam_config.yaml'
        )

    def load_config(self) -> IAMConfig:
        """Load IAM configuration from file."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Config file not found: {self.config_path}")
            return self._get_default_config()

        try:
            with open(self.config_path, 'r') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    data = yaml.safe_load(f)
                elif self.config_path.endswith('.json'):
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {self.config_path}")

            self.config = IAMConfig(
                security_settings=data.get('security_settings', {}),
                data_classifications=data.get('data_classifications', {}),
                dashboard_types=data.get('dashboard_types', []),
                roles=data.get('roles', {}),
                personas=data.get('personas', {}),
                role_templates=data.get('role_templates', {})
            )

            logger.info(f"Loaded IAM config from {self.config_path}")
            return self.config

        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> IAMConfig:
        """Get minimal default configuration."""
        return IAMConfig(
            security_settings={
                'session_timeout': 3600,
                'require_mfa_for_executives': True
            },
            data_classifications={
                'PUBLIC': 0,
                'INTERNAL': 1,
                'CONFIDENTIAL': 2,
                'RESTRICTED': 3
            },
            dashboard_types=[
                'CFO_EXECUTIVE',
                'CTO_TECHNICAL',
                'COO_OPERATIONAL',
                'CEO_STRATEGIC'
            ],
            roles={},
            personas={},
            role_templates={}
        )

    def get_role_config(self, role_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific role."""
        if not self.config:
            self.load_config()
        return self.config.roles.get(role_name)

    def get_persona_config(self, persona_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific persona."""
        if not self.config:
            self.load_config()
        return self.config.personas.get(persona_name)

    def get_all_roles(self) -> Dict[str, Any]:
        """Get all configured roles."""
        if not self.config:
            self.load_config()
        return self.config.roles

    def get_all_personas(self) -> Dict[str, Any]:
        """Get all configured personas."""
        if not self.config:
            self.load_config()
        return self.config.personas

    def create_user_from_persona(self, persona_name: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user configuration from persona template.

        Args:
            persona_name: Name of persona template
            user_data: User-specific data (user_id, username, email, etc.)

        Returns:
            Complete user configuration
        """
        persona = self.get_persona_config(persona_name)
        if not persona:
            raise ValueError(f"Persona not found: {persona_name}")

        # Merge persona template with user data
        user_config = {
            'user_id': user_data['user_id'],
            'username': user_data['username'],
            'email': user_data['email'],
            'full_name': user_data.get('full_name', user_data['username']),
            'department': persona.get('department', user_data.get('department', 'Unknown')),
            'roles': persona.get('roles', []),
            'default_dashboard': persona.get('default_dashboard'),
            'notification_preferences': persona.get('notification_preferences', {}),
            'custom_settings': persona.get('custom_settings', {})
        }

        # Add password if provided
        if 'password' in user_data:
            user_config['password'] = user_data['password']

        return user_config

    def save_config(self, output_path: Optional[str] = None):
        """Save current configuration to file.

        Args:
            output_path: Path to save config. If None, overwrites current config.
        """
        if not self.config:
            raise ValueError("No configuration loaded")

        save_path = output_path or self.config_path

        config_dict = {
            'security_settings': self.config.security_settings,
            'data_classifications': self.config.data_classifications,
            'dashboard_types': self.config.dashboard_types,
            'roles': self.config.roles,
            'personas': self.config.personas,
            'role_templates': self.config.role_templates
        }

        try:
            with open(save_path, 'w') as f:
                if save_path.endswith('.yaml') or save_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
                elif save_path.endswith('.json'):
                    json.dump(config_dict, f, indent=2)
                else:
                    raise ValueError(f"Unsupported format: {save_path}")

            logger.info(f"Saved IAM config to {save_path}")

        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise

    def add_custom_role(self, role_name: str, role_config: Dict[str, Any]):
        """Add a custom role to configuration.

        Args:
            role_name: Unique role identifier
            role_config: Role configuration dictionary
        """
        if not self.config:
            self.load_config()

        self.config.roles[role_name] = role_config
        logger.info(f"Added custom role: {role_name}")

    def add_custom_persona(self, persona_name: str, persona_config: Dict[str, Any]):
        """Add a custom persona template.

        Args:
            persona_name: Unique persona identifier
            persona_config: Persona configuration dictionary
        """
        if not self.config:
            self.load_config()

        self.config.personas[persona_name] = persona_config
        logger.info(f"Added custom persona: {persona_name}")

    def validate_config(self) -> List[str]:
        """Validate configuration and return any errors.

        Returns:
            List of validation error messages
        """
        errors = []

        if not self.config:
            self.load_config()

        # Validate roles
        for role_name, role_config in self.config.roles.items():
            if 'display_name' not in role_config:
                errors.append(f"Role '{role_name}' missing display_name")
            if 'data_access_level' not in role_config:
                errors.append(f"Role '{role_name}' missing data_access_level")
            if 'allowed_dashboards' not in role_config:
                errors.append(f"Role '{role_name}' missing allowed_dashboards")

        # Validate personas
        for persona_name, persona_config in self.config.personas.items():
            if 'roles' not in persona_config:
                errors.append(f"Persona '{persona_name}' missing roles")
            else:
                # Check that referenced roles exist
                for role in persona_config['roles']:
                    if role not in self.config.roles:
                        errors.append(f"Persona '{persona_name}' references unknown role '{role}'")

        return errors


# Global config loader instance
_config_loader = None


def get_config_loader(config_path: Optional[str] = None) -> IAMConfigLoader:
    """Get global config loader instance.

    Args:
        config_path: Optional custom config path

    Returns:
        IAMConfigLoader instance
    """
    global _config_loader
    if _config_loader is None or config_path:
        _config_loader = IAMConfigLoader(config_path)
    return _config_loader


def load_iam_config(config_path: Optional[str] = None) -> IAMConfig:
    """Load IAM configuration.

    Args:
        config_path: Optional custom config path

    Returns:
        IAMConfig object
    """
    loader = get_config_loader(config_path)
    return loader.load_config()
