"""
BI Tool Connectors
==================

Integrations with popular BI tools (Tableau, Power BI, Looker).
"""

# Copyright (c) 2025 OpenFinOps Contributors
# Licensed under the Apache License, Version 2.0

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class ConnectionConfig:
    """
    BI tool connection configuration.

    Attributes:
        host: Host URL
        username: Username
        api_key: API key or token
        workspace: Workspace/project ID
        options: Additional connection options
    """

    host: str
    username: str = ""
    api_key: str = ""
    workspace: str = ""
    options: Dict[str, Any] = None

    def __post_init__(self):
        if self.options is None:
            self.options = {}


class BIConnector(ABC):
    """
    Base class for BI tool connectors.
    """

    def __init__(self, config: ConnectionConfig):
        """
        Initialize BI connector.

        Args:
            config: Connection configuration
        """
        self.config = config
        self._connected = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to BI tool.

        Returns:
            Success status
        """
        pass

    @abstractmethod
    def publish_dataset(
        self, dataset_name: str, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Publish dataset to BI tool.

        Args:
            dataset_name: Name of dataset
            data: Dataset rows
            metadata: Dataset metadata

        Returns:
            Dataset ID
        """
        pass

    @abstractmethod
    def update_dataset(
        self, dataset_id: str, data: List[Dict[str, Any]]
    ) -> bool:
        """
        Update existing dataset.

        Args:
            dataset_id: Dataset ID
            data: Updated data

        Returns:
            Success status
        """
        pass

    @abstractmethod
    def create_dashboard(
        self, dashboard_name: str, dataset_id: str, config: Dict[str, Any]
    ) -> str:
        """
        Create dashboard in BI tool.

        Args:
            dashboard_name: Dashboard name
            dataset_id: Dataset to use
            config: Dashboard configuration

        Returns:
            Dashboard ID
        """
        pass

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected

    def disconnect(self):
        """Disconnect from BI tool."""
        self._connected = False
        logger.info(f"Disconnected from {self.__class__.__name__}")


