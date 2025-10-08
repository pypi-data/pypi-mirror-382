"""
Template Commands
Manage account templates and customizations
"""

import click
import yaml
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from lzaas.core.models import ACCOUNT_TEMPLATES

console = Console()


@click.group()
def template():
    """Manage account templates and customizations"""
    pass


@template.command()
@click.option(
    "--template",
    "-t",
    type=click.Choice(["dev", "prod", "sandbox", "client"]),
    help="Show specific template details",
)
def list(template):
    """List available account templates"""

    if template:
        # Show specific template details
        if template not in ACCOUNT_TEMPLATES:
            console.print(f"[red]❌ Template '{template}' not found[/red]")
            return

        template_obj = ACCOUNT_TEMPLATES[template]

        # Template header
        console.print(f"\n[bold cyan]📋 Template: {template_obj.name}[/bold cyan]")

        # Basic info panel
        info_panel = Panel(
            f"[white]{template_obj.description}[/white]\n\n"
            f"[dim]Organizational Unit:[/dim] {template_obj.ou}\n"
            f"[dim]Default VPC CIDR:[/dim] {template_obj.vpc_cidr}\n"
            f"[dim]Estimated Cost:[/dim] {template_obj.cost_estimate}",
            title="Template Information",
            border_style="blue",
        )
        console.print(info_panel)

        # Features
        console.print(f"\n[bold]🔧 Features:[/bold]")
        for feature in template_obj.features:
            console.print(f"  • {feature}")

        # Customizations
        console.print(f"\n[bold]⚙️  Customizations:[/bold]")
        for key, value in template_obj.customizations.items():
            console.print(f"  • {key}: {value}")

        # Usage example
        console.print(f"\n[bold]💡 Usage Example:[/bold]")
        console.print(
            f"[dim]lzaas account create --template {template} --email your@email.com[/dim]"
        )

    else:
        # Show all templates
        console.print(f"\n[bold cyan]🏗️  Available Account Templates[/bold cyan]")

        table = Table()
        table.add_column("Template", style="cyan", no_wrap=True)
        table.add_column("Name", style="white")
        table.add_column("OU", style="blue")
        table.add_column("Cost Estimate", style="green")
        table.add_column("Description", style="dim")

        for template_id, template_obj in ACCOUNT_TEMPLATES.items():
            table.add_row(
                template_id,
                template_obj.name,
                template_obj.ou,
                template_obj.cost_estimate,
                template_obj.description,
            )

        console.print(table)
        console.print(
            f"\n[dim]💡 Use 'lzaas template list --template <name>' for details[/dim]"
        )


@template.command()
@click.option(
    "--template",
    "-t",
    required=True,
    type=click.Choice(["dev", "prod", "sandbox", "client"]),
    help="Template to export",
)
@click.option(
    "--format",
    "-f",
    default="yaml",
    type=click.Choice(["yaml", "json"]),
    help="Export format",
)
@click.option("--output", "-o", help="Output file (default: stdout)")
def export(template, format, output):
    """Export template configuration"""

    if template not in ACCOUNT_TEMPLATES:
        console.print(f"[red]❌ Template '{template}' not found[/red]")
        return

    template_obj = ACCOUNT_TEMPLATES[template]
    template_dict = template_obj.to_dict()

    # Format output
    if format == "yaml":
        content = yaml.dump(template_dict, default_flow_style=False, indent=2)
    else:  # json
        import json

        content = json.dumps(template_dict, indent=2)

    # Output
    if output:
        try:
            with open(output, "w") as f:
                f.write(content)
            console.print(f"[green]✅ Template exported to {output}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to write file: {str(e)}[/red]")
    else:
        console.print(f"\n[bold cyan]📄 Template: {template}[/bold cyan]")
        console.print(content)


