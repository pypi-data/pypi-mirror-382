"""
Distributed System Telemetry and Trace Visualization
====================================================

Advanced telemetry system for distributed AI training environments with
comprehensive trace visualization, performance analysis, and bottleneck detection.

Features:
- Distributed trace collection and correlation
- Service mesh communication patterns
- Inter-node latency analysis
- Request flow visualization
- Performance bottleneck identification
- Custom span instrumentation
- Real-time trace streaming
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
import uuid
import threading
from collections import defaultdict, deque
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Set, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum


class SpanKind(Enum):
    """OpenTelemetry-compatible span kinds"""
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class TraceStatus(Enum):
    """Trace completion status"""
    OK = "ok"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class SpanContext:
    """Trace and span context for distributed correlation"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    trace_flags: int = 1
    trace_state: Dict[str, str] = field(default_factory=dict)


@dataclass
class SpanEvent:
    """Individual event within a span"""
    timestamp: float
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Distributed tracing span"""
    context: SpanContext
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    status: TraceStatus = TraceStatus.OK
    kind: SpanKind = SpanKind.INTERNAL
    service_name: str = "unknown"
    node_id: str = "unknown"
    tags: Dict[str, Any] = field(default_factory=dict)
    events: List[SpanEvent] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)

    def finish(self, status: TraceStatus = TraceStatus.OK):
        """Mark span as completed"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        self.status = status

    def add_event(self, name: str, attributes: Dict[str, Any] = None):
        """Add event to span"""
        event = SpanEvent(
            timestamp=time.time(),
            name=name,
            attributes=attributes or {}
        )
        self.events.append(event)

    def add_tag(self, key: str, value: Any):
        """Add tag to span"""
        self.tags[key] = value

    def log(self, message: str):
        """Add log message to span"""
        self.logs.append(f"{time.time()}: {message}")


@dataclass
class TraceData:
    """Complete trace with all spans"""
    trace_id: str
    spans: List[Span]
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    service_count: int = 0
    node_count: int = 0
    span_count: int = 0
    error_count: int = 0

    def __post_init__(self):
        """Calculate trace statistics"""
        if self.spans:
            self.span_count = len(self.spans)
            self.service_count = len(set(span.service_name for span in self.spans))
            self.node_count = len(set(span.node_id for span in self.spans))
            self.error_count = sum(1 for span in self.spans if span.status == TraceStatus.ERROR)

            # Calculate trace duration
            finished_spans = [s for s in self.spans if s.end_time is not None]
            if finished_spans:
                self.end_time = max(s.end_time for s in finished_spans)
                self.duration_ms = (self.end_time - self.start_time) * 1000


