"""
Migration Commands - Infrastructure as Code Compliant
Handle existing account migrations through Git repository updates
"""

import json
import os
from datetime import datetime
from pathlib import Path

import click
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from lzaas.core.aft_manager import AFTManager
from lzaas.utils.validators import validate_email, validate_ou_name

console = Console()


@click.group()
def migrate():
    """Migrate existing accounts through Infrastructure as Code (Git-based)"""
    pass


@migrate.command()
@click.option("--source", "-s", required=True, help="Source account name or ID")
@click.option("--target", "-t", required=True, help="Target OU name")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be done without executing"
)
@click.pass_context
def simple(ctx, source, target, dry_run):
    """
    Simple migration command for moving accounts to different OUs

    This command follows Infrastructure as Code principles:
    1. Updates account request files in Git repository
    2. Creates a Pull Request for review
    3. AFT pipeline processes changes when PR is merged
    4. All changes are tracked and auditable through Git
    """

    console.print(
        f"\n[bold cyan]🔄 Infrastructure as Code Account Migration[/bold cyan]"
    )
    console.print(f"[dim]All changes will be made through Git repository updates[/dim]")

    try:
        # Load user configuration for GitHub integration
        user_config = ctx.obj.get("user_config", {})
        github_config = user_config.get("github", {})
        aft_config = user_config.get("aft", {})

        if not github_config.get("organization"):
            console.print(
                f"[red]❌ GitHub organization not configured. Run 'lzaas config init'[/red]"
            )
            return

        if not aft_config.get("account_request_repo_name"):
            console.print(
                f"[red]❌ Account request repository not configured. Run 'lzaas config init'[/red]"
            )
            return

        # Initialize AFT manager with proper profile
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validating migration request...", total=None)

            # Step 1: Find and validate source account
            account_info = None
            if source.isdigit() and len(source) == 12:
                # Source is account ID - look it up
                account_info = aft_manager.find_account_by_id(source)
            else:
                # Source is account name - search for it
                account_info = aft_manager.find_account_by_name(source)

            if not account_info:
                progress.remove_task(task)
                console.print(
                    f"[red]❌ Account '{source}' not found in AWS Organizations[/red]"
                )
                return

            progress.update(task, description="Validating target OU...")

            # Step 2: Validate target OU exists
            target_ou_info = aft_manager.find_ou_by_name(target)
            if not target_ou_info:
                progress.remove_task(task)
                console.print(f"[red]❌ Target OU '{target}' not found[/red]")
                console.print(
                    f"[yellow]💡 Use 'lzaas migrate list-ous' to see available OUs[/yellow]"
                )
                return

            progress.update(task, description="Checking current account location...")

            # Step 3: Get current account location
            current_parent = aft_manager.get_account_parent(account_info["Id"])
            if not current_parent:
                progress.remove_task(task)
                console.print(
                    f"[red]❌ Could not determine current location of account[/red]"
                )
                return

            progress.update(task, description="Preparing Git repository changes...")

            # Step 4: Prepare repository changes
            repo_changes = aft_manager.prepare_migration_changes(
                account_info=account_info,
                target_ou=target_ou_info,
                current_parent=current_parent,
            )

            progress.remove_task(task)

        # Display migration plan
        migration_table = Table(title="🏗️ Infrastructure as Code Migration Plan")
        migration_table.add_column("Field", style="cyan", no_wrap=True)
        migration_table.add_column("Value", style="white")

        migration_table.add_row(
            "Source Account", f"{account_info['Name']} ({account_info['Id']})"
        )
        migration_table.add_row(
            "Current Location", current_parent.get("Name", current_parent["Id"])
        )
        migration_table.add_row(
            "Target OU", f"{target_ou_info['Name']} ({target_ou_info['Id']})"
        )
        migration_table.add_row(
            "Repository",
            f"{github_config['organization']}/{aft_config['account_request_repo_name']}",
        )
        migration_table.add_row("Method", "Git-based Infrastructure as Code")

        console.print(migration_table)

        # Show what files will be changed
        console.print(f"\n[bold yellow]📝 Repository Changes:[/bold yellow]")
        for file_path, change_type in repo_changes["files"].items():
            if change_type == "create":
                console.print(
                    f"[green]  + {file_path}[/green] (create new account request)"
                )
            elif change_type == "update":
                console.print(
                    f"[yellow]  ~ {file_path}[/yellow] (update OU assignment)"
                )
            elif change_type == "delete":
                console.print(f"[red]  - {file_path}[/red] (remove old request)")

        console.print(f"\n[bold yellow]🔄 Process Flow:[/bold yellow]")
        console.print("1. Create feature branch in repository")
        console.print("2. Update account request files with new OU assignment")
        console.print("3. Commit changes with migration metadata")
        console.print("4. Create Pull Request for review")
        console.print("5. When PR is merged, AFT pipeline processes the migration")
        console.print("6. Account is moved to new OU by AFT system")

        if dry_run:
            console.print(
                f"\n[yellow]🔍 DRY RUN MODE - No changes will be made[/yellow]"
            )

            # Show the exact Terraform changes that would be made
            console.print(f"\n[bold]📋 Terraform Changes Preview:[/bold]")
            terraform_content = repo_changes.get("terraform_preview", "")
            if terraform_content:
                console.print(f"[dim]{terraform_content}[/dim]")

            console.print(f"\n[bold]🔗 Pull Request Details:[/bold]")
            pr_details = repo_changes.get("pr_details", {})
            console.print(
                f"Branch: [cyan]{pr_details.get('branch_name', 'migrate-account-' + account_info['Id'])}[/cyan]"
            )
            title = pr_details.get(
                "title",
                f'Migrate {account_info["Name"]} to {target_ou_info["Name"]} OU',
            )
            console.print(f"Title: [cyan]{title}[/cyan]")
            console.print(
                f"Description: [dim]{pr_details.get('description', 'Automated account migration via LZaaS CLI')}[/dim]"
            )

            return

        # Confirm before proceeding
        console.print(f"\n[bold red]⚠️  IMPORTANT:[/bold red]")
        console.print("This migration follows Infrastructure as Code principles:")
        console.print("• Changes will be made through Git repository")
        console.print("• A Pull Request will be created for review")
        console.print("• Actual account move happens when PR is merged")
        console.print("• All changes are tracked and auditable")

        if not click.confirm(
            f"\nProceed with Git-based migration of '{account_info['Name']}' to OU '{target_ou_info['Name']}'?"
        ):
            console.print("[yellow]Migration cancelled[/yellow]")
            return

        # Execute the migration through Git
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating Git branch...", total=None)

            try:
                # Execute the Git-based migration
                result = aft_manager.execute_git_migration(
                    account_info=account_info,
                    target_ou=target_ou_info,
                    repo_changes=repo_changes,
                    github_config=github_config,
                    aft_config=aft_config,
                )

                progress.remove_task(task)

                if result["success"]:
                    console.print(
                        f"\n[green]✅ Migration initiated successfully through Infrastructure as Code![/green]"
                    )

                    console.print(f"\n[bold cyan]📋 Migration Details:[/bold cyan]")
                    console.print(f"Branch: [cyan]{result['branch_name']}[/cyan]")
                    console.print(f"Pull Request: [blue]{result['pr_url']}[/blue]")
                    console.print(f"Commit: [dim]{result['commit_sha']}[/dim]")

                    console.print(f"\n[bold cyan]📋 Next Steps:[/bold cyan]")
                    console.print("1. Review the Pull Request in GitHub")
                    console.print("2. Approve and merge the PR when ready")
                    console.print(
                        "3. AFT pipeline will automatically process the migration"
                    )
                    console.print("4. Monitor AFT pipeline execution in AWS Console")
                    console.print(
                        "5. Verify account appears in new OU after completion"
                    )

                    console.print(f"\n[bold]Monitor progress:[/bold]")
                    console.print(f"[blue]{result['pr_url']}[/blue]")
                    console.print(
                        f"[dim]lzaas status check --account-id {account_info['Id']}[/dim]"
                    )

                else:
                    console.print(f"[red]❌ Migration failed: {result['error']}[/red]")
                    if "github" in result["error"].lower():
                        console.print(
                            f"[yellow]💡 Check your GitHub token permissions and repository access[/yellow]"
                        )

            except Exception as e:
                progress.remove_task(task)
                console.print(
                    f"[red]❌ Error during Git-based migration: {str(e)}[/red]"
                )

    except Exception as e:
        console.print(f"[red]❌ Error during migration: {str(e)}[/red]")


