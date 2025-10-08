"""
Account Management Commands
Handle AWS account creation, listing, and lifecycle operations
"""

import json
import uuid
from datetime import datetime

import click
from rich import print as rprint
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from lzaas.core.aft_manager import AFTManager
from lzaas.core.models import AccountRequest
from lzaas.utils.validators import validate_account_name, validate_email

console = Console()


@click.group()
def account():
    """Manage AWS account requests and lifecycle"""
    pass


@account.command()
@click.option(
    "--template",
    "-t",
    required=True,
    type=click.Choice(["dev", "prod", "sandbox", "client"]),
    help="Account template to use",
)
@click.option("--email", "-e", required=True, help="Account email address")
@click.option("--name", "-n", help="Account name (auto-generated if not provided)")
@click.option("--client-id", "-c", default="internal", help="Client identifier")
@click.option("--ou", default="Development", help="Organizational Unit")
@click.option("--vpc-cidr", default="10.1.0.0/16", help="VPC CIDR block")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be created without executing"
)
@click.pass_context
def create(ctx, template, email, name, client_id, ou, vpc_cidr, dry_run):
    """Create a new AWS account request"""

    # Validate inputs
    if not validate_email(email):
        console.print("[red]❌ Invalid email address format[/red]")
        return

    # Auto-generate name if not provided
    if not name:
        timestamp = datetime.now().strftime("%Y%m%d")
        name = f"{template.title()} Account {timestamp}"

    if not validate_account_name(name):
        console.print("[red]❌ Invalid account name format[/red]")
        return

    # Generate request ID
    request_id = (
        f"{template}-{datetime.now().strftime('%Y-%m-%d')}-{str(uuid.uuid4())[:8]}"
    )

    # Create account request object
    account_request = AccountRequest(
        request_id=request_id,
        template=template,
        email=email,
        name=name,
        client_id=client_id,
        ou=ou,
        vpc_cidr=vpc_cidr,
        requested_by=ctx.obj.get("profile", "unknown"),
        status="pending",
    )

    # Display what will be created
    console.print(f"\n[bold cyan]📋 Account Request Summary[/bold cyan]")

    table = Table()
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Request ID", request_id)
    table.add_row("Template", template)
    table.add_row("Account Email", email)
    table.add_row("Account Name", name)
    table.add_row("Client ID", client_id)
    table.add_row("Organizational Unit", ou)
    table.add_row("VPC CIDR", vpc_cidr)
    table.add_row("Status", "pending")

    console.print(table)

    if dry_run:
        console.print("\n[yellow]🔍 Dry run mode - no changes will be made[/yellow]")
        return

    # Confirm creation
    if not Confirm.ask("\n[bold]Create this account request?[/bold]"):
        console.print("[yellow]❌ Account request cancelled[/yellow]")
        return

    try:
        # Initialize AFT manager
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        # Create the account request
        console.print("\n[yellow]⏳ Creating account request...[/yellow]")
        result = aft_manager.create_account_request(account_request)

        if result["success"]:
            console.print(f"[green]✅ Account request created successfully![/green]")
            console.print(f"[green]📝 Request ID: {request_id}[/green]")
            console.print(
                f"[blue]💡 Track progress with: lzaas status --request-id {request_id}[/blue]"
            )
        else:
            console.print(
                f"[red]❌ Failed to create account request: {result['error']}[/red]"
            )

    except Exception as e:
        console.print(f"[red]❌ Error creating account request: {str(e)}[/red]")


@account.command()
@click.option("--client-id", "-c", help="Filter by client ID")
@click.option("--status", "-s", help="Filter by status")
@click.option("--limit", "-l", default=20, help="Maximum number of results")
@click.pass_context
def list(ctx, client_id, status, limit):
    """List account requests"""

    try:
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        console.print("[yellow]⏳ Fetching account requests...[/yellow]")

        # Get account requests
        requests = aft_manager.list_account_requests(
            client_id=client_id, status=status, limit=limit
        )

        if not requests:
            console.print("[yellow]📭 No account requests found[/yellow]")
            return

        # Display results in table
        table = Table(title=f"🏗️  Account Requests ({len(requests)} found)")
        table.add_column("Request ID", style="cyan", no_wrap=True)
        table.add_column("Template", style="blue")
        table.add_column("Account Name", style="white")
        table.add_column("Client", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Created", style="dim")

        for req in requests:
            status_emoji = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌",
            }.get(req.get("status", "unknown"), "❓")

            table.add_row(
                req.get("request_id", "N/A"),
                req.get("template", "N/A"),
                req.get("account_name", "N/A"),
                req.get("client_id", "N/A"),
                f"{status_emoji} {req.get('status', 'unknown')}",
                req.get("created_date", "N/A"),
            )

        console.print(table)

        # Show summary
        console.print(
            f"\n[dim]💡 Use 'lzaas status --request-id <id>' for detailed status[/dim]"
        )

    except Exception as e:
        console.print(f"[red]❌ Error listing account requests: {str(e)}[/red]")


