"""Policy Plugin Base Class"""

from abc import abstractmethod
from typing import Dict, Any
from dataclasses import dataclass
from .base import PluginBase


@dataclass
class PolicyViolation:
    """Policy violation result."""
    policy_name: str
    resource_id: str
    violation_type: str
    severity: str
    message: str
    remediation: str


class PolicyPlugin(PluginBase):
    """
    Base class for policy enforcement plugins.

    Policy plugins implement custom governance and compliance rules.
    """

    @abstractmethod
    def evaluate_policy(
        self,
        resource: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> PolicyViolation:
        """
        Evaluate policy against a resource.

        Args:
            resource: Resource to evaluate
            context: Additional context

        Returns:
            PolicyViolation if violated, None otherwise
        """
        pass
