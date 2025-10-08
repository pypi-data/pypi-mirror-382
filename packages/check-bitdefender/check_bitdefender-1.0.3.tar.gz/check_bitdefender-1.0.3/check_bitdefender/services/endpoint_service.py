"""Endpoints service implementation."""

from typing import Dict, List, Any, Optional

from check_bitdefender.core.logging_config import get_verbose_logger


class EndpointsService:
    """Service for listing endpoints."""

    def __init__(self, defender_client: Any, verbose_level: int = 0) -> None:
        """Initialize with Defender client."""
        self.defender = defender_client
        self.logger = get_verbose_logger(__name__, verbose_level)

    def get_result(
        self, endpoint_id: Optional[str] = None, dns_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get endpoint count result with value and details."""
        self.logger.method_entry("get_result")

        # Get all endpoints
        self.logger.info("Fetching all endpoints from Defender API")
        endpoints_data = self.defender.list_endpoints()

        if not endpoints_data.get("value"):
            self.logger.info("No endpoints found")
            result = {
                "value": 0,
                "details": ["No endpoints found in BitDefender GravityZone"],
            }
            self.logger.method_exit("get_result", result)
            return result

        endpoints = endpoints_data["value"]
        endpoint_count = len(endpoints)

        # Create detailed output
        details = [f"Total endpoints: {endpoint_count}"]

        # Liat endpoints
        # Define the sort order
        status_priority = {"Onboarded": 1, "InsufficientInfo": 2, "Unsupported": 3}

        # Sort by priority
        sorted_endpoints = sorted(
            endpoints,
            key=lambda x: (
                status_priority.get(x["onboardingStatus"] or "", 99),
                x["computerDnsName"] or "",
            ),
        )
        for endpoint in sorted_endpoints:
            onboarded = "✓" if endpoint["onboardingStatus"] == "Onboarded" else "✗"
            details.append(
                f"{endpoint['id']}: {endpoint['computerDnsName']} ({endpoint['osPlatform']}) {onboarded}"
            )

        result = {"value": endpoint_count, "details": details}

        self.logger.info(f"Found {endpoint_count} endpoints")
        self.logger.method_exit("get_result", result)
        return result

    def get_details(self) -> List[str]:
        """Get detailed endpoint information."""
        self.logger.method_entry("get_details")

        # Get all endpoints
        self.logger.info("Fetching all endpoints from Defender API")
        endpoints_data = self.defender.list_endpoints()

        if not endpoints_data.get("value"):
            self.logger.info("No endpoints found")
            self.logger.method_exit("get_details", [])
            return []

        endpoints = endpoints_data["value"]
        details = []

        for endpoint in endpoints:
            endpoint_id = endpoint.get("id", "unknown")[:10]  # Truncate ID for display
            dns_name = endpoint.get("computerDnsName", "unknown")
            status = endpoint.get("onboardingStatus", "unknown")
            platform = endpoint.get("osPlatform", "unknown")

            details.append(f"{endpoint_id} {dns_name} {status} {platform}")

        self.logger.info(f"Prepared details for {len(details)} endpoints")
        self.logger.method_exit("get_details", details)
        return details
