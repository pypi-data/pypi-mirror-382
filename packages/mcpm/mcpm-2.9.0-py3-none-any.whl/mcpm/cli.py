"""
MCPM CLI - Main entry point for the Model Context Protocol Manager CLI
"""

# Import rich-click configuration before anything else
from typing import Any, Dict

from rich.console import Console
from rich.traceback import Traceback
from rich.traceback import install as install_rich_traceback

from mcpm.clients.client_config import ClientConfigManager
from mcpm.commands import (
    client,
    config,
    doctor,
    edit,
    info,
    inspect,
    install,
    list,
    migrate,
    new,
    profile,
    run,
    search,
    uninstall,
    usage,
)
from mcpm.commands.share import share
from mcpm.utils.logging_config import setup_logging
from mcpm.utils.rich_click_config import click, get_header_text
import os
from pathlib import Path

console = Console()          # stdout for regular CLI output
err_console = Console(stderr=True)  # stderr for errors/tracebacks
client_config_manager = ClientConfigManager()

# Setup Rich logging early - this runs when the module is imported
setup_logging()

# Install Rich's global exception handler to use stderr instead of stdout
# This prevents Rich/rich-gradient from routing tracebacks to stdout
install_rich_traceback(console=err_console, show_locals=True)

# Custom context settings to handle main command help specially
CONTEXT_SETTINGS: Dict[str, Any] = dict(help_option_names=[])


def print_logo():
    """Print an elegant gradient logo with invisible Panel for width control"""
    console.print(get_header_text())


def handle_exceptions(func):
    """Decorator to catch unhandled exceptions and provide a helpful error message."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            err_console.print(Traceback(show_locals=True))
            err_console.print("[bold red]An unexpected error occurred.[/bold red]")
            err_console.print(
                "Please report this issue on our GitHub repository: "
                "[link=https://github.com/pathintegral-institute/mcpm.sh/issues]https://github.com/pathintegral-institute/mcpm.sh/issues[/link]"
            )

    return wrapper


@click.group(
    name="mcpm",
    context_settings=CONTEXT_SETTINGS,
    invoke_without_command=True,
    help="""
Centralized MCP server management - discover, install, run, and share servers.

Manage servers globally, organize with profiles, monitor usage, and integrate
with all MCP clients.
""",
)
@click.option("-v", "--version", is_flag=True, help="Show version and exit.")
@click.option("-h", "--help", "help_flag", is_flag=True, help="Show this message and exit.")
@click.pass_context
@handle_exceptions
def main(ctx, version, help_flag):
    """Main entry point for MCPM CLI."""

    try:
        # Check if the current working directory is valid.
        os.getcwd()
    except OSError:
        # If getcwd() fails, it means the directory doesn't exist.
        # This can happen when mcpm is called from certain environments
        # like some Electron apps that don't set a valid cwd.
        home_dir = str(Path.home())
        err_console.print(
            f"Current working directory is invalid. Changing to home directory: {home_dir}",
            style="bold yellow"
        )
        os.chdir(home_dir)

    if version:
        print_logo()
        return

    if help_flag:
        # Show custom help with header and footer for main command only
        console.print(get_header_text())
        # Temporarily disable global footer to avoid duplication
        original_footer = click.rich_click.FOOTER_TEXT
        click.rich_click.FOOTER_TEXT = None
        click.echo(ctx.get_help())
        click.rich_click.FOOTER_TEXT = original_footer
        return

    # If no command was invoked, show help with header and footer
    if ctx.invoked_subcommand is None:
        console.print(get_header_text())
        # Temporarily disable global footer to avoid duplication
        original_footer = click.rich_click.FOOTER_TEXT
        click.rich_click.FOOTER_TEXT = None
        click.echo(ctx.get_help())
        click.rich_click.FOOTER_TEXT = original_footer


# Register v2.0 commands
main.add_command(search.search)
main.add_command(info.info)
main.add_command(list.list, name="ls")
main.add_command(install.install)
main.add_command(uninstall.uninstall)
main.add_command(edit.edit)
main.add_command(new.new)
main.add_command(run.run)
main.add_command(inspect.inspect)
main.add_command(profile.profile, name="profile")
main.add_command(doctor.doctor)
main.add_command(usage.usage)
main.add_command(config.config)
main.add_command(migrate.migrate)
main.add_command(share)


# Keep these for now but they could be simplified later
main.add_command(client.client)

if __name__ == "__main__":
    main()
