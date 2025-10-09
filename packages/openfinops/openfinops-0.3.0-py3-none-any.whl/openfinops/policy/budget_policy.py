"""
Budget Policy Enforcement
=========================

Budget policies with thresholds, alerts, and automatic enforcement.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

from .policy_engine import Policy, PolicyType, PolicySeverity, PolicyEvaluation

logger = logging.getLogger(__name__)


class BudgetPeriod(Enum):
    """Budget period types."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


@dataclass
class BudgetThreshold:
    """
    Budget threshold definition.

    Attributes:
        percentage: Threshold as percentage of budget (0-100)
        actions: Actions to take when threshold is exceeded
        severity: Severity level for this threshold
    """

    percentage: float
    actions: List[str] = field(default_factory=list)
    severity: PolicySeverity = PolicySeverity.WARNING


@dataclass
class BudgetViolation:
    """
    Budget violation details.

    Attributes:
        budget_name: Name of budget
        current_spend: Current spending
        budget_limit: Budget limit
        percentage_used: Percentage of budget used
        exceeded_by: Amount over budget
        threshold: Threshold that was exceeded
        timestamp: Violation timestamp
    """

    budget_name: str
    current_spend: float
    budget_limit: float
    percentage_used: float
    exceeded_by: float
    threshold: BudgetThreshold
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


class BudgetPolicy(Policy):
    """
    Budget enforcement policy.

    Enforces spending limits with configurable thresholds and actions.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        limit: float = 0.0,
        period: BudgetPeriod = BudgetPeriod.MONTHLY,
        scope: Optional[Dict[str, Any]] = None,
        thresholds: Optional[List[BudgetThreshold]] = None,
        auto_adjust: bool = False,
        rollover_unused: bool = False,
        severity: PolicySeverity = PolicySeverity.ERROR,
        actions: Optional[List[str]] = None,
    ):
        """
        Initialize budget policy.

        Args:
            name: Policy name
            description: Policy description
            limit: Budget limit
            period: Budget period
            scope: Budget scope (e.g., {"team": "platform"})
            thresholds: Warning thresholds before limit
            auto_adjust: Automatically adjust budget based on trends
            rollover_unused: Rollover unused budget to next period
            severity: Default severity
            actions: Actions to take on budget exceeded
        """
        super().__init__(
            name=name,
            description=description,
            policy_type=PolicyType.BUDGET,
            severity=severity,
            scope=scope or {},
            actions=actions or ["alert", "notify"],
        )

        self.limit = limit
        self.period = period
        self.auto_adjust = auto_adjust
        self.rollover_unused = rollover_unused

        # Default thresholds if not provided
        if thresholds is None:
            self.thresholds = [
                BudgetThreshold(
                    percentage=80.0,
                    actions=["alert"],
                    severity=PolicySeverity.WARNING,
                ),
                BudgetThreshold(
                    percentage=90.0,
                    actions=["alert", "notify"],
                    severity=PolicySeverity.ERROR,
                ),
                BudgetThreshold(
                    percentage=100.0,
                    actions=["alert", "notify", "block"],
                    severity=PolicySeverity.CRITICAL,
                ),
            ]
        else:
            self.thresholds = sorted(thresholds, key=lambda t: t.percentage)

    def _evaluate_conditions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate budget conditions."""
        current_spend = context.get("current_spend", 0.0)
        period_start = context.get("period_start")
        period_end = context.get("period_end")

        violations = []

        # Calculate percentage used
        percentage_used = (current_spend / self.limit * 100) if self.limit > 0 else 0

        # Check each threshold
        for threshold in self.thresholds:
            if percentage_used >= threshold.percentage:
                exceeded_by = current_spend - (self.limit * threshold.percentage / 100)

                violation = BudgetViolation(
                    budget_name=self.name,
                    current_spend=current_spend,
                    budget_limit=self.limit,
                    percentage_used=percentage_used,
                    exceeded_by=exceeded_by,
                    threshold=threshold,
                )

                violations.append(
                    {
                        "type": "budget_threshold_exceeded",
                        "threshold_percentage": threshold.percentage,
                        "current_spend": current_spend,
                        "budget_limit": self.limit,
                        "percentage_used": percentage_used,
                        "exceeded_by": exceeded_by,
                        "severity": threshold.severity.value,
                        "actions": threshold.actions,
                        "period_start": period_start,
                        "period_end": period_end,
                    }
                )

                # Only report the highest threshold exceeded
                break

        return violations

    def get_remaining_budget(self, current_spend: float) -> float:
        """
        Get remaining budget.

        Args:
            current_spend: Current spending

        Returns:
            Remaining budget amount
        """
        return max(0, self.limit - current_spend)

    def get_forecast(
        self, current_spend: float, days_elapsed: int, days_total: int
    ) -> Dict[str, Any]:
        """
        Forecast budget usage for the period.

        Args:
            current_spend: Current spending
            days_elapsed: Days elapsed in period
            days_total: Total days in period

        Returns:
            Forecast information
        """
        if days_elapsed == 0:
            return {
                "forecast_spend": current_spend,
                "forecast_percentage": 0,
                "is_over_budget": False,
            }

        # Simple linear projection
        daily_rate = current_spend / days_elapsed
        forecast_spend = daily_rate * days_total

        forecast_percentage = (forecast_spend / self.limit * 100) if self.limit > 0 else 0
        is_over_budget = forecast_spend > self.limit

        return {
            "forecast_spend": forecast_spend,
            "forecast_percentage": forecast_percentage,
            "is_over_budget": is_over_budget,
            "daily_rate": daily_rate,
            "days_remaining": days_total - days_elapsed,
            "recommended_daily_rate": self.limit / days_total if days_total > 0 else 0,
        }

    def adjust_budget(self, adjustment: float, reason: str = ""):
        """
        Adjust budget limit.

        Args:
            adjustment: Amount to adjust (positive or negative)
            reason: Reason for adjustment
        """
        old_limit = self.limit
        self.limit += adjustment

        logger.info(
            f"Budget '{self.name}' adjusted from {old_limit} to {self.limit}. Reason: {reason}"
        )

    def reset_for_new_period(self, rollover_amount: float = 0.0):
        """
        Reset budget for new period.

        Args:
            rollover_amount: Amount to rollover from previous period
        """
        if self.rollover_unused and rollover_amount > 0:
            self.limit += rollover_amount
            logger.info(f"Budget '{self.name}' rolled over {rollover_amount}")