@migrate.command()
@click.pass_context
def list_ous(ctx):
    """List all available Organizational Units"""

    try:
        # Initialize AFT manager with proper profile
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        console.print(f"\n[bold cyan]📋 Available Organizational Units[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching organizational structure...", total=None)

            # Get all OUs
            ou_structure = aft_manager.get_organizational_structure()

            progress.remove_task(task)

        # Display organizational structure
        console.print(
            f"\n[bold]🏗️  {ou_structure['root']['name']} ({ou_structure['root']['id']})[/bold]"
        )

        if not ou_structure["ous"]:
            console.print("[yellow]No Organizational Units found[/yellow]")
        else:
            for ou in ou_structure["ous"]:
                indent = "  " * ou["level"]
                console.print(f"{indent}├─ {ou['name']} ({ou['id']})")

        console.print(f"\n[dim]💡 Use OU names (not IDs) with migration commands[/dim]")
        console.print(
            f"[dim]Example: lzaas migrate simple --source spitzkop --target Sandbox[/dim]"
        )

    except Exception as e:
        console.print(f"[red]❌ Error listing OUs: {str(e)}[/red]")


@migrate.command()
@click.option("--account-id", "-a", help="Filter by specific account ID")
@click.option("--ou", "-o", help="Filter by Organizational Unit")
@click.pass_context
def status(ctx, account_id, ou):
    """Check migration status and ongoing operations"""

    try:
        # Initialize AFT manager with proper profile
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        console.print(f"\n[bold cyan]📊 Migration Status Dashboard[/bold cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking migration status...", total=None)

            # Get migration status
            migration_status = aft_manager.get_migration_status(
                account_id=account_id, ou_filter=ou
            )

            progress.remove_task(task)

        # Display ongoing migrations
        if migration_status.get("ongoing_migrations"):
            console.print(f"\n[bold yellow]🔄 Ongoing Migrations:[/bold yellow]")

            ongoing_table = Table()
            ongoing_table.add_column("Account", style="cyan")
            ongoing_table.add_column("Source OU", style="white")
            ongoing_table.add_column("Target OU", style="green")
            ongoing_table.add_column("Status", style="yellow")
            ongoing_table.add_column("Started", style="dim")

            for migration in migration_status["ongoing_migrations"]:
                ongoing_table.add_row(
                    f"{migration['account_name']} ({migration['account_id']})",
                    migration["source_ou"],
                    migration["target_ou"],
                    migration["status"],
                    migration["started_at"],
                )

            console.print(ongoing_table)
        else:
            console.print(f"\n[green]✅ No ongoing migrations[/green]")

        # Display recent migrations
        if migration_status.get("recent_migrations"):
            console.print(
                f"\n[bold cyan]📈 Recent Migrations (Last 7 days):[/bold cyan]"
            )

            recent_table = Table()
            recent_table.add_column("Account", style="cyan")
            recent_table.add_column("Source OU", style="white")
            recent_table.add_column("Target OU", style="green")
            recent_table.add_column("Status", style="white")
            recent_table.add_column("Completed", style="dim")

            for migration in migration_status["recent_migrations"]:
                status_color = "green" if migration["status"] == "SUCCESS" else "red"
                recent_table.add_row(
                    f"{migration['account_name']} ({migration['account_id']})",
                    migration["source_ou"],
                    migration["target_ou"],
                    f"[{status_color}]{migration['status']}[/{status_color}]",
                    migration["completed_at"],
                )

            console.print(recent_table)
        else:
            console.print(f"\n[dim]No recent migrations found[/dim]")

        # Display summary
        console.print(f"\n[bold cyan]📊 Summary:[/bold cyan]")
        console.print(
            f"Active migrations: {len(migration_status.get('ongoing_migrations', []))}"
        )
        console.print(
            f"Recent migrations: {len(migration_status.get('recent_migrations', []))}"
        )

    except Exception as e:
        console.print(f"[red]❌ Error checking migration status: {str(e)}[/red]")
