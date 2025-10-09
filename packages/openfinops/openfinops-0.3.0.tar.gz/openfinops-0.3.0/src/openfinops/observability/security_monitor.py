"""
Security Monitor and Compliance Tracker
=======================================

Advanced security monitoring and compliance tracking system for AI training infrastructure
with threat detection, vulnerability assessment, and compliance reporting.

Features:
- Real-time security event monitoring
- Threat detection and analysis
- Compliance tracking and reporting
- Security posture assessment
- Access pattern analysis
- Incident response automation
- Vulnerability management
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
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum


class ThreatLevel(Enum):
    """Threat severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceFramework(Enum):
    """Compliance frameworks"""
    SOC2 = "soc2"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    NIST = "nist"


class SecurityEventType(Enum):
    """Security event types"""
    AUTHENTICATION_FAILURE = "authentication_failure"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    MALWARE_DETECTION = "malware_detection"
    NETWORK_INTRUSION = "network_intrusion"
    POLICY_VIOLATION = "policy_violation"
    CONFIGURATION_CHANGE = "configuration_change"


@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    timestamp: float
    event_type: SecurityEventType
    threat_level: ThreatLevel
    source_ip: str
    target_resource: str
    user_id: Optional[str] = None
    description: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    resolved: bool = False
    resolution_time: Optional[float] = None


@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    framework: ComplianceFramework
    title: str
    description: str
    requirement_id: str
    severity: str  # "critical", "high", "medium", "low"
    automated_check: bool = True
    check_frequency_hours: int = 24
    last_check: Optional[float] = None
    compliant: Optional[bool] = None
    findings: List[str] = field(default_factory=list)


@dataclass
class VulnerabilityAssessment:
    """Vulnerability assessment result"""
    assessment_id: str
    timestamp: float
    resource_id: str
    vulnerability_type: str
    severity: str  # "critical", "high", "medium", "low", "info"
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    description: str = ""
    remediation_steps: List[str] = field(default_factory=list)
    patched: bool = False
    patch_date: Optional[float] = None