class BudgetAllocator:
    """
    Allocates budgets across teams, projects, or cost centers.
    """

    def __init__(self, total_budget: float):
        """
        Initialize budget allocator.

        Args:
            total_budget: Total budget to allocate
        """
        self.total_budget = total_budget
        self._allocations: Dict[str, float] = {}

    def allocate(self, allocations: Dict[str, float], method: str = "fixed"):
        """
        Allocate budget across entities.

        Args:
            allocations: Dictionary of entity: amount/percentage
            method: Allocation method ("fixed" or "percentage")
        """
        if method == "percentage":
            # Allocations are percentages
            total_pct = sum(allocations.values())
            if total_pct > 100:
                raise ValueError(f"Total allocation exceeds 100%: {total_pct}")

            self._allocations = {
                entity: (pct / 100) * self.total_budget
                for entity, pct in allocations.items()
            }
        else:
            # Allocations are fixed amounts
            total_allocated = sum(allocations.values())
            if total_allocated > self.total_budget:
                raise ValueError(
                    f"Total allocation ({total_allocated}) exceeds budget ({self.total_budget})"
                )

            self._allocations = allocations.copy()

    def get_allocation(self, entity: str) -> float:
        """Get allocated budget for entity."""
        return self._allocations.get(entity, 0.0)

    def get_unallocated(self) -> float:
        """Get unallocated budget."""
        allocated = sum(self._allocations.values())
        return self.total_budget - allocated

    def reallocate(self, from_entity: str, to_entity: str, amount: float):
        """
        Reallocate budget between entities.

        Args:
            from_entity: Entity to take budget from
            to_entity: Entity to give budget to
            amount: Amount to reallocate
        """
        if from_entity not in self._allocations:
            raise ValueError(f"Entity not found: {from_entity}")

        if self._allocations[from_entity] < amount:
            raise ValueError(
                f"Insufficient budget in {from_entity}: {self._allocations[from_entity]}"
            )

        self._allocations[from_entity] -= amount
        self._allocations[to_entity] = self._allocations.get(to_entity, 0) + amount

        logger.info(f"Reallocated {amount} from {from_entity} to {to_entity}")

    def get_allocation_summary(self) -> Dict[str, Any]:
        """Get allocation summary."""
        total_allocated = sum(self._allocations.values())

        return {
            "total_budget": self.total_budget,
            "total_allocated": total_allocated,
            "unallocated": self.total_budget - total_allocated,
            "allocation_percentage": (
                total_allocated / self.total_budget * 100 if self.total_budget > 0 else 0
            ),
            "allocations": self._allocations.copy(),
        }