class TableauConnector(BIConnector):
    """
    Tableau Server/Online connector.
    """

    def connect(self) -> bool:
        """Connect to Tableau."""
        logger.info(f"Connecting to Tableau at {self.config.host}")

        try:
            # In production, use Tableau REST API
            # For now, simulate connection
            self._connected = True
            logger.info("Connected to Tableau successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Tableau: {e}")
            return False

    def publish_dataset(
        self, dataset_name: str, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Publish dataset to Tableau."""
        if not self._connected:
            raise ConnectionError("Not connected to Tableau")

        logger.info(f"Publishing dataset '{dataset_name}' to Tableau")

        # In production, use Tableau Hyper API or REST API
        # For now, simulate publishing
        dataset_id = f"tableau-ds-{hash(dataset_name)}"

        logger.info(
            f"Published {len(data)} rows to Tableau dataset {dataset_id}"
        )

        return dataset_id

    def update_dataset(self, dataset_id: str, data: List[Dict[str, Any]]) -> bool:
        """Update Tableau dataset."""
        if not self._connected:
            raise ConnectionError("Not connected to Tableau")

        logger.info(f"Updating Tableau dataset {dataset_id}")

        # In production, use Tableau API
        logger.info(f"Updated {len(data)} rows in Tableau")

        return True

    def create_dashboard(
        self, dashboard_name: str, dataset_id: str, config: Dict[str, Any]
    ) -> str:
        """Create Tableau dashboard."""
        if not self._connected:
            raise ConnectionError("Not connected to Tableau")

        logger.info(f"Creating Tableau dashboard '{dashboard_name}'")

        # In production, use Tableau REST API or .twb files
        dashboard_id = f"tableau-dash-{hash(dashboard_name)}"

        logger.info(f"Created Tableau dashboard {dashboard_id}")

        return dashboard_id

    def export_workbook(self, workbook_id: str, format: str = "pdf") -> bytes:
        """
        Export Tableau workbook.

        Args:
            workbook_id: Workbook ID
            format: Export format (pdf, png, csv)

        Returns:
            Exported content
        """
        if not self._connected:
            raise ConnectionError("Not connected to Tableau")

        logger.info(f"Exporting Tableau workbook {workbook_id} as {format}")

        # In production, use Tableau REST API
        return b""


class PowerBIConnector(BIConnector):
    """
    Microsoft Power BI connector.
    """

    def connect(self) -> bool:
        """Connect to Power BI."""
        logger.info(f"Connecting to Power BI at {self.config.host}")

        try:
            # In production, use Power BI REST API with Azure AD auth
            # For now, simulate connection
            self._connected = True
            logger.info("Connected to Power BI successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Power BI: {e}")
            return False

    def publish_dataset(
        self, dataset_name: str, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Publish dataset to Power BI."""
        if not self._connected:
            raise ConnectionError("Not connected to Power BI")

        logger.info(f"Publishing dataset '{dataset_name}' to Power BI")

        # In production, use Power BI REST API
        dataset_id = f"powerbi-ds-{hash(dataset_name)}"

        logger.info(f"Published {len(data)} rows to Power BI dataset {dataset_id}")

        return dataset_id

    def update_dataset(self, dataset_id: str, data: List[Dict[str, Any]]) -> bool:
        """Update Power BI dataset."""
        if not self._connected:
            raise ConnectionError("Not connected to Power BI")

        logger.info(f"Updating Power BI dataset {dataset_id}")

        # In production, use Power BI Push Datasets API
        logger.info(f"Updated {len(data)} rows in Power BI")

        return True

    def create_dashboard(
        self, dashboard_name: str, dataset_id: str, config: Dict[str, Any]
    ) -> str:
        """Create Power BI dashboard."""
        if not self._connected:
            raise ConnectionError("Not connected to Power BI")

        logger.info(f"Creating Power BI dashboard '{dashboard_name}'")

        # In production, use Power BI REST API
        dashboard_id = f"powerbi-dash-{hash(dashboard_name)}"

        logger.info(f"Created Power BI dashboard {dashboard_id}")

        return dashboard_id

    def refresh_dataset(self, dataset_id: str) -> bool:
        """
        Trigger dataset refresh.

        Args:
            dataset_id: Dataset ID

        Returns:
            Success status
        """
        if not self._connected:
            raise ConnectionError("Not connected to Power BI")

        logger.info(f"Triggering refresh for Power BI dataset {dataset_id}")

        # In production, use Power BI REST API
        return True


class LookerConnector(BIConnector):
    """
    Looker connector.
    """

    def connect(self) -> bool:
        """Connect to Looker."""
        logger.info(f"Connecting to Looker at {self.config.host}")

        try:
            # In production, use Looker API
            # For now, simulate connection
            self._connected = True
            logger.info("Connected to Looker successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Looker: {e}")
            return False

    def publish_dataset(
        self, dataset_name: str, data: List[Dict[str, Any]], metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Publish dataset to Looker."""
        if not self._connected:
            raise ConnectionError("Not connected to Looker")

        logger.info(f"Publishing dataset '{dataset_name}' to Looker")

        # In production, create Looker view or use database connection
        dataset_id = f"looker-ds-{hash(dataset_name)}"

        logger.info(f"Published {len(data)} rows to Looker dataset {dataset_id}")

        return dataset_id

    def update_dataset(self, dataset_id: str, data: List[Dict[str, Any]]) -> bool:
        """Update Looker dataset."""
        if not self._connected:
            raise ConnectionError("Not connected to Looker")

        logger.info(f"Updating Looker dataset {dataset_id}")

        # In production, update underlying database table
        logger.info(f"Updated {len(data)} rows in Looker")

        return True

    def create_dashboard(
        self, dashboard_name: str, dataset_id: str, config: Dict[str, Any]
    ) -> str:
        """Create Looker dashboard."""
        if not self._connected:
            raise ConnectionError("Not connected to Looker")

        logger.info(f"Creating Looker dashboard '{dashboard_name}'")

        # In production, use Looker API to create dashboard with LookML
        dashboard_id = f"looker-dash-{hash(dashboard_name)}"

        logger.info(f"Created Looker dashboard {dashboard_id}")

        return dashboard_id

    def run_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Run Looker query.

        Args:
            query: LookML query

        Returns:
            Query results
        """
        if not self._connected:
            raise ConnectionError("Not connected to Looker")

        logger.info(f"Running Looker query")

        # In production, use Looker API
        return []


# Helper functions
def create_bi_connector(
    tool: str,
    config: ConnectionConfig,
) -> BIConnector:
    """
    Create BI connector for specified tool.

    Args:
        tool: BI tool name (tableau, powerbi, looker)
        config: Connection configuration

    Returns:
        BI connector instance
    """
    tool = tool.lower()

    connectors = {
        "tableau": TableauConnector,
        "powerbi": PowerBIConnector,
        "power_bi": PowerBIConnector,
        "looker": LookerConnector,
    }

    if tool not in connectors:
        raise ValueError(f"Unsupported BI tool: {tool}")

    connector_class = connectors[tool]
    return connector_class(config)


def sync_data_to_bi(
    connector: BIConnector,
    dataset_name: str,
    data: List[Dict[str, Any]],
    create_dashboard: bool = False,
    dashboard_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """
    Sync data to BI tool.

    Args:
        connector: BI connector
        dataset_name: Dataset name
        data: Data to sync
        create_dashboard: Whether to create dashboard
        dashboard_config: Dashboard configuration

    Returns:
        Created resource IDs
    """
    # Connect if not connected
    if not connector.is_connected():
        connector.connect()

    # Publish dataset
    dataset_id = connector.publish_dataset(dataset_name, data)

    result = {"dataset_id": dataset_id}

    # Create dashboard if requested
    if create_dashboard:
        dashboard_name = dashboard_config.get("name", f"{dataset_name} Dashboard") if dashboard_config else f"{dataset_name} Dashboard"
        dashboard_id = connector.create_dashboard(
            dashboard_name,
            dataset_id,
            dashboard_config or {},
        )
        result["dashboard_id"] = dashboard_id

    return result
