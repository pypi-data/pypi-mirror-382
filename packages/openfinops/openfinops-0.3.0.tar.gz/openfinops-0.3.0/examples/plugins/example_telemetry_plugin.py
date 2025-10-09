"""
Example Telemetry Plugin
=========================

Example of a custom telemetry plugin for Oracle Cloud Infrastructure (OCI).
"""

from typing import List
import time
import uuid

from openfinops.plugins import TelemetryPlugin, PluginMetadata, PluginType
from openfinops.observability.cost_observatory import CostEntry, CostCategory


class OracleCloudTelemetryPlugin(TelemetryPlugin):
    """
    Telemetry plugin for Oracle Cloud Infrastructure.

    Collects cost and usage data from Oracle Cloud.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="oracle-cloud-telemetry",
            version="1.0.0",
            author="OpenFinOps Contributors",
            description="Collect cost and usage data from Oracle Cloud",
            plugin_type=PluginType.TELEMETRY,
            dependencies=["oci>=2.0.0"],
            config_schema={
                "tenancy_ocid": {"type": "string", "required": True},
                "region": {"type": "string", "required": True},
                "compartment_id": {"type": "string", "required": False},
            },
            homepage="https://github.com/openfinops/openfinops-plugin-oracle-cloud",
            tags=["oracle", "cloud", "telemetry"],
        )

    def initialize(self) -> None:
        """Initialize OCI client."""
        # In production, you would do:
        # import oci
        # config = oci.config.from_file()
        # self.usage_client = oci.usage_api.UsageapiClient(config)

        # For this example:
        self.region = self.get_config_value("region", required=True)
        self.tenancy_ocid = self.get_config_value("tenancy_ocid", required=True)

        print(f"✓ Initialized Oracle Cloud plugin for region: {self.region}")

    def collect_telemetry(self) -> List[CostEntry]:
        """
        Collect cost data from Oracle Cloud.

        Returns:
            List of CostEntry objects
        """
        if not self.is_ready:
            raise RuntimeError("Plugin not initialized")

        # In production, you would query actual Oracle Cloud usage data
        # For this example, we'll create mock data
        cost_entries = []

        # Mock compute instance costs
        cost_entries.append(
            CostEntry(
                entry_id=str(uuid.uuid4()),
                timestamp=time.time(),
                resource_id="instance-xyz123",
                category=CostCategory.COMPUTE,
                amount=125.50,
                region=self.region,
                tags={
                    "environment": "production",
                    "team": "infrastructure",
                    "provider": "oracle",
                    "service": "compute",
                    "shape": "VM.Standard2.4",
                },
                description="Oracle Compute Instance",
            )
        )

        # Mock object storage costs
        cost_entries.append(
            CostEntry(
                entry_id=str(uuid.uuid4()),
                timestamp=time.time(),
                resource_id="bucket-data-001",
                category=CostCategory.STORAGE,
                amount=45.20,
                region=self.region,
                tags={
                    "environment": "production",
                    "team": "data",
                    "provider": "oracle",
                    "service": "object-storage",
                },
                description="Oracle Object Storage",
            )
        )

        print(f"✓ Collected {len(cost_entries)} cost entries from Oracle Cloud")

        return cost_entries

    def shutdown(self) -> None:
        """Cleanup resources."""
        # Close connections, cleanup
        print(f"✓ Shut down Oracle Cloud plugin")


# Example usage
if __name__ == "__main__":
    from openfinops.plugins import registry

    # Register plugin
    registry.register(OracleCloudTelemetryPlugin)

    # Load plugin
    plugin = registry.load_plugin(
        "oracle-cloud-telemetry",
        config={
            "tenancy_ocid": "ocid1.tenancy.oc1..example",
            "region": "us-ashburn-1",
        }
    )

    # Collect data
    entries = plugin.collect_telemetry()

    print(f"\nCollected {len(entries)} entries:")
    for entry in entries:
        service = entry.tags.get("service", entry.category.value)
        print(f"  - {service}: ${entry.amount:.2f}")

    # Unload
    registry.unload_plugin("oracle-cloud-telemetry")
