"""Mock Defender client for fixture tests."""

import json
from pathlib import Path

from check_bitdefender.core.exceptions import ValidationError


class MockDefenderClient:
    """Mock BitDefender GravityZone client using fixture data."""

    def __init__(self):
        """Initialize with fixture data."""
        fixtures_dir = Path(__file__).parent

        # Load endpoint data
        with open(fixtures_dir / "endpoint_data.json") as f:
            self.endpoint_data = json.load(f)

        # Load vulnerability data
        with open(fixtures_dir / "vulnerability_data.json") as f:
            self.vulnerability_data = json.load(f)

        # Load alerts data
        with open(fixtures_dir / "alerts_data.json") as f:
            self.alerts_data = json.load(f)

    def get_endpoint_by_id(self, endpoint_id):
        """Get endpoint by ID from fixtures."""
        endpoint = self.endpoint_data["endpoint_by_id"].get(endpoint_id)
        if not endpoint:
            raise ValidationError(f"Endpoint not found: {endpoint_id}")
        return endpoint

    def get_endpoint_by_dns_name(self, dns_name):
        """Get endpoint by DNS name from fixtures."""
        return self.endpoint_data["endpoint_by_dns"].get(dns_name, {"value": []})

    def get_endpoint_vulnerabilities(self, endpoint_id):
        """Get vulnerabilities for endpoint from fixtures."""
        return self.vulnerability_data["vulnerabilities_by_endpoint"].get(
            endpoint_id, {"value": []}
        )

    def get_alerts(self):
        """Get all alerts from fixtures."""
        return self.alerts_data["alerts"]