@account.command()
@click.option("--request-id", "-r", required=True, help="Account request ID")
@click.pass_context
def delete(ctx, request_id):
    """Delete an account request (only if not yet processed)"""

    try:
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        # Get request details first
        console.print(f"[yellow]⏳ Checking request {request_id}...[/yellow]")
        request_details = aft_manager.get_account_request(request_id)

        if not request_details:
            console.print(f"[red]❌ Request {request_id} not found[/red]")
            return

        # Check if request can be deleted
        status = request_details.get("status", "unknown")
        if status not in ["pending", "failed"]:
            console.print(f"[red]❌ Cannot delete request with status '{status}'[/red]")
            console.print(
                "[yellow]💡 Only pending or failed requests can be deleted[/yellow]"
            )
            return

        # Show request details
        console.print(f"\n[bold red]⚠️  Delete Account Request[/bold red]")
        console.print(f"Request ID: {request_id}")
        console.print(f"Account Name: {request_details.get('account_name', 'N/A')}")
        console.print(f"Status: {status}")

        # Confirm deletion
        if not Confirm.ask(
            "\n[bold red]Are you sure you want to delete this request?[/bold red]"
        ):
            console.print("[yellow]❌ Deletion cancelled[/yellow]")
            return

        # Delete the request
        console.print("[yellow]⏳ Deleting account request...[/yellow]")
        result = aft_manager.delete_account_request(request_id)

        if result["success"]:
            console.print(
                f"[green]✅ Account request {request_id} deleted successfully[/green]"
            )
        else:
            console.print(f"[red]❌ Failed to delete request: {result['error']}[/red]")

    except Exception as e:
        console.print(f"[red]❌ Error deleting account request: {str(e)}[/red]")


@account.command()
@click.option(
    "--template",
    "-t",
    type=click.Choice(["dev", "prod", "sandbox", "client"]),
    help="Show template details",
)
def templates(template):
    """List available account templates"""

    templates_info = {
        "dev": {
            "name": "Development Account",
            "description": "Standard development environment with basic resources",
            "ou": "Development",
            "vpc_cidr": "10.1.0.0/16",
            "features": ["VPC Flow Logs", "CloudTrail", "Basic Monitoring"],
            "cost_estimate": "$50-100/month",
        },
        "prod": {
            "name": "Production Account",
            "description": "Production environment with enhanced security and monitoring",
            "ou": "Production",
            "vpc_cidr": "10.2.0.0/16",
            "features": ["Enhanced Monitoring", "Backup Policies", "Security Controls"],
            "cost_estimate": "$200-500/month",
        },
        "sandbox": {
            "name": "Sandbox Account",
            "description": "Experimental environment with minimal restrictions",
            "ou": "Sandbox",
            "vpc_cidr": "10.3.0.0/16",
            "features": ["Basic Resources", "Auto-cleanup Policies"],
            "cost_estimate": "$20-50/month",
        },
        "client": {
            "name": "Client Account",
            "description": "Customizable account for external clients",
            "ou": "Clients",
            "vpc_cidr": "10.4.0.0/16",
            "features": ["Client Isolation", "Custom Branding", "Dedicated Support"],
            "cost_estimate": "$100-300/month",
        },
    }

    if template:
        # Show specific template details
        if template not in templates_info:
            console.print(f"[red]❌ Template '{template}' not found[/red]")
            return

        info = templates_info[template]
        console.print(f"\n[bold cyan]📋 Template: {info['name']}[/bold cyan]")
        console.print(f"Description: {info['description']}")
        console.print(f"Organizational Unit: {info['ou']}")
        console.print(f"Default VPC CIDR: {info['vpc_cidr']}")
        console.print(f"Cost Estimate: {info['cost_estimate']}")

        console.print(f"\n[bold]Features:[/bold]")
        for feature in info["features"]:
            console.print(f"  • {feature}")

        console.print(
            f"\n[dim]💡 Create account: lzaas account create --template {template} --email your@email.com[/dim]"
        )
    else:
        # Show all templates
        table = Table(title="🏗️  Available Account Templates")
        table.add_column("Template", style="cyan", no_wrap=True)
        table.add_column("Name", style="white")
        table.add_column("OU", style="blue")
        table.add_column("Cost Estimate", style="green")
        table.add_column("Description", style="dim")

        for template_id, info in templates_info.items():
            table.add_row(
                template_id,
                info["name"],
                info["ou"],
                info["cost_estimate"],
                info["description"],
            )

        console.print(table)
        console.print(
            f"\n[dim]💡 Use 'lzaas account templates --template <name>' for details[/dim]"
        )


