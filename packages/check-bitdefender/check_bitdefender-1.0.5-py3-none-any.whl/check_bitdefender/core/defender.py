"""BitDefender GravityZone API client."""

import base64
import time
import requests
from typing import Any, Dict, Optional, cast
from check_bitdefender.core.exceptions import DefenderAPIError
from check_bitdefender.core.logging_config import get_verbose_logger

class DefenderClient:
    """Client for BitDefender GravityZone API."""

    application_json = "application/json"

    def __init__(
        self,
        authenticator: Any,
        timeout: int = 15,
        region: str = "api",
        verbose_level: int = 0,
        parent_id: Optional[str] = None,
    ) -> None:
        """Initialize with authenticator and optional region.

        Args:
            authenticator: Authentication provider (API token string)
            timeout: Request timeout in seconds
            region: Geographic region (api)
            verbose_level: Verbosity level for logging
            parent_id: Optional parent node ID to filter endpoints
        """
        self.authenticator = authenticator
        self.timeout = timeout
        self.region = region
        self.parent_id = parent_id
        self.base_url = self._get_base_url(region)
        self.logger = get_verbose_logger(__name__, verbose_level)

    def _get_base_url(self, region: str) -> str:
        """Get base URL for the specified region."""
        endpoints = {
            "api": "https://cloudgz.gravityzone.bitdefender.com",
        }
        return endpoints.get(region, endpoints["api"])

    def _get_auth_header(self) -> str:
        """Get authentication header value.

        Returns:
            Basic authentication header value
        """
        encoded = base64.b64encode((self.authenticator + ":").encode()).decode()
        return f"Basic {encoded}"

    def list_endpoints(self, parent_id: Optional[str] = None) -> Dict[str, Any]:
        """List all endpoints from BitDefender GravityZone.

        Uses the JSONRPC API endpoint to retrieve the list of all endpoints
        managed by BitDefender GravityZone. Automatically handles pagination
        to retrieve all endpoints.

        Args:
            parent_id: Optional parent node ID to filter endpoints.
                      If not provided, uses the parent_id from client initialization.

        Returns:
            Dictionary containing endpoint list with structure:
            {
                "value": [
                    {
                        "id": "endpoint_id",
                        "fqdn": "hostname.domain.com",
                        "onboardingStatus": "Onboarded|InsufficientInfo|Unsupported",
                        "osPlatform": "Windows|Linux|Mac",
                        ...
                    },
                    ...
                ]
            }

        Raises:
            DefenderAPIError: If the API request fails
        """
        self.logger.method_entry("list_endpoints")
        start_time = time.time()

        url = f"{self.base_url}/api/v1.0/jsonrpc/network"
        headers = {
            "Content-Type": self.application_json,
            "Authorization": self._get_auth_header()
        }

        # Use provided parent_id or fall back to instance parent_id
        effective_parent_id = parent_id or self.parent_id

        all_items = []
        page = 1
        per_page = 100  # Maximum items per page for better performance
        total_pages = None

        if effective_parent_id:
            self.logger.info(f"Requesting endpoints list from {url} (parent_id: {effective_parent_id})")
        else:
            self.logger.info(f"Requesting endpoints list from {url}")

        try:
            while True:
                # Prepare JSONRPC request with pagination

                payload = {
                   "params": {
                       "parentId": effective_parent_id,
                       "page": 1,
                       "perPage": 100,
                       "filters": {
                           "type": {
                               "computers": True,
                               "virtualMachines": True
                           },
                           "depth": {
                               "allItemsRecursively": True
                           }
                       },
                       "options": {
                           "companies": {
                               "returnAllProducts": True
                           },
                           "endpoints": {
                               "returnProductOutdated": True,
                               "includeScanLogs": True
                           }
                       }
                   },
                   "jsonrpc": "2.0",
                   "method": "getNetworkInventoryItems",
                   "id": "301f7b05-ec02-481b-9ed6-c07b97de2b7b"
              }



                self.logger.debug(f"Request method: {payload['method']}, page: {page}/{total_pages or '?'}")

                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                    verify=True
                )
                response.raise_for_status()

                data = response.json()

                # Extract items from JSONRPC response
                if "result" not in data:
                    raise DefenderAPIError("Invalid API response: missing 'result' field")

                result = data["result"]
                items = result.get("items", [])

                # Get pagination info
                if total_pages is None:
                    total_pages = result.get("pagesCount", 1)
                    total_items = result.get("total", 0)
                    self.logger.info(f"Total endpoints: {total_items}, pages: {total_pages}")

                # Add items to collection
                all_items.extend(items)
                self.logger.debug(f"Retrieved {len(items)} items from page {page}, total so far: {len(all_items)}")

                # Check if we've retrieved all pages
                if page >= total_pages:
                    break

                page += 1

            elapsed_time = time.time() - start_time
            self.logger.info(f"API request completed in {elapsed_time:.2f}s, retrieved {len(all_items)} endpoints")

            # Transform to match expected format
            transformed_response = {
                "value": [
                    {
                        "id": item.get("id"),
                        "fqdn": item.get("details", {}).get("fqdn") or item.get("fqdn") or item.get("name", ""),
                        "onboardingStatus": self._map_managed_status(item.get("details", {}).get("isManaged")),
                        "osPlatform": self._extract_os_platform(item.get("details", {}).get("operatingSystemVersion", "")),
                        # Try lastSeen first, fall back to lastSuccessfulScan.date
                        "lastSeen": item.get("lastSeen") or item.get("lastSuccessfulScan", {}).get("date"),
                    }
                    for item in all_items
                ]
            }

            self.logger.method_exit("list_endpoints", f"{len(transformed_response['value'])} endpoints")
            return transformed_response

        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"API request failed after {elapsed_time:.2f}s: {str(e)}")
            raise DefenderAPIError(f"Failed to list endpoints: {str(e)}")

    def _map_managed_status(self, is_managed: bool) -> str:
        """Map isManaged boolean to onboarding status string.

        Args:
            is_managed: Whether the endpoint is managed

        Returns:
            Onboarding status string
        """
        return "Onboarded" if is_managed else "InsufficientInfo"

    def _extract_os_platform(self, os_version: str) -> str:
        """Extract OS platform from version string.

        Args:
            os_version: Operating system version string

        Returns:
            Platform name (Windows, Linux, Mac, or Unknown)
        """
        os_lower = os_version.lower()
        if "windows" in os_lower:
            return "Windows"
        elif "linux" in os_lower:
            return "Linux"
        elif "mac" in os_lower or "darwin" in os_lower:
            return "Mac"
        else:
            return "Unknown"

    def get_endpoint_details(self, endpoint_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific endpoint.

        Args:
            endpoint_id: The endpoint ID to retrieve details for

        Returns:
            Dictionary containing endpoint details with structure:
            {
                "id": "endpoint_id",
                "name": "hostname",
                "operatingSystem": "OS name",
                "lastSeen": "2015-06-22T13:46:59",
                "lastSuccessfulScan": {
                    "name": "scan_name",
                    "date": "2023-07-19T04:09:29+00:00"
                },
                "malwareStatus": {
                    "detection": false,
                    "infected": false
                },
                "riskScore": {
                    "value": "81%"
                }
            }

        Raises:
            DefenderAPIError: If the API request fails
        """
        self.logger.method_entry("get_endpoint_details", endpoint_id=endpoint_id)
        start_time = time.time()

        url = f"{self.base_url}/api/v1.0/jsonrpc/network"
        headers = {
            "Content-Type": self.application_json,
            "Authorization": self._get_auth_header()
        }

        payload = {
            "params": {
                "endpointId": endpoint_id,
                "options": {
                    "includeScanLogs": True
                }
            },
            "jsonrpc": "2.0",
            "method": "getManagedEndpointDetails",
            "id": f"check_bitdefender_details_{endpoint_id}"
        }

        self.logger.info(f"Requesting endpoint details from {url} (endpoint_id: {endpoint_id})")
        self.logger.debug(f"Request method: {payload['method']}")

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
                verify=True
            )
            response.raise_for_status()

            data = response.json()

            # Extract result from JSONRPC response
            if "result" not in data:
                raise DefenderAPIError("Invalid API response: missing 'result' field")

            result = data["result"]
            elapsed_time = time.time() - start_time
            self.logger.info(f"API request completed in {elapsed_time:.2f}s")
            self.logger.method_exit("get_endpoint_details", "success")

            return cast(Dict[str, Any], result)

        except requests.exceptions.RequestException as e:
            elapsed_time = time.time() - start_time
            self.logger.error(f"API request failed after {elapsed_time:.2f}s: {str(e)}")
            raise DefenderAPIError(f"Failed to get endpoint details: {str(e)}")
