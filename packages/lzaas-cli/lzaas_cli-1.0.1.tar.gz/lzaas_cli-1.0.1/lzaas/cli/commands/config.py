#!/usr/bin/env python3
"""
LZaaS CLI Configuration Management
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import click
import yaml
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()


class ConfigManager:
    """Manages LZaaS CLI configuration"""

    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.yaml"
        self.credentials_file = self.config_dir / "credentials.yaml"

    def _get_config_dir(self) -> Path:
        """Get XDG-compliant config directory"""
        if os.name == "nt":  # Windows
            config_home = Path(os.environ.get("APPDATA", "~/.config"))
        else:  # Unix-like
            config_home = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config"))

        config_dir = config_home.expanduser() / "lzaas"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_file.exists():
            return self._get_default_config()

        try:
            with open(self.config_file, "r") as f:
                return yaml.safe_load(f) or self._get_default_config()
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/red]")
            return self._get_default_config()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=True)
            return True
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            return False

    def load_credentials(self) -> Dict[str, Any]:
        """Load credentials from file"""
        if not self.credentials_file.exists():
            return {}

        try:
            with open(self.credentials_file, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            console.print(f"[red]Error loading credentials: {e}[/red]")
            return {}

    def save_credentials(self, credentials: Dict[str, Any]) -> bool:
        """Save credentials to file"""
        try:
            # Set restrictive permissions for credentials file
            with open(self.credentials_file, "w") as f:
                yaml.dump(credentials, f, default_flow_style=False, sort_keys=True)
            os.chmod(self.credentials_file, 0o600)  # Read/write for owner only
            return True
        except Exception as e:
            console.print(f"[red]Error saving credentials: {e}[/red]")
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "general": {
                "default_region": "eu-west-3",
                "output_format": "table",
                "log_level": "INFO",
                "auto_approve": False,
                "aws_profile": "lzaas-mgmt-admin",
            },
            "aft": {
                "management_account_id": "307946641011",
                "aft_management_account_id": "307946641011",
                "ct_management_account_id": "307946641011",
                "log_archive_account_id": "",
                "audit_account_id": "",
                "aft_framework_repo_url": "",
                "aft_framework_repo_git_ref": "",
                "vcs_provider": "github",
                "account_request_repo_name": "sse-landing-zone",
                "global_customizations_repo_name": "",
                "account_customizations_repo_name": "",
                "account_provisioning_customizations_repo_name": "",
            },
            "control_plane": {"type": "aws_aft", "endpoint": "", "region": "eu-west-3"},
            "github": {
                "organization": "Cloud-Cockpit",
                "token": "",  # Will be stored in credentials file
                "workflows_enabled": True,
            },
            "templates": {
                "default_template": "dev",
                "template_validation": True,
                "custom_template_path": "",
            },
        }


config_manager = ConfigManager()


@click.group()
def config():
    """Manage LZaaS CLI configuration and credentials"""
    pass


@config.command()
def init():
    """Initialize LZaaS CLI configuration interactively"""
    console.print("[bold cyan]🔧 LZaaS CLI Configuration Setup[/bold cyan]")
    console.print("─" * 60)

    current_config = config_manager.load_config()
    current_creds = config_manager.load_credentials()

    # General settings
    console.print("\n[bold yellow]General Settings[/bold yellow]")
    current_config["general"]["default_region"] = Prompt.ask(
        "Default AWS region", default=current_config["general"]["default_region"]
    )

    current_config["general"]["aws_profile"] = Prompt.ask(
        "AWS Profile (for SSO use your SSO profile name)",
        default=current_config["general"]["aws_profile"],
    )

    current_config["general"]["output_format"] = Prompt.ask(
        "Output format",
        choices=["table", "json", "yaml"],
        default=current_config["general"]["output_format"],
    )

    # AWS AFT Configuration
    console.print(
        "\n[bold yellow]AWS Account Factory for Terraform (AFT) Configuration[/bold yellow]"
    )
    current_config["aft"]["management_account_id"] = Prompt.ask(
        "Management Account ID", default=current_config["aft"]["management_account_id"]
    )

    current_config["aft"]["aft_management_account_id"] = Prompt.ask(
        "AFT Management Account ID",
        default=current_config["aft"]["aft_management_account_id"],
    )

    current_config["aft"]["account_request_repo_name"] = Prompt.ask(
        "Account Request Repository Name",
        default=current_config["aft"]["account_request_repo_name"],
    )

    # GitHub Configuration
    console.print("\n[bold yellow]GitHub Integration[/bold yellow]")
    current_config["github"]["organization"] = Prompt.ask(
        "GitHub Organization", default=current_config["github"]["organization"]
    )

    if Confirm.ask("Configure GitHub token for API access?"):
        github_token = Prompt.ask("GitHub Personal Access Token", password=True)
        if github_token:
            current_creds["github"] = {"token": github_token}

    # AWS Credentials
    console.print("\n[bold yellow]AWS Credentials[/bold yellow]")
    console.print(
        "[dim]Note: If using AWS SSO, you can skip this and use your configured profile[/dim]"
    )
    if Confirm.ask("Configure AWS credentials (skip if using SSO)?"):
        aws_access_key = Prompt.ask("AWS Access Key ID")
        aws_secret_key = Prompt.ask("AWS Secret Access Key", password=True)
        aws_session_token = Prompt.ask("AWS Session Token (optional)", default="")

        current_creds["aws"] = {
            "access_key_id": aws_access_key,
            "secret_access_key": aws_secret_key,
        }
        if aws_session_token:
            current_creds["aws"]["session_token"] = aws_session_token

    # Save configuration
    if config_manager.save_config(current_config):
        console.print("\n[green]✅ Configuration saved successfully[/green]")
    else:
        console.print("\n[red]❌ Failed to save configuration[/red]")
        return

    if current_creds and config_manager.save_credentials(current_creds):
        console.print("[green]✅ Credentials saved successfully[/green]")
    elif current_creds:
        console.print("[red]❌ Failed to save credentials[/red]")

    console.print(
        f"\n[blue]📁 Configuration stored in: {config_manager.config_dir}[/blue]"
    )


@config.command()
def show():
    """Show current configuration"""
    config_data = config_manager.load_config()

    console.print("[bold cyan]📋 LZaaS CLI Configuration[/bold cyan]")
    console.print("─" * 60)

    # General settings
    table = Table(title="General Settings")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    for key, value in config_data.get("general", {}).items():
        table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)

    # AFT settings
    console.print("\n")
    aft_table = Table(title="AFT Configuration")
    aft_table.add_column("Setting", style="cyan")
    aft_table.add_column("Value", style="green")

    for key, value in config_data.get("aft", {}).items():
        display_value = str(value) if value else "[dim]Not configured[/dim]"
        aft_table.add_row(key.replace("_", " ").title(), display_value)

    console.print(aft_table)

    # GitHub settings
    console.print("\n")
    github_table = Table(title="GitHub Integration")
    github_table.add_column("Setting", style="cyan")
    github_table.add_column("Value", style="green")

    for key, value in config_data.get("github", {}).items():
        if key == "token":
            continue  # Don't show token in config
        display_value = str(value) if value else "[dim]Not configured[/dim]"
        github_table.add_row(key.replace("_", " ").title(), display_value)

    console.print(github_table)

    # Show credentials status with improved logic
    from lzaas.core.system_checker import system_checker

    aws_status, aws_detail = system_checker.get_aws_auth_status()
    creds = config_manager.load_credentials()

    console.print("\n[bold yellow]Credentials Status:[/bold yellow]")
    console.print(f"AWS Credentials: {aws_status}")
    console.print(f"  └─ {aws_detail}")
    console.print(
        f"GitHub Token: {'✅ Configured' if 'github' in creds else '❌ Not configured'}"
    )

    console.print(f"\n[blue]📁 Config location: {config_manager.config_file}[/blue]")


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str):
    """Set a configuration value"""
    config_data = config_manager.load_config()

    # Parse nested key (e.g., "general.default_region")
    keys = key.split(".")
    current = config_data

    # Navigate to the parent of the target key
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    # Set the value
    final_key = keys[-1]

    # Try to convert value to appropriate type
    if value.lower() in ("true", "false"):
        converted_value: Any = value.lower() == "true"
    elif value.isdigit():
        converted_value = int(value)
    else:
        converted_value = value

    current[final_key] = converted_value

    if config_manager.save_config(config_data):
        console.print(f"[green]✅ Set {key} = {value}[/green]")
    else:
        console.print(f"[red]❌ Failed to set {key}[/red]")


@config.command()
@click.argument("key")
def get(key: str):
    """Get a configuration value"""
    config_data = config_manager.load_config()

    # Parse nested key
    keys = key.split(".")
    current = config_data

    try:
        for k in keys:
            current = current[k]
        console.print(f"[cyan]{key}[/cyan]: [green]{current}[/green]")
    except KeyError:
        console.print(f"[red]❌ Configuration key '{key}' not found[/red]")


@config.command()
def reset():
    """Reset configuration to defaults"""
    if Confirm.ask("Are you sure you want to reset all configuration to defaults?"):
        default_config = config_manager._get_default_config()
        if config_manager.save_config(default_config):
            console.print("[green]✅ Configuration reset to defaults[/green]")
        else:
            console.print("[red]❌ Failed to reset configuration[/red]")


@config.command()
def validate():
    """Validate current configuration"""
    config_data = config_manager.load_config()
    creds = config_manager.load_credentials()

    console.print("[bold cyan]🔍 Configuration Validation[/bold cyan]")
    console.print("─" * 60)

    issues = []

    # Check required AFT settings
    required_aft_fields = [
        "management_account_id",
        "aft_management_account_id",
        "account_request_repo_name",
    ]

    for field in required_aft_fields:
        if not config_data.get("aft", {}).get(field):
            issues.append(f"AFT setting '{field}' is not configured")

    # Check AWS credentials - improved logic for SSO profiles
    from lzaas.core.system_checker import system_checker

    aws_status, aws_detail = system_checker.get_aws_auth_status()
    if "❌" in aws_status:
        issues.append("AWS credentials are not configured or accessible")

    # Check GitHub configuration
    if not config_data.get("github", {}).get("organization"):
        issues.append("GitHub organization is not configured")

    if "github" not in creds:
        issues.append("GitHub token is not configured")

    # Display results
    if issues:
        console.print("[red]❌ Configuration Issues Found:[/red]")
        for issue in issues:
            console.print(f"  • {issue}")
        console.print(
            f"\n[yellow]💡 Run 'lzaas config init' to fix these issues[/yellow]"
        )
    else:
        console.print("[green]✅ Configuration is valid[/green]")


if __name__ == "__main__":
    config()
