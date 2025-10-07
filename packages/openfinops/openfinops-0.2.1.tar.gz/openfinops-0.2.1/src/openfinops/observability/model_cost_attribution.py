"""
Model-Level Cost Attribution System
===================================

Comprehensive cost tracking and attribution for AI models throughout their lifecycle:
- Development and experimentation costs
- Training infrastructure costs
- Model serving and inference costs
- Storage and data pipeline costs
- Configurable unit cost definitions for compute, storage, and other resources

Features:
- Phase-separated cost tracking (build vs production)
- Granular model-level cost attribution
- Configurable unit cost pricing
- Resource utilization mapping to costs
- Cost allocation by model version, experiment, or deployment
- Multi-cloud cost normalization
- ROI analysis for model investments
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
from collections import defaultdict, deque
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import threading
import statistics

from .cost_observatory import CostCategory, CostEntry


class ModelLifecyclePhase(Enum):
    """Model lifecycle phases for cost attribution"""
    DEVELOPMENT = "development"           # Research, experimentation, data exploration
    TRAINING = "training"                # Model training and hyperparameter tuning
    VALIDATION = "validation"            # Model validation and testing
    DEPLOYMENT_PREP = "deployment_prep"  # Model packaging, optimization, staging
    PRODUCTION = "production"            # Live model serving and inference
    MONITORING = "monitoring"            # Model performance monitoring
    RETRAINING = "retraining"           # Model updates and retraining
    DECOMMISSION = "decommission"       # Model retirement and cleanup


class ResourceType(Enum):
    """Resource types for cost calculation"""
    COMPUTE_GPU = "compute_gpu"          # GPU compute hours
    COMPUTE_CPU = "compute_cpu"          # CPU compute hours
    MEMORY = "memory"                    # Memory usage (GB-hours)
    STORAGE_SSD = "storage_ssd"          # SSD storage (GB-hours)
    STORAGE_HDD = "storage_hdd"          # HDD storage (GB-hours)
    STORAGE_OBJECT = "storage_object"    # Object storage (GB-months)
    NETWORK_INGRESS = "network_ingress"  # Data ingress (GB)
    NETWORK_EGRESS = "network_egress"    # Data egress (GB)
    SOFTWARE_LICENSE = "software_license" # Software licensing costs
    INFERENCE_REQUEST = "inference_request" # Per-inference request cost


@dataclass
class UnitCostConfig:
    """Configurable unit cost definitions"""
    resource_type: ResourceType
    unit_price: float                    # Price per unit (e.g., $/hour, $/GB)
    currency: str = "USD"
    region: str = "us-west-2"
    cloud_provider: str = "aws"
    instance_type: Optional[str] = None  # e.g., "p3.2xlarge", "n1-standard-4"
    description: str = ""
    effective_date: float = field(default_factory=time.time)

    def calculate_cost(self, usage_amount: float) -> float:
        """Calculate cost based on usage amount"""
        return self.unit_price * usage_amount


@dataclass
class ModelMetadata:
    """Model metadata for cost attribution"""
    model_id: str
    model_name: str
    model_version: str
    model_type: str                      # e.g., "transformer", "cnn", "gpt"
    owner: str                          # Team or person responsible
    project_id: str
    created_at: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass
class ResourceUsage:
    """Resource usage record for cost calculation"""
    usage_id: str
    model_id: str
    phase: ModelLifecyclePhase
    resource_type: ResourceType
    usage_amount: float                  # Amount used (hours, GB, requests, etc.)
    usage_duration: float                # Duration in seconds
    timestamp: float = field(default_factory=time.time)
    instance_id: Optional[str] = None    # Instance or resource identifier
    region: str = "us-west-2"
    cloud_provider: str = "aws"
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelCostEntry:
    """Model-specific cost entry with attribution"""
    cost_id: str
    model_id: str
    phase: ModelLifecyclePhase
    resource_usage: ResourceUsage
    unit_cost_config: UnitCostConfig
    calculated_cost: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_usage(cls, resource_usage: ResourceUsage, unit_cost_config: UnitCostConfig) -> 'ModelCostEntry':
        """Create cost entry from resource usage and unit cost config"""
        calculated_cost = unit_cost_config.calculate_cost(resource_usage.usage_amount)

        return cls(
            cost_id=str(uuid.uuid4()),
            model_id=resource_usage.model_id,
            phase=resource_usage.phase,
            resource_usage=resource_usage,
            unit_cost_config=unit_cost_config,
            calculated_cost=calculated_cost,
            tags=resource_usage.tags
        )


@dataclass
class ModelCostSummary:
    """Cost summary for a model"""
    model_id: str
    model_metadata: ModelMetadata
    total_cost: float
    cost_by_phase: Dict[ModelLifecyclePhase, float]
    cost_by_resource_type: Dict[ResourceType, float]
    start_date: float
    end_date: float
    currency: str = "USD"

    def get_build_phase_cost(self) -> float:
        """Get cost for build phases (development, training, validation, deployment_prep)"""
        build_phases = [
            ModelLifecyclePhase.DEVELOPMENT,
            ModelLifecyclePhase.TRAINING,
            ModelLifecyclePhase.VALIDATION,
            ModelLifecyclePhase.DEPLOYMENT_PREP
        ]
        return sum(self.cost_by_phase.get(phase, 0.0) for phase in build_phases)

    def get_production_phase_cost(self) -> float:
        """Get cost for production phases (production, monitoring, retraining)"""
        production_phases = [
            ModelLifecyclePhase.PRODUCTION,
            ModelLifecyclePhase.MONITORING,
            ModelLifecyclePhase.RETRAINING
        ]
        return sum(self.cost_by_phase.get(phase, 0.0) for phase in production_phases)


class ModelCostAttribution:
    """Model-level cost attribution and tracking system"""

    def __init__(self):
        # Core data structures
        self.models: Dict[str, ModelMetadata] = {}
        self.unit_cost_configs: Dict[str, UnitCostConfig] = {}  # Keyed by resource_type + region + provider
        self.resource_usage_history = deque(maxlen=1000000)  # Large history for analysis
        self.model_cost_entries = deque(maxlen=1000000)

        # Aggregated cost tracking
        self.model_costs = defaultdict(lambda: defaultdict(float))  # model_id -> phase -> cost
        self.phase_costs = defaultdict(float)  # phase -> total_cost
        self.resource_costs = defaultdict(float)  # resource_type -> total_cost

        # Thread safety
        self.cost_lock = threading.Lock()

        # Initialize default unit cost configurations
        self._initialize_default_unit_costs()

    def _initialize_default_unit_costs(self):
        """Initialize default unit cost configurations"""
        default_configs = [
            # AWS GPU instances
            UnitCostConfig(ResourceType.COMPUTE_GPU, 3.06, region="us-west-2", cloud_provider="aws",
                          instance_type="p3.2xlarge", description="Tesla V100 GPU"),
            UnitCostConfig(ResourceType.COMPUTE_GPU, 12.24, region="us-west-2", cloud_provider="aws",
                          instance_type="p3.8xlarge", description="4x Tesla V100 GPU"),
            UnitCostConfig(ResourceType.COMPUTE_GPU, 24.48, region="us-west-2", cloud_provider="aws",
                          instance_type="p3.16xlarge", description="8x Tesla V100 GPU"),

            # AWS CPU instances
            UnitCostConfig(ResourceType.COMPUTE_CPU, 0.0464, region="us-west-2", cloud_provider="aws",
                          instance_type="c5.large", description="2 vCPU, 4GB RAM"),
            UnitCostConfig(ResourceType.COMPUTE_CPU, 0.192, region="us-west-2", cloud_provider="aws",
                          instance_type="c5.xlarge", description="4 vCPU, 8GB RAM"),

            # Memory pricing
            UnitCostConfig(ResourceType.MEMORY, 0.0116, region="us-west-2", cloud_provider="aws",
                          description="Memory per GB-hour"),

            # Storage pricing
            UnitCostConfig(ResourceType.STORAGE_SSD, 0.10, region="us-west-2", cloud_provider="aws",
                          description="EBS SSD storage per GB-month"),
            UnitCostConfig(ResourceType.STORAGE_HDD, 0.045, region="us-west-2", cloud_provider="aws",
                          description="EBS HDD storage per GB-month"),
            UnitCostConfig(ResourceType.STORAGE_OBJECT, 0.023, region="us-west-2", cloud_provider="aws",
                          description="S3 Standard storage per GB-month"),

            # Network pricing
            UnitCostConfig(ResourceType.NETWORK_EGRESS, 0.09, region="us-west-2", cloud_provider="aws",
                          description="Data egress per GB"),
            UnitCostConfig(ResourceType.NETWORK_INGRESS, 0.0, region="us-west-2", cloud_provider="aws",
                          description="Data ingress (free)"),

            # Inference pricing
            UnitCostConfig(ResourceType.INFERENCE_REQUEST, 0.0001, region="us-west-2", cloud_provider="aws",
                          description="Per inference request")
        ]

        for config in default_configs:
            key = f"{config.resource_type.value}_{config.region}_{config.cloud_provider}"
            if config.instance_type:
                key += f"_{config.instance_type}"
            self.unit_cost_configs[key] = config

    def register_model(self, model_metadata: ModelMetadata):
        """Register a new model for cost tracking"""
        with self.cost_lock:
            self.models[model_metadata.model_id] = model_metadata

    def add_unit_cost_config(self, config: UnitCostConfig):
        """Add or update unit cost configuration"""
        key = f"{config.resource_type.value}_{config.region}_{config.cloud_provider}"
        if config.instance_type:
            key += f"_{config.instance_type}"

        with self.cost_lock:
            self.unit_cost_configs[key] = config

    def get_unit_cost_config(self, resource_type: ResourceType, region: str = "us-west-2",
                           cloud_provider: str = "aws", instance_type: Optional[str] = None) -> Optional[UnitCostConfig]:
        """Get unit cost configuration for resource"""
        key = f"{resource_type.value}_{region}_{cloud_provider}"
        if instance_type:
            key += f"_{instance_type}"

        return self.unit_cost_configs.get(key)

    def track_resource_usage(self, resource_usage: ResourceUsage):
        """Track resource usage for a model"""
        with self.cost_lock:
            # Add to usage history
            self.resource_usage_history.append(resource_usage)

            # Find appropriate unit cost configuration
            unit_cost_config = self.get_unit_cost_config(
                resource_usage.resource_type,
                resource_usage.region,
                resource_usage.cloud_provider
            )

            if not unit_cost_config:
                # Log warning or use default pricing
                print(f"Warning: No unit cost config found for {resource_usage.resource_type} "
                      f"in {resource_usage.region} on {resource_usage.cloud_provider}")
                return

            # Create cost entry
            cost_entry = ModelCostEntry.from_usage(resource_usage, unit_cost_config)
            self.model_cost_entries.append(cost_entry)

            # Update aggregations
            self._update_cost_aggregations(cost_entry)

    def _update_cost_aggregations(self, cost_entry: ModelCostEntry):
        """Update cost aggregation caches"""
        # Model-specific costs by phase
        self.model_costs[cost_entry.model_id][cost_entry.phase] += cost_entry.calculated_cost

        # Global aggregations
        self.phase_costs[cost_entry.phase] += cost_entry.calculated_cost
        self.resource_costs[cost_entry.resource_usage.resource_type] += cost_entry.calculated_cost

    def get_model_cost_summary(self, model_id: str, start_time: Optional[float] = None,
                             end_time: Optional[float] = None) -> Optional[ModelCostSummary]:
        """Get comprehensive cost summary for a model"""
        if model_id not in self.models:
            return None

        model_metadata = self.models[model_id]

        # Filter cost entries by time range if specified
        filtered_entries = [
            entry for entry in self.model_cost_entries
            if entry.model_id == model_id and
            (start_time is None or entry.timestamp >= start_time) and
            (end_time is None or entry.timestamp <= end_time)
        ]

        if not filtered_entries:
            return None

        # Calculate costs by phase and resource type
        cost_by_phase = defaultdict(float)
        cost_by_resource_type = defaultdict(float)
        total_cost = 0.0

        for entry in filtered_entries:
            cost_by_phase[entry.phase] += entry.calculated_cost
            cost_by_resource_type[entry.resource_usage.resource_type] += entry.calculated_cost
            total_cost += entry.calculated_cost

        # Determine time range
        timestamps = [entry.timestamp for entry in filtered_entries]
        start_date = min(timestamps)
        end_date = max(timestamps)

        return ModelCostSummary(
            model_id=model_id,
            model_metadata=model_metadata,
            total_cost=total_cost,
            cost_by_phase=dict(cost_by_phase),
            cost_by_resource_type=dict(cost_by_resource_type),
            start_date=start_date,
            end_date=end_date
        )

    def get_all_models_cost_summary(self, start_time: Optional[float] = None,
                                  end_time: Optional[float] = None) -> List[ModelCostSummary]:
        """Get cost summaries for all models"""
        summaries = []
        for model_id in self.models:
            summary = self.get_model_cost_summary(model_id, start_time, end_time)
            if summary:
                summaries.append(summary)
        return summaries

    def get_build_vs_production_costs(self, model_id: Optional[str] = None,
                                    start_time: Optional[float] = None,
                                    end_time: Optional[float] = None) -> Dict[str, float]:
        """Get build vs production cost breakdown"""
        if model_id:
            summary = self.get_model_cost_summary(model_id, start_time, end_time)
            if not summary:
                return {"build_cost": 0.0, "production_cost": 0.0}
            return {
                "build_cost": summary.get_build_phase_cost(),
                "production_cost": summary.get_production_phase_cost()
            }
        else:
            # Global build vs production costs
            summaries = self.get_all_models_cost_summary(start_time, end_time)
            build_cost = sum(s.get_build_phase_cost() for s in summaries)
            production_cost = sum(s.get_production_phase_cost() for s in summaries)
            return {
                "build_cost": build_cost,
                "production_cost": production_cost
            }

    def estimate_monthly_cost(self, model_id: str, phase: ModelLifecyclePhase) -> float:
        """Estimate monthly cost based on recent usage patterns"""
        # Get recent cost entries (last 7 days)
        cutoff_time = time.time() - (7 * 24 * 3600)
        recent_entries = [
            entry for entry in self.model_cost_entries
            if entry.model_id == model_id and
               entry.phase == phase and
               entry.timestamp >= cutoff_time
        ]

        if not recent_entries:
            return 0.0

        # Calculate daily average and project to monthly
        daily_costs = defaultdict(float)
        for entry in recent_entries:
            day_key = time.strftime("%Y-%m-%d", time.localtime(entry.timestamp))
            daily_costs[day_key] += entry.calculated_cost

        if not daily_costs:
            return 0.0

        avg_daily_cost = statistics.mean(daily_costs.values())
        return avg_daily_cost * 30  # Project to monthly

    def get_cost_trends(self, model_id: Optional[str] = None,
                       days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """Get cost trends over time"""
        cutoff_time = time.time() - (days * 24 * 3600)

        # Filter entries
        entries = [
            entry for entry in self.model_cost_entries
            if entry.timestamp >= cutoff_time and
            (model_id is None or entry.model_id == model_id)
        ]

        # Group by date
        daily_costs = defaultdict(lambda: defaultdict(float))
        daily_phase_costs = defaultdict(lambda: defaultdict(float))

        for entry in entries:
            date_key = time.strftime("%Y-%m-%d", time.localtime(entry.timestamp))
            daily_costs[date_key]["total"] += entry.calculated_cost
            daily_phase_costs[date_key][entry.phase.value] += entry.calculated_cost

        # Convert to list format for visualization
        trend_data = []
        phase_trend_data = []

        for date_key in sorted(daily_costs.keys()):
            trend_data.append({
                "date": date_key,
                "total_cost": daily_costs[date_key]["total"]
            })

            phase_data = {"date": date_key}
            phase_data.update(daily_phase_costs[date_key])
            phase_trend_data.append(phase_data)

        return {
            "daily_costs": trend_data,
            "daily_phase_costs": phase_trend_data
        }

    def export_cost_data(self, model_id: Optional[str] = None,
                        start_time: Optional[float] = None,
                        end_time: Optional[float] = None) -> Dict[str, Any]:
        """Export comprehensive cost data for analysis"""
        # Filter entries
        filtered_entries = [
            entry for entry in self.model_cost_entries
            if (model_id is None or entry.model_id == model_id) and
               (start_time is None or entry.timestamp >= start_time) and
               (end_time is None or entry.timestamp <= end_time)
        ]

        # Convert to serializable format
        export_data = {
            "models": {k: asdict(v) for k, v in self.models.items()},
            "unit_cost_configs": {k: asdict(v) for k, v in self.unit_cost_configs.items()},
            "cost_entries": [
                {
                    "cost_id": entry.cost_id,
                    "model_id": entry.model_id,
                    "phase": entry.phase.value,
                    "resource_type": entry.resource_usage.resource_type.value,
                    "usage_amount": entry.resource_usage.usage_amount,
                    "calculated_cost": entry.calculated_cost,
                    "timestamp": entry.timestamp,
                    "region": entry.resource_usage.region,
                    "cloud_provider": entry.resource_usage.cloud_provider,
                    "tags": entry.tags
                }
                for entry in filtered_entries
            ],
            "export_timestamp": time.time(),
            "summary": {
                "total_models": len(self.models),
                "total_entries": len(filtered_entries),
                "date_range": {
                    "start": min(entry.timestamp for entry in filtered_entries) if filtered_entries else None,
                    "end": max(entry.timestamp for entry in filtered_entries) if filtered_entries else None
                }
            }
        }

        return export_data


# Convenience functions for easy usage
def create_model_cost_tracker() -> ModelCostAttribution:
    """Create a new model cost attribution tracker"""
    return ModelCostAttribution()


def track_training_cost(tracker: ModelCostAttribution, model_id: str,
                       gpu_hours: float, instance_type: str = "p3.2xlarge",
                       region: str = "us-west-2", cloud_provider: str = "aws"):
    """Convenience function to track training costs"""
    usage = ResourceUsage(
        usage_id=str(uuid.uuid4()),
        model_id=model_id,
        phase=ModelLifecyclePhase.TRAINING,
        resource_type=ResourceType.COMPUTE_GPU,
        usage_amount=gpu_hours,
        usage_duration=gpu_hours * 3600,  # Convert to seconds
        region=region,
        cloud_provider=cloud_provider,
        metadata={"instance_type": instance_type}
    )

    tracker.track_resource_usage(usage)


def track_inference_cost(tracker: ModelCostAttribution, model_id: str,
                        request_count: int, region: str = "us-west-2",
                        cloud_provider: str = "aws"):
    """Convenience function to track inference costs"""
    usage = ResourceUsage(
        usage_id=str(uuid.uuid4()),
        model_id=model_id,
        phase=ModelLifecyclePhase.PRODUCTION,
        resource_type=ResourceType.INFERENCE_REQUEST,
        usage_amount=request_count,
        usage_duration=0.0,  # Instantaneous
        region=region,
        cloud_provider=cloud_provider
    )

    tracker.track_resource_usage(usage)