@template.command()
@click.option(
    "--template",
    "-t",
    required=True,
    type=click.Choice(["dev", "prod", "sandbox", "client"]),
    help="Template to validate",
)
def validate(template):
    """Validate template configuration"""

    if template not in ACCOUNT_TEMPLATES:
        console.print(f"[red]❌ Template '{template}' not found[/red]")
        return

    template_obj = ACCOUNT_TEMPLATES[template]

    console.print(f"\n[bold cyan]🔍 Validating Template: {template}[/bold cyan]")

    # Validation checks
    checks = []

    # Check required fields
    if template_obj.name:
        checks.append(("Name", "✅", "Present"))
    else:
        checks.append(("Name", "❌", "Missing"))

    if template_obj.description:
        checks.append(("Description", "✅", "Present"))
    else:
        checks.append(("Description", "❌", "Missing"))

    if template_obj.ou:
        checks.append(("Organizational Unit", "✅", template_obj.ou))
    else:
        checks.append(("Organizational Unit", "❌", "Missing"))

    # Validate VPC CIDR
    import ipaddress

    try:
        ipaddress.IPv4Network(template_obj.vpc_cidr)
        checks.append(("VPC CIDR", "✅", f"Valid: {template_obj.vpc_cidr}"))
    except:
        checks.append(("VPC CIDR", "❌", f"Invalid: {template_obj.vpc_cidr}"))

    # Check features
    if template_obj.features and len(template_obj.features) > 0:
        checks.append(("Features", "✅", f"{len(template_obj.features)} feature(s)"))
    else:
        checks.append(("Features", "⚠️", "No features defined"))

    # Check customizations
    if template_obj.customizations:
        checks.append(
            ("Customizations", "✅", f"{len(template_obj.customizations)} setting(s)")
        )
    else:
        checks.append(("Customizations", "⚠️", "No customizations defined"))

    # Display results
    table = Table(title="Validation Results")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Details", style="dim")

    for check, status, details in checks:
        table.add_row(check, status, details)

    console.print(table)

    # Summary
    passed = sum(1 for _, status, _ in checks if status == "✅")
    warnings = sum(1 for _, status, _ in checks if status == "⚠️")
    failed = sum(1 for _, status, _ in checks if status == "❌")

    if failed > 0:
        console.print(
            f"\n[red]❌ Validation failed: {failed} error(s), {warnings} warning(s)[/red]"
        )
    elif warnings > 0:
        console.print(
            f"\n[yellow]⚠️  Validation passed with warnings: {warnings} warning(s)[/yellow]"
        )
    else:
        console.print(f"\n[green]✅ Validation passed: All checks successful[/green]")


@template.command()
def compare():
    """Compare all templates side by side"""

    console.print(f"\n[bold cyan]📊 Template Comparison[/bold cyan]")

    # Create comparison table
    table = Table()
    table.add_column("Attribute", style="cyan", no_wrap=True)

    # Add columns for each template
    for template_id in ACCOUNT_TEMPLATES.keys():
        table.add_column(template_id.title(), style="white")

    # Compare attributes
    attributes = [
        ("Name", lambda t: t.name),
        ("OU", lambda t: t.ou),
        ("VPC CIDR", lambda t: t.vpc_cidr),
        ("Cost Estimate", lambda t: t.cost_estimate),
        ("Feature Count", lambda t: str(len(t.features))),
        ("Customizations", lambda t: str(len(t.customizations))),
    ]

    for attr_name, attr_func in attributes:
        row = [attr_name]
        for template_obj in ACCOUNT_TEMPLATES.values():
            row.append(attr_func(template_obj))
        table.add_row(*row)

    console.print(table)

    # Feature comparison
    console.print(f"\n[bold cyan]🔧 Feature Comparison[/bold cyan]")

    # Collect all unique features
    all_features = set()
    for template_obj in ACCOUNT_TEMPLATES.values():
        all_features.update(template_obj.features)

    feature_table = Table()
    feature_table.add_column("Feature", style="cyan")

    for template_id in ACCOUNT_TEMPLATES.keys():
        feature_table.add_column(template_id.title(), style="white")

    for feature in sorted(all_features):
        row = [feature]
        for template_obj in ACCOUNT_TEMPLATES.values():
            if feature in template_obj.features:
                row.append("✅")
            else:
                row.append("❌")
        feature_table.add_row(*row)

    console.print(feature_table)

    console.print(
        f"\n[dim]💡 Use 'lzaas template list --template <name>' for detailed information[/dim]"
    )
