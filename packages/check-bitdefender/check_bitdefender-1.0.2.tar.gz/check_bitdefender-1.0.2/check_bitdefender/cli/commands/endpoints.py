"""List endpoints commands for CLI."""

import sys
from typing import Optional, Any

from check_bitdefender.core.auth import get_token
from check_bitdefender.core.config import load_config
from check_bitdefender.core.defender import DefenderClient
from check_bitdefender.core.nagios import NagiosPlugin
from check_bitdefender.services.endpoint_service import EndpointsService
from ..decorators import common_options


def register_endpoints_commands(main_group: Any) -> None:
    """Register list endpoints commands with the main CLI group."""

    @main_group.command("endpoints")
    @common_options
    def endpoints_cmd(
        config: str,
        verbose: int,
        endpoint_id: Optional[str],
        dns_name: Optional[str],
        warning: Optional[float],
        critical: Optional[float],
    ) -> None:
        """List all endpoints in BitDefender GravityZone for Endpoint."""
        warning = warning if warning is not None else 10
        critical = critical if critical is not None else 25

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
            service = EndpointsService(client, verbose_level=verbose)

            # Create Nagios plugin
            plugin = NagiosPlugin(service, "endpoints")

            # Execute check
            result = plugin.check(warning=warning, critical=critical, verbose=verbose)

            sys.exit(result or 0)

        except Exception as e:
            print(f"UNKNOWN: {str(e)}")
            sys.exit(3)
