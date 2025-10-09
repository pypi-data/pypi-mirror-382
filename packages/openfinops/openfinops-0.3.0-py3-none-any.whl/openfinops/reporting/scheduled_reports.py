"""
Scheduled Reports
=================

Automated report generation and delivery on schedules.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ScheduleFrequency(Enum):
    """Report schedule frequencies."""

    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class ReportSchedule:
    """
    Report schedule definition.

    Attributes:
        id: Schedule ID
        name: Schedule name
        report_config: Report configuration
        frequency: Schedule frequency
        recipients: Email recipients
        enabled: Whether schedule is active
        next_run: Next scheduled run time
        last_run: Last run time
        format: Export format
        options: Additional options
    """

    id: str
    name: str
    report_config: Dict[str, Any]
    frequency: ScheduleFrequency
    recipients: List[str] = field(default_factory=list)
    enabled: bool = True
    next_run: Optional[float] = None
    last_run: Optional[float] = None
    format: str = "pdf"
    options: Dict[str, Any] = field(default_factory=dict)


class ScheduledReportManager:
    """
    Manages scheduled report generation and delivery.
    """

    def __init__(self):
        """Initialize scheduled report manager."""
        self._schedules: Dict[str, ReportSchedule] = {}
        self._schedule_counter = 0
        self._delivery_handlers: Dict[str, Callable] = {}

    def create_schedule(
        self,
        name: str,
        report_config: Dict[str, Any],
        frequency: ScheduleFrequency,
        recipients: List[str],
        format: str = "pdf",
        enabled: bool = True,
        **options,
    ) -> ReportSchedule:
        """
        Create a new report schedule.

        Args:
            name: Schedule name
            report_config: Report configuration
            frequency: Schedule frequency
            recipients: Email recipients
            format: Export format
            enabled: Whether schedule is active
            **options: Additional options

        Returns:
            Created schedule
        """
        self._schedule_counter += 1
        schedule_id = f"SCH-{self._schedule_counter:06d}"

        # Calculate next run time
        next_run = self._calculate_next_run(frequency)

        schedule = ReportSchedule(
            id=schedule_id,
            name=name,
            report_config=report_config,
            frequency=frequency,
            recipients=recipients,
            enabled=enabled,
            next_run=next_run,
            format=format,
            options=options,
        )

        self._schedules[schedule_id] = schedule
        logger.info(f"Created schedule {schedule_id}: {name}")

        return schedule

    def _calculate_next_run(
        self, frequency: ScheduleFrequency, from_time: Optional[datetime] = None
    ) -> float:
        """Calculate next run time based on frequency."""
        base_time = from_time or datetime.now()

        if frequency == ScheduleFrequency.HOURLY:
            next_time = base_time + timedelta(hours=1)
        elif frequency == ScheduleFrequency.DAILY:
            next_time = base_time + timedelta(days=1)
        elif frequency == ScheduleFrequency.WEEKLY:
            next_time = base_time + timedelta(weeks=1)
        elif frequency == ScheduleFrequency.MONTHLY:
            # Approximate month as 30 days
            next_time = base_time + timedelta(days=30)
        elif frequency == ScheduleFrequency.QUARTERLY:
            # Approximate quarter as 90 days
            next_time = base_time + timedelta(days=90)
        else:
            next_time = base_time + timedelta(days=1)

        return next_time.timestamp()

    def get_schedule(self, schedule_id: str) -> Optional[ReportSchedule]:
        """Get a schedule by ID."""
        return self._schedules.get(schedule_id)

    def list_schedules(self, enabled_only: bool = False) -> List[ReportSchedule]:
        """
        List all schedules.

        Args:
            enabled_only: Only return enabled schedules

        Returns:
            List of schedules
        """
        schedules = list(self._schedules.values())

        if enabled_only:
            schedules = [s for s in schedules if s.enabled]

        return schedules

    def update_schedule(
        self, schedule_id: str, **updates
    ) -> Optional[ReportSchedule]:
        """
        Update a schedule.

        Args:
            schedule_id: Schedule ID
            **updates: Fields to update

        Returns:
            Updated schedule
        """
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return None

        for key, value in updates.items():
            if hasattr(schedule, key):
                setattr(schedule, key, value)

        logger.info(f"Updated schedule {schedule_id}")
        return schedule

    def delete_schedule(self, schedule_id: str):
        """Delete a schedule."""
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            logger.info(f"Deleted schedule {schedule_id}")

    def enable_schedule(self, schedule_id: str):
        """Enable a schedule."""
        schedule = self.get_schedule(schedule_id)
        if schedule:
            schedule.enabled = True
            logger.info(f"Enabled schedule {schedule_id}")

    def disable_schedule(self, schedule_id: str):
        """Disable a schedule."""
        schedule = self.get_schedule(schedule_id)
        if schedule:
            schedule.enabled = False
            logger.info(f"Disabled schedule {schedule_id}")

    def get_due_schedules(self, current_time: Optional[float] = None) -> List[ReportSchedule]:
        """
        Get schedules that are due to run.

        Args:
            current_time: Current timestamp (defaults to now)

        Returns:
            List of due schedules
        """
        if current_time is None:
            current_time = datetime.now().timestamp()

        due_schedules = []

        for schedule in self._schedules.values():
            if (
                schedule.enabled
                and schedule.next_run
                and schedule.next_run <= current_time
            ):
                due_schedules.append(schedule)

        return due_schedules

    def mark_schedule_run(self, schedule_id: str, success: bool = True):
        """
        Mark a schedule as run and update next run time.

        Args:
            schedule_id: Schedule ID
            success: Whether run was successful
        """
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return

        schedule.last_run = datetime.now().timestamp()

        # Calculate next run time
        schedule.next_run = self._calculate_next_run(schedule.frequency)

        logger.info(
            f"Schedule {schedule_id} marked as run. Next run: {datetime.fromtimestamp(schedule.next_run)}"
        )

    def register_delivery_handler(self, handler_name: str, handler_func: Callable):
        """
        Register a delivery handler.

        Args:
            handler_name: Handler name
            handler_func: Function to handle delivery
        """
        self._delivery_handlers[handler_name] = handler_func
        logger.info(f"Registered delivery handler: {handler_name}")

    def deliver_report(
        self,
        schedule: ReportSchedule,
        report_content: Any,
    ) -> bool:
        """
        Deliver a report to recipients.

        Args:
            schedule: Schedule configuration
            report_content: Generated report content

        Returns:
            Success status
        """
        delivery_method = schedule.options.get("delivery_method", "email")

        if delivery_method in self._delivery_handlers:
            handler = self._delivery_handlers[delivery_method]
            try:
                handler(schedule.recipients, report_content, schedule.options)
                logger.info(f"Report delivered via {delivery_method}")
                return True
            except Exception as e:
                logger.error(f"Failed to deliver report: {e}")
                return False

        # Default: log delivery
        logger.info(
            f"Would deliver report to {len(schedule.recipients)} recipients via {delivery_method}"
        )
        return True

    def get_schedule_statistics(self) -> Dict[str, Any]:
        """
        Get schedule statistics.

        Returns:
            Statistics summary
        """
        total = len(self._schedules)
        enabled = sum(1 for s in self._schedules.values() if s.enabled)

        # Count by frequency
        by_frequency = {}
        for schedule in self._schedules.values():
            freq = schedule.frequency.value
            by_frequency[freq] = by_frequency.get(freq, 0) + 1

        # Due schedules
        due_count = len(self.get_due_schedules())

        return {
            "total_schedules": total,
            "enabled_schedules": enabled,
            "disabled_schedules": total - enabled,
            "by_frequency": by_frequency,
            "due_to_run": due_count,
        }


def create_daily_cost_report_schedule(
    recipients: List[str],
    report_name: str = "Daily Cost Report",
) -> Dict[str, Any]:
    """
    Create configuration for daily cost report schedule.

    Args:
        recipients: Email recipients
        report_name: Report name

    Returns:
        Schedule configuration
    """
    return {
        "name": report_name,
        "report_config": {
            "type": "cost_summary",
            "parameters": {"time_range": "last_24_hours"},
        },
        "frequency": ScheduleFrequency.DAILY,
        "recipients": recipients,
        "format": "pdf",
        "delivery_method": "email",
    }


def create_weekly_budget_report_schedule(
    recipients: List[str],
    report_name: str = "Weekly Budget Report",
) -> Dict[str, Any]:
    """
    Create configuration for weekly budget report schedule.

    Args:
        recipients: Email recipients
        report_name: Report name

    Returns:
        Schedule configuration
    """
    return {
        "name": report_name,
        "report_config": {
            "type": "budget_analysis",
            "parameters": {"time_range": "last_7_days"},
        },
        "frequency": ScheduleFrequency.WEEKLY,
        "recipients": recipients,
        "format": "excel",
        "delivery_method": "email",
    }
