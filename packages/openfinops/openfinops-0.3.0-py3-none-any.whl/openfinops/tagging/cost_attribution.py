"""
Tag-Based Cost Attribution
===========================

Attribute costs to teams, projects, and cost centers based on tags.

Provides:
- Cost attribution by tag dimensions
- Support for virtual tags
- Multi-dimensional attribution
- Attribution reports
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class AttributionResult:
    """
    Result of cost attribution.

    Attributes:
        dimension: Tag key used for attribution (e.g., "team", "project")
        value: Tag value (e.g., "platform", "ml-training")
        total_cost: Total cost attributed to this value
        resource_count: Number of resources
        percentage: Percentage of total cost
        resources: List of resource IDs
    """

    dimension: str
    value: str
    total_cost: float
    resource_count: int
    percentage: float
    resources: List[str] = field(default_factory=list)


class TagBasedAttribution:
    """
    Cost attribution engine using resource tags.

    Attributes costs based on tag dimensions with support for
    both physical and virtual tags.
    """

    def __init__(self):
        """Initialize attribution engine."""
        self._virtual_tagger = None

    def set_virtual_tagger(self, virtual_tagger: Any):
        """
        Set virtual tagger for inferring missing tags.

        Args:
            virtual_tagger: VirtualTagger instance
        """
        self._virtual_tagger = virtual_tagger

    def attribute_costs(
        self,
        resources_with_costs: List[Dict[str, Any]],
        dimension: str,
        use_virtual_tags: bool = True,
        untagged_label: str = "untagged",
    ) -> List[AttributionResult]:
        """
        Attribute costs by a tag dimension.

        Args:
            resources_with_costs: List of resources with 'cost' and 'tags' fields
            dimension: Tag key to attribute by (e.g., "team", "project")
            use_virtual_tags: Use virtual tags for untagged resources
            untagged_label: Label for resources without the tag

        Returns:
            List of attribution results
        """
        attribution_map: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"cost": 0.0, "count": 0, "resources": []}
        )

        total_cost = 0.0

        for resource in resources_with_costs:
            resource_id = resource.get("id", "unknown")
            cost = resource.get("cost", 0.0)
            tags = resource.get("tags", {})

            # Get tag value
            tag_value = tags.get(dimension)

            # Try virtual tags if not found
            if not tag_value and use_virtual_tags and self._virtual_tagger:
                virtual_tags = self._virtual_tagger.get_virtual_tags(resource_id)
                tag_value = virtual_tags.get(dimension)

            # Use untagged label if still not found
            if not tag_value:
                tag_value = untagged_label

            # Accumulate
            attribution_map[tag_value]["cost"] += cost
            attribution_map[tag_value]["count"] += 1
            attribution_map[tag_value]["resources"].append(resource_id)
            total_cost += cost

        # Convert to AttributionResult objects
        results = []
        for value, data in attribution_map.items():
            percentage = (data["cost"] / total_cost * 100) if total_cost > 0 else 0

            results.append(
                AttributionResult(
                    dimension=dimension,
                    value=value,
                    total_cost=data["cost"],
                    resource_count=data["count"],
                    percentage=percentage,
                    resources=data["resources"],
                )
            )

        # Sort by cost descending
        results.sort(key=lambda r: r.total_cost, reverse=True)

        return results

    def multi_dimensional_attribution(
        self,
        resources_with_costs: List[Dict[str, Any]],
        dimensions: List[str],
        use_virtual_tags: bool = True,
    ) -> Dict[str, List[AttributionResult]]:
        """
        Attribute costs across multiple dimensions.

        Args:
            resources_with_costs: List of resources with costs
            dimensions: List of tag keys to attribute by
            use_virtual_tags: Use virtual tags

        Returns:
            Dictionary mapping dimension to attribution results
        """
        results = {}

        for dimension in dimensions:
            results[dimension] = self.attribute_costs(
                resources_with_costs,
                dimension,
                use_virtual_tags=use_virtual_tags,
            )

        return results

    def get_untagged_resources(
        self,
        resources_with_costs: List[Dict[str, Any]],
        dimension: str,
        use_virtual_tags: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get resources missing a specific tag.

        Args:
            resources_with_costs: List of resources
            dimension: Tag key to check
            use_virtual_tags: Consider virtual tags

        Returns:
            List of resources missing the tag
        """
        untagged = []

        for resource in resources_with_costs:
            resource_id = resource.get("id")
            tags = resource.get("tags", {})

            has_tag = dimension in tags and tags[dimension]

            # Check virtual tags
            if not has_tag and use_virtual_tags and self._virtual_tagger:
                virtual_tags = self._virtual_tagger.get_virtual_tags(resource_id)
                has_tag = dimension in virtual_tags and virtual_tags[dimension]

            if not has_tag:
                untagged.append(resource)

        return untagged

    def get_attribution_summary(
        self,
        resources_with_costs: List[Dict[str, Any]],
        dimensions: List[str],
    ) -> Dict[str, Any]:
        """
        Get summary of cost attribution.

        Args:
            resources_with_costs: List of resources
            dimensions: Dimensions to summarize

        Returns:
            Attribution summary
        """
        total_cost = sum(r.get("cost", 0) for r in resources_with_costs)
        total_resources = len(resources_with_costs)

        by_dimension = {}

        for dimension in dimensions:
            attribution = self.attribute_costs(resources_with_costs, dimension)

            # Find untagged
            untagged_result = next(
                (r for r in attribution if r.value == "untagged"), None
            )

            untagged_cost = untagged_result.total_cost if untagged_result else 0
            untagged_count = untagged_result.resource_count if untagged_result else 0

            by_dimension[dimension] = {
                "total_values": len(attribution),
                "tagged_cost": total_cost - untagged_cost,
                "untagged_cost": untagged_cost,
                "tagged_resources": total_resources - untagged_count,
                "untagged_resources": untagged_count,
                "attribution_coverage": (
                    ((total_cost - untagged_cost) / total_cost * 100)
                    if total_cost > 0
                    else 0
                ),
                "top_5": attribution[:5],
            }

        return {
            "total_cost": total_cost,
            "total_resources": total_resources,
            "by_dimension": by_dimension,
        }

    def showback_report(
        self,
        resources_with_costs: List[Dict[str, Any]],
        dimension: str,
        top_n: int = 10,
    ) -> Dict[str, Any]:
        """
        Generate a showback/chargeback report.

        Args:
            resources_with_costs: List of resources with costs
            dimension: Dimension to report on (e.g., "team", "project")
            top_n: Number of top cost consumers to include

        Returns:
            Showback report
        """
        attribution = self.attribute_costs(resources_with_costs, dimension)

        # Get top N
        top_consumers = attribution[:top_n]

        # Calculate totals
        total_cost = sum(r.total_cost for r in attribution)
        top_n_cost = sum(r.total_cost for r in top_consumers)
        other_cost = total_cost - top_n_cost

        return {
            "dimension": dimension,
            "total_cost": total_cost,
            "top_consumers": [
                {
                    "value": r.value,
                    "cost": r.total_cost,
                    "percentage": r.percentage,
                    "resources": r.resource_count,
                }
                for r in top_consumers
            ],
            "others": {
                "cost": other_cost,
                "percentage": (other_cost / total_cost * 100) if total_cost > 0 else 0,
                "count": len(attribution) - top_n,
            },
        }

    def trend_analysis(
        self,
        historical_data: List[Dict[str, Any]],
        dimension: str,
        group_by_period: str = "day",
    ) -> Dict[str, Any]:
        """
        Analyze cost attribution trends over time.

        Args:
            historical_data: List of {timestamp, resources_with_costs}
            dimension: Dimension to analyze
            group_by_period: "day", "week", or "month"

        Returns:
            Trend analysis
        """
        # Placeholder for trend analysis
        # Would group data by period and track attribution changes
        return {
            "dimension": dimension,
            "period": group_by_period,
            "trends": [],  # Would contain time-series data
        }