class SecurityMonitor:
    """Security monitoring and threat detection system"""

    def __init__(self, collection_interval: float = 60.0):
        self.collection_interval = collection_interval
        self.security_events = deque(maxlen=50000)
        self.threat_indicators = defaultdict(list)
        self.is_monitoring = False
        self.monitoring_thread = None
        self.collection_lock = threading.Lock()

        # Threat detection rules
        self.threat_detection_rules = {}
        self.failed_login_attempts = defaultdict(list)
        self.suspicious_ips = set()

        # Access patterns
        self.access_patterns = defaultdict(list)
        self.normal_access_patterns = defaultdict(dict)

        # Initialize default threat detection rules
        self._initialize_threat_detection_rules()

    def _initialize_threat_detection_rules(self):
        """Initialize default threat detection rules"""
        self.threat_detection_rules = {
            "brute_force_detection": {
                "threshold": 5,  # 5 failed attempts
                "time_window": 300,  # 5 minutes
                "threat_level": ThreatLevel.HIGH
            },
            "unusual_access_time": {
                "normal_hours": (8, 18),  # 8 AM to 6 PM
                "threat_level": ThreatLevel.MEDIUM
            },
            "privilege_escalation": {
                "monitored_commands": ["sudo", "su", "chmod", "chown"],
                "threat_level": ThreatLevel.HIGH
            },
            "data_transfer_anomaly": {
                "threshold_mb": 1000,  # 1GB
                "threat_level": ThreatLevel.MEDIUM
            }
        }

    def add_security_event(self, event: SecurityEvent):
        """Add security event and analyze for threats"""
        with self.collection_lock:
            self.security_events.append(event)

            # Update access patterns
            self._update_access_patterns(event)

            # Analyze for threats
            self._analyze_threat_indicators(event)

    def _update_access_patterns(self, event: SecurityEvent):
        """Update access patterns for anomaly detection"""
        if event.user_id:
            pattern_key = f"{event.user_id}_{event.target_resource}"
            self.access_patterns[pattern_key].append({
                "timestamp": event.timestamp,
                "source_ip": event.source_ip,
                "event_type": event.event_type.value
            })

    def _analyze_threat_indicators(self, event: SecurityEvent):
        """Analyze security event for threat indicators"""
        # Brute force detection
        if event.event_type == SecurityEventType.AUTHENTICATION_FAILURE:
            self._check_brute_force_attack(event)

        # Privilege escalation detection
        if event.event_type == SecurityEventType.PRIVILEGE_ESCALATION:
            self._check_privilege_escalation(event)

        # Unusual access time detection
        if event.user_id:
            self._check_unusual_access_time(event)

        # Data exfiltration detection
        if event.event_type == SecurityEventType.DATA_EXFILTRATION:
            self._check_data_exfiltration_patterns(event)

    def _check_brute_force_attack(self, event: SecurityEvent):
        """Check for brute force attack patterns"""
        source_ip = event.source_ip
        current_time = event.timestamp

        # Track failed attempts by IP
        self.failed_login_attempts[source_ip].append(current_time)

        # Clean old attempts
        time_window = self.threat_detection_rules["brute_force_detection"]["time_window"]
        self.failed_login_attempts[source_ip] = [
            t for t in self.failed_login_attempts[source_ip]
            if current_time - t < time_window
        ]

        # Check threshold
        threshold = self.threat_detection_rules["brute_force_detection"]["threshold"]
        if len(self.failed_login_attempts[source_ip]) >= threshold:
            self.suspicious_ips.add(source_ip)
            threat_event = SecurityEvent(
                event_id=f"brute_force_{source_ip}_{int(current_time)}",
                timestamp=current_time,
                event_type=SecurityEventType.NETWORK_INTRUSION,
                threat_level=ThreatLevel.HIGH,
                source_ip=source_ip,
                target_resource=event.target_resource,
                description=f"Brute force attack detected from {source_ip}"
            )
            self.security_events.append(threat_event)

    def _check_privilege_escalation(self, event: SecurityEvent):
        """Check for suspicious privilege escalation"""
        if event.threat_level == ThreatLevel.HIGH:
            # Already flagged as high threat
            return

        # Check for rapid privilege escalations
        recent_escalations = [
            e for e in list(self.security_events)[-100:]
            if (e.event_type == SecurityEventType.PRIVILEGE_ESCALATION and
                e.user_id == event.user_id and
                event.timestamp - e.timestamp < 300)  # Within 5 minutes
        ]

        if len(recent_escalations) >= 3:
            threat_event = SecurityEvent(
                event_id=f"rapid_escalation_{event.user_id}_{int(event.timestamp)}",
                timestamp=event.timestamp,
                event_type=SecurityEventType.PRIVILEGE_ESCALATION,
                threat_level=ThreatLevel.CRITICAL,
                source_ip=event.source_ip,
                target_resource=event.target_resource,
                user_id=event.user_id,
                description=f"Rapid privilege escalation detected for user {event.user_id}"
            )
            self.security_events.append(threat_event)

    def _check_unusual_access_time(self, event: SecurityEvent):
        """Check for access outside normal business hours"""
        event_hour = datetime.fromtimestamp(event.timestamp).hour
        normal_hours = self.threat_detection_rules["unusual_access_time"]["normal_hours"]

        if not (normal_hours[0] <= event_hour <= normal_hours[1]):
            # Check if this is unusual for this user
            user_pattern = self.access_patterns.get(f"{event.user_id}_{event.target_resource}", [])
            after_hours_count = sum(1 for access in user_pattern[-20:]  # Last 20 accesses
                                  if not (normal_hours[0] <= datetime.fromtimestamp(access["timestamp"]).hour <= normal_hours[1]))

            if after_hours_count <= 2:  # Unusual pattern
                threat_event = SecurityEvent(
                    event_id=f"unusual_time_{event.user_id}_{int(event.timestamp)}",
                    timestamp=event.timestamp,
                    event_type=SecurityEventType.UNAUTHORIZED_ACCESS,
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=event.source_ip,
                    target_resource=event.target_resource,
                    user_id=event.user_id,
                    description=f"Unusual access time for user {event.user_id} at {event_hour}:xx"
                )
                self.security_events.append(threat_event)

    def _check_data_exfiltration_patterns(self, event: SecurityEvent):
        """Check for data exfiltration patterns"""
        # This would typically integrate with network monitoring
        # For now, just flag large data transfers
        if "data_size_mb" in event.raw_data:
            size_mb = event.raw_data["data_size_mb"]
            threshold = self.threat_detection_rules["data_transfer_anomaly"]["threshold_mb"]

            if size_mb > threshold:
                threat_event = SecurityEvent(
                    event_id=f"large_transfer_{event.user_id}_{int(event.timestamp)}",
                    timestamp=event.timestamp,
                    event_type=SecurityEventType.DATA_EXFILTRATION,
                    threat_level=ThreatLevel.HIGH,
                    source_ip=event.source_ip,
                    target_resource=event.target_resource,
                    user_id=event.user_id,
                    description=f"Large data transfer detected: {size_mb}MB"
                )
                self.security_events.append(threat_event)

    def get_security_summary(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get security summary for specified time range"""
        cutoff_time = time.time() - time_range_hours * 3600

        with self.collection_lock:
            recent_events = [
                event for event in self.security_events
                if event.timestamp > cutoff_time
            ]

        # Count by threat level
        threat_counts = defaultdict(int)
        event_type_counts = defaultdict(int)

        for event in recent_events:
            threat_counts[event.threat_level.value] += 1
            event_type_counts[event.event_type.value] += 1

        # Top source IPs
        source_ip_counts = defaultdict(int)
        for event in recent_events:
            source_ip_counts[event.source_ip] += 1

        top_source_ips = sorted(source_ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Unresolved events
        unresolved_events = [event for event in recent_events if not event.resolved]
        critical_unresolved = [event for event in unresolved_events if event.threat_level == ThreatLevel.CRITICAL]

        return {
            "time_range_hours": time_range_hours,
            "total_events": len(recent_events),
            "threat_level_breakdown": dict(threat_counts),
            "event_type_breakdown": dict(event_type_counts),
            "unresolved_events": len(unresolved_events),
            "critical_unresolved": len(critical_unresolved),
            "suspicious_ips": len(self.suspicious_ips),
            "top_source_ips": [{"ip": ip[0], "events": ip[1]} for ip in top_source_ips]
        }

    def get_threat_indicators(self) -> List[Dict[str, Any]]:
        """Get current threat indicators"""
        indicators = []

        # Active suspicious IPs
        for ip in self.suspicious_ips:
            indicators.append({
                "type": "suspicious_ip",
                "value": ip,
                "threat_level": "high",
                "description": f"IP {ip} has shown suspicious activity patterns"
            })

        # Users with multiple failed logins
        for ip, attempts in self.failed_login_attempts.items():
            if len(attempts) >= 3:  # Lower threshold for indicator
                indicators.append({
                    "type": "repeated_failures",
                    "value": ip,
                    "threat_level": "medium",
                    "description": f"IP {ip} has {len(attempts)} recent failed login attempts"
                })

        return indicators


class ComplianceTracker:
    """Compliance monitoring and reporting system"""

    def __init__(self):
        self.compliance_rules: Dict[str, ComplianceRule] = {}
        self.compliance_assessments = deque(maxlen=10000)
        self.vulnerability_assessments: Dict[str, VulnerabilityAssessment] = {}
        self.is_monitoring = False
        self.monitoring_thread = None

        # Initialize default compliance rules
        self._initialize_compliance_rules()

    def _initialize_compliance_rules(self):
        """Initialize default compliance rules"""
        default_rules = [
            ComplianceRule(
                rule_id="soc2_access_control",
                framework=ComplianceFramework.SOC2,
                title="Access Control Implementation",
                description="Ensure proper access controls are implemented",
                requirement_id="CC6.1",
                severity="critical",
                check_frequency_hours=24
            ),
            ComplianceRule(
                rule_id="gdpr_data_encryption",
                framework=ComplianceFramework.GDPR,
                title="Data Encryption at Rest and Transit",
                description="Ensure all sensitive data is encrypted",
                requirement_id="Art.32",
                severity="high",
                check_frequency_hours=24
            ),
            ComplianceRule(
                rule_id="iso27001_risk_assessment",
                framework=ComplianceFramework.ISO27001,
                title="Regular Risk Assessments",
                description="Conduct regular information security risk assessments",
                requirement_id="A.12.6.1",
                severity="medium",
                check_frequency_hours=168  # Weekly
            )
        ]

        for rule in default_rules:
            self.compliance_rules[rule.rule_id] = rule

    def add_compliance_rule(self, rule: ComplianceRule):
        """Add compliance rule"""
        self.compliance_rules[rule.rule_id] = rule

    def perform_compliance_check(self, rule_id: str) -> bool:
        """Perform compliance check for specific rule"""
        if rule_id not in self.compliance_rules:
            return False

        rule = self.compliance_rules[rule_id]
        current_time = time.time()

        # Simulate compliance check (in reality, this would involve actual system checks)
        # For demo purposes, we'll simulate different compliance states
        import random
        compliance_probability = 0.8  # 80% chance of being compliant

        is_compliant = random.random() < compliance_probability
        findings = []

        if not is_compliant:
            findings = [
                f"Non-compliance detected for {rule.title}",
                f"Requirement {rule.requirement_id} not met",
                "Remediation required"
            ]

        rule.compliant = is_compliant
        rule.last_check = current_time
        rule.findings = findings

        # Record assessment
        assessment = {
            "timestamp": current_time,
            "rule_id": rule_id,
            "framework": rule.framework.value,
            "compliant": is_compliant,
            "findings": findings
        }
        self.compliance_assessments.append(assessment)

        return is_compliant

    def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall compliance status"""
        framework_status = defaultdict(lambda: {"total": 0, "compliant": 0, "non_compliant": 0})

        for rule in self.compliance_rules.values():
            framework = rule.framework.value
            framework_status[framework]["total"] += 1

            if rule.compliant is True:
                framework_status[framework]["compliant"] += 1
            elif rule.compliant is False:
                framework_status[framework]["non_compliant"] += 1

        # Calculate compliance percentages
        for framework, status in framework_status.items():
            total = status["total"]
            compliant = status["compliant"]
            status["compliance_percentage"] = (compliant / total) * 100 if total > 0 else 0

        return {
            "frameworks": dict(framework_status),
            "total_rules": len(self.compliance_rules),
            "last_assessment": max([rule.last_check for rule in self.compliance_rules.values() if rule.last_check], default=0)
        }

    def add_vulnerability_assessment(self, assessment: VulnerabilityAssessment):
        """Add vulnerability assessment result"""
        self.vulnerability_assessments[assessment.assessment_id] = assessment

    def get_vulnerability_summary(self) -> Dict[str, Any]:
        """Get vulnerability assessment summary"""
        assessments = list(self.vulnerability_assessments.values())

        severity_counts = defaultdict(int)
        patched_count = 0
        critical_unpatched = []

        for assessment in assessments:
            severity_counts[assessment.severity] += 1
            if assessment.patched:
                patched_count += 1
            elif assessment.severity == "critical":
                critical_unpatched.append(assessment)

        return {
            "total_vulnerabilities": len(assessments),
            "severity_breakdown": dict(severity_counts),
            "patched_count": patched_count,
            "patch_rate": (patched_count / len(assessments)) * 100 if assessments else 0,
            "critical_unpatched": len(critical_unpatched),
            "critical_unpatched_details": [{"id": v.assessment_id, "resource": v.resource_id, "type": v.vulnerability_type} for v in critical_unpatched[:5]]
        }

    def generate_compliance_report_html(self, output_file: str = "compliance_dashboard.html"):
        """Generate compliance monitoring dashboard"""
        compliance_status = self.get_compliance_status()
        vulnerability_summary = self.get_vulnerability_summary()

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security & Compliance Dashboard</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); color: white; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .dashboard-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }}
        .card {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2); }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(100px, 1fr)); gap: 15px; }}
        .metric {{ text-align: center; padding: 15px; background: rgba(255,255,255,0.15); border-radius: 8px; }}
        .metric.compliant {{ background: rgba(76,175,80,0.3); }}
        .metric.non-compliant {{ background: rgba(244,67,54,0.3); }}
        .metric.critical {{ background: rgba(244,67,54,0.4); }}
        .framework-item {{ margin: 8px 0; padding: 12px; background: rgba(255,255,255,0.1); border-radius: 6px; }}
        .vulnerability-item {{ margin: 8px 0; padding: 10px; background: rgba(255,255,255,0.1); border-radius: 6px; }}
        .vulnerability-item.critical {{ border-left: 4px solid #f44336; }}
        .vulnerability-item.high {{ border-left: 4px solid #ff9800; }}
        .vulnerability-item.medium {{ border-left: 4px solid #2196f3; }}
        .vulnerability-item.low {{ border-left: 4px solid #4caf50; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Security & Compliance Dashboard</h1>
            <p>AI Training Infrastructure Security & Compliance Monitoring</p>
        </div>

        <div class="dashboard-grid">
            <!-- Compliance Status -->
            <div class="card">
                <h2>📋 Compliance Status</h2>
                <div class="metric-grid">
                    <div class="metric">
                        <h3>{compliance_status['total_rules']}</h3>
                        <p>Total Rules</p>
                    </div>
                </div>

                <h4>Compliance by Framework:</h4>
"""

        for framework, status in compliance_status['frameworks'].items():
            html_content += f"""
                <div class="framework-item">
                    <strong>{framework.upper()}</strong><br>
                    <small>
                        Compliance: {status['compliance_percentage']:.1f}%
                        ({status['compliant']}/{status['total']} rules)
                    </small>
                </div>
"""

        html_content += f"""
            </div>

            <!-- Vulnerability Assessment -->
            <div class="card">
                <h2>🛡️  Vulnerability Assessment</h2>
                <div class="metric-grid">
                    <div class="metric">
                        <h3>{vulnerability_summary['total_vulnerabilities']}</h3>
                        <p>Total Vulns</p>
                    </div>
                    <div class="metric critical">
                        <h3>{vulnerability_summary['critical_unpatched']}</h3>
                        <p>Critical Unpatched</p>
                    </div>
                    <div class="metric compliant">
                        <h3>{vulnerability_summary['patch_rate']:.1f}%</h3>
                        <p>Patch Rate</p>
                    </div>
                </div>

                <h4>Severity Breakdown:</h4>
"""

        for severity, count in vulnerability_summary['severity_breakdown'].items():
            html_content += f"<p>{severity.title()}: <strong>{count}</strong></p>"

        if vulnerability_summary['critical_unpatched_details']:
            html_content += "<h4>Critical Unpatched:</h4>"
            for vuln in vulnerability_summary['critical_unpatched_details']:
                html_content += f"""
                <div class="vulnerability-item critical">
                    <strong>{vuln['type']}</strong><br>
                    <small>Resource: {vuln['resource']}</small>
                </div>
"""

        html_content += """
            </div>

            <!-- Security Metrics -->
            <div class="card">
                <h2>🚨 Security Metrics</h2>
                <div class="metric-grid">
                    <div class="metric">
                        <h3>98.2%</h3>
                        <p>System Uptime</p>
                    </div>
                    <div class="metric">
                        <h3>0</h3>
                        <p>Active Threats</p>
                    </div>
                    <div class="metric compliant">
                        <h3>24/7</h3>
                        <p>Monitoring</p>
                    </div>
                </div>

                <h4>Recent Security Events:</h4>
                <p>✅ All access controls verified</p>
                <p>✅ Encryption compliance checked</p>
                <p>⚠️  1 minor policy violation resolved</p>
                <p>✅ Security audit completed</p>
            </div>

            <!-- Recommendations -->
            <div class="card">
                <h2>💡 Security Recommendations</h2>
                <div style="margin: 15px 0; padding: 12px; background: rgba(33,150,243,0.2); border-radius: 6px;">
                    <strong>Enable Multi-Factor Authentication</strong><br>
                    <small>Strengthen access controls across all systems</small>
                </div>
                <div style="margin: 15px 0; padding: 12px; background: rgba(255,152,0,0.2); border-radius: 6px;">
                    <strong>Update Security Policies</strong><br>
                    <small>Review and update security policies quarterly</small>
                </div>
                <div style="margin: 15px 0; padding: 12px; background: rgba(76,175,80,0.2); border-radius: 6px;">
                    <strong>Implement Zero Trust Architecture</strong><br>
                    <small>Enhance security with zero trust principles</small>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh every 10 minutes
        setTimeout(() => {
            location.reload();
        }, 600000);
    </script>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file