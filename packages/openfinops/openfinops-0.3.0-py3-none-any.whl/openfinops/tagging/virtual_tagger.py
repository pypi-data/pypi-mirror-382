"""
Virtual Tagging System
======================

Infers tags from patterns, relationships, and historical data without physically tagging resources.

Provides:
- Tag inference from naming conventions
- Relationship-based tagging (resources in same VPC get same tags)
- Historical pattern learning
- Cost attribution without physical tags
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class VirtualTag:
    """
    Represents a virtual (inferred) tag.

    Attributes:
        key: Tag key
        value: Tag value
        resource_id: Resource ID this tag applies to
        confidence: Confidence score (0.0-1.0)
        inference_method: How the tag was inferred
        metadata: Additional context
    """

    key: str
    value: str
    resource_id: str
    confidence: float
    inference_method: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class VirtualTagger:
    """
    Virtual tagging engine for tag inference.

    Infers tags without physically applying them to resources,
    enabling cost attribution even for untagged resources.
    """

    def __init__(self):
        """Initialize virtual tagger."""
        self._virtual_tags: Dict[str, List[VirtualTag]] = defaultdict(list)
        self._inference_rules: List[Dict[str, Any]] = []
        self._resource_relationships: Dict[str, Set[str]] = defaultdict(set)

        # Initialize default inference rules
        self._init_default_rules()

    def _init_default_rules(self):
        """Initialize default inference rules."""
        # Name-based inference
        self.add_inference_rule(
            {
                "name": "environment_from_name",
                "method": "regex",
                "patterns": {
                    "environment": [
                        (r"^prod-", "production"),
                        (r"-prod-", "production"),
                        (r"^staging-", "staging"),
                        (r"^dev-", "development"),
                    ]
                },
                "confidence": 0.90,
            }
        )

        # Resource group/VPC inference
        self.add_inference_rule(
            {
                "name": "inherit_from_parent",
                "method": "relationship",
                "inherit_tags": ["team", "cost_center", "project"],
                "confidence": 0.80,
            }
        )

    def add_inference_rule(self, rule: Dict[str, Any]):
        """
        Add a tag inference rule.

        Args:
            rule: Inference rule configuration
        """
        self._inference_rules.append(rule)

    def infer_tags(
        self,
        resource: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[VirtualTag]:
        """
        Infer virtual tags for a resource.

        Args:
            resource: Resource to tag
            context: Additional context (related resources, etc.)

        Returns:
            List of inferred virtual tags
        """
        context = context or {}
        virtual_tags = []
        resource_id = resource.get("id", "")

        # Apply each inference rule
        for rule in self._inference_rules:
            method = rule.get("method")

            if method == "regex":
                virtual_tags.extend(self._infer_from_regex(resource, rule))
            elif method == "relationship":
                virtual_tags.extend(
                    self._infer_from_relationship(resource, rule, context)
                )
            elif method == "historical":
                virtual_tags.extend(self._infer_from_history(resource, rule))

        # Store virtual tags
        for tag in virtual_tags:
            self._virtual_tags[resource_id].append(tag)

        return virtual_tags

    def _infer_from_regex(
        self, resource: Dict[str, Any], rule: Dict[str, Any]
    ) -> List[VirtualTag]:
        """Infer tags using regex patterns."""
        virtual_tags = []
        resource_id = resource.get("id", "")
        resource_name = resource.get("name", "")

        patterns = rule.get("patterns", {})
        confidence = rule.get("confidence", 0.85)

        for tag_key, tag_patterns in patterns.items():
            for pattern_str, value in tag_patterns:
                pattern = re.compile(pattern_str, re.IGNORECASE)
                if pattern.search(resource_name):
                    virtual_tags.append(
                        VirtualTag(
                            key=tag_key,
                            value=value,
                            resource_id=resource_id,
                            confidence=confidence,
                            inference_method="regex_pattern",
                            metadata={
                                "pattern": pattern_str,
                                "matched_text": resource_name,
                                "rule": rule.get("name"),
                            },
                        )
                    )
                    break  # Use first match

        return virtual_tags

    def _infer_from_relationship(
        self, resource: Dict[str, Any], rule: Dict[str, Any], context: Dict[str, Any]
    ) -> List[VirtualTag]:
        """Infer tags from related resources."""
        virtual_tags = []
        resource_id = resource.get("id", "")

        # Get related resources
        parent_id = resource.get("parent_id") or context.get("parent_id")
        if not parent_id:
            return virtual_tags

        # Check if parent has tags to inherit
        parent_tags = context.get("parent_tags", {})
        inherit_tags = rule.get("inherit_tags", [])
        confidence = rule.get("confidence", 0.80)

        for tag_key in inherit_tags:
            if tag_key in parent_tags:
                virtual_tags.append(
                    VirtualTag(
                        key=tag_key,
                        value=parent_tags[tag_key],
                        resource_id=resource_id,
                        confidence=confidence,
                        inference_method="relationship",
                        metadata={
                            "parent_id": parent_id,
                            "inherited_from": "parent",
                            "rule": rule.get("name"),
                        },
                    )
                )

        return virtual_tags

    def _infer_from_history(
        self, resource: Dict[str, Any], rule: Dict[str, Any]
    ) -> List[VirtualTag]:
        """Infer tags from historical patterns."""
        # Placeholder for ML-based inference from historical data
        # In production, this would analyze historical tagging patterns
        return []

    def get_virtual_tags(
        self, resource_id: str, min_confidence: float = 0.0
    ) -> Dict[str, str]:
        """
        Get virtual tags for a resource.

        Args:
            resource_id: Resource identifier
            min_confidence: Minimum confidence threshold

        Returns:
            Dictionary of tag key-value pairs
        """
        virtual_tags_list = self._virtual_tags.get(resource_id, [])

        # Filter by confidence and deduplicate
        tags_dict = {}
        for tag in virtual_tags_list:
            if tag.confidence >= min_confidence:
                # If multiple values for same key, use highest confidence
                if tag.key not in tags_dict or tag.confidence > tags_dict[tag.key][1]:
                    tags_dict[tag.key] = (tag.value, tag.confidence)

        # Return just the values
        return {key: value for key, (value, _) in tags_dict.items()}

    def bulk_infer(
        self, resources: List[Dict[str, Any]], build_relationships: bool = True
    ) -> Dict[str, List[VirtualTag]]:
        """
        Infer tags for multiple resources at once.

        Args:
            resources: List of resources
            build_relationships: Build resource relationship graph

        Returns:
            Dictionary mapping resource_id to list of VirtualTags
        """
        results = {}

        # Build relationship graph if requested
        if build_relationships:
            self._build_relationship_graph(resources)

        # Infer for each resource
        for resource in resources:
            resource_id = resource.get("id", "")

            # Find parent context
            parent_id = resource.get("parent_id")
            context = {}

            if parent_id:
                # Find parent resource
                parent = next(
                    (r for r in resources if r.get("id") == parent_id), None
                )
                if parent:
                    context["parent_id"] = parent_id
                    context["parent_tags"] = parent.get("tags", {})

            virtual_tags = self.infer_tags(resource, context)
            results[resource_id] = virtual_tags

        return results

    def _build_relationship_graph(self, resources: List[Dict[str, Any]]):
        """Build resource relationship graph."""
        self._resource_relationships.clear()

        for resource in resources:
            resource_id = resource.get("id")
            parent_id = resource.get("parent_id")

            if parent_id:
                self._resource_relationships[parent_id].add(resource_id)

    def get_tagging_suggestions(
        self, resource_id: str, existing_tags: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Get suggestions to physically tag a resource based on virtual tags.

        Args:
            resource_id: Resource identifier
            existing_tags: Current physical tags

        Returns:
            List of tag suggestions
        """
        virtual_tags = self._virtual_tags.get(resource_id, [])
        suggestions = []

        for vtag in virtual_tags:
            if vtag.key not in existing_tags:
                suggestions.append(
                    {
                        "key": vtag.key,
                        "value": vtag.value,
                        "confidence": vtag.confidence,
                        "reason": f"Inferred via {vtag.inference_method}",
                    }
                )

        # Sort by confidence
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)

        return suggestions

    def get_inference_coverage(
        self, resources: List[Dict[str, Any]], required_tags: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate coverage of virtual tags.

        Args:
            resources: List of resources
            required_tags: Required tag keys

        Returns:
            Coverage statistics
        """
        total = len(resources)
        if total == 0:
            return {"coverage": 0}

        tag_coverage = {tag: 0 for tag in required_tags}

        for resource in resources:
            resource_id = resource.get("id", "")
            virtual_tags = self.get_virtual_tags(resource_id)

            for tag in required_tags:
                if tag in virtual_tags:
                    tag_coverage[tag] += 1

        coverage_pct = {
            tag: (count / total) * 100 for tag, count in tag_coverage.items()
        }

        overall = (
            sum(
                1
                for resource in resources
                if all(
                    tag in self.get_virtual_tags(resource.get("id", ""))
                    for tag in required_tags
                )
            )
            / total
        ) * 100

        return {
            "total_resources": total,
            "overall_coverage": overall,
            "by_tag": coverage_pct,
            "tag_counts": tag_coverage,
        }

    def clear(self):
        """Clear all virtual tags."""
        self._virtual_tags.clear()
        self._resource_relationships.clear()