class DistributedTelemetry:
    """Distributed telemetry collection and analysis system"""

    def __init__(self, service_name: str, node_id: str = None):
        self.service_name = service_name
        self.node_id = node_id or f"node_{int(time.time())}"
        self.active_spans: Dict[str, Span] = {}
        self.completed_traces: Dict[str, TraceData] = {}
        self.trace_buffer = deque(maxlen=10000)  # Keep recent traces
        self.span_processor_threads: List[threading.Thread] = []
        self.is_collecting = False
        self.collection_lock = threading.Lock()

        # Performance metrics
        self.service_metrics = defaultdict(lambda: {
            'request_count': 0,
            'error_count': 0,
            'total_duration': 0.0,
            'avg_duration': 0.0,
            'p95_duration': 0.0,
            'p99_duration': 0.0
        })

        # Inter-service communication patterns
        self.communication_matrix = defaultdict(lambda: defaultdict(int))
        self.latency_matrix = defaultdict(lambda: defaultdict(list))

    def create_span(self, operation_name: str, parent_context: SpanContext = None,
                   kind: SpanKind = SpanKind.INTERNAL, tags: Dict[str, Any] = None) -> Span:
        """Create new distributed tracing span"""
        trace_id = parent_context.trace_id if parent_context else str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        parent_span_id = parent_context.span_id if parent_context else None

        context = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id
        )

        span = Span(
            context=context,
            operation_name=operation_name,
            start_time=time.time(),
            kind=kind,
            service_name=self.service_name,
            node_id=self.node_id,
            tags=tags or {}
        )

        with self.collection_lock:
            self.active_spans[span_id] = span

        return span

    def finish_span(self, span: Span, status: TraceStatus = TraceStatus.OK):
        """Complete span and process for traces"""
        span.finish(status)

        with self.collection_lock:
            # Remove from active spans
            if span.context.span_id in self.active_spans:
                del self.active_spans[span.context.span_id]

            # Add to trace collection
            trace_id = span.context.trace_id
            if trace_id not in self.completed_traces:
                self.completed_traces[trace_id] = TraceData(
                    trace_id=trace_id,
                    spans=[],
                    start_time=span.start_time
                )

            self.completed_traces[trace_id].spans.append(span)

            # Update service metrics
            self._update_service_metrics(span)

            # Update communication patterns
            self._update_communication_patterns(span)

    def _update_service_metrics(self, span: Span):
        """Update service performance metrics"""
        service = span.service_name
        metrics = self.service_metrics[service]

        metrics['request_count'] += 1
        if span.status == TraceStatus.ERROR:
            metrics['error_count'] += 1

        if span.duration_ms:
            metrics['total_duration'] += span.duration_ms
            metrics['avg_duration'] = metrics['total_duration'] / metrics['request_count']

    def _update_communication_patterns(self, span: Span):
        """Update inter-service communication patterns"""
        # Find parent span to establish communication link
        if span.context.parent_span_id:
            parent_service = None
            for active_span in self.active_spans.values():
                if active_span.context.span_id == span.context.parent_span_id:
                    parent_service = active_span.service_name
                    break

            if parent_service and parent_service != span.service_name:
                self.communication_matrix[parent_service][span.service_name] += 1
                if span.duration_ms:
                    self.latency_matrix[parent_service][span.service_name].append(span.duration_ms)

    def get_trace(self, trace_id: str) -> Optional[TraceData]:
        """Retrieve complete trace by ID"""
        with self.collection_lock:
            trace = self.completed_traces.get(trace_id)
            if trace:
                # Ensure trace statistics are updated
                trace.__post_init__()
            return trace

    def get_recent_traces(self, limit: int = 100) -> List[TraceData]:
        """Get recent completed traces"""
        with self.collection_lock:
            traces = list(self.completed_traces.values())
            # Sort by start time, most recent first
            traces.sort(key=lambda t: t.start_time, reverse=True)
            return traces[:limit]

    def get_service_metrics(self) -> Dict[str, Any]:
        """Get aggregated service performance metrics"""
        with self.collection_lock:
            metrics = {}
            for service_name, service_metrics in self.service_metrics.items():
                # Calculate percentiles for completed traces
                durations = []
                for trace in self.completed_traces.values():
                    service_spans = [s for s in trace.spans
                                   if s.service_name == service_name and s.duration_ms]
                    durations.extend([s.duration_ms for s in service_spans])

                if durations:
                    durations.sort()
                    p95_idx = int(0.95 * len(durations))
                    p99_idx = int(0.99 * len(durations))
                    service_metrics['p95_duration'] = durations[p95_idx] if p95_idx < len(durations) else 0
                    service_metrics['p99_duration'] = durations[p99_idx] if p99_idx < len(durations) else 0

                metrics[service_name] = service_metrics.copy()

            return metrics

    def get_communication_patterns(self) -> Dict[str, Any]:
        """Get inter-service communication analysis"""
        with self.collection_lock:
            patterns = {}

            # Request counts between services
            for source_service, targets in self.communication_matrix.items():
                if source_service not in patterns:
                    patterns[source_service] = {}

                for target_service, count in targets.items():
                    patterns[source_service][target_service] = {
                        'request_count': count,
                        'avg_latency_ms': 0.0,
                        'max_latency_ms': 0.0
                    }

                    # Calculate latency statistics
                    latencies = self.latency_matrix[source_service][target_service]
                    if latencies:
                        patterns[source_service][target_service]['avg_latency_ms'] = sum(latencies) / len(latencies)
                        patterns[source_service][target_service]['max_latency_ms'] = max(latencies)

            return patterns

    def analyze_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks"""
        bottlenecks = []

        # Analyze service response times
        service_metrics = self.get_service_metrics()
        for service_name, metrics in service_metrics.items():
            if metrics['avg_duration'] > 1000:  # > 1 second average
                bottlenecks.append({
                    'type': 'slow_service',
                    'service': service_name,
                    'avg_duration_ms': metrics['avg_duration'],
                    'severity': 'high' if metrics['avg_duration'] > 5000 else 'medium',
                    'recommendation': f"Optimize {service_name} - average response time is {metrics['avg_duration']:.1f}ms"
                })

        # Analyze communication patterns for high latency
        comm_patterns = self.get_communication_patterns()
        for source, targets in comm_patterns.items():
            for target, stats in targets.items():
                if stats['avg_latency_ms'] > 500:  # > 500ms inter-service latency
                    bottlenecks.append({
                        'type': 'high_latency_communication',
                        'source_service': source,
                        'target_service': target,
                        'avg_latency_ms': stats['avg_latency_ms'],
                        'severity': 'high' if stats['avg_latency_ms'] > 2000 else 'medium',
                        'recommendation': f"Optimize network communication between {source} and {target}"
                    })

        # Analyze error rates
        for service_name, metrics in service_metrics.items():
            error_rate = (metrics['error_count'] / metrics['request_count']) * 100 if metrics['request_count'] > 0 else 0
            if error_rate > 5:  # > 5% error rate
                bottlenecks.append({
                    'type': 'high_error_rate',
                    'service': service_name,
                    'error_rate_percent': error_rate,
                    'severity': 'critical' if error_rate > 20 else 'high',
                    'recommendation': f"Investigate errors in {service_name} - {error_rate:.1f}% error rate"
                })

        return sorted(bottlenecks, key=lambda b: {'critical': 3, 'high': 2, 'medium': 1}.get(b['severity'], 0), reverse=True)

    def export_traces(self, trace_ids: List[str] = None) -> Dict[str, Any]:
        """Export traces in OpenTelemetry format"""
        with self.collection_lock:
            if trace_ids:
                traces = [self.completed_traces[tid] for tid in trace_ids if tid in self.completed_traces]
            else:
                traces = list(self.completed_traces.values())

        # Convert to OpenTelemetry-compatible format
        resource_spans = []
        for trace in traces:
            spans_data = []
            for span in trace.spans:
                span_data = {
                    'traceId': span.context.trace_id,
                    'spanId': span.context.span_id,
                    'parentSpanId': span.context.parent_span_id,
                    'name': span.operation_name,
                    'startTimeUnixNano': int(span.start_time * 1e9),
                    'endTimeUnixNano': int(span.end_time * 1e9) if span.end_time else None,
                    'durationNano': int(span.duration_ms * 1e6) if span.duration_ms else None,
                    'kind': span.kind.value,
                    'status': span.status.value,
                    'attributes': span.tags,
                    'events': [asdict(event) for event in span.events],
                    'links': []
                }
                spans_data.append(span_data)

            resource_spans.append({
                'resource': {
                    'attributes': {
                        'service.name': self.service_name,
                        'node.id': self.node_id
                    }
                },
                'spans': spans_data
            })

        return {
            'resourceSpans': resource_spans,
            'exportTime': time.time(),
            'traceCount': len(traces),
            'spanCount': sum(len(t.spans) for t in traces)
        }


class TraceVisualizer:
    """Generate interactive visualizations for distributed traces"""

    def __init__(self, telemetry: DistributedTelemetry):
        self.telemetry = telemetry

    def generate_trace_timeline_html(self, trace_id: str, output_file: str = "trace_timeline.html"):
        """Generate interactive timeline visualization for a specific trace"""
        trace = self.telemetry.get_trace(trace_id)
        if not trace:
            return None

        # Generate HTML with embedded JavaScript
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Distributed Trace Timeline - {trace_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .trace-info {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; text-align: center; }}
        .timeline {{ margin: 20px 0; }}
        .span-row {{ margin: 8px 0; display: flex; align-items: center; }}
        .span-label {{ width: 200px; font-size: 12px; padding-right: 10px; }}
        .span-bar {{ height: 24px; position: relative; background: linear-gradient(90deg, #4CAF50, #45a049); border-radius: 4px; margin-right: 10px; }}
        .span-duration {{ font-size: 11px; color: #666; min-width: 80px; }}
        .span-error {{ background: linear-gradient(90deg, #f44336, #d32f2f) !important; }}
        .span-server {{ background: linear-gradient(90deg, #2196F3, #1976D2) !important; }}
        .span-client {{ background: linear-gradient(90deg, #FF9800, #F57C00) !important; }}
        .span-details {{ font-size: 10px; color: white; position: absolute; left: 5px; top: 50%; transform: translateY(-50%); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Distributed Trace Timeline</h1>
            <p>Trace ID: <code>{trace.trace_id}</code></p>
        </div>

        <div class="trace-info">
            <div class="metric-card">
                <h3>{trace.span_count}</h3>
                <p>Total Spans</p>
            </div>
            <div class="metric-card">
                <h3>{trace.service_count}</h3>
                <p>Services</p>
            </div>
            <div class="metric-card">
                <h3>{trace.node_count}</h3>
                <p>Nodes</p>
            </div>
            <div class="metric-card">
                <h3>{trace.duration_ms:.1f}ms</h3>
                <p>Total Duration</p>
            </div>
            <div class="metric-card">
                <h3>{trace.error_count}</h3>
                <p>Errors</p>
            </div>
        </div>

        <div class="timeline">
            <h2>📊 Span Timeline</h2>
"""

        # Generate timeline visualization
        if trace.spans:
            min_start = min(s.start_time for s in trace.spans)
            max_end = max(s.end_time for s in trace.spans if s.end_time) or max(s.start_time for s in trace.spans)
            total_duration = max_end - min_start

            for span in sorted(trace.spans, key=lambda s: s.start_time):
                if span.end_time:
                    relative_start = ((span.start_time - min_start) / total_duration) * 100
                    relative_width = ((span.end_time - span.start_time) / total_duration) * 100
                else:
                    relative_start = 0
                    relative_width = 5  # Small width for incomplete spans

                span_class = "span-error" if span.status == TraceStatus.ERROR else f"span-{span.kind.value}"

                html_content += f"""
            <div class="span-row">
                <div class="span-label">{span.service_name}<br><small>{span.operation_name}</small></div>
                <div class="span-bar {span_class}" style="width: {max(relative_width, 2)}%; margin-left: {relative_start}%;">
                    <div class="span-details">{span.node_id}</div>
                </div>
                <div class="span-duration">{span.duration_ms:.1f}ms</div>
            </div>
"""

        html_content += """
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file

    def generate_service_map_html(self, output_file: str = "service_communication_map.html"):
        """Generate interactive service communication map"""
        comm_patterns = self.telemetry.get_communication_patterns()
        service_metrics = self.telemetry.get_service_metrics()

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Service Communication Map</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .services {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .service-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; }}
        .service-metrics {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin: 15px 0; }}
        .metric {{ text-align: center; }}
        .communications {{ margin-top: 15px; }}
        .comm-item {{ background: rgba(255,255,255,0.2); padding: 8px; margin: 5px 0; border-radius: 6px; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Service Communication Map</h1>
            <p>Real-time distributed system communication analysis</p>
        </div>

        <div class="services">
"""

        for service_name, metrics in service_metrics.items():
            html_content += f"""
            <div class="service-card">
                <h3>{service_name}</h3>
                <div class="service-metrics">
                    <div class="metric">
                        <strong>{metrics['request_count']}</strong><br>
                        <small>Requests</small>
                    </div>
                    <div class="metric">
                        <strong>{metrics['error_count']}</strong><br>
                        <small>Errors</small>
                    </div>
                    <div class="metric">
                        <strong>{metrics['avg_duration']:.1f}ms</strong><br>
                        <small>Avg Duration</small>
                    </div>
                    <div class="metric">
                        <strong>{metrics['p95_duration']:.1f}ms</strong><br>
                        <small>P95 Duration</small>
                    </div>
                </div>
"""

            # Add communication patterns
            if service_name in comm_patterns:
                html_content += f"""
                <div class="communications">
                    <h4>📡 Outgoing Communications</h4>
"""
                for target, stats in comm_patterns[service_name].items():
                    html_content += f"""
                    <div class="comm-item">
                        → {target}<br>
                        <small>{stats['request_count']} requests | {stats['avg_latency_ms']:.1f}ms avg</small>
                    </div>
"""
                html_content += "</div>"

            html_content += "</div>"

        html_content += """
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file