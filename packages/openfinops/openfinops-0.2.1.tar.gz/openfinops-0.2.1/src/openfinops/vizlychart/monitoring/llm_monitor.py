"""
OpenFinOps - LLM Training Monitoring
Real training hooks for PyTorch, HuggingFace, and other frameworks
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
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from collections import defaultdict
import psutil
import subprocess


@dataclass
class TrainingMetrics:
    """Training metrics data structure"""
    timestamp: float
    epoch: int
    step: int
    loss: float
    learning_rate: float
    gpu_memory_used: Optional[float] = None
    gpu_utilization: Optional[float] = None
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    tokens_per_second: Optional[float] = None
    cost_estimate: Optional[float] = None


class LLMTrainingMonitor:
    """Production-ready LLM training monitoring"""

    def __init__(self, project_name: str = "default", api_endpoint: Optional[str] = None):
        self.project_name = project_name
        self.api_endpoint = api_endpoint
        self.metrics_buffer: List[TrainingMetrics] = []
        self.callbacks: List[Callable] = []
        self.monitoring_active = False
        self.gpu_available = self._check_gpu_availability()

    def _check_gpu_availability(self) -> bool:
        """Check if NVIDIA GPU is available"""
        try:
            subprocess.run(['nvidia-smi'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_gpu_metrics(self) -> Dict[str, float]:
        """Get real GPU utilization and memory usage"""
        if not self.gpu_available:
            return {}

        try:
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, check=True)

            values = result.stdout.strip().split(', ')
            gpu_util = float(values[0])
            gpu_mem_used = float(values[1])  # MB
            gpu_mem_total = float(values[2])  # MB

            return {
                'gpu_utilization': gpu_util,
                'gpu_memory_used': (gpu_mem_used / gpu_mem_total) * 100,
                'gpu_memory_mb': gpu_mem_used
            }
        except Exception:
            return {}

    def _get_system_metrics(self) -> Dict[str, float]:
        """Get system CPU and memory metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent
        }

    def _estimate_cost(self, gpu_util: float, duration_minutes: float) -> float:
        """Estimate training cost based on GPU utilization"""
        # AWS p3.2xlarge pricing: ~$3.06/hour for V100
        # Azure NC6s_v3: ~$3.168/hour for V100
        base_cost_per_hour = 3.10
        utilization_factor = gpu_util / 100.0
        cost_per_minute = (base_cost_per_hour / 60) * utilization_factor
        return cost_per_minute * duration_minutes

    def log_training_step(self, epoch: int, step: int, loss: float,
                         learning_rate: float, tokens_per_second: Optional[float] = None):
        """Log training metrics for a single step"""
        if not self.monitoring_active:
            return

        # Gather system metrics
        gpu_metrics = self._get_gpu_metrics()
        system_metrics = self._get_system_metrics()

        # Create metrics object
        metrics = TrainingMetrics(
            timestamp=time.time(),
            epoch=epoch,
            step=step,
            loss=loss,
            learning_rate=learning_rate,
            gpu_memory_used=gpu_metrics.get('gpu_memory_used'),
            gpu_utilization=gpu_metrics.get('gpu_utilization'),
            cpu_percent=system_metrics.get('cpu_percent'),
            memory_percent=system_metrics.get('memory_percent'),
            tokens_per_second=tokens_per_second,
            cost_estimate=self._estimate_cost(
                gpu_metrics.get('gpu_utilization', 0),
                1.0  # 1 minute estimate
            )
        )

        # Buffer metrics
        self.metrics_buffer.append(metrics)

        # Execute callbacks
        for callback in self.callbacks:
            try:
                callback(metrics)
            except Exception as e:
                print(f"Callback error: {e}")

        # Auto-flush buffer if it gets large
        if len(self.metrics_buffer) > 100:
            self.flush_metrics()

    def start_monitoring(self):
        """Start monitoring training"""
        self.monitoring_active = True
        print(f"🔍 LLM Training Monitoring started for project: {self.project_name}")

    def stop_monitoring(self):
        """Stop monitoring and flush remaining metrics"""
        self.monitoring_active = False
        self.flush_metrics()
        print("✅ LLM Training Monitoring stopped")

    def flush_metrics(self):
        """Flush metrics buffer to storage/API"""
        if not self.metrics_buffer:
            return

        # Save to local file
        filename = f"llm_training_metrics_{self.project_name}_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump([
                {
                    'timestamp': m.timestamp,
                    'epoch': m.epoch,
                    'step': m.step,
                    'loss': m.loss,
                    'learning_rate': m.learning_rate,
                    'gpu_memory_used': m.gpu_memory_used,
                    'gpu_utilization': m.gpu_utilization,
                    'cpu_percent': m.cpu_percent,
                    'memory_percent': m.memory_percent,
                    'tokens_per_second': m.tokens_per_second,
                    'cost_estimate': m.cost_estimate
                } for m in self.metrics_buffer
            ], f, indent=2)

        # Send to API if endpoint provided
        if self.api_endpoint:
            self._send_to_api(self.metrics_buffer)

        # Clear buffer
        self.metrics_buffer.clear()
        print(f"📊 Flushed {len(self.metrics_buffer)} training metrics")

    def _send_to_api(self, metrics: List[TrainingMetrics]):
        """Send metrics to OpenFinOps API endpoint"""
        try:
            import requests
            response = requests.post(
                f"{self.api_endpoint}/training/metrics",
                json={
                    'project': self.project_name,
                    'metrics': [m.__dict__ for m in metrics]
                },
                timeout=10
            )
            if response.status_code == 200:
                print("✅ Metrics sent to OpenFinOps API")
            else:
                print(f"⚠️ API response: {response.status_code}")
        except Exception as e:
            print(f"❌ Failed to send metrics to API: {e}")

    def add_callback(self, callback: Callable[[TrainingMetrics], None]):
        """Add callback function for real-time metrics processing"""
        self.callbacks.append(callback)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary statistics of collected metrics"""
        if not self.metrics_buffer:
            return {}

        losses = [m.loss for m in self.metrics_buffer]
        gpu_utils = [m.gpu_utilization for m in self.metrics_buffer if m.gpu_utilization]
        costs = [m.cost_estimate for m in self.metrics_buffer if m.cost_estimate]

        return {
            'total_steps': len(self.metrics_buffer),
            'avg_loss': sum(losses) / len(losses) if losses else 0,
            'min_loss': min(losses) if losses else 0,
            'avg_gpu_utilization': sum(gpu_utils) / len(gpu_utils) if gpu_utils else 0,
            'total_estimated_cost': sum(costs) if costs else 0,
            'training_duration_minutes': (
                (self.metrics_buffer[-1].timestamp - self.metrics_buffer[0].timestamp) / 60
                if len(self.metrics_buffer) > 1 else 0
            )
        }


# HuggingFace Transformers Integration
class HuggingFaceCallback:
    """Callback for HuggingFace Transformers training"""

    def __init__(self, monitor: LLMTrainingMonitor):
        self.monitor = monitor

    def on_step_end(self, args, state, control, **kwargs):
        """Called at the end of each training step"""
        if state.log_history:
            latest_log = state.log_history[-1]
            self.monitor.log_training_step(
                epoch=int(state.epoch),
                step=state.global_step,
                loss=latest_log.get('train_loss', 0),
                learning_rate=latest_log.get('learning_rate', 0)
            )


# PyTorch Lightning Integration
class LightningCallback:
    """Callback for PyTorch Lightning training"""

    def __init__(self, monitor: LLMTrainingMonitor):
        self.monitor = monitor

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx):
        """Called after each training batch"""
        if 'loss' in outputs:
            self.monitor.log_training_step(
                epoch=trainer.current_epoch,
                step=trainer.global_step,
                loss=float(outputs['loss']),
                learning_rate=trainer.optimizers[0].param_groups[0]['lr']
            )


# Convenient factory functions
def create_monitor(project_name: str = "llm_training") -> LLMTrainingMonitor:
    """Create a new LLM training monitor"""
    return LLMTrainingMonitor(project_name=project_name)


def monitor_huggingface_training(trainer, project_name: str = "hf_training"):
    """Add OpenFinOps monitoring to HuggingFace Trainer"""
    monitor = create_monitor(project_name)
    callback = HuggingFaceCallback(monitor)
    trainer.add_callback(callback)
    monitor.start_monitoring()
    return monitor


# Example usage
if __name__ == "__main__":
    # Example: Manual monitoring
    monitor = create_monitor("test_project")
    monitor.start_monitoring()

    # Simulate training steps
    for epoch in range(2):
        for step in range(10):
            loss = 2.5 - (epoch * 0.5) - (step * 0.05)
            lr = 0.001 * (0.9 ** (epoch * 10 + step))

            monitor.log_training_step(
                epoch=epoch,
                step=step,
                loss=loss,
                learning_rate=lr,
                tokens_per_second=150.0
            )

            time.sleep(0.1)  # Simulate training time

    monitor.stop_monitoring()
    print("\nTraining Summary:")
    print(json.dumps(monitor.get_metrics_summary(), indent=2))