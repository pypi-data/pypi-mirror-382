#!/usr/bin/env python3
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

"""
LLM Configuration Module for Intelligent Recommendations
=========================================================

Configurable LLM support for generating intelligent recommendations:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Azure OpenAI
- Local models (Ollama, LLaMA)
- Fallback to rule-based recommendations
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    RULE_BASED = "rule_based"  # Fallback to rule-based logic


@dataclass
class LLMConfig:
    """LLM configuration for recommendations engine."""
    provider: LLMProvider
    model_name: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 1000
    timeout: int = 30

    # Azure-specific
    azure_deployment: Optional[str] = None
    azure_api_version: str = "2024-02-15-preview"

    # Local model specific
    local_endpoint: Optional[str] = None

    # Cost tracking
    track_api_costs: bool = True
    max_monthly_cost: float = 100.0  # USD


class LLMRecommendationEngine:
    """Intelligent LLM-powered recommendation engine."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize LLM engine with configuration."""
        self.logger = logging.getLogger(__name__)
        self.config = config or self._get_default_config()
        self.client = None
        self._initialize_client()

    def _get_default_config(self) -> LLMConfig:
        """Get default configuration from environment."""
        # Try to detect from environment variables
        if os.getenv('OPENAI_API_KEY'):
            return LLMConfig(
                provider=LLMProvider.OPENAI,
                model_name=os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
                api_key=os.getenv('OPENAI_API_KEY')
            )
        elif os.getenv('ANTHROPIC_API_KEY'):
            return LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model_name=os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229'),
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        elif os.getenv('AZURE_OPENAI_API_KEY'):
            return LLMConfig(
                provider=LLMProvider.AZURE_OPENAI,
                model_name=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4'),
                api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                azure_deployment=os.getenv('AZURE_OPENAI_DEPLOYMENT')
            )
        elif os.getenv('OLLAMA_ENDPOINT'):
            return LLMConfig(
                provider=LLMProvider.OLLAMA,
                model_name=os.getenv('OLLAMA_MODEL', 'llama2'),
                local_endpoint=os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434')
            )
        else:
            # Default to rule-based (no LLM required)
            self.logger.info("No LLM configuration found. Using rule-based recommendations.")
            return LLMConfig(
                provider=LLMProvider.RULE_BASED,
                model_name="rule_based_v1"
            )

    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        try:
            if self.config.provider == LLMProvider.OPENAI:
                self._init_openai()
            elif self.config.provider == LLMProvider.ANTHROPIC:
                self._init_anthropic()
            elif self.config.provider == LLMProvider.AZURE_OPENAI:
                self._init_azure_openai()
            elif self.config.provider == LLMProvider.OLLAMA:
                self._init_ollama()
            elif self.config.provider == LLMProvider.RULE_BASED:
                self.client = None  # No client needed
            else:
                self.logger.warning(f"Unknown provider: {self.config.provider}. Using rule-based.")
                self.config.provider = LLMProvider.RULE_BASED
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM client: {e}. Falling back to rule-based.")
            self.config.provider = LLMProvider.RULE_BASED
            self.client = None

    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.config.api_key)
            self.logger.info(f"Initialized OpenAI client with model: {self.config.model_name}")
        except ImportError:
            self.logger.error("OpenAI library not installed. Run: pip install openai")
            raise

    def _init_anthropic(self):
        """Initialize Anthropic client."""
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.config.api_key)
            self.logger.info(f"Initialized Anthropic client with model: {self.config.model_name}")
        except ImportError:
            self.logger.error("Anthropic library not installed. Run: pip install anthropic")
            raise

    def _init_azure_openai(self):
        """Initialize Azure OpenAI client."""
        try:
            import openai
            from openai import AzureOpenAI
            self.client = AzureOpenAI(
                api_key=self.config.api_key,
                api_version=self.config.azure_api_version,
                azure_endpoint=self.config.endpoint
            )
            self.logger.info(f"Initialized Azure OpenAI client: {self.config.azure_deployment}")
        except ImportError:
            self.logger.error("OpenAI library not installed. Run: pip install openai")
            raise

    def _init_ollama(self):
        """Initialize Ollama local client."""
        try:
            import requests
            # Test connection
            response = requests.get(f"{self.config.local_endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                self.client = self.config.local_endpoint
                self.logger.info(f"Initialized Ollama client: {self.config.model_name}")
            else:
                raise ConnectionError(f"Ollama not responding at {self.config.local_endpoint}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Ollama: {e}")
            raise

    def generate_recommendation(
        self,
        context: Dict[str, Any],
        recommendation_type: str
    ) -> Dict[str, Any]:
        """Generate intelligent recommendation using configured LLM."""

        if self.config.provider == LLMProvider.RULE_BASED:
            return self._rule_based_recommendation(context, recommendation_type)

        # Build prompt for LLM
        prompt = self._build_recommendation_prompt(context, recommendation_type)

        try:
            if self.config.provider == LLMProvider.OPENAI:
                return self._query_openai(prompt)
            elif self.config.provider == LLMProvider.ANTHROPIC:
                return self._query_anthropic(prompt)
            elif self.config.provider == LLMProvider.AZURE_OPENAI:
                return self._query_azure_openai(prompt)
            elif self.config.provider == LLMProvider.OLLAMA:
                return self._query_ollama(prompt)
        except Exception as e:
            self.logger.error(f"LLM query failed: {e}. Falling back to rule-based.")
            return self._rule_based_recommendation(context, recommendation_type)

    def _build_recommendation_prompt(
        self,
        context: Dict[str, Any],
        recommendation_type: str
    ) -> str:
        """Build structured prompt for LLM."""

        system_prompt = """You are an expert AI/ML infrastructure and FinOps consultant.
        Analyze the provided metrics and generate specific, actionable recommendations.

        Focus on:
        1. Hardware optimization (GPU types, instance sizing)
        2. Scaling strategies (horizontal/vertical, auto-scaling)
        3. Cost reduction opportunities
        4. Performance improvements

        Respond in JSON format with:
        - title: Brief recommendation title
        - description: Detailed explanation
        - actions: List of specific action items
        - impact: Estimated cost/performance impact
        - effort: Implementation effort (Low/Medium/High)
        - confidence: Confidence score 0.0-1.0
        """

        user_prompt = f"""
        Recommendation Type: {recommendation_type}

        Current Metrics:
        {json.dumps(context, indent=2)}

        Provide a detailed recommendation to optimize this infrastructure.
        """

        return system_prompt + "\n\n" + user_prompt

    def _query_openai(self, prompt: str) -> Dict[str, Any]:
        """Query OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": prompt.split("\n\n")[0]},
                {"role": "user", "content": "\n\n".join(prompt.split("\n\n")[1:])}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

    def _query_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Query Anthropic API."""
        response = self.client.messages.create(
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        # Parse JSON from response
        content = response.content[0].text
        return json.loads(content)

    def _query_azure_openai(self, prompt: str) -> Dict[str, Any]:
        """Query Azure OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.config.azure_deployment,
            messages=[
                {"role": "system", "content": prompt.split("\n\n")[0]},
                {"role": "user", "content": "\n\n".join(prompt.split("\n\n")[1:])}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return json.loads(response.choices[0].message.content)

    def _query_ollama(self, prompt: str) -> Dict[str, Any]:
        """Query Ollama local API."""
        import requests
        response = requests.post(
            f"{self.client}/api/generate",
            json={
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return json.loads(response.json()['response'])

    def _rule_based_recommendation(
        self,
        context: Dict[str, Any],
        recommendation_type: str
    ) -> Dict[str, Any]:
        """Fallback rule-based recommendation logic."""

        # Simple rule-based logic
        if recommendation_type == "hardware":
            return self._rule_based_hardware(context)
        elif recommendation_type == "scaling":
            return self._rule_based_scaling(context)
        else:
            return {
                "title": "General Optimization",
                "description": "Monitor your metrics and adjust resources as needed.",
                "actions": ["Review current resource utilization", "Set up alerts"],
                "impact": "Varies",
                "effort": "Low",
                "confidence": 0.5
            }

    def _rule_based_hardware(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based hardware recommendations."""
        gpu_util = context.get('gpu_utilization', 0)
        cost_per_hour = context.get('cost_per_hour', 0)

        if gpu_util < 50:
            return {
                "title": "Downgrade GPU Instance",
                "description": f"Current GPU utilization is {gpu_util}%. Consider smaller instance.",
                "actions": [
                    "Switch to smaller GPU (e.g., T4 instead of A100)",
                    "Use multi-instance GPU if supported",
                    "Consider CPU-only for inference"
                ],
                "impact": f"Save ~${cost_per_hour * 0.5:.2f}/hour",
                "effort": "Medium",
                "confidence": 0.8
            }
        elif gpu_util > 90:
            return {
                "title": "Upgrade GPU Instance",
                "description": f"GPU utilization at {gpu_util}%. Performance bottleneck detected.",
                "actions": [
                    "Upgrade to more powerful GPU (e.g., A100 or H100)",
                    "Add more GPU instances",
                    "Enable GPU memory optimization"
                ],
                "impact": "Improve performance by 40-60%",
                "effort": "Low",
                "confidence": 0.9
            }
        else:
            return {
                "title": "Hardware Optimization Looks Good",
                "description": f"GPU utilization at {gpu_util}% is optimal.",
                "actions": ["Continue monitoring", "Set up utilization alerts"],
                "impact": "Maintain current efficiency",
                "effort": "Low",
                "confidence": 0.95
            }

    def _rule_based_scaling(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based scaling recommendations."""
        current_instances = context.get('instance_count', 1)
        avg_utilization = context.get('avg_utilization', 50)
        peak_utilization = context.get('peak_utilization', 50)

        if avg_utilization < 40 and current_instances > 1:
            return {
                "title": "Scale Down Infrastructure",
                "description": f"Average utilization {avg_utilization}% with {current_instances} instances.",
                "actions": [
                    f"Reduce to {max(1, current_instances - 1)} instances",
                    "Enable auto-scaling with lower threshold",
                    "Consolidate workloads"
                ],
                "impact": f"Save ${context.get('cost_per_hour', 5) * 0.3:.2f}/hour",
                "effort": "Low",
                "confidence": 0.85
            }
        elif peak_utilization > 85:
            return {
                "title": "Scale Up for Peak Load",
                "description": f"Peak utilization {peak_utilization}% indicates capacity issues.",
                "actions": [
                    f"Increase to {current_instances + 1} instances",
                    "Enable auto-scaling for peaks",
                    "Implement load balancing"
                ],
                "impact": "Handle 30% more load, reduce latency",
                "effort": "Medium",
                "confidence": 0.9
            }
        else:
            return {
                "title": "Scaling Configuration Optimal",
                "description": "Current scaling configuration is well-balanced.",
                "actions": [
                    "Enable predictive auto-scaling",
                    "Set up capacity planning alerts"
                ],
                "impact": "Maintain optimal performance",
                "effort": "Low",
                "confidence": 0.9
            }


# Configuration helper
def get_llm_config() -> LLMConfig:
    """Get LLM configuration from environment or config file."""
    config_path = os.getenv('OPENFINOPS_LLM_CONFIG', 'llm_config.json')

    if os.path.exists(config_path):
        with open(config_path) as f:
            data = json.load(f)
            return LLMConfig(
                provider=LLMProvider(data['provider']),
                model_name=data['model_name'],
                api_key=data.get('api_key'),
                endpoint=data.get('endpoint'),
                temperature=data.get('temperature', 0.3),
                max_tokens=data.get('max_tokens', 1000)
            )
    else:
        # Return default from environment
        return LLMRecommendationEngine()._get_default_config()
