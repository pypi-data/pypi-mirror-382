"""
Example Recommendation Plugin
==============================

Example of a custom recommendation plugin for rightsizing.
"""

from typing import List
from openfinops.plugins import (
    RecommendationPlugin,
    PluginMetadata,
    PluginType,
    Recommendation,
)


class RightsizingRecommendationPlugin(RecommendationPlugin):
    """
    Generate rightsizing recommendations based on historical usage.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="rightsizing-recommendations",
            version="1.0.0",
            author="OpenFinOps Contributors",
            description="ML-powered EC2 instance rightsizing",
            plugin_type=PluginType.RECOMMENDATION,
            dependencies=["numpy>=1.20.0"],
            config_schema={
                "cpu_threshold": {"type": "number", "required": False},
                "memory_threshold": {"type": "number", "required": False},
                "lookback_days": {"type": "integer", "required": False},
            },
            homepage="https://github.com/openfinops/openfinops-plugin-rightsizing",
            tags=["optimization", "ec2", "recommendations"],
        )

    def initialize(self) -> None:
        """Initialize plugin."""
        self.cpu_threshold = self.get_config_value("cpu_threshold", default=30.0)
        self.memory_threshold = self.get_config_value("memory_threshold", default=40.0)
        self.lookback_days = self.get_config_value("lookback_days", default=30)

        print(
            f"✓ Initialized rightsizing plugin "
            f"(CPU threshold: {self.cpu_threshold}%, "
            f"Memory threshold: {self.memory_threshold}%)"
        )

    def generate_recommendations(self, **kwargs) -> List[Recommendation]:
        """
        Generate rightsizing recommendations.

        Returns:
            List of Recommendation objects
        """
        if not self.is_ready:
            raise RuntimeError("Plugin not initialized")

        # In production, you would:
        # 1. Query historical metrics from ObservabilityHub
        # 2. Analyze CPU/memory patterns
        # 3. Use ML model to predict optimal instance types
        # 4. Calculate cost savings

        # For this example, generate mock recommendations
        recommendations = []

        # Example 1: Downsize over-provisioned instance
        recommendations.append(
            Recommendation(
                resource_id="i-0123456789abcdef0",
                recommendation_type="downsize",
                current_state="c5.4xlarge",
                recommended_state="c5.2xlarge",
                annual_savings=8760.0,  # $1/hour * 8760 hours
                confidence=0.95,
                implementation_effort="low",
                description=(
                    "Instance i-0123456789abcdef0 is over-provisioned. "
                    f"Average CPU: 18%, Average Memory: 25%. "
                    "Downsize from c5.4xlarge to c5.2xlarge for "
                    "$8,760/year savings."
                ),
            )
        )

        # Example 2: Switch to ARM-based instance
        recommendations.append(
            Recommendation(
                resource_id="i-0fedcba9876543210",
                recommendation_type="architecture_change",
                current_state="m5.xlarge",
                recommended_state="m6g.xlarge",
                annual_savings=2190.0,  # 20% savings
                confidence=0.90,
                implementation_effort="medium",
                description=(
                    "Switch to ARM-based Graviton2 instance (m6g.xlarge) "
                    "for 20% cost savings with same performance."
                ),
            )
        )

        print(f"✓ Generated {len(recommendations)} recommendations")

        return recommendations

    def shutdown(self) -> None:
        """Cleanup."""
        print("✓ Shut down rightsizing plugin")


# Example usage
if __name__ == "__main__":
    from openfinops.plugins import registry

    # Register and load
    registry.register(RightsizingRecommendationPlugin)
    plugin = registry.load_plugin(
        "rightsizing-recommendations",
        config={
            "cpu_threshold": 25.0,
            "memory_threshold": 35.0,
            "lookback_days": 30,
        }
    )

    # Generate recommendations
    recommendations = plugin.generate_recommendations()

    print(f"\n📊 Rightsizing Recommendations:\n")
    for rec in recommendations:
        print(f"Resource: {rec.resource_id}")
        print(f"  Type: {rec.recommendation_type}")
        print(f"  Current: {rec.current_state} → Recommended: {rec.recommended_state}")
        print(f"  Annual Savings: ${rec.annual_savings:,.0f}")
        print(f"  Confidence: {rec.confidence:.0%}")
        print(f"  Description: {rec.description}")
        print()

    # Cleanup
    registry.unload_plugin("rightsizing-recommendations")
