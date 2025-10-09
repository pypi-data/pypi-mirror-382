"""
OpenFinOps - Agentic AI Workflow Monitoring
Real tracking for multi-agent systems, LangChain, AutoGPT, etc.
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



import time
import json
import uuid
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from collections import defaultdict
from enum import Enum
import threading
from contextlib import contextmanager


class AgentEventType(Enum):
    """Types of agent events to track"""
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    LLM_CALL = "llm_call"
    LLM_RESPONSE = "llm_response"
    DECISION = "decision"
    COMMUNICATION = "communication"
    ERROR = "error"
    MEMORY_UPDATE = "memory_update"


@dataclass
class AgentEvent:
    """Single agent event data structure"""
    event_id: str
    timestamp: float
    agent_id: str
    event_type: AgentEventType
    data: Dict[str, Any]
    parent_event_id: Optional[str] = None
    session_id: Optional[str] = None
    cost_estimate: Optional[float] = None
    duration_ms: Optional[float] = None


@dataclass
class AgentSession:
    """Agent session tracking"""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    agents: List[str] = None
    total_events: int = 0
    total_cost: float = 0.0
    success: Optional[bool] = None
    error_count: int = 0

    def __post_init__(self):
        if self.agents is None:
            self.agents = []


class AgentWorkflowMonitor:
    """Production-ready agent workflow monitoring"""

    def __init__(self, project_name: str = "agent_workflow"):
        self.project_name = project_name
        self.events: List[AgentEvent] = []
        self.sessions: Dict[str, AgentSession] = {}
        self.active_agents: Dict[str, Dict] = {}
        self.event_callbacks: List[callable] = []
        self._lock = threading.Lock()

    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new agent workflow session"""
        if session_id is None:
            session_id = str(uuid.uuid4())

        with self._lock:
            self.sessions[session_id] = AgentSession(
                session_id=session_id,
                start_time=time.time()
            )

        print(f"🤖 Started agent session: {session_id}")
        return session_id

    def end_session(self, session_id: str, success: bool = True):
        """End an agent workflow session"""
        with self._lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.end_time = time.time()
                session.success = success

                # Calculate session metrics
                session_events = [e for e in self.events if e.session_id == session_id]
                session.total_events = len(session_events)
                session.total_cost = sum(e.cost_estimate or 0 for e in session_events)
                session.error_count = len([e for e in session_events if e.event_type == AgentEventType.ERROR])

        print(f"✅ Ended agent session: {session_id} ({'success' if success else 'failure'})")

    def register_agent(self, agent_id: str, agent_type: str, session_id: str,
                      metadata: Optional[Dict] = None):
        """Register a new agent in the workflow"""
        with self._lock:
            self.active_agents[agent_id] = {
                'agent_id': agent_id,
                'agent_type': agent_type,
                'session_id': session_id,
                'start_time': time.time(),
                'metadata': metadata or {}
            }

            # Add to session
            if session_id in self.sessions:
                if agent_id not in self.sessions[session_id].agents:
                    self.sessions[session_id].agents.append(agent_id)

        self._log_event(
            agent_id=agent_id,
            event_type=AgentEventType.AGENT_START,
            data={
                'agent_type': agent_type,
                'metadata': metadata or {}
            },
            session_id=session_id
        )

    def log_llm_call(self, agent_id: str, prompt: str, model: str,
                     tokens_used: Optional[int] = None, cost: Optional[float] = None,
                     session_id: Optional[str] = None) -> str:
        """Log LLM API call"""
        event_id = self._log_event(
            agent_id=agent_id,
            event_type=AgentEventType.LLM_CALL,
            data={
                'prompt': prompt[:200] + "..." if len(prompt) > 200 else prompt,
                'model': model,
                'tokens_used': tokens_used,
                'prompt_length': len(prompt)
            },
            session_id=session_id,
            cost_estimate=cost
        )
        return event_id

    def log_llm_response(self, agent_id: str, response: str, parent_event_id: str,
                        tokens_used: Optional[int] = None, cost: Optional[float] = None,
                        session_id: Optional[str] = None):
        """Log LLM API response"""
        self._log_event(
            agent_id=agent_id,
            event_type=AgentEventType.LLM_RESPONSE,
            data={
                'response': response[:200] + "..." if len(response) > 200 else response,
                'tokens_used': tokens_used,
                'response_length': len(response)
            },
            parent_event_id=parent_event_id,
            session_id=session_id,
            cost_estimate=cost
        )

    def log_tool_call(self, agent_id: str, tool_name: str, parameters: Dict,
                     session_id: Optional[str] = None) -> str:
        """Log agent tool usage"""
        event_id = self._log_event(
            agent_id=agent_id,
            event_type=AgentEventType.TOOL_CALL,
            data={
                'tool_name': tool_name,
                'parameters': parameters
            },
            session_id=session_id
        )
        return event_id

    def log_tool_result(self, agent_id: str, tool_name: str, result: Any,
                       parent_event_id: str, success: bool = True,
                       session_id: Optional[str] = None):
        """Log tool execution result"""
        self._log_event(
            agent_id=agent_id,
            event_type=AgentEventType.TOOL_RESULT,
            data={
                'tool_name': tool_name,
                'result': str(result)[:500] + "..." if len(str(result)) > 500 else str(result),
                'success': success
            },
            parent_event_id=parent_event_id,
            session_id=session_id
        )

    def log_decision(self, agent_id: str, decision_point: str, options: List[str],
                    chosen: str, reasoning: Optional[str] = None,
                    session_id: Optional[str] = None):
        """Log agent decision making"""
        self._log_event(
            agent_id=agent_id,
            event_type=AgentEventType.DECISION,
            data={
                'decision_point': decision_point,
                'options': options,
                'chosen': chosen,
                'reasoning': reasoning
            },
            session_id=session_id
        )

    def log_communication(self, sender_agent_id: str, receiver_agent_id: str,
                         message: str, message_type: str = "message",
                         session_id: Optional[str] = None):
        """Log inter-agent communication"""
        self._log_event(
            agent_id=sender_agent_id,
            event_type=AgentEventType.COMMUNICATION,
            data={
                'receiver': receiver_agent_id,
                'message': message,
                'message_type': message_type
            },
            session_id=session_id
        )

    def log_memory_update(self, agent_id: str, memory_type: str, operation: str,
                         data: Any, session_id: Optional[str] = None):
        """Log agent memory operations"""
        self._log_event(
            agent_id=agent_id,
            event_type=AgentEventType.MEMORY_UPDATE,
            data={
                'memory_type': memory_type,
                'operation': operation,  # 'store', 'retrieve', 'update', 'delete'
                'data_summary': str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
            },
            session_id=session_id
        )

    def log_error(self, agent_id: str, error: Exception, context: str,
                 session_id: Optional[str] = None):
        """Log agent errors"""
        self._log_event(
            agent_id=agent_id,
            event_type=AgentEventType.ERROR,
            data={
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context
            },
            session_id=session_id
        )

    def _log_event(self, agent_id: str, event_type: AgentEventType, data: Dict,
                  parent_event_id: Optional[str] = None, session_id: Optional[str] = None,
                  cost_estimate: Optional[float] = None) -> str:
        """Internal method to log events"""
        event_id = str(uuid.uuid4())

        event = AgentEvent(
            event_id=event_id,
            timestamp=time.time(),
            agent_id=agent_id,
            event_type=event_type,
            data=data,
            parent_event_id=parent_event_id,
            session_id=session_id,
            cost_estimate=cost_estimate
        )

        with self._lock:
            self.events.append(event)

        # Execute callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Callback error: {e}")

        return event_id

    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a specific session"""
        session = self.sessions.get(session_id)
        if not session:
            return {}

        session_events = [e for e in self.events if e.session_id == session_id]

        # Agent activity analysis
        agent_stats = defaultdict(lambda: {
            'events': 0, 'llm_calls': 0, 'tool_calls': 0, 'errors': 0, 'cost': 0.0
        })

        for event in session_events:
            stats = agent_stats[event.agent_id]
            stats['events'] += 1
            stats['cost'] += event.cost_estimate or 0

            if event.event_type == AgentEventType.LLM_CALL:
                stats['llm_calls'] += 1
            elif event.event_type == AgentEventType.TOOL_CALL:
                stats['tool_calls'] += 1
            elif event.event_type == AgentEventType.ERROR:
                stats['errors'] += 1

        # Communication analysis
        communications = [e for e in session_events if e.event_type == AgentEventType.COMMUNICATION]
        communication_graph = defaultdict(lambda: defaultdict(int))
        for comm in communications:
            sender = comm.agent_id
            receiver = comm.data.get('receiver')
            communication_graph[sender][receiver] += 1

        # Timeline analysis
        timeline = []
        for event in sorted(session_events, key=lambda x: x.timestamp):
            timeline.append({
                'timestamp': event.timestamp,
                'agent_id': event.agent_id,
                'event_type': event.event_type.value,
                'summary': self._get_event_summary(event)
            })

        return {
            'session': asdict(session),
            'agent_stats': dict(agent_stats),
            'communication_graph': dict(communication_graph),
            'timeline': timeline,
            'total_events': len(session_events),
            'duration_seconds': (session.end_time or time.time()) - session.start_time,
            'success_rate': 1.0 - (session.error_count / max(session.total_events, 1))
        }

    def _get_event_summary(self, event: AgentEvent) -> str:
        """Get human-readable summary of an event"""
        if event.event_type == AgentEventType.LLM_CALL:
            return f"LLM call to {event.data.get('model', 'unknown')}"
        elif event.event_type == AgentEventType.TOOL_CALL:
            return f"Used tool: {event.data.get('tool_name', 'unknown')}"
        elif event.event_type == AgentEventType.DECISION:
            return f"Decision: {event.data.get('chosen', 'unknown')}"
        elif event.event_type == AgentEventType.COMMUNICATION:
            return f"Sent message to {event.data.get('receiver', 'unknown')}"
        else:
            return event.event_type.value

    def export_session_data(self, session_id: str, filename: Optional[str] = None) -> str:
        """Export session data to JSON file"""
        analytics = self.get_session_analytics(session_id)

        if filename is None:
            filename = f"agent_session_{session_id}_{int(time.time())}.json"

        with open(filename, 'w') as f:
            json.dump(analytics, f, indent=2, default=str)

        print(f"📊 Exported session data to: {filename}")
        return filename

    @contextmanager
    def track_agent_operation(self, agent_id: str, operation_name: str,
                             session_id: Optional[str] = None):
        """Context manager for tracking agent operations with timing"""
        start_time = time.time()
        start_event_id = self._log_event(
            agent_id=agent_id,
            event_type=AgentEventType.AGENT_START,
            data={'operation': operation_name},
            session_id=session_id
        )

        try:
            yield
            success = True
        except Exception as e:
            success = False
            self.log_error(agent_id, e, f"During operation: {operation_name}", session_id)
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            self._log_event(
                agent_id=agent_id,
                event_type=AgentEventType.AGENT_END,
                data={
                    'operation': operation_name,
                    'success': success,
                    'duration_ms': duration_ms
                },
                parent_event_id=start_event_id,
                session_id=session_id
            )


# LangChain Integration
class LangChainMonitorCallback:
    """Callback for LangChain agent monitoring"""

    def __init__(self, monitor: AgentWorkflowMonitor, agent_id: str, session_id: str):
        self.monitor = monitor
        self.agent_id = agent_id
        self.session_id = session_id

    def on_llm_start(self, serialized, prompts, **kwargs):
        """Called when LLM starts"""
        for prompt in prompts:
            self.monitor.log_llm_call(
                agent_id=self.agent_id,
                prompt=prompt,
                model=serialized.get('model', 'unknown'),
                session_id=self.session_id
            )

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Called when tool starts"""
        return self.monitor.log_tool_call(
            agent_id=self.agent_id,
            tool_name=serialized.get('name', 'unknown'),
            parameters={'input': input_str},
            session_id=self.session_id
        )

    def on_tool_end(self, output, **kwargs):
        """Called when tool ends"""
        # This would need the parent event ID from on_tool_start
        pass


