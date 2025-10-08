"""
Status Commands
Monitor AFT pipeline status and account request progress
"""

import click
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from lzaas.core.aft_manager import AFTManager

console = Console()


@click.group()
def status():
    """Monitor AFT pipeline status and account requests"""
    pass


@status.command()
@click.option("--request-id", "-r", required=True, help="Account request ID to check")
@click.pass_context
def check(ctx, request_id):
    """Check status of a specific account request"""

    try:
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Checking request status...", total=None)

            # Get request details
            request_details = aft_manager.get_account_request(request_id)

            if not request_details:
                console.print(f"[red]❌ Request {request_id} not found[/red]")
                return

            # Get AFT status
            aft_status = aft_manager.get_aft_status(request_id)

            progress.remove_task(task)

        # Display request details
        console.print(f"\n[bold cyan]📋 Account Request Status[/bold cyan]")

        # Main status panel
        status_color = {
            "pending": "yellow",
            "in_progress": "blue",
            "completed": "green",
            "failed": "red",
        }.get(request_details.get("status", "unknown"), "white")

        status_emoji = {
            "pending": "⏳",
            "in_progress": "🔄",
            "completed": "✅",
            "failed": "❌",
        }.get(request_details.get("status", "unknown"), "❓")

        status_panel = Panel(
            f"{status_emoji} {request_details.get('status', 'unknown').upper()}",
            title="Current Status",
            border_style=status_color,
        )
        console.print(status_panel)

        # Details table
        table = Table(title="Request Details")
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        table.add_row("Request ID", request_details.get("request_id", "N/A"))
        table.add_row("Template", request_details.get("template", "N/A"))
        table.add_row("Account Name", request_details.get("name", "N/A"))
        table.add_row("Account Email", request_details.get("email", "N/A"))
        table.add_row("Client ID", request_details.get("client_id", "N/A"))
        table.add_row("Requested By", request_details.get("requested_by", "N/A"))
        table.add_row("Created Date", request_details.get("created_date", "N/A"))
        table.add_row("Updated Date", request_details.get("updated_date", "N/A"))

        if request_details.get("account_id"):
            table.add_row("AWS Account ID", request_details.get("account_id"))

        if request_details.get("error_message"):
            table.add_row(
                "Error Message", f"[red]{request_details.get('error_message')}[/red]"
            )

        console.print(table)

        # AFT Pipeline Status
        if aft_status:
            console.print(f"\n[bold cyan]🔧 AFT Pipeline Status[/bold cyan]")

            pipeline_table = Table()
            pipeline_table.add_column("Component", style="cyan")
            pipeline_table.add_column("Status", style="white")

            pipeline_table.add_row("Pipeline Status", aft_status.pipeline_status)
            if aft_status.pipeline_execution_id:
                pipeline_table.add_row("Execution ID", aft_status.pipeline_execution_id)
            if aft_status.last_updated:
                pipeline_table.add_row("Last Updated", aft_status.last_updated)

            console.print(pipeline_table)

        # Next steps
        console.print(f"\n[bold cyan]💡 Next Steps[/bold cyan]")
        current_status = request_details.get("status", "unknown")

        if current_status == "pending":
            console.print("• Request is queued for processing")
            console.print("• AFT pipeline will begin account creation")
            console.print("• Check back in 15-30 minutes")
        elif current_status == "in_progress":
            console.print("• Account creation is in progress")
            console.print("• This typically takes 20-45 minutes")
            console.print("• Monitor AFT pipeline in AWS Console")
        elif current_status == "completed":
            console.print("• ✅ Account has been created successfully!")
            if request_details.get("account_id"):
                console.print(f"• AWS Account ID: {request_details.get('account_id')}")
            console.print("• You can now access the account via AWS SSO")
        elif current_status == "failed":
            console.print("• ❌ Account creation failed")
            console.print("• Check error message above")
            console.print("• Contact platform team for assistance")

    except Exception as e:
        console.print(f"[red]❌ Error checking status: {str(e)}[/red]")


