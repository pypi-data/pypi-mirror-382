"""Last scan service implementation."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
from check_bitdefender.core.logging_config import get_verbose_logger


class LastScanService:
    """Service for checking endpoint last scan status."""

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
        """Check last scan status for an endpoint.

        Returns the number of days since the endpoint was last scanned.
        - 999: Endpoint not found
        - N: Number of days since last scan

        Args:
            endpoint_id: Optional endpoint ID to check
            dns_name: Optional DNS name to check

        Returns:
            Dictionary with:
            - value: Days since last scan (999 if not found)
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
                "value": 999,  # Not found
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
            elif dns_name and endpoint.get("fqdn") == dns_name:
                matching_endpoint = endpoint
                break

        if not matching_endpoint:
            self.logger.info(f"Endpoint not found: {dns_name or endpoint_id}")
            result = {
                "value": 999,  # Not found
                "details": [f"Host not found ({dns_name or endpoint_id})"],
            }
            self.logger.method_exit("get_result", result)
            return result


        endpoint_id = matching_endpoint["id"]
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

        # Calculate days since last scan
        computer_name = matching_endpoint.get("fqdn", dns_name or endpoint_id)

        # Get last successful scan data from details
        last_scan_data = details_data.get("lastSuccessfulScan")
        if not last_scan_data or not isinstance(last_scan_data, dict):
            self.logger.info(f"Endpoint has no last scan data: {computer_name}")
            result = {
                "value": 999,  # No last scan data
                "details": [
                    f"Host found but no last scan data ({computer_name})",
                    "Endpoint may never have been scanned"
                ],
            }
            self.logger.method_exit("get_result", result)
            return result

        last_scan_date = last_scan_data.get("date")

        if not last_scan_date:
            self.logger.info(f"Endpoint has no last scan date: {computer_name}")
            result = {
                "value": 999,  # No last scan data
                "details": [
                    f"Host found but no last scan date ({computer_name})",
                    "Endpoint may never have been scanned"
                ],
            }
            self.logger.method_exit("get_result", result)
            return result

        try:
            # Parse the last scan date (ISO format timestamp)
            if isinstance(last_scan_date, str):
                # Handle ISO format: "2024-01-15T10:30:00Z" or "2024-01-15T10:30:00"
                last_scan_dt = datetime.fromisoformat(last_scan_date.replace('Z', '+00:00'))
                # If datetime is naive (no timezone), assume UTC
                if last_scan_dt.tzinfo is None:
                    last_scan_dt = last_scan_dt.replace(tzinfo=timezone.utc)
            else:
                # If it's already a datetime object or timestamp
                last_scan_dt = datetime.fromtimestamp(last_scan_date, tz=timezone.utc)

            # Calculate days difference
            now = datetime.now(timezone.utc)
            days_diff = (now - last_scan_dt).days

            self.logger.info(f"Endpoint {computer_name} last scanned {days_diff} days ago")

            result = {
                "value": days_diff,
                "details": [f"Host last scanned {days_diff} days ago ({computer_name})"],
            }

        except (ValueError, AttributeError, TypeError) as e:
            self.logger.error(f"Failed to parse last scan date: {last_scan_date}, error: {e}")
            result = {
                "value": 999,  # Parse error treated as unknown
                "details": [
                    f"Host found but unable to parse last scan date ({computer_name})",
                    f"Last scan value: {last_scan_date}"
                ],
            }

        self.logger.method_exit("get_result", result)
        return result