# Example usage
if __name__ == "__main__":
    # Create monitor
    monitor = AgentWorkflowMonitor("test_workflow")

    # Start session
    session_id = monitor.start_session()

    # Register agents
    monitor.register_agent("planner_agent", "planning", session_id)
    monitor.register_agent("executor_agent", "execution", session_id)

    # Simulate agent workflow
    with monitor.track_agent_operation("planner_agent", "create_plan", session_id):
        # Simulate LLM call
        llm_event = monitor.log_llm_call(
            agent_id="planner_agent",
            prompt="Create a plan to solve this problem",
            model="gpt-4",
            tokens_used=150,
            cost=0.003,
            session_id=session_id
        )

        monitor.log_llm_response(
            agent_id="planner_agent",
            response="Here's the plan...",
            parent_event_id=llm_event,
            tokens_used=200,
            cost=0.004,
            session_id=session_id
        )

        # Simulate decision
        monitor.log_decision(
            agent_id="planner_agent",
            decision_point="Choose execution strategy",
            options=["parallel", "sequential"],
            chosen="parallel",
            reasoning="Better performance",
            session_id=session_id
        )

    # Inter-agent communication
    monitor.log_communication(
        sender_agent_id="planner_agent",
        receiver_agent_id="executor_agent",
        message="Execute plan with parallel strategy",
        session_id=session_id
    )

    # End session
    monitor.end_session(session_id, success=True)

    # Get analytics
    analytics = monitor.get_session_analytics(session_id)
    print("\nSession Analytics:")
    print(json.dumps(analytics, indent=2, default=str))

    # Export data
    monitor.export_session_data(session_id)