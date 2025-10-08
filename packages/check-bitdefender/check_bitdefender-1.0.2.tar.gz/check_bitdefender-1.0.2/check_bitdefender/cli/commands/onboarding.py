"""Onboarding status commands for CLI."""

import sys
from typing import Optional, Any

from check_bitdefender.core.auth import get_token
from check_bitdefender.core.config import load_config
from check_bitdefender.core.defender import DefenderClient
from check_bitdefender.core.nagios import NagiosPlugin
from check_bitdefender.services.onboarding_service import OnboardingService
from ..decorators import common_options


def register_onboarding_commands(main_group: Any) -> None:
    """Register onboarding commands with the main CLI group."""

    @main_group.command("onboarding")
    @common_options
    def onboarding_cmd(
        config: str,
        verbose: int,
        endpoint_id: Optional[str],
        dns_name: Optional[str],
        warning: Optional[float],
        critical: Optional[float],
    ) -> None:
        """Check endpoint onboarding status in BitDefender GravityZone.

        Verifies if an endpoint is properly onboarded to BitDefender.
        Returns CRITICAL if endpoint not found or not onboarded.
        """
        # Set default thresholds: value=1 means not found/not onboarded (CRITICAL)
        # Use warning=2 (never triggered) and critical=1 (triggers on not found)
        warning = warning if warning is not None else 2
        critical = critical if critical is not None else 1

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
            service = OnboardingService(client, verbose_level=verbose)

            # Create Nagios plugin
            plugin = NagiosPlugin(service, "onboarding")

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
