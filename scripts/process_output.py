#!/usr/bin/env python3
"""
Process Output Script for AI Notetaking Pipeline.

Command-line interface for processing AI-generated responses into Notion pages and Anki decks.
Supports selective processing with progress indicators and error handling.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table

from src.response_parser import ResponseParser
from src.notion_facade import NotionClient, NotionClientError
from src.anki_generator import generate_deck_from_flashcards
from src.config_loader import ConfigLoader
from src.models import AIResponse

console = Console()


@click.command()
@click.option(
    "--input",
    "-i",
    required=True,
    help="Path to JSON response file from AI service"
)
@click.option(
    "--topic",
    "-t",
    required=True,
    help="Topic for processing (cooking, general)"
)
@click.option(
    "--source-url",
    "-s",
    help="Source URL of the original content (for metadata)"
)
@click.option(
    "--notion-only",
    is_flag=True,
    help="Only create Notion page, skip Anki deck generation"
)
@click.option(
    "--anki-only",
    is_flag=True,
    help="Only create Anki deck, skip Notion page creation"
)
def process_output_cmd(
    input: str,
    topic: str,
    source_url: str = None,
    notion_only: bool = False,
    anki_only: bool = False
):
    """
    Process AI-generated response into Notion pages and Anki decks.

    This command takes a JSON response from an AI service and converts it into
    structured learning materials: Notion pages for detailed notes and Anki decks
    for spaced repetition learning.
    """
    # Validate flags
    if notion_only and anki_only:
        console.print("[red]Error:[/red] Cannot specify both --notion-only and --anki-only")
        raise click.Abort()

    # Determine what to process
    process_notion = not anki_only
    process_anki = not notion_only

    try:
        # Validate topic
        available_topics = list_topics()
        if topic not in available_topics:
            console.print(f"[red]Error:[/red] Topic '{topic}' not found.")
            console.print(f"Available topics: {', '.join(available_topics)}")
            raise click.Abort()

        # Validate input file
        input_path = Path(input)
        if not input_path.exists():
            console.print(f"[red]Error:[/red] Input file not found: {input}")
            raise click.Abort()

        # Load topic configuration
        topic_config = get_topic_config(topic)

        # Display processing plan
        console.print(f"[blue]Processing AI response for topic:[/blue] {topic}")
        console.print(f"[blue]Input file:[/blue] {input}")
        if source_url:
            console.print(f"[blue]Source URL:[/blue] {source_url}")
        console.print()

        # Show what will be created
        operations = []
        if process_notion:
            operations.append("Notion page")
        if process_anki:
            operations.append("Anki deck")
        console.print(f"[green]Will create:[/green] {', '.join(operations)}")
        console.print()

        # Read and parse the response
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            # Step 1: Read and parse JSON response
            task = progress.add_task("Reading and parsing AI response...", total=None)

            try:
                with open(input_path, 'r', encoding='utf-8') as f:
                    json_content = f.read()

                parser = ResponseParser()
                ai_response = parser.parse_response(json_content)

                progress.update(task, completed=True, description="✓ AI response parsed successfully")

            except Exception as e:
                progress.update(task, description=f"✗ Failed to parse response: {e}")
                raise click.Abort()

            # Step 2: Create Notion page if requested
            notion_url = None
            if process_notion:
                task = progress.add_task("Creating Notion page...", total=None)

                try:
                    notion_client = NotionClient()
                    notion_url = notion_client.create_learning_page(
                        ai_response.note,
                        topic_config,
                        source_url
                    )
                    progress.update(task, completed=True, description="✓ Notion page created successfully")

                except NotionClientError as e:
                    progress.update(task, description=f"✗ Notion page creation failed: {e}")
                    if not process_anki:
                        # If only doing Notion and it failed, abort
                        raise click.Abort()
                    # If also doing Anki, continue but mark Notion as failed
                    notion_url = None

            # Step 3: Create Anki deck if requested
            anki_path = None
            if process_anki:
                task = progress.add_task("Creating Anki deck...", total=None)

                try:
                    anki_path = generate_deck_from_flashcards(
                        ai_response.flashcards,
                        topic,
                        topic_config.anki_deck_name,
                        topic_config.anki_tags,
                        source_url
                    )
                    progress.update(task, completed=True, description="✓ Anki deck created successfully")

                except Exception as e:
                    progress.update(task, description=f"✗ Anki deck creation failed: {e}")
                    if not process_notion:
                        # If only doing Anki and it failed, abort
                        raise click.Abort()
                    # If also doing Notion, continue but mark Anki as failed
                    anki_path = None

        # Display results
        console.print()
        console.print("[green]Processing completed![/green]")
        console.print()

        # Create results table
        table = Table(title="Processing Results")
        table.add_column("Output Type", style="cyan", no_wrap=True)
        table.add_column("Status", style="green", no_wrap=True)
        table.add_column("Details", style="white")

        if process_notion:
            if notion_url:
                table.add_row("Notion Page", "✓ Success", f"[link={notion_url}]View Page[/link]")
            else:
                table.add_row("Notion Page", "✗ Failed", "Check logs for details")

        if process_anki:
            if anki_path:
                table.add_row("Anki Deck", "✓ Success", f"Saved to: {anki_path}")
            else:
                table.add_row("Anki Deck", "✗ Failed", "Check logs for details")

        console.print(table)

        # Summary statistics
        note_title = ai_response.note.title
        flashcard_count = len(ai_response.flashcards)

        console.print()
        console.print("[blue]Summary:[/blue]")
        console.print(f"• Note title: {note_title}")
        console.print(f"• Flashcards generated: {flashcard_count}")

    except Exception as e:
        console.print(f"[red]Unexpected error during processing:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    process_output_cmd()
