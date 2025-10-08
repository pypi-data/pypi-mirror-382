#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
import shutil
from .templates import TEMPLATE_BASIC, TEMPLATE_REQUIREMENTS, TEMPLATE_ENV, TEMPLATE_README, TEMPLATE_GITIGNORE
from .template_fetcher import get_template_by_name, fetch_template_content

console = Console()

@click.command()
@click.argument('name', default='my-stagehand-app', required=False)
@click.option('--template', '-t', default='basic', help='Template to use (basic or GitHub examples: quickstart, example, agent-example)')
def main(name, template):
    """Start your Stagehand project with a single command"""

    console.print("""[yellow]
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡾⠻⣶⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢠⡶⠛⢳⡆⠀⠀⠀⠀⢸⡇⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⢸⣷⠶⣦⣴⠶⣾⡇⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⢸⡇⠀⢸⡇⠀⢸⡇⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠘⠷⣤⢾⡏⠉⠉⠉⠙⣾⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠈⣻⡿⠟⠂⠀⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⠀⠀⠀⠀⢰⡏⠀⠀⠀⢀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣷⡀⠀⠀⠀⠀⠀⠀⢀⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠷⣦⣤⣤⣴⠾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    [/yellow]""")
    console.print("[yellow]Stagehand[/yellow]")
    console.print("[dim]The AI Browser Framework[/dim]\n")

    project_name = name

    # Sanitize project name for directory
    project_dir = project_name.lower().replace(" ", "-").replace("_", "-")
    project_path = Path.cwd() / project_dir

    # Check if directory exists
    if project_path.exists():
        console.print(f"[red]Error: Directory '{project_dir}' already exists[/red]")
        sys.exit(1)

    # Create project structure
    try:
        console.print(f"Creating [bold cyan]{project_dir}[/bold cyan]...\n")

        # Create directories
        project_path.mkdir(parents=True, exist_ok=True)

        # Determine which template to use
        template_content = TEMPLATE_BASIC

        # If not using basic template, try to fetch from GitHub
        if template != 'basic':
            console.print(f"Fetching template [cyan]{template}[/cyan] from GitHub...")
            template_info = get_template_by_name(template)
            if template_info:
                fetched_content = fetch_template_content(template_info)
                if fetched_content:
                    template_content = fetched_content
                    console.print(f"[green]✓[/green] Using template from GitHub: {template}")
                else:
                    console.print(f"[yellow]⚠[/yellow] Could not fetch template, using basic template")
            else:
                console.print(f"[yellow]⚠[/yellow] Template '{template}' not found, using basic template")

        # Create main.py
        main_file = project_path / "main.py"
        main_file.write_text(template_content)

        # Create requirements.txt
        requirements_file = project_path / "requirements.txt"
        requirements_file.write_text(TEMPLATE_REQUIREMENTS)

        # Create .env.example
        env_file = project_path / ".env.example"
        env_file.write_text(TEMPLATE_ENV)

        # Create README.md
        readme_file = project_path / "README.md"
        readme_file.write_text(TEMPLATE_README.format(project_name=project_name))

        # Create .gitignore
        gitignore_file = project_path / ".gitignore"
        gitignore_file.write_text(TEMPLATE_GITIGNORE)

        # Success message
        console.print(f"[green]✓[/green] Find your project at [cyan]{project_path}[/cyan]\n")

        # Styled next steps
        console.print(Panel(
            f"[bold cyan]1.[/bold cyan] cd {project_dir}\n"
            f"[bold cyan]2.[/bold cyan] cp .env.example .env\n"
            f"[bold cyan]3.[/bold cyan] [dim]Add your Browserbase API key to .env[/dim]\n"
            f"[bold cyan]4.[/bold cyan] pip install -r requirements.txt\n"
            f"[bold cyan]5.[/bold cyan] python main.py",
            title="[bold yellow]🚀 Launch now 🚀[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        ))

    except Exception as e:
        console.print(f"[red]Error creating project: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()