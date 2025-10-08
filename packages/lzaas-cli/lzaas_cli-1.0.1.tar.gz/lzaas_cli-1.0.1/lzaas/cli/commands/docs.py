#!/usr/bin/env python3
"""
LZaaS CLI Documentation Commands
"""

import os
import webbrowser
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown

console = Console()


@click.group()
def docs():
    """Access LZaaS documentation and guides"""
    pass


@docs.command()
@click.option("--browser", is_flag=True, help="Open in web browser")
def user_guide(browser):
    """Open the complete LZaaS User Guide"""

    # Get the path to the user guide in the lzaas-cli repository docs folder
    current_dir = Path(__file__).parent.parent.parent.parent
    user_guide_path = current_dir / "docs" / "USER_GUIDE.md"

    if not user_guide_path.exists():
        console.print("[red]❌ User guide not found at expected location[/red]")
        console.print(f"[yellow]Expected: {user_guide_path}[/yellow]")
        return

    if browser:
        # Convert to HTML and open in browser (future enhancement)
        console.print("[yellow]⚠️  Browser viewing not yet implemented[/yellow]")
        console.print(f"[blue]📖 User guide location: {user_guide_path}[/blue]")
        console.print(
            "[cyan]💡 Use your preferred markdown viewer or IDE to open the file[/cyan]"
        )
    else:
        # Display in terminal
        try:
            with open(user_guide_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Show first part of the guide
            lines = content.split("\n")
            preview_lines = lines[:50]  # Show first 50 lines
            preview_content = "\n".join(preview_lines)

            console.print("[bold cyan]📖 LZaaS User Guide (Preview)[/bold cyan]")
            console.print("─" * 60)

            # Render markdown
            md = Markdown(preview_content)
            console.print(md)

            console.print("─" * 60)
            console.print(f"[green]📍 Full guide location: {user_guide_path}[/green]")
            console.print(
                "[cyan]💡 Open this file in your IDE or markdown viewer for the complete guide[/cyan]"
            )

        except Exception as e:
            console.print(f"[red]❌ Error reading user guide: {e}[/red]")
            console.print(f"[blue]📖 User guide location: {user_guide_path}[/blue]")


@docs.command()
def quick_reference():
    """Show quick reference and command cheat sheet"""

    # Get the path to the quick reference in the lzaas-cli repository docs folder
    current_dir = Path(__file__).parent.parent.parent.parent
    quick_ref_path = current_dir / "docs" / "QUICK_REFERENCE.md"

    if not quick_ref_path.exists():
        console.print("[red]❌ Quick reference not found[/red]")
        return

    try:
        with open(quick_ref_path, "r", encoding="utf-8") as f:
            content = f.read()

        console.print("[bold cyan]🚀 LZaaS CLI Quick Reference[/bold cyan]")
        console.print("─" * 60)

        # Render markdown
        md = Markdown(content)
        console.print(md)

    except Exception as e:
        console.print(f"[red]❌ Error reading quick reference: {e}[/red]")
        console.print(f"[blue]📖 Quick reference location: {quick_ref_path}[/blue]")


@docs.command()
def installation():
    """Show installation guide"""

    current_dir = Path(__file__).parent.parent.parent.parent
    install_guide_path = current_dir / "docs" / "INSTALLATION_GUIDE.md"

    if not install_guide_path.exists():
        console.print("[red]❌ Installation guide not found[/red]")
        return

    console.print("[bold cyan]🛠️  LZaaS Installation Guide[/bold cyan]")
    console.print("─" * 60)
    console.print(
        f"[green]📍 Installation guide location: {install_guide_path}[/green]"
    )
    console.print(
        "[cyan]💡 Open this file in your IDE or markdown viewer for complete installation instructions[/cyan]"
    )

    # Show quick installation summary
    console.print("\n[bold yellow]Quick Installation Summary:[/bold yellow]")
    console.print("1. [blue]./uninstall-lzaas.sh[/blue] - Clean previous installations")
    console.print("2. [blue]./install-lzaas.sh[/blue] - Install in virtual environment")
    console.print(
        "3. [blue]source lzaas-env/bin/activate[/blue] - Activate environment"
    )
    console.print("4. [blue]lzaas info[/blue] - Verify installation")


@docs.command()
def list():
    """List all available documentation"""

    console.print("[bold cyan]📚 LZaaS Documentation[/bold cyan]")
    console.print("─" * 60)

    # Get the path to the lzaas-cli repository docs folder
    current_dir = Path(__file__).parent.parent.parent.parent
    docs_dir = current_dir / "docs"

    console.print("[bold green]User Documentation:[/bold green]")
    console.print(
        "• [blue]lzaas docs user-guide[/blue] - Complete user guide with business logic"
    )
    console.print("• [blue]lzaas docs quick-reference[/blue] - Command cheat sheet")
    console.print("• [blue]lzaas docs installation[/blue] - Installation instructions")

    console.print("\n[bold green]Available Documentation Files:[/bold green]")
    if docs_dir.exists():
        for doc_file in sorted(docs_dir.glob("*.md")):
            console.print(f"• [cyan]{doc_file.name}[/cyan] - {doc_file}")
    else:
        console.print("[yellow]⚠️  Documentation directory not found[/yellow]")

    console.print("\n[bold green]Command Help:[/bold green]")
    console.print("• [blue]lzaas --help[/blue] - General CLI help")
    console.print("• [blue]lzaas account --help[/blue] - Account management help")
    console.print("• [blue]lzaas template --help[/blue] - Template management help")
    console.print("• [blue]lzaas migrate --help[/blue] - Migration operations help")
    console.print("• [blue]lzaas status --help[/blue] - Status and monitoring help")


if __name__ == "__main__":
    docs()
