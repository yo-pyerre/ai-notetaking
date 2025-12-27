#!/usr/bin/env python3
"""
Generate Prompt Script for AI Learning Pipeline.

Interactive command-line interface for generating structured prompts for video analysis.
"""

import questionary
from rich.console import Console
from rich.panel import Panel

from src.prompt_generator import PromptGenerator
from src.config_loader import ConfigLoader

console = Console()


def main():
    """
    Main function to run the interactive prompt generation CLI.
    """
    try:
        config_loader = ConfigLoader()
        prompt_generator = PromptGenerator()
        defaults = config_loader.load_defaults_config()
        
        # --- Interactive CLI ---
        console.print("[bold blue]Welcome to the AI Notetaking Prompt Generator![/bold blue]")

        # 1. Select a topic
        available_topics = config_loader.list_topics()
        topic_name = questionary.select(
            "Select a topic:",
            choices=available_topics
        ).ask()

        if not topic_name:
            return

        topic_config = config_loader.get_topic_config(topic_name)

        # 2. Select an output format
        output_format = questionary.select(
            "Select an output format:",
            choices=topic_config.supported_outputs
        ).ask()

        if not output_format:
            return

        # 3. Enter the video URL
        video_url = questionary.text("Enter the video URL:").ask()

        if not video_url:
            return

        # --- Prompt Generation ---
        console.print(f"\n[blue]Generating prompt for topic '{topic_name}' and output format '{output_format}'...[/blue]")

        prompt = prompt_generator.generate_prompt(
            video_url=video_url,
            topic_config=topic_config,
            output_format=output_format,
            defaults=defaults,
            topic=topic_name
        )

        # --- Output ---
        console.print(Panel(prompt, title="Generated Prompt", border_style="green", expand=False))

        save_to_file = questionary.confirm("Save the prompt to a file?").ask()

        if save_to_file:
            output_path = f"output/prompts/{topic_name}_{output_format}_prompt.txt"
            prompt_generator.save_prompt(prompt, output_path)
            console.print(f"\n[green]Prompt saved to:[/green] {output_path}")

    except Exception as e:
        console.print(f"\n[red]An error occurred:[/red] {e}")


if __name__ == "__main__":
    main()
