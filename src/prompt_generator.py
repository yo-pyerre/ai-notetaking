"""
Prompt Generator for AI Learning Pipeline.

Generates structured prompts for multimodal AI analysis based on video content and topics.
Handles template loading, placeholder replacement, and JSON schema injection.
"""

import json
from pathlib import Path

from src.models import TopicConfig

PRIMING_TEXT_DIR = "priming_text"
OUTPUT_TEXT_DIR = "output_text"

class PromptGenerator:
    """Generates prompts for AI analysis of educational video content."""

    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the prompt generator.

        Args:
            templates_dir: Path to the templates directory (default: "templates")
        """
        self.templates_dir = Path(templates_dir)

    def load_template(self, template_name: str, tempalte_sub_dir: str = "") -> str:
        """
        Load a template file by name.

        Args:
            template_name: Name of the template file (e.g., "cooking.txt")

        Returns:
            str: Template content

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = self.templates_dir / tempalte_sub_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def generate_prompt(self, source: str, topic_config: TopicConfig, output_format: str, topic: str) -> str:
        """
        Generate a complete prompt for AI analysis.

        Args:
            source: Source material to be analyzed
            topic_config: The configuration for the selected topic.
            output_format: The selected output format (e.g., "notion", "anki").
            topic: The name of the topic.

        Returns:
            str: Complete formatted prompt

        Raises:
            ValueError: If topic is not supported
        """
        if output_format == 'notion':
            prompt =  self.format_notion_prompt(
                source=source,
                topic_config=topic_config,
                topic=topic
            )

        return prompt
    
    
    def format_notion_prompt(self, source: str, topic_config: TopicConfig, topic: str):
        """
        Formats a prompt that can be used to generate a notion page.

        Args:
            source: Source material to be analyzed
            topic_config: The configuration for the selected topic.
            output_format: The selected output format (e.g., "notion", "anki").
            topic: The name of the topic.

        Returns:
            str: Complete formatted prompt
        """

        priming_text = self.load_template(f'{topic}.txt', PRIMING_TEXT_DIR)
        output_text = self.load_template('notion.txt', OUTPUT_TEXT_DIR)

        required_fields = '\n'.join('- ' + field for field in topic_config.notion.required_fields)
        
        output_text = output_text.replace('{required_fields}', required_fields)
        output_text = output_text.replace('{source}', source)

        return priming_text + '\n' + output_text
        

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
    
