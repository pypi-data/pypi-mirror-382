"""Detail commands for CLI."""

import sys
from typing import Optional, Any

from check_bitdefender.core.auth import get_token
from check_bitdefender.core.config import load_config
from check_bitdefender.core.defender import DefenderClient
from check_bitdefender.core.nagios import NagiosPlugin
from check_bitdefender.services.detail_service import DetailService
from ..decorators import common_options


def register_detail_commands(main_group: Any) -> None:
    """Register detail commands with the main CLI group."""

    @main_group.command("detail")
    @common_options
    def detail_cmd(
        config: str,
        verbose: int,
        endpoint_id: Optional[str],
        dns_name: Optional[str],
        warning: Optional[float],
        critical: Optional[float],
    ) -> None:
        """Get detailed information about an endpoint in BitDefender GravityZone.

        Retrieves comprehensive endpoint details including OS, malware status, and risk score.
        Returns OK if endpoint is found, CRITICAL if not found.
        """
        # Set default thresholds: value=1 means found (OK), value=0 means not found (CRITICAL)
        # Use warning=0 (triggers on not found) and critical=0 (triggers on not found)
        warning = warning if warning is not None else 0
        critical = critical if critical is not None else 0

        try:
            # Load configuration
            cfg = load_config(config)

            # Get authenticator
            authenticator = get_token(cfg)

            # Get parent_id from config if available
            parent_id = None
            if cfg.has_section("settings"):
                parent_id = cfg["settings"].get("parent_id")

            # Create Defender client
            client = DefenderClient(authenticator, verbose_level=verbose, parent_id=parent_id)

            # Create the service
            service = DetailService(client, verbose_level=verbose)

            # Create Nagios plugin
            plugin = NagiosPlugin(service, "detail")

            # Execute check
            result = plugin.check(
                endpoint_id=endpoint_id,
                dns_name=dns_name,
                warning=warning,
                critical=critical,
                verbose=verbose
            )

            sys.exit(result or 0)

        except Exception as e:
            print(f"UNKNOWN: {str(e)}")
            sys.exit(3)
