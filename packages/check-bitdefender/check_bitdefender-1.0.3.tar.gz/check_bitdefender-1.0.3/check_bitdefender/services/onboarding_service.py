"""Onboarding status service implementation."""

from typing import Dict, Any, Optional
from check_bitdefender.core.logging_config import get_verbose_logger


class OnboardingService:
    """Service for checking endpoint onboarding status."""

    def __init__(self, defender_client: Any, verbose_level: int = 0) -> None:
        """Initialize with Defender client.

        Args:
            defender_client: DefenderClient instance
            verbose_level: Verbosity level for logging
        """
        self.defender = defender_client
        self.logger = get_verbose_logger(__name__, verbose_level)

    def get_result(
        self, endpoint_id: Optional[str] = None, dns_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check onboarding status for an endpoint.

        Returns a numeric value indicating onboarding status:
        - 0: Onboarded and active
        - 1: Not found

        Args:
            endpoint_id: Optional endpoint ID to check
            dns_name: Optional DNS name to check

        Returns:
            Dictionary with:
            - value: 0 if onboarded, 1 if not found
            - details: List of detail strings for verbose output
        """
        self.logger.method_entry("get_result", endpoint_id=endpoint_id, dns_name=dns_name)

        if not endpoint_id and not dns_name:
            raise ValueError("Either endpoint_id or dns_name must be provided")

        # Get all endpoints
        self.logger.info(f"Searching for endpoint: {dns_name or endpoint_id}")
        endpoints_data = self.defender.list_endpoints()

        if not endpoints_data.get("value"):
            self.logger.info("No endpoints found in system")
            result = {
                "value": 1,  # Not found
                "details": [f"Host not found ({dns_name or endpoint_id})"],
            }
            self.logger.method_exit("get_result", result)
            return result

        endpoints = endpoints_data["value"]

        # Find the matching endpoint
        matching_endpoint = None
        for endpoint in endpoints:
            if endpoint_id and endpoint.get("id") == endpoint_id:
                matching_endpoint = endpoint
                break
            elif dns_name and endpoint.get("computerDnsName") == dns_name:
                matching_endpoint = endpoint
                break

        if not matching_endpoint:
            self.logger.info(f"Endpoint not found: {dns_name or endpoint_id}")
            result = {
                "value": 1,  # Not found
                "details": [f"Host not found ({dns_name or endpoint_id})"],
            }
            self.logger.method_exit("get_result", result)
            return result

        # Check onboarding status
        onboarding_status = matching_endpoint.get("onboardingStatus")
        computer_name = matching_endpoint.get("computerDnsName", dns_name or endpoint_id)

        if onboarding_status == "Onboarded":
            self.logger.info(f"Endpoint is onboarded: {computer_name}")
            result = {
                "value": 0,  # Onboarded
                "details": [f"Host onboarded ({computer_name})"],
            }
        else:
            self.logger.info(f"Endpoint not onboarded: {computer_name}, status: {onboarding_status}")
            result = {
                "value": 1,  # Not onboarded
                "details": [
                    f"Host not onboarded ({computer_name})",
                    f"Onboarding status: {onboarding_status}"
                ],
            }

        self.logger.method_exit("get_result", result)
        return result
