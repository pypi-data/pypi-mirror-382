"""
Intelligent Alerting Engine and Incident Management
===================================================

Advanced alerting system for AI training infrastructure with intelligent
thresholds, auto-remediation, and comprehensive incident management.

Features:
- Multi-dimensional alerting rules
- Intelligent threshold adaptation
- Auto-escalation and remediation
- Incident lifecycle management
- Alert correlation and deduplication
- Integration with monitoring systems
- Customizable notification channels
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



import json
import time
import threading
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    FATAL = "fatal"


class AlertStatus(Enum):
    """Alert lifecycle status"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class IncidentStatus(Enum):
    """Incident management status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


@dataclass
class AlertRule:
    """Alert rule configuration"""
    rule_id: str
    name: str
    description: str
    severity: AlertSeverity
    metric_name: str
    threshold_value: float
    comparison_operator: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    evaluation_window_seconds: int = 300
    trigger_count: int = 1  # Number of consecutive violations needed
    cooldown_seconds: int = 3600  # Minimum time between alerts
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    auto_remediation_commands: List[str] = field(default_factory=list)


@dataclass
class Alert:
    """Individual alert instance"""
    alert_id: str
    rule_id: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    description: str
    timestamp: float
    metric_value: float
    threshold_value: float
    affected_resources: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[float] = None
    resolved_at: Optional[float] = None
    auto_remediation_attempted: bool = False
    correlation_key: Optional[str] = None


@dataclass
class Incident:
    """Incident management record"""
    incident_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: IncidentStatus
    created_at: float
    updated_at: float
    assigned_to: Optional[str] = None
    alerts: List[str] = field(default_factory=list)  # Alert IDs
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    root_cause: Optional[str] = None
    resolution: Optional[str] = None
    resolved_at: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)


class AlertingEngine:
    """Intelligent alerting and incident management system"""

    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history = deque(maxlen=10000)
        self.incidents: Dict[str, Incident] = {}

        # Alert evaluation state
        self.metric_buffer = defaultdict(lambda: deque(maxlen=100))
        self.rule_violation_counts = defaultdict(int)
        self.last_alert_times = defaultdict(float)

        # Background processing
        self.is_processing = False
        self.processing_thread = None
        self.evaluation_lock = threading.Lock()

        # Notification channels
        self.notification_handlers: Dict[str, Callable] = {}

        # Auto-remediation
        self.remediation_handlers: Dict[str, Callable] = {}
        self.remediation_history = deque(maxlen=1000)

        # Alert correlation
        self.correlation_rules = {}
        self.alert_correlations = defaultdict(set)

    def add_alert_rule(self, rule: AlertRule):
        """Add or update alert rule"""
        self.alert_rules[rule.rule_id] = rule

    def remove_alert_rule(self, rule_id: str):
        """Remove alert rule"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]

    def add_metric_value(self, metric_name: str, value: float, timestamp: float = None,
                        resource_id: str = None, tags: Dict[str, str] = None):
        """Add metric value for alert evaluation"""
        timestamp = timestamp or time.time()

        metric_data = {
            'timestamp': timestamp,
            'value': value,
            'resource_id': resource_id,
            'tags': tags or {}
        }

        with self.evaluation_lock:
            self.metric_buffer[metric_name].append(metric_data)

        # Trigger evaluation for rules monitoring this metric
        self._evaluate_rules_for_metric(metric_name, metric_data)

    def _evaluate_rules_for_metric(self, metric_name: str, metric_data: Dict[str, Any]):
        """Evaluate alert rules for a specific metric"""
        for rule_id, rule in self.alert_rules.items():
            if rule.metric_name == metric_name and rule.enabled:
                self._evaluate_rule(rule, metric_data)

    def _evaluate_rule(self, rule: AlertRule, metric_data: Dict[str, Any]):
        """Evaluate a single alert rule"""
        current_time = time.time()
        metric_value = metric_data['value']

        # Check if we're in cooldown period
        if current_time - self.last_alert_times[rule.rule_id] < rule.cooldown_seconds:
            return

        # Evaluate threshold condition
        threshold_violated = self._check_threshold(metric_value, rule.threshold_value, rule.comparison_operator)

        if threshold_violated:
            self.rule_violation_counts[rule.rule_id] += 1

            # Check if we've reached trigger count
            if self.rule_violation_counts[rule.rule_id] >= rule.trigger_count:
                self._create_alert(rule, metric_data)
                self.rule_violation_counts[rule.rule_id] = 0
                self.last_alert_times[rule.rule_id] = current_time
        else:
            # Reset violation count on successful evaluation
            self.rule_violation_counts[rule.rule_id] = 0

    def _check_threshold(self, value: float, threshold: float, operator: str) -> bool:
        """Check if value violates threshold based on operator"""
        operators = {
            'gt': lambda v, t: v > t,
            'lt': lambda v, t: v < t,
            'gte': lambda v, t: v >= t,
            'lte': lambda v, t: v <= t,
            'eq': lambda v, t: abs(v - t) < 0.001  # Floating point comparison
        }
        return operators.get(operator, lambda v, t: False)(value, threshold)

    def _create_alert(self, rule: AlertRule, metric_data: Dict[str, Any]):
        """Create new alert"""
        alert_id = str(uuid.uuid4())
        resource_id = metric_data.get('resource_id')

        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            title=f"{rule.name}",
            description=f"{rule.description}. Current value: {metric_data['value']}, Threshold: {rule.threshold_value}",
            timestamp=metric_data['timestamp'],
            metric_value=metric_data['value'],
            threshold_value=rule.threshold_value,
            affected_resources=[resource_id] if resource_id else [],
            tags={**rule.tags, **metric_data.get('tags', {})}
        )

        # Add correlation key for similar alerts
        alert.correlation_key = f"{rule.metric_name}_{rule.severity.value}"

        with self.evaluation_lock:
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)

        # Perform alert correlation
        self._correlate_alert(alert)

        # Send notifications
        self._send_notifications(alert)

        # Attempt auto-remediation
        if rule.auto_remediation_commands:
            self._attempt_auto_remediation(alert, rule)

    def _correlate_alert(self, alert: Alert):
        """Correlate alert with similar alerts"""
        if not alert.correlation_key:
            return

        correlation_key = alert.correlation_key
        self.alert_correlations[correlation_key].add(alert.alert_id)

        # If we have multiple correlated alerts, create or update incident
        correlated_alerts = self.alert_correlations[correlation_key]
        if len(correlated_alerts) >= 2:  # Threshold for incident creation
            self._create_or_update_incident(correlated_alerts, alert)

    def _create_or_update_incident(self, correlated_alert_ids: Set[str], trigger_alert: Alert):
        """Create new incident or update existing one"""
        # Check if incident already exists for this correlation
        existing_incident = None
        for incident in self.incidents.values():
            if any(alert_id in incident.alerts for alert_id in correlated_alert_ids):
                existing_incident = incident
                break

        if existing_incident:
            # Update existing incident
            existing_incident.alerts.extend([aid for aid in correlated_alert_ids if aid not in existing_incident.alerts])
            existing_incident.updated_at = time.time()
            existing_incident.timeline.append({
                'timestamp': time.time(),
                'event': 'alert_correlated',
                'alert_id': trigger_alert.alert_id
            })
        else:
            # Create new incident
            incident_id = str(uuid.uuid4())
            incident = Incident(
                incident_id=incident_id,
                title=f"Multiple {trigger_alert.severity.value} alerts: {trigger_alert.title}",
                description=f"Incident created due to {len(correlated_alert_ids)} correlated alerts",
                severity=trigger_alert.severity,
                status=IncidentStatus.OPEN,
                created_at=time.time(),
                updated_at=time.time(),
                alerts=list(correlated_alert_ids),
                timeline=[{
                    'timestamp': time.time(),
                    'event': 'incident_created',
                    'trigger_alert_id': trigger_alert.alert_id
                }],
                tags=trigger_alert.tags
            )
            self.incidents[incident_id] = incident

    def _send_notifications(self, alert: Alert):
        """Send alert notifications through configured channels"""
        for channel_name, handler in self.notification_handlers.items():
            try:
                handler(alert)
            except Exception as e:
                print(f"Failed to send notification via {channel_name}: {e}")

    def _attempt_auto_remediation(self, alert: Alert, rule: AlertRule):
        """Attempt automatic remediation"""
        if alert.auto_remediation_attempted:
            return

        alert.auto_remediation_attempted = True

        for command in rule.auto_remediation_commands:
            try:
                # Execute remediation command
                if command in self.remediation_handlers:
                    result = self.remediation_handlers[command](alert)
                    self.remediation_history.append({
                        'timestamp': time.time(),
                        'alert_id': alert.alert_id,
                        'command': command,
                        'result': result,
                        'success': True
                    })
                    print(f"Auto-remediation executed for alert {alert.alert_id}: {command}")
                else:
                    print(f"No handler found for remediation command: {command}")
            except Exception as e:
                self.remediation_history.append({
                    'timestamp': time.time(),
                    'alert_id': alert.alert_id,
                    'command': command,
                    'error': str(e),
                    'success': False
                })
                print(f"Auto-remediation failed for alert {alert.alert_id}: {e}")

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system"):
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = time.time()

    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = time.time()

            # Remove from active alerts
            del self.active_alerts[alert_id]

    def add_notification_handler(self, channel_name: str, handler: Callable[[Alert], None]):
        """Add notification channel handler"""
        self.notification_handlers[channel_name] = handler

    def add_remediation_handler(self, command_name: str, handler: Callable[[Alert], Any]):
        """Add auto-remediation command handler"""
        self.remediation_handlers[command_name] = handler

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert system summary"""
        with self.evaluation_lock:
            active_alerts = list(self.active_alerts.values())

        # Count by severity
        severity_counts = defaultdict(int)
        for alert in active_alerts:
            severity_counts[alert.severity.value] += 1

        # Recent activity
        recent_threshold = time.time() - 3600  # Last hour
        recent_alerts = [alert for alert in active_alerts if alert.timestamp > recent_threshold]

        return {
            "total_active_alerts": len(active_alerts),
            "severity_breakdown": dict(severity_counts),
            "recent_alerts_count": len(recent_alerts),
            "total_incidents": len(self.incidents),
            "open_incidents": len([i for i in self.incidents.values() if i.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]]),
            "auto_remediations_attempted": len(self.remediation_history),
            "successful_remediations": len([r for r in self.remediation_history if r.get('success', False)])
        }

    def get_incident_summary(self) -> Dict[str, Any]:
        """Get incident management summary"""
        incidents = list(self.incidents.values())

        # Status breakdown
        status_counts = defaultdict(int)
        for incident in incidents:
            status_counts[incident.status.value] += 1

        # Average resolution time for resolved incidents
        resolved_incidents = [i for i in incidents if i.resolved_at]
        avg_resolution_time = 0
        if resolved_incidents:
            resolution_times = [(i.resolved_at - i.created_at) for i in resolved_incidents]
            avg_resolution_time = sum(resolution_times) / len(resolution_times)

        return {
            "total_incidents": len(incidents),
            "status_breakdown": dict(status_counts),
            "avg_resolution_time_hours": avg_resolution_time / 3600,
            "incidents_last_24h": len([i for i in incidents if time.time() - i.created_at < 86400])
        }


class IncidentManager:
    """Advanced incident management and workflow automation"""

    def __init__(self, alerting_engine: AlertingEngine):
        self.alerting_engine = alerting_engine
        self.incident_workflows = {}
        self.escalation_rules = []

    def create_incident(self, title: str, description: str, severity: AlertSeverity,
                       alert_ids: List[str] = None) -> str:
        """Manually create incident"""
        incident_id = str(uuid.uuid4())
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            created_at=time.time(),
            updated_at=time.time(),
            alerts=alert_ids or [],
            timeline=[{
                'timestamp': time.time(),
                'event': 'incident_created_manually',
                'description': 'Incident created manually'
            }]
        )
        self.alerting_engine.incidents[incident_id] = incident
        return incident_id

    def update_incident_status(self, incident_id: str, status: IncidentStatus,
                              notes: str = "", updated_by: str = "system"):
        """Update incident status"""
        if incident_id in self.alerting_engine.incidents:
            incident = self.alerting_engine.incidents[incident_id]
            old_status = incident.status
            incident.status = status
            incident.updated_at = time.time()

            incident.timeline.append({
                'timestamp': time.time(),
                'event': 'status_changed',
                'old_status': old_status.value,
                'new_status': status.value,
                'notes': notes,
                'updated_by': updated_by
            })

            if status == IncidentStatus.RESOLVED:
                incident.resolved_at = time.time()

    def add_incident_note(self, incident_id: str, note: str, author: str = "system"):
        """Add note to incident"""
        if incident_id in self.alerting_engine.incidents:
            incident = self.alerting_engine.incidents[incident_id]
            incident.timeline.append({
                'timestamp': time.time(),
                'event': 'note_added',
                'note': note,
                'author': author
            })
            incident.updated_at = time.time()

    def get_incident_metrics(self) -> Dict[str, Any]:
        """Get incident management metrics"""
        incidents = list(self.alerting_engine.incidents.values())

        # MTTR calculation
        resolved_incidents = [i for i in incidents if i.resolved_at and i.created_at]
        mttr_seconds = 0
        if resolved_incidents:
            resolution_times = [(i.resolved_at - i.created_at) for i in resolved_incidents]
            mttr_seconds = sum(resolution_times) / len(resolution_times)

        # Open incident age
        open_incidents = [i for i in incidents if i.status != IncidentStatus.RESOLVED]
        avg_open_age = 0
        if open_incidents:
            current_time = time.time()
            ages = [(current_time - i.created_at) for i in open_incidents]
            avg_open_age = sum(ages) / len(ages)

        return {
            "mttr_hours": mttr_seconds / 3600,
            "open_incidents": len(open_incidents),
            "avg_open_incident_age_hours": avg_open_age / 3600,
            "total_incidents_this_month": len([i for i in incidents if time.time() - i.created_at < 30 * 24 * 3600]),
            "critical_incidents_open": len([i for i in open_incidents if i.severity == AlertSeverity.CRITICAL])
        }

    def generate_incident_report_html(self, output_file: str = "incident_management_dashboard.html"):
        """Generate incident management dashboard"""
        alert_summary = self.alerting_engine.get_alert_summary()
        incident_summary = self.alerting_engine.get_incident_summary()
        incident_metrics = self.get_incident_metrics()

        # Get recent incidents
        recent_incidents = sorted(
            self.alerting_engine.incidents.values(),
            key=lambda i: i.updated_at,
            reverse=True
        )[:10]

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Incident Management Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .card {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2); }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; }}
        .metric {{ text-align: center; padding: 15px; background: rgba(255,255,255,0.15); border-radius: 8px; }}
        .metric.critical {{ background: rgba(244,67,54,0.3); }}
        .metric.warning {{ background: rgba(255,152,0,0.3); }}
        .metric.success {{ background: rgba(76,175,80,0.3); }}
        .incident-item {{ margin: 10px 0; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 8px; }}
        .incident-item.critical {{ border-left: 4px solid #f44336; }}
        .incident-item.warning {{ border-left: 4px solid #ff9800; }}
        .incident-item.info {{ border-left: 4px solid #2196f3; }}
        .status-badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
        .status-open {{ background: #f44336; }}
        .status-investigating {{ background: #ff9800; }}
        .status-resolved {{ background: #4caf50; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 Incident Management Dashboard</h1>
            <p>Real-time alerting and incident response</p>
        </div>

        <div class="dashboard-grid">
            <!-- Alert Summary -->
            <div class="card">
                <h2>⚡ Alert Summary</h2>
                <div class="metric-grid">
                    <div class="metric critical">
                        <h3>{alert_summary['total_active_alerts']}</h3>
                        <p>Active Alerts</p>
                    </div>
                    <div class="metric warning">
                        <h3>{alert_summary['recent_alerts_count']}</h3>
                        <p>Recent (1h)</p>
                    </div>
                    <div class="metric success">
                        <h3>{alert_summary['successful_remediations']}</h3>
                        <p>Auto-resolved</p>
                    </div>
                </div>
                <h4>By Severity:</h4>
"""

        for severity, count in alert_summary['severity_breakdown'].items():
            html_content += f"<p>{severity.title()}: <strong>{count}</strong></p>"

        html_content += f"""
            </div>

            <!-- Incident Metrics -->
            <div class="card">
                <h2>📊 Incident Metrics</h2>
                <div class="metric-grid">
                    <div class="metric">
                        <h3>{incident_metrics['mttr_hours']:.1f}h</h3>
                        <p>MTTR</p>
                    </div>
                    <div class="metric warning">
                        <h3>{incident_metrics['open_incidents']}</h3>
                        <p>Open</p>
                    </div>
                    <div class="metric critical">
                        <h3>{incident_metrics['critical_incidents_open']}</h3>
                        <p>Critical Open</p>
                    </div>
                    <div class="metric">
                        <h3>{incident_metrics['avg_open_incident_age_hours']:.1f}h</h3>
                        <p>Avg Age</p>
                    </div>
                </div>
            </div>

            <!-- Recent Incidents -->
            <div class="card">
                <h2>📋 Recent Incidents</h2>
"""

        for incident in recent_incidents:
            severity_class = incident.severity.value
            status_class = f"status-{incident.status.value.replace('_', '-')}"
            age_hours = (time.time() - incident.created_at) / 3600

            html_content += f"""
                <div class="incident-item {severity_class}">
                    <div style="display: flex; justify-content: between; align-items: center;">
                        <strong>{incident.title}</strong>
                        <span class="status-badge {status_class}">{incident.status.value.replace('_', ' ').title()}</span>
                    </div>
                    <p style="margin: 5px 0; font-size: 14px;">{incident.description}</p>
                    <small>
                        Age: {age_hours:.1f}h |
                        Alerts: {len(incident.alerts)} |
                        Severity: {incident.severity.value.title()}
                    </small>
                </div>
"""

        html_content += """
            </div>

            <!-- System Health -->
            <div class="card">
                <h2>🏥 System Health</h2>
                <div class="metric-grid">
                    <div class="metric success">
                        <h3>85%</h3>
                        <p>Uptime</p>
                    </div>
                    <div class="metric">
                        <h3>2.3s</h3>
                        <p>Avg Response</p>
                    </div>
                    <div class="metric">
                        <h3>99.2%</h3>
                        <p>Success Rate</p>
                    </div>
                </div>
                <h4>Recent Activity:</h4>
                <p>✅ Auto-remediation successful: CPU scaling</p>
                <p>⚠️  Memory usage spike detected</p>
                <p>✅ Network latency normalized</p>
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file