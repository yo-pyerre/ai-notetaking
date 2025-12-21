#!/usr/bin/env python3
"""
Generate Prompt Script for AI Learning Pipeline.

Command-line interface for generating structured prompts for video analysis.
Supports different topics (cooking, general) with appropriate templates.
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

import click
from rich.console import Console
from rich.panel import Panel

from models import AIResponse
from prompt_generator import generate_prompt, save_prompt
from config_loader import list_topics

console = Console()


@click.command()
@click.option(
    "--url",
    "-u",
    required=True,
    help="URL of the video to analyze"
)
@click.option(
    "--topic",
    "-t",
    required=True,
    help="Topic for analysis (cooking, general)"
)
@click.option(
    "--output",
    "-o",
    help="Output file path for the generated prompt (default: output/prompts/prompt.txt)"
)
@click.option(
    "--preview",
    "-p",
    is_flag=True,
    help="Preview the prompt without saving to file"
)
def generate_prompt_cmd(url: str, topic: str, output: str = None, preview: bool = False):
    """
    Generate a structured prompt for AI video analysis.

    This command creates a comprehensive prompt based on the specified topic,
    ready to be used with multimodal AI services for educational content analysis.
    """
    try:
        # Validate topic
        available_topics = list_topics()
        if topic not in available_topics:
            console.print(f"[red]Error:[/red] Topic '{topic}' not found.")
            console.print(f"Available topics: {', '.join(available_topics)}")
            raise click.Abort()

        # Generate the prompt
        console.print(f"[blue]Generating prompt for topic:[/blue] {topic}")
        console.print(f"[blue]Video URL:[/blue] {url}")
        console.print()

        prompt = generate_prompt(url, topic)

        if preview:
            # Show preview of the prompt
            console.print("[green]Prompt Preview:[/green]")
            console.print(Panel(prompt, title="Generated Prompt", border_style="blue"))
        else:
            # Determine output path
            if output is None:
                output = f"output/prompts/{topic}_prompt.txt"

            # Save the prompt
            save_prompt(prompt, output)
            console.print(f"[green]Prompt saved to:[/green] {output}")

            # Show a brief preview
            preview_lines = prompt.split('\n')[:10]  # First 10 lines
            preview_text = '\n'.join(preview_lines)
            if len(prompt.split('\n')) > 10:
                preview_text += "\n... (truncated)"

            console.print()
            console.print("[blue]Prompt Preview (first 10 lines):[/blue]")
            console.print(Panel(preview_text, border_style="blue"))

    except Exception as e:
        console.print(f"[red]Error generating prompt:[/red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    generate_prompt_cmd()