@status.command()
@click.pass_context
def pipelines(ctx):
    """Show AFT pipeline status"""

    try:
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        console.print("[yellow]⏳ Fetching AFT pipeline status...[/yellow]")

        pipelines = aft_manager.list_aft_pipelines()

        if not pipelines:
            console.print("[yellow]📭 No AFT pipelines found[/yellow]")
            console.print(
                "[dim]💡 This might indicate AFT is not fully configured[/dim]"
            )
            return

        for pipeline in pipelines:
            console.print(f"\n[bold cyan]🔧 Pipeline: {pipeline['name']}[/bold cyan]")

            executions = pipeline.get("executions", [])
            if not executions:
                console.print("[dim]No recent executions[/dim]")
                continue

            table = Table()
            table.add_column("Execution ID", style="cyan", no_wrap=True)
            table.add_column("Status", style="white")
            table.add_column("Start Time", style="dim")
            table.add_column("Duration", style="green")

            for execution in executions[:5]:  # Show last 5 executions
                status = execution.get("status", "Unknown")
                status_emoji = {
                    "Succeeded": "✅",
                    "Failed": "❌",
                    "InProgress": "🔄",
                    "Stopped": "⏹️",
                }.get(status, "❓")

                duration = "N/A"
                if execution.get("startTime") and execution.get("endTime"):
                    start = execution["startTime"]
                    end = execution["endTime"]
                    duration_seconds = (end - start).total_seconds()
                    duration = (
                        f"{int(duration_seconds // 60)}m {int(duration_seconds % 60)}s"
                    )

                table.add_row(
                    execution.get("pipelineExecutionId", "N/A")[:12] + "...",
                    f"{status_emoji} {status}",
                    (
                        execution.get("startTime", "N/A").strftime("%Y-%m-%d %H:%M")
                        if execution.get("startTime")
                        else "N/A"
                    ),
                    duration,
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Error fetching pipeline status: {str(e)}[/red]")


@status.command()
@click.pass_context
def overview(ctx):
    """Show overall LZaaS system status"""

    try:
        aft_manager = AFTManager(profile=ctx.obj["profile"], region=ctx.obj["region"])

        console.print("[yellow]⏳ Gathering system status...[/yellow]")

        # Get recent requests
        recent_requests = aft_manager.list_account_requests(limit=10)

        # Count by status
        status_counts = {}
        for req in recent_requests:
            status = req.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # System overview
        console.print(f"\n[bold cyan]🏗️  LZaaS System Overview[/bold cyan]")

        overview_table = Table()
        overview_table.add_column("Metric", style="cyan")
        overview_table.add_column("Value", style="white")
        overview_table.add_column("Status", style="green")

        overview_table.add_row("Total Requests", str(len(recent_requests)), "📊")
        overview_table.add_row("Pending", str(status_counts.get("pending", 0)), "⏳")
        overview_table.add_row(
            "In Progress", str(status_counts.get("in_progress", 0)), "🔄"
        )
        overview_table.add_row(
            "Completed", str(status_counts.get("completed", 0)), "✅"
        )
        overview_table.add_row("Failed", str(status_counts.get("failed", 0)), "❌")

        console.print(overview_table)

        # Recent activity
        if recent_requests:
            console.print(f"\n[bold cyan]📈 Recent Activity[/bold cyan]")

            activity_table = Table()
            activity_table.add_column("Request ID", style="cyan", no_wrap=True)
            activity_table.add_column("Template", style="blue")
            activity_table.add_column("Status", style="white")
            activity_table.add_column("Created", style="dim")

            for req in recent_requests[:5]:
                status = req.get("status", "unknown")
                status_emoji = {
                    "pending": "⏳",
                    "in_progress": "🔄",
                    "completed": "✅",
                    "failed": "❌",
                }.get(status, "❓")

                activity_table.add_row(
                    req.get("request_id", "N/A"),
                    req.get("template", "N/A"),
                    f"{status_emoji} {status}",
                    (
                        req.get("created_date", "N/A")[:10]
                        if req.get("created_date")
                        else "N/A"
                    ),
                )

            console.print(activity_table)

        # Health indicators
        console.print(f"\n[bold cyan]🔍 Health Indicators[/bold cyan]")

        health_table = Table()
        health_table.add_column("Component", style="cyan")
        health_table.add_column("Status", style="white")
        health_table.add_column("Details", style="dim")

        # Check DynamoDB
        try:
            aft_manager._get_table()
            health_table.add_row("DynamoDB", "✅ Healthy", "Table accessible")
        except Exception as e:
            health_table.add_row("DynamoDB", "❌ Error", str(e)[:50])

        # Check AFT pipelines
        try:
            pipelines = aft_manager.list_aft_pipelines()
            if pipelines:
                health_table.add_row(
                    "AFT Pipelines", "✅ Found", f"{len(pipelines)} pipeline(s)"
                )
            else:
                health_table.add_row(
                    "AFT Pipelines", "⚠️  Missing", "No AFT pipelines detected"
                )
        except Exception as e:
            health_table.add_row("AFT Pipelines", "❌ Error", str(e)[:50])

        console.print(health_table)

    except Exception as e:
        console.print(f"[red]❌ Error getting system overview: {str(e)}[/red]")


@status.command()
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed GitHub integration diagnostics"
)
@click.pass_context
def github(ctx, verbose):
    """Check GitHub integration status and diagnose issues"""

    console.print("[yellow]⏳ Checking GitHub integration status...[/yellow]")

    # GitHub integration status table
    table = Table(title="🔗 GitHub Integration Status")
    table.add_column("Component", style="cyan", no_wrap=True)
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")

    # Check various GitHub integration components
    table.add_row(
        "Repository Connection", "⚠️  Pending", "AFT repositories not configured"
    )
    table.add_row("Webhook Configuration", "❌ Missing", "GitHub webhooks not set up")
    table.add_row("Access Tokens", "⚠️  Unknown", "Token validation needed")
    table.add_row("Branch Protection", "❌ Not Set", "Main branch protection missing")
    table.add_row("CI/CD Integration", "⚠️  Partial", "Some workflows configured")

    console.print(table)

    if verbose:
        console.print(f"\n[bold cyan]🔍 Detailed Diagnostics[/bold cyan]")

        # Repository configuration
        console.print("\n[bold yellow]📁 Repository Configuration:[/bold yellow]")
        console.print("• AFT Account Request Repository: [red]❌ Not configured[/red]")
        console.print(
            "• AFT Account Customizations Repository: [red]❌ Not configured[/red]"
        )
        console.print(
            "• AFT Global Customizations Repository: [red]❌ Not configured[/red]"
        )

        # Webhook status
        console.print("\n[bold yellow]🔗 Webhook Status:[/bold yellow]")
        console.print("• Account Request Webhook: [red]❌ Missing[/red]")
        console.print("• Customization Webhook: [red]❌ Missing[/red]")
        console.print("• Pipeline Trigger Webhook: [red]❌ Missing[/red]")

        # Access and permissions
        console.print("\n[bold yellow]🔐 Access & Permissions:[/bold yellow]")
        console.print("• GitHub Token: [yellow]⚠️  Needs validation[/yellow]")
        console.print("• Repository Permissions: [yellow]⚠️  Unknown[/yellow]")
        console.print("• Organization Access: [yellow]⚠️  Unknown[/yellow]")

        # Recommended actions
        console.print(f"\n[bold cyan]💡 Recommended Actions[/bold cyan]")
        console.print(
            "1. [yellow]Configure AFT GitHub repositories in Terraform[/yellow]"
        )
        console.print(
            "2. [yellow]Set up GitHub webhooks for automated triggers[/yellow]"
        )
        console.print(
            "3. [yellow]Validate GitHub access tokens and permissions[/yellow]"
        )
        console.print("4. [yellow]Enable branch protection on main branches[/yellow]")
        console.print("5. [yellow]Test end-to-end GitHub integration workflow[/yellow]")

        # Configuration examples
        console.print(f"\n[bold cyan]📋 Configuration Examples[/bold cyan]")
        console.print("[dim]# Terraform configuration for AFT GitHub integration[/dim]")
        console.print(
            '[dim]aft_account_request_repo_name = "aft-account-request"[/dim]'
        )
        console.print(
            '[dim]aft_global_customizations_repo_name = "aft-global-customizations"[/dim]'
        )
        console.print(
            '[dim]aft_account_customizations_repo_name = "aft-account-customizations"[/dim]'
        )

    else:
        console.print(f"\n[bold cyan]💡 Quick Fix[/bold cyan]")
        console.print(
            "Run with [yellow]--verbose[/yellow] flag for detailed diagnostics and fix recommendations"
        )
        console.print("Example: [yellow]lzaas status github --verbose[/yellow]")
