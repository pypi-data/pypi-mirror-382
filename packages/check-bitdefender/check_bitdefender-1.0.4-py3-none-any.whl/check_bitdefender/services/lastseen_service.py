"""Last seen service implementation."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from check_bitdefender.core.logging_config import get_verbose_logger


class LastSeenService:
    """Service for checking endpoint last seen status."""

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
        """Check last seen status for an endpoint.

        Returns the number of days since the endpoint was last seen.
        - 999: Endpoint not found
        - N: Number of days since last seen

        Args:
            endpoint_id: Optional endpoint ID to check
            dns_name: Optional DNS name to check

        Returns:
            Dictionary with:
            - value: Days since last seen (999 if not found)
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

        # Calculate days since last seen
        computer_name = matching_endpoint.get("fqdn", dns_name or endpoint_id)
        last_seen_date = details_data.get("lastSeen")

        if not last_seen_date:
            self.logger.info(f"Endpoint has no last seen date: {computer_name}")
            result = {
                "value": 999,  # No last seen data
                "details": [
                    f"Host found but no last seen data ({computer_name})",
                    "Endpoint may never have been scanned"
                ],
            }
            self.logger.method_exit("get_result", result)
            return result

        try:
            # Parse the last seen date (ISO format timestamp)
            if isinstance(last_seen_date, str):
                # Handle ISO format: "2024-01-15T10:30:00Z" or "2024-01-15T10:30:00"
                last_seen_dt = datetime.fromisoformat(last_seen_date.replace('Z', '+00:00'))
                # If datetime is naive (no timezone), assume local timezone (+2)
                if last_seen_dt.tzinfo is None:
                    local_tz = timezone(timedelta(hours=2))
                    last_seen_dt = last_seen_dt.replace(tzinfo=local_tz)
            else:
                # If it's already a datetime object or timestamp
                local_tz = timezone(timedelta(hours=2))
                last_seen_dt = datetime.fromtimestamp(last_seen_date, tz=local_tz)

            # Calculate days difference using local timezone
            local_tz = timezone(timedelta(hours=2))
            now = datetime.now(local_tz)
            days_diff = (now - last_seen_dt).days

            self.logger.info(f"Endpoint {computer_name} last seen {days_diff} days ago")

            result = {
                "value": days_diff,
                "details": [f"Host last seen {days_diff} days ago ({computer_name})"],
            }

        except (ValueError, AttributeError, TypeError) as e:
            self.logger.error(f"Failed to parse last seen date: {last_seen_date}, error: {e}")
            result = {
                "value": 999,  # Parse error treated as unknown
                "details": [
                    f"Host found but unable to parse last seen date ({computer_name})",
                    f"Last seen value: {last_seen_date}"
                ],
            }

        self.logger.method_exit("get_result", result)
        return result