@account.command()
@click.option("--account-name", help="Specific account name to check status for")
@click.option("--ou", help="Filter by Organizational Unit (e.g., Sandbox)")
@click.pass_context
def status(ctx, account_name, ou):
    """Check status of accounts and account requests"""

    try:
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        console.print("[yellow]⏳ Checking account status...[/yellow]")

        if account_name:
            # Check specific account
            console.print(f"\n[bold cyan]📋 Account Status: {account_name}[/bold cyan]")

            # Mock data for demonstration - replace with actual AFT queries
            if account_name.upper() == "SPITZKOP":
                table = Table()
                table.add_column("Field", style="cyan", no_wrap=True)
                table.add_column("Value", style="white")

                table.add_row("Account Name", "SPITZKOP")
                table.add_row("Account ID", "123456789012")
                table.add_row("Current OU", "Root")
                table.add_row("Status", "✅ Active")
                table.add_row("Created Date", "2024-01-15")
                table.add_row("Last Updated", "2025-01-08")
                table.add_row("Migration Status", "⚠️  Pending migration to Sandbox OU")

                console.print(table)

                console.print(f"\n[bold cyan]💡 Recommended Actions[/bold cyan]")
                console.print(
                    "• [yellow]Migrate to Sandbox OU using: lzaas migrate account --account-name SPITZKOP --target-ou Sandbox[/yellow]"
                )
                console.print(
                    "• [yellow]Apply sandbox template: --template sandbox[/yellow]"
                )
            else:
                console.print(
                    f"[yellow]📭 Account '{account_name}' not found or no status available[/yellow]"
                )
        else:
            # List all accounts with status
            console.print(f"\n[bold cyan]📋 Account Status Overview[/bold cyan]")

            table = Table()
            table.add_column("Account Name", style="cyan", no_wrap=True)
            table.add_column("Account ID", style="green")
            table.add_column("OU", style="blue")
            table.add_column("Status", style="white")
            table.add_column("Template", style="yellow")
            table.add_column("Last Updated", style="dim")

            # Mock data - replace with actual AFT queries
            accounts = [
                {
                    "name": "SPITZKOP",
                    "id": "123456789012",
                    "ou": "Root",
                    "status": "✅ Active",
                    "template": "standalone",
                    "updated": "2025-01-08",
                },
                {
                    "name": "dev-environment",
                    "id": "123456789013",
                    "ou": "Development",
                    "status": "✅ Active",
                    "template": "dev",
                    "updated": "2025-01-07",
                },
                {
                    "name": "staging-test",
                    "id": "123456789014",
                    "ou": "Staging",
                    "status": "🔄 Updating",
                    "template": "staging",
                    "updated": "2025-01-08",
                },
            ]

            # Filter by OU if specified
            if ou:
                accounts = [acc for acc in accounts if acc["ou"].lower() == ou.lower()]
                if not accounts:
                    console.print(f"[yellow]📭 No accounts found in OU '{ou}'[/yellow]")
                    return

            for account in accounts:
                table.add_row(
                    account["name"],
                    account["id"],
                    account["ou"],
                    account["status"],
                    account["template"],
                    account["updated"],
                )

            console.print(table)

            console.print(f"\n[bold cyan]📊 Summary[/bold cyan]")
            console.print(f"• Total accounts: {len(accounts)}")
            if ou:
                console.print(f"• Filtered by OU: {ou}")
            console.print("• Use --account-name for detailed status")

    except Exception as e:
        console.print(f"[red]❌ Error checking account status: {str(e)}[/red]")
