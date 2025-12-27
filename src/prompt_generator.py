"""
Prompt Generator for AI Learning Pipeline.

Generates structured prompts for multimodal AI analysis based on video content and topics.
Handles template loading, placeholder replacement, and JSON schema injection.
"""

import json
from pathlib import Path

from src.models import TopicConfig


class PromptGenerator:
    """Generates prompts for AI analysis of educational video content."""

    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the prompt generator.

        Args:
            templates_dir: Path to the templates directory (default: "templates")
        """
        self.templates_dir = Path(templates_dir)

    def load_template(self, template_name: str) -> str:
        """
        Load a template file by name.

        Args:
            template_name: Name of the template file (e.g., "cooking.txt")

        Returns:
            str: Template content

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_output_format_spec(self, topic_config: TopicConfig, output_format: str) -> str:
        """
        Generate the JSON schema specification for AI responses.

        Args:
            topic_config: The configuration for the selected topic.
            output_format: The selected output format (e.g., "notion", "anki").

        Returns:
            str: JSON schema specification as a formatted string
        """
        try:
            response_structure = getattr(topic_config, output_format)
        except AttributeError:
            raise ValueError(f"Unsupported output format '{output_format}'")

        sample_dict = response_structure.sample
        spec_details = response_structure.details

        if output_format == "notion":
            # Dynamically replace the custom_fields in the sample
            notion_config = topic_config.outputs.notion
            sample_dict["note"]["database_fields"] = {field: "value" for field in notion_config.schema.custom_fields}

        formatted_json = json.dumps(sample_dict, indent=2, ensure_ascii=False)
        spec = f"```json\n{formatted_json}\n```\n\nWhere:\n{spec_details}"

        return spec

    def generate_prompt(self, video_url: str, topic_config: TopicConfig, output_format: str, topic: str) -> str:
        """
        Generate a complete prompt for AI analysis.

        Args:
            video_url: URL of the video to analyze
            topic_config: The configuration for the selected topic.
            output_format: The selected output format (e.g., "notion", "anki").
            topic: The name of the topic.

        Returns:
            str: Complete formatted prompt

        Raises:
            ValueError: If topic is not supported or template loading fails
        """
        try:
            output_config = getattr(topic_config.outputs, output_format)
            template_name = output_config.prompt_template
        except AttributeError:
            raise ValueError(f"Unsupported output format '{output_format}'")

        template_content = self.load_template(template_name)
        output_format_spec = self.get_output_format_spec(topic_config, output_format, defaults)

        prompt = template_content.replace("{video_url}", video_url)
        prompt = prompt.replace("{priming_text}", topic_config.priming_text)
        prompt = prompt.replace("{output_format_spec}", output_format_spec)
        prompt = prompt.replace("{topic}", topic)

        return prompt

    def save_prompt(self, prompt: str, output_path: str) -> None:
        """
        Save a generated prompt to a file.

        Args:
            prompt: The generated prompt content
            output_path: Path where to save the prompt
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
