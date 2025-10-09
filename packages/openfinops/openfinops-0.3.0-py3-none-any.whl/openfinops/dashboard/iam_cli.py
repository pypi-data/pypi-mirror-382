#!/usr/bin/env python3
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

"""
IAM Configuration CLI for OpenFinOps
====================================

Command-line tool to manage IAM roles, personas, and users.

Usage:
    # List all roles
    python iam_cli.py list-roles

    # List all personas
    python iam_cli.py list-personas

    # Create user from persona
    python iam_cli.py create-user --persona cfo_persona --username john.doe --email john@company.com

    # Add custom role
    python iam_cli.py add-role --config custom_role.yaml

    # Validate configuration
    python iam_cli.py validate

    # Export configuration
    python iam_cli.py export --output my_iam_config.yaml
"""

import argparse
import sys
import json
import yaml
from typing import Dict, Any
from pathlib import Path

from iam_config_loader import get_config_loader, IAMConfigLoader
from iam_system import get_iam_manager


class IAMCLICommands:
    """IAM CLI command implementations."""

    def __init__(self, config_path: str = None):
        self.loader = get_config_loader(config_path)
        self.loader.load_config()

    def list_roles(self, output_format: str = 'table'):
        """List all configured roles."""
        roles = self.loader.get_all_roles()

        if output_format == 'json':
            print(json.dumps(roles, indent=2))
        elif output_format == 'yaml':
            print(yaml.dump(roles, default_flow_style=False))
        else:
            # Table format
            print(f"{'Role Name':<25} {'Display Name':<35} {'Access Level':<15} {'MFA Required':<12}")
            print("=" * 90)
            for role_name, config in roles.items():
                display_name = config.get('display_name', role_name)
                access_level = config.get('data_access_level', 'N/A')
                mfa = 'Yes' if config.get('require_mfa', False) else 'No'
                print(f"{role_name:<25} {display_name:<35} {access_level:<15} {mfa:<12}")

    def list_personas(self, output_format: str = 'table'):
        """List all configured personas."""
        personas = self.loader.get_all_personas()

        if output_format == 'json':
            print(json.dumps(personas, indent=2))
        elif output_format == 'yaml':
            print(yaml.dump(personas, default_flow_style=False))
        else:
            # Table format
            print(f"{'Persona Name':<25} {'Roles':<30} {'Department':<20} {'Default Dashboard':<25}")
            print("=" * 105)
            for persona_name, config in personas.items():
                roles = ', '.join(config.get('roles', []))
                department = config.get('department', 'N/A')
                dashboard = config.get('default_dashboard', 'N/A')
                print(f"{persona_name:<25} {roles:<30} {department:<20} {dashboard:<25}")

    def show_role(self, role_name: str, output_format: str = 'yaml'):
        """Show detailed configuration for a role."""
        role_config = self.loader.get_role_config(role_name)

        if not role_config:
            print(f"Error: Role '{role_name}' not found", file=sys.stderr)
            return 1

        if output_format == 'json':
            print(json.dumps({role_name: role_config}, indent=2))
        else:
            print(yaml.dump({role_name: role_config}, default_flow_style=False))

        return 0

    def show_persona(self, persona_name: str, output_format: str = 'yaml'):
        """Show detailed configuration for a persona."""
        persona_config = self.loader.get_persona_config(persona_name)

        if not persona_config:
            print(f"Error: Persona '{persona_name}' not found", file=sys.stderr)
            return 1

        if output_format == 'json':
            print(json.dumps({persona_name: persona_config}, indent=2))
        else:
            print(yaml.dump({persona_name: persona_config}, default_flow_style=False))

        return 0

    def create_user(self, persona: str, username: str, email: str,
                   full_name: str = None, password: str = None):
        """Create a user from persona template."""
        try:
            user_data = {
                'user_id': f"user-{username}",
                'username': username,
                'email': email,
                'full_name': full_name or username
            }

            if password:
                user_data['password'] = password

            user_config = self.loader.create_user_from_persona(persona, user_data)

            # Create user in IAM system
            iam = get_iam_manager()
            user = iam.create_user(user_config)

            print(f"✓ Successfully created user '{username}' from persona '{persona}'")
            print(f"  User ID: {user.user_id}")
            print(f"  Email: {user.email}")
            print(f"  Roles: {', '.join(user.roles)}")
            print(f"  Department: {user.department}")
            return 0

        except Exception as e:
            print(f"Error creating user: {e}", file=sys.stderr)
            return 1

    def add_role(self, config_file: str):
        """Add a custom role from configuration file."""
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    role_data = yaml.safe_load(f)
                else:
                    role_data = json.load(f)

            # Expect format: { "role_name": { config } }
            for role_name, role_config in role_data.items():
                self.loader.add_custom_role(role_name, role_config)
                print(f"✓ Added role '{role_name}'")

            return 0

        except Exception as e:
            print(f"Error adding role: {e}", file=sys.stderr)
            return 1

    def add_persona(self, config_file: str):
        """Add a custom persona from configuration file."""
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    persona_data = yaml.safe_load(f)
                else:
                    persona_data = json.load(f)

            for persona_name, persona_config in persona_data.items():
                self.loader.add_custom_persona(persona_name, persona_config)
                print(f"✓ Added persona '{persona_name}'")

            return 0

        except Exception as e:
            print(f"Error adding persona: {e}", file=sys.stderr)
            return 1

    def validate(self):
        """Validate IAM configuration."""
        print("Validating IAM configuration...")
        errors = self.loader.validate_config()

        if not errors:
            print("✓ Configuration is valid")
            return 0
        else:
            print(f"✗ Found {len(errors)} validation errors:")
            for error in errors:
                print(f"  - {error}")
            return 1

    def export_config(self, output_path: str):
        """Export current configuration to file."""
        try:
            self.loader.save_config(output_path)
            print(f"✓ Exported configuration to {output_path}")
            return 0
        except Exception as e:
            print(f"Error exporting configuration: {e}", file=sys.stderr)
            return 1

    def list_users(self):
        """List all users in IAM system."""
        iam = get_iam_manager()

        print(f"{'User ID':<25} {'Username':<20} {'Email':<30} {'Roles':<30}")
        print("=" * 110)

        for user_id, user in iam.users.items():
            roles = ', '.join(user.roles)
            print(f"{user_id:<25} {user.username:<20} {user.email:<30} {roles:<30}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='OpenFinOps IAM Configuration Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--config',
        help='Path to custom IAM configuration file',
        default=None
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # list-roles command
    list_roles_parser = subparsers.add_parser('list-roles', help='List all roles')
    list_roles_parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table')

    # list-personas command
    list_personas_parser = subparsers.add_parser('list-personas', help='List all personas')
    list_personas_parser.add_argument('--format', choices=['table', 'json', 'yaml'], default='table')

    # show-role command
    show_role_parser = subparsers.add_parser('show-role', help='Show role details')
    show_role_parser.add_argument('role_name', help='Role name')
    show_role_parser.add_argument('--format', choices=['json', 'yaml'], default='yaml')

    # show-persona command
    show_persona_parser = subparsers.add_parser('show-persona', help='Show persona details')
    show_persona_parser.add_argument('persona_name', help='Persona name')
    show_persona_parser.add_argument('--format', choices=['json', 'yaml'], default='yaml')

    # create-user command
    create_user_parser = subparsers.add_parser('create-user', help='Create user from persona')
    create_user_parser.add_argument('--persona', required=True, help='Persona template name')
    create_user_parser.add_argument('--username', required=True, help='Username')
    create_user_parser.add_argument('--email', required=True, help='Email address')
    create_user_parser.add_argument('--full-name', help='Full name')
    create_user_parser.add_argument('--password', help='Password')

    # add-role command
    add_role_parser = subparsers.add_parser('add-role', help='Add custom role')
    add_role_parser.add_argument('--config', dest='role_config', required=True, help='Role config file')

    # add-persona command
    add_persona_parser = subparsers.add_parser('add-persona', help='Add custom persona')
    add_persona_parser.add_argument('--config', dest='persona_config', required=True, help='Persona config file')

    # validate command
    subparsers.add_parser('validate', help='Validate IAM configuration')

    # export command
    export_parser = subparsers.add_parser('export', help='Export configuration')
    export_parser.add_argument('--output', required=True, help='Output file path')

    # list-users command
    subparsers.add_parser('list-users', help='List all users')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize CLI commands
    cli = IAMCLICommands(config_path=args.config)

    # Execute command
    if args.command == 'list-roles':
        return cli.list_roles(args.format)
    elif args.command == 'list-personas':
        return cli.list_personas(args.format)
    elif args.command == 'show-role':
        return cli.show_role(args.role_name, args.format)
    elif args.command == 'show-persona':
        return cli.show_persona(args.persona_name, args.format)
    elif args.command == 'create-user':
        return cli.create_user(
            args.persona, args.username, args.email,
            args.full_name, args.password
        )
    elif args.command == 'add-role':
        return cli.add_role(args.role_config)
    elif args.command == 'add-persona':
        return cli.add_persona(args.persona_config)
    elif args.command == 'validate':
        return cli.validate()
    elif args.command == 'export':
        return cli.export_config(args.output)
    elif args.command == 'list-users':
        return cli.list_users()
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
