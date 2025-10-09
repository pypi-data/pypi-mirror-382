"""
FinOps-as-Code Provider
========================

Provider configuration for managing OpenFinOps resources as code.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """
    OpenFinOps provider configuration.

    Attributes:
        endpoint: API endpoint URL
        api_key: API authentication key
        org_id: Organization ID
        region: Default region
        timeout: Request timeout in seconds
        verify_ssl: Verify SSL certificates
        options: Additional provider options
    """

    endpoint: str
    api_key: str = ""
    org_id: str = ""
    region: str = "us-east-1"
    timeout: int = 30
    verify_ssl: bool = True
    options: Dict[str, Any] = field(default_factory=dict)

    def to_terraform(self) -> Dict[str, Any]:
        """
        Convert provider config to Terraform format.

        Returns:
            Terraform provider configuration
        """
        config = {
            "endpoint": self.endpoint,
            "region": self.region,
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl,
        }

        if self.api_key:
            config["api_key"] = self.api_key

        if self.org_id:
            config["org_id"] = self.org_id

        if self.options:
            config.update(self.options)

        return config


class OpenFinOpsProvider:
    """
    OpenFinOps Infrastructure-as-Code provider.

    Manages OpenFinOps resources programmatically.
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self._resources: Dict[str, Any] = {}
        self._initialized = False

    def initialize(self) -> bool:
        """
        Initialize provider connection.

        Returns:
            Success status
        """
        logger.info(f"Initializing OpenFinOps provider: {self.config.endpoint}")

        try:
            # In production, validate connection to API
            self._initialized = True
            logger.info("Provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize provider: {e}")
            return False

    def register_resource(self, resource_type: str, resource_id: str, resource: Any):
        """
        Register a resource with the provider.

        Args:
            resource_type: Type of resource
            resource_id: Resource identifier
            resource: Resource instance
        """
        key = f"{resource_type}.{resource_id}"
        self._resources[key] = resource
        logger.debug(f"Registered resource: {key}")

    def get_resource(self, resource_type: str, resource_id: str) -> Optional[Any]:
        """
        Get a registered resource.

        Args:
            resource_type: Type of resource
            resource_id: Resource identifier

        Returns:
            Resource instance or None
        """
        key = f"{resource_type}.{resource_id}"
        return self._resources.get(key)

    def list_resources(self, resource_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List registered resources.

        Args:
            resource_type: Filter by resource type (optional)

        Returns:
            Dictionary of resources
        """
        if resource_type:
            return {
                k: v
                for k, v in self._resources.items()
                if k.startswith(f"{resource_type}.")
            }
        return self._resources.copy()

    def validate(self) -> Dict[str, Any]:
        """
        Validate provider configuration and resources.

        Returns:
            Validation results
        """
        errors = []
        warnings = []

        # Validate configuration
        if not self.config.endpoint:
            errors.append("Endpoint is required")

        if not self.config.api_key:
            warnings.append("API key not set - some operations may fail")

        # Validate resources
        for resource_id, resource in self._resources.items():
            if hasattr(resource, "validate"):
                result = resource.validate()
                if not result.get("valid", True):
                    errors.extend(
                        [f"{resource_id}: {err}" for err in result.get("errors", [])]
                    )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "resource_count": len(self._resources),
        }

    def plan(self) -> Dict[str, Any]:
        """
        Generate execution plan for resources.

        Returns:
            Execution plan
        """
        plan = {
            "create": [],
            "update": [],
            "delete": [],
            "no_change": [],
        }

        for resource_id, resource in self._resources.items():
            if hasattr(resource, "get_plan_action"):
                action = resource.get_plan_action()
                plan[action].append(resource_id)
            else:
                plan["create"].append(resource_id)

        return plan

    def apply(self, auto_approve: bool = False) -> Dict[str, Any]:
        """
        Apply resource changes.

        Args:
            auto_approve: Skip confirmation prompt

        Returns:
            Apply results
        """
        if not self._initialized:
            raise RuntimeError("Provider not initialized")

        # Validate first
        validation = self.validate()
        if not validation["valid"]:
            raise ValueError(f"Validation failed: {validation['errors']}")

        # Get plan
        plan = self.plan()

        if not auto_approve:
            logger.warning("Auto-approve is False - apply would prompt for confirmation")

        results = {
            "created": [],
            "updated": [],
            "deleted": [],
            "failed": [],
        }

        # Apply creates
        for resource_id in plan["create"]:
            resource = self._resources[resource_id]
            try:
                if hasattr(resource, "create"):
                    resource.create()
                results["created"].append(resource_id)
                logger.info(f"Created: {resource_id}")
            except Exception as e:
                results["failed"].append({"resource": resource_id, "error": str(e)})
                logger.error(f"Failed to create {resource_id}: {e}")

        # Apply updates
        for resource_id in plan["update"]:
            resource = self._resources[resource_id]
            try:
                if hasattr(resource, "update"):
                    resource.update()
                results["updated"].append(resource_id)
                logger.info(f"Updated: {resource_id}")
            except Exception as e:
                results["failed"].append({"resource": resource_id, "error": str(e)})
                logger.error(f"Failed to update {resource_id}: {e}")

        # Apply deletes
        for resource_id in plan["delete"]:
            resource = self._resources[resource_id]
            try:
                if hasattr(resource, "delete"):
                    resource.delete()
                results["deleted"].append(resource_id)
                logger.info(f"Deleted: {resource_id}")
            except Exception as e:
                results["failed"].append({"resource": resource_id, "error": str(e)})
                logger.error(f"Failed to delete {resource_id}: {e}")

        return results

    def destroy(self) -> Dict[str, Any]:
        """
        Destroy all managed resources.

        Returns:
            Destroy results
        """
        results = {"destroyed": [], "failed": []}

        for resource_id, resource in self._resources.items():
            try:
                if hasattr(resource, "delete"):
                    resource.delete()
                results["destroyed"].append(resource_id)
                logger.info(f"Destroyed: {resource_id}")
            except Exception as e:
                results["failed"].append({"resource": resource_id, "error": str(e)})
                logger.error(f"Failed to destroy {resource_id}: {e}")

        return results

    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        return self._initialized


def create_provider(
    endpoint: str,
    api_key: str = "",
    org_id: str = "",
    **options,
) -> OpenFinOpsProvider:
    """
    Create OpenFinOps provider.

    Args:
        endpoint: API endpoint URL
        api_key: API authentication key
        org_id: Organization ID
        **options: Additional provider options

    Returns:
        OpenFinOps provider instance
    """
    config = ProviderConfig(
        endpoint=endpoint,
        api_key=api_key,
        org_id=org_id,
        options=options,
    )

    provider = OpenFinOpsProvider(config)
    provider.initialize()

    return provider
