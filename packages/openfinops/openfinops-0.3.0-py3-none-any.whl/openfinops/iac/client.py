"""
OpenFinOps API Client
======================

HTTP client for managing OpenFinOps resources via API.
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
import logging
import json

logger = logging.getLogger(__name__)


class OpenFinOpsClient:
    """
    HTTP client for OpenFinOps API.
    """

    def __init__(
        self,
        endpoint: str,
        api_key: str = "",
        timeout: int = 30,
        verify_ssl: bool = True,
    ):
        """
        Initialize API client.

        Args:
            endpoint: API endpoint URL
            api_key: API authentication key
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
        """
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._session = None

    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers.

        Returns:
            HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make HTTP request.

        Args:
            method: HTTP method
            path: API path
            data: Request body
            params: Query parameters

        Returns:
            Response data
        """
        url = f"{self.endpoint}{path}"

        logger.debug(f"{method} {url}")

        # In production, use requests library
        # For now, simulate API call
        response = {
            "success": True,
            "data": data or {},
            "message": f"Simulated {method} {path}",
        }

        return response

    # Budget operations
    def create_budget(self, budget: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create budget.

        Args:
            budget: Budget configuration

        Returns:
            Created budget with ID
        """
        logger.info(f"Creating budget: {budget.get('name')}")
        return self._request("POST", "/api/v1/budgets", data=budget)

    def get_budget(self, budget_id: str) -> Dict[str, Any]:
        """
        Get budget by ID.

        Args:
            budget_id: Budget ID

        Returns:
            Budget data
        """
        logger.debug(f"Getting budget: {budget_id}")
        return self._request("GET", f"/api/v1/budgets/{budget_id}")

    def update_budget(self, budget_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update budget.

        Args:
            budget_id: Budget ID
            updates: Fields to update

        Returns:
            Updated budget
        """
        logger.info(f"Updating budget: {budget_id}")
        return self._request("PUT", f"/api/v1/budgets/{budget_id}", data=updates)

    def delete_budget(self, budget_id: str) -> Dict[str, Any]:
        """
        Delete budget.

        Args:
            budget_id: Budget ID

        Returns:
            Deletion result
        """
        logger.info(f"Deleting budget: {budget_id}")
        return self._request("DELETE", f"/api/v1/budgets/{budget_id}")

    def list_budgets(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List budgets.

        Args:
            filters: Optional filters

        Returns:
            List of budgets
        """
        logger.debug("Listing budgets")
        response = self._request("GET", "/api/v1/budgets", params=filters)
        return response.get("data", {}).get("budgets", [])

    # Policy operations
    def create_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create policy.

        Args:
            policy: Policy configuration

        Returns:
            Created policy with ID
        """
        logger.info(f"Creating policy: {policy.get('name')}")
        return self._request("POST", "/api/v1/policies", data=policy)

    def get_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Get policy by ID.

        Args:
            policy_id: Policy ID

        Returns:
            Policy data
        """
        logger.debug(f"Getting policy: {policy_id}")
        return self._request("GET", f"/api/v1/policies/{policy_id}")

    def update_policy(self, policy_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update policy.

        Args:
            policy_id: Policy ID
            updates: Fields to update

        Returns:
            Updated policy
        """
        logger.info(f"Updating policy: {policy_id}")
        return self._request("PUT", f"/api/v1/policies/{policy_id}", data=updates)

    def delete_policy(self, policy_id: str) -> Dict[str, Any]:
        """
        Delete policy.

        Args:
            policy_id: Policy ID

        Returns:
            Deletion result
        """
        logger.info(f"Deleting policy: {policy_id}")
        return self._request("DELETE", f"/api/v1/policies/{policy_id}")

    def list_policies(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List policies.

        Args:
            filters: Optional filters

        Returns:
            List of policies
        """
        logger.debug("Listing policies")
        response = self._request("GET", "/api/v1/policies", params=filters)
        return response.get("data", {}).get("policies", [])

    # Alert operations
    def create_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create alert.

        Args:
            alert: Alert configuration

        Returns:
            Created alert with ID
        """
        logger.info(f"Creating alert: {alert.get('name')}")
        return self._request("POST", "/api/v1/alerts", data=alert)

    def get_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Get alert by ID.

        Args:
            alert_id: Alert ID

        Returns:
            Alert data
        """
        logger.debug(f"Getting alert: {alert_id}")
        return self._request("GET", f"/api/v1/alerts/{alert_id}")

    def update_alert(self, alert_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update alert.

        Args:
            alert_id: Alert ID
            updates: Fields to update

        Returns:
            Updated alert
        """
        logger.info(f"Updating alert: {alert_id}")
        return self._request("PUT", f"/api/v1/alerts/{alert_id}", data=updates)

    def delete_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Delete alert.

        Args:
            alert_id: Alert ID

        Returns:
            Deletion result
        """
        logger.info(f"Deleting alert: {alert_id}")
        return self._request("DELETE", f"/api/v1/alerts/{alert_id}")

    def list_alerts(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List alerts.

        Args:
            filters: Optional filters

        Returns:
            List of alerts
        """
        logger.debug("Listing alerts")
        response = self._request("GET", "/api/v1/alerts", params=filters)
        return response.get("data", {}).get("alerts", [])

    # Dashboard operations
    def create_dashboard(self, dashboard: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create dashboard.

        Args:
            dashboard: Dashboard configuration

        Returns:
            Created dashboard with ID
        """
        logger.info(f"Creating dashboard: {dashboard.get('name')}")
        return self._request("POST", "/api/v1/dashboards", data=dashboard)

    def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Get dashboard by ID.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Dashboard data
        """
        logger.debug(f"Getting dashboard: {dashboard_id}")
        return self._request("GET", f"/api/v1/dashboards/{dashboard_id}")

    def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update dashboard.

        Args:
            dashboard_id: Dashboard ID
            updates: Fields to update

        Returns:
            Updated dashboard
        """
        logger.info(f"Updating dashboard: {dashboard_id}")
        return self._request("PUT", f"/api/v1/dashboards/{dashboard_id}", data=updates)

    def delete_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Delete dashboard.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            Deletion result
        """
        logger.info(f"Deleting dashboard: {dashboard_id}")
        return self._request("DELETE", f"/api/v1/dashboards/{dashboard_id}")

    def list_dashboards(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List dashboards.

        Args:
            filters: Optional filters

        Returns:
            List of dashboards
        """
        logger.debug("Listing dashboards")
        response = self._request("GET", "/api/v1/dashboards", params=filters)
        return response.get("data", {}).get("dashboards", [])

    # Generic resource operations
    def get_resource(self, resource_type: str, resource_id: str) -> Dict[str, Any]:
        """
        Get resource by type and ID.

        Args:
            resource_type: Type of resource
            resource_id: Resource ID

        Returns:
            Resource data
        """
        methods = {
            "budget": self.get_budget,
            "policy": self.get_policy,
            "alert": self.get_alert,
            "dashboard": self.get_dashboard,
        }

        method = methods.get(resource_type)
        if not method:
            raise ValueError(f"Unknown resource type: {resource_type}")

        return method(resource_id)

    def list_resources(
        self, resource_type: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List resources by type.

        Args:
            resource_type: Type of resource
            filters: Optional filters

        Returns:
            List of resources
        """
        methods = {
            "budget": self.list_budgets,
            "policy": self.list_policies,
            "alert": self.list_alerts,
            "dashboard": self.list_dashboards,
        }

        method = methods.get(resource_type)
        if not method:
            raise ValueError(f"Unknown resource type: {resource_type}")

        return method(filters)


def create_client(
    endpoint: str,
    api_key: str = "",
    **options,
) -> OpenFinOpsClient:
    """
    Create OpenFinOps API client.

    Args:
        endpoint: API endpoint URL
        api_key: API authentication key
        **options: Additional client options

    Returns:
        API client instance
    """
    return OpenFinOpsClient(
        endpoint=endpoint,
        api_key=api_key,
        **options,
    )
