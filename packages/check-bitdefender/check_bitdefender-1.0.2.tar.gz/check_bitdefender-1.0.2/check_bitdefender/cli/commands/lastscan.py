"""Last scan commands for CLI."""

import sys
from typing import Optional, Any

from check_bitdefender.core.auth import get_token
from check_bitdefender.core.config import load_config
from check_bitdefender.core.defender import DefenderClient
from check_bitdefender.core.nagios import NagiosPlugin
from check_bitdefender.services.lastscan_service import LastScanService
from ..decorators import common_options


def register_lastscan_commands(main_group: Any) -> None:
    """Register lastscan commands with the main CLI group."""

    @main_group.command("lastscan")
    @common_options
    def lastscan_cmd(
        config: str,
        verbose: int,
        endpoint_id: Optional[str],
        dns_name: Optional[str],
        warning: Optional[float],
        critical: Optional[float],
    ) -> None:
        """Check endpoint last scan status in BitDefender GravityZone.

        Checks how many days since the endpoint was last scanned.
        Returns WARNING if not scanned for more than warning days.
        Returns CRITICAL if not scanned for more than critical days or not found.
        """
        # Set default thresholds: warning at 7 days, critical at 30 days
        warning = warning if warning is not None else 7
        critical = critical if critical is not None else 30

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
            service = LastScanService(client, verbose_level=verbose)

            # Create Nagios plugin
            plugin = NagiosPlugin(service, "lastscan")

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