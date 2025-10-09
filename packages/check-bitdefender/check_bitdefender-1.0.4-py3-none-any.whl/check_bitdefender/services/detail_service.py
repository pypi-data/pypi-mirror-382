"""Detail service implementation."""

from typing import Dict, Any, Optional, List, TYPE_CHECKING
from check_bitdefender.core.logging_config import get_verbose_logger

if TYPE_CHECKING:
    from check_bitdefender.core.defender import DefenderClient


class DetailService:
    """Service for getting detailed endpoint information."""

    def __init__(self, defender_client: "DefenderClient", verbose_level: int = 0) -> None:
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
        """Get detailed information for an endpoint.

        Returns a numeric value indicating if the endpoint was found:
        - 0: Not found
        - 1: Found

        Args:
            endpoint_id: Optional endpoint ID to check
            dns_name: Optional DNS name to check

        Returns:
            Dictionary with:
            - value: 1 if found, 0 if not found
            - details: List of detail strings for verbose output
        """
        self.logger.method_entry("get_result", endpoint_id=endpoint_id, dns_name=dns_name)

        if not endpoint_id and not dns_name:
            raise ValueError("Either endpoint_id or dns_name must be provided")

        # First, find the endpoint to get its ID if dns_name was provided
        if not endpoint_id:
            self.logger.info(f"Looking up endpoint by DNS name: {dns_name}")
            endpoints_data = self.defender.list_endpoints()

            if not endpoints_data.get("value"):
                self.logger.info("No endpoints found in system")
                result = {
                    "value": 0,  # Not found
                    "details": [f"Host not found ({dns_name})"],
                }
                self.logger.method_exit("get_result", result)
                return result

            # Find matching endpoint by DNS name
            matching_endpoint = None
            for endpoint in endpoints_data["value"]:
                if endpoint.get("fqdn") == dns_name:
                    matching_endpoint = endpoint
                    endpoint_id = endpoint.get("id")
                    break

            if not matching_endpoint or not endpoint_id:
                self.logger.info(f"Endpoint not found: {dns_name}")
                result = {
                    "value": 0,  # Not found
                    "details": [f"Host not found ({dns_name})"],
                }
                self.logger.method_exit("get_result", result)
                return result

        # Get detailed information about the endpoint
        self.logger.info(f"Fetching details for endpoint: {endpoint_id}")
        try:
            details_data = self.defender.get_endpoint_details(endpoint_id)
        except Exception as e:
            self.logger.error(f"Failed to get endpoint details: {str(e)}")
            result = {
                "value": 0,  # Not found/error
                "details": [f"Failed to get endpoint details: {str(e)}"],
            }
            self.logger.method_exit("get_result", result)
            return result

        # Extract relevant information
        endpoint_id_str = details_data.get("id", "N/A")
        name = details_data.get("name", dns_name or "N/A")
        operating_system = details_data.get("operatingSystem", "N/A")

        # Extract last successful scan
        last_scan_data = details_data.get("lastSuccessfulScan", {})
        last_scan = last_scan_data.get("date", "N/A") if last_scan_data else "N/A"

        # Use lastSuccessfulScan.date for lastSeen (same as list_endpoints)
        last_seen = last_scan

        # Extract malware status
        malware_status = details_data.get("malwareStatus", {})
        malware_detection = str(malware_status.get("detection", False)).lower()
        malware_infected = str(malware_status.get("infected", False)).lower()

        # Extract risk score
        risk_score_data = details_data.get("riskScore", {})
        risk_score = risk_score_data.get("value", "N/A") if risk_score_data else "N/A"

        # Build detail output
        detail_lines: List[str] = [
            f"Host found ({name})",
            f"id: {endpoint_id_str}",
            f"name: {name}",
            f"operatingSystem: {operating_system}",
            f"lastSeen: {last_seen}",
            f"lastSuccessfulScan: {last_scan}",
            f"malwareStatus_detection: {malware_detection}",
            f"malwareStatus_infected: {malware_infected}",
            f"riskScore: {risk_score}",
        ]

        self.logger.info(f"Endpoint found: {name}")
        result = {
            "value": 1,  # Found
            "details": detail_lines,
        }

        self.logger.method_exit("get_result", result)
        return result