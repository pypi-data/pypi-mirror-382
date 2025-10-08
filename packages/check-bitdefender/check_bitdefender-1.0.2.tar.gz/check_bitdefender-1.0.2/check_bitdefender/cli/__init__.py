"""CLI module for check_bitdefender."""

import click
from .commands import register_all_commands


@click.group()
@click.version_option()
def main() -> None:
    """Check BitDefender GravityZone API endpoints and validate values."""
    pass


# Register all commands
register_all_commands(main)
