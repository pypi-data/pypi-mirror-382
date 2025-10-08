#!/usr/bin/env python3
"""
LZaaS CLI Main Entry Point
Landing Zone as a Service - AWS Account Factory Automation
"""

import os
import sys

import click
from rich import print as rprint
from rich.console import Console
from rich.table import Table

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lzaas import __version__
from lzaas.cli.commands.account import account
from lzaas.cli.commands.config import config
from lzaas.cli.commands.docs import docs
from lzaas.cli.commands.migrate import migrate
from lzaas.cli.commands.status import status
from lzaas.cli.commands.template import template

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--profile", default=None, help="AWS profile to use (overrides config)")
@click.option("--region", default=None, help="AWS region to use (overrides config)")
@click.pass_context
def cli(ctx, verbose, profile, region):
    """
    🚀 LZaaS CLI - Landing Zone as a Service

    Automate AWS Account Factory operations with ease.
    Manage account requests, templates, and monitor AFT workflows.

    Examples:
      lzaas account create --template dev --email dev@company.com
      lzaas account list --client internal
      lzaas status --request-id dev-2025-001
      lzaas template list
    """
    ctx.ensure_object(dict)

    # Load user configuration and apply precedence: CLI args > User config > Spitzkop defaults
    from lzaas.cli.commands.config import config_manager

    user_config = config_manager.load_config()

    # Apply configuration precedence
    final_profile = profile or user_config.get("general", {}).get(
        "aws_profile", "lzaas-mgmt-admin"
    )
    final_region = region or user_config.get("general", {}).get(
        "default_region", "eu-west-3"
    )

    ctx.obj["verbose"] = verbose
    ctx.obj["profile"] = final_profile
    ctx.obj["region"] = final_region
    ctx.obj["user_config"] = user_config

    if verbose:
        console.print(f"[green]✓[/green] Using AWS profile: {final_profile}")
        console.print(f"[green]✓[/green] Using AWS region: {final_region}")
        if profile:
            console.print(f"[dim]  └─ Profile overridden via CLI argument[/dim]")
        elif user_config.get("general", {}).get("aws_profile"):
            console.print(f"[dim]  └─ Profile loaded from user configuration[/dim]")
        else:
            console.print(f"[dim]  └─ Using Spitzkop default profile[/dim]")


@cli.command()
def info():
    """Display LZaaS system information and health status"""
    from lzaas.core.system_checker import system_checker

    console.print("[bold cyan]🔍 Checking system status...[/bold cyan]")

    # Get real-time system status
    status_data = system_checker.get_system_status()
    config_status = system_checker.get_configuration_status()

    table = Table(title="🏗️  LZaaS System Information")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Details", style="white")

    # System info with real-time data
    table.add_row("LZaaS CLI", "✅ Active", f"Version {__version__}")

    # AWS Connectivity
    aws_status, aws_details, aws_color = status_data["aws_connectivity"]
    table.add_row("AWS Connectivity", aws_status, aws_details)

    # AFT Infrastructure
    aft_status, aft_details, aft_color = status_data["aft_infrastructure"]
    table.add_row("AFT Infrastructure", aft_status, aft_details)

    # GitHub Integration
    github_status, github_details, github_color = status_data["github_integration"]
    table.add_row("GitHub Integration", github_status, github_details)

    # DynamoDB
    dynamo_status, dynamo_details, dynamo_color = status_data["dynamodb"]
    table.add_row("DynamoDB", dynamo_status, dynamo_details)

    # Template System
    template_status, template_details, template_color = status_data["template_system"]
    table.add_row("Template System", template_status, template_details)

    console.print(table)

    # Configuration status
    console.print("\n[bold yellow]⚙️  Configuration Status:[/bold yellow]")
    config_table = Table()
    config_table.add_column("Component", style="cyan")
    config_table.add_column("Status", style="green")

    config_table.add_row(
        "General Settings",
        "✅ Configured" if config_status["general_configured"] else "❌ Not configured",
    )
    config_table.add_row(
        "AFT Settings",
        "✅ Configured" if config_status["aft_configured"] else "❌ Not configured",
    )
    config_table.add_row(
        "GitHub Settings",
        "✅ Configured" if config_status["github_configured"] else "❌ Not configured",
    )
    config_table.add_row(
        "AWS Credentials",
        "✅ Configured" if config_status["aws_credentials"] else "❌ Not configured",
    )

    console.print(config_table)

    # Show configuration help if needed
    if not all(config_status.values()):
        console.print(
            "\n[yellow]💡 Run 'lzaas config init' to configure missing settings[/yellow]"
        )

    # Quick start guide
    console.print("\n[bold cyan]🚀 Quick Start:[/bold cyan]")
    console.print("1. [yellow]lzaas config init[/yellow] - Configure LZaaS CLI")
    console.print(
        "2. [yellow]lzaas account create --template dev --email test@company.com[/yellow]"
    )
    console.print("3. [yellow]lzaas status --request-id <request-id>[/yellow]")
    console.print("4. [yellow]lzaas account list[/yellow]")

    console.print("\n[bold cyan]📚 Documentation:[/bold cyan]")
    console.print(
        "• User Guide: [blue]lzaas docs user-guide[/blue] - Complete user documentation"
    )
    console.print(
        "• Quick Reference: [blue]lzaas docs quick-reference[/blue] - Command cheat sheet"
    )
    console.print(
        "• Installation: [blue]lzaas docs installation[/blue] - Setup instructions"
    )
    console.print(
        "• All Docs: [blue]lzaas docs list[/blue] - List all available documentation"
    )


# Add command groups
cli.add_command(account)
cli.add_command(config)
cli.add_command(template)
cli.add_command(status)
cli.add_command(migrate)
cli.add_command(docs)

if __name__ == "__main__":
    cli()
