"""
Command Line Interface for AI Learning Pipeline.

Provides CLI commands for managing the pipeline operations.
"""

import click
from rich.console import Console
from rich.table import Table

from config_loader import get_topic_config, list_topics, get_defaults

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI Learning Pipeline - Transform educational videos into structured learning materials."""
    pass


@cli.command()
def list_topics_cmd():
    """List all available topics."""
    try:
        topics = list_topics()
        if not topics:
            console.print("[yellow]No topics configured.[/yellow]")
            return

        table = Table(title="Available Topics")
        table.add_column("Topic Name", style="cyan", no_wrap=True)

        for topic in topics:
            table.add_row(topic)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing topics: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument("topic_name")
def show_topic(topic_name: str):
    """Show configuration for a specific topic."""
    try:
        config = get_topic_config(topic_name)

        console.print(f"[bold blue]Configuration for topic: {topic_name}[/bold blue]")
        console.print()

        # Basic info
        console.print("[bold]Basic Information:[/bold]")
        console.print(f"  Notion Database ID: {config.notion_database_id}")
        console.print(f"  Anki Deck Name: {config.anki_deck_name}")
        console.print(f"  Prompt Template: {config.prompt_template}")
        console.print()

        # Notion schema
        console.print("[bold]Notion Schema:[/bold]")
        console.print(f"  Required Fields: {', '.join(config.notion_schema.required_fields)}")
        console.print(f"  Custom Fields: {', '.join(config.notion_schema.custom_fields)}")
        console.print()

        # Anki tags
        console.print("[bold]Anki Tags:[/bold]")
        console.print(f"  Tags: {', '.join(config.anki_tags)}")

    except Exception as e:
        console.print(f"[red]Error showing topic configuration: {e}[/red]")
        raise click.Abort()


@cli.command()
def show_defaults():
    """Show default configuration values."""
    try:
        defaults = get_defaults()

        console.print("[bold blue]Default Configuration[/bold blue]")
        console.print()

        console.print("[bold]Anki Defaults:[/bold]")
        console.print(f"  Model ID: {defaults.anki.model_id}")
        console.print(f"  Deck ID Base: {defaults.anki.deck_id_base}")
        console.print()

        console.print("[bold]Output Directories:[/bold]")
        console.print(f"  Prompts: {defaults.output.prompts_dir}")
        console.print(f"  Responses: {defaults.output.responses_dir}")
        console.print(f"  Anki Files: {defaults.output.anki_dir}")
        console.print()

        console.print("[bold]Notion Defaults:[/bold]")
        console.print(f"  Default Page Icon: {defaults.notion.default_page_icon}")

    except Exception as e:
        console.print(f"[red]Error showing defaults: {e}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    cli()
