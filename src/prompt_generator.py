"""
Prompt Generator for AI Learning Pipeline.

Generates structured prompts for multimodal AI analysis based on video content and topics.
Handles template loading, placeholder replacement, and JSON schema injection.
"""

import json
from pathlib import Path
from typing import Optional

from src.models import AIResponse


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

    def get_output_format_spec(self) -> str:
        """
        Generate the JSON schema specification for AI responses.

        Returns:
            str: JSON schema specification as a formatted string
        """
        # Create a sample response structure to show the expected format
        sample_dict = {
            "note": {
                "title": "Sample Title",
                "summary": "Brief summary of the content",
                "key_points": ["Key point 1", "Key point 2", "Key point 3"],
                "database_fields": {"custom_field": "value"}
            },
            "flashcards": [
                {"front": "Question?", "back": "Answer", "tags": ["tag1", "tag2"]},
                {"front": "Another question?", "back": "Another answer", "tags": ["tag1"]}
            ]
        }

        # Create formatted JSON string
        formatted_json = json.dumps(sample_dict, indent=2, ensure_ascii=False)

        spec = f"""```json
{formatted_json}
```

Where:
- `note`: Contains the main structured notes with:
  - `title`: A concise, descriptive title for the content
  - `summary`: A brief overview of the main topic and key takeaways
  - `key_points`: Array of important points, concepts, or steps
  - `database_fields`: Object with topic-specific custom fields for Notion
- `flashcards`: Array of flashcard objects, each with:
  - `front`: The question or prompt side of the flashcard
  - `back`: The answer or explanation side
  - `tags`: Array of strings for categorization and filtering"""

        return spec

    def generate_prompt(self, video_url: str, topic: str, template_name: Optional[str] = None) -> str:
        """
        Generate a complete prompt for AI analysis.

        Args:
            video_url: URL of the video to analyze
            topic: Topic name (e.g., "cooking", "general")
            template_name: Optional template name override

        Returns:
            str: Complete formatted prompt

        Raises:
            ValueError: If topic is not supported or template loading fails
        """
        # Determine template name from topic if not provided
        if template_name is None:
            # This could be extended to load from config, but for now use simple mapping
            template_mapping = {
                "cooking": "cooking.txt",
                "general": "general.txt"
            }

            if topic not in template_mapping:
                available_topics = list(template_mapping.keys())
                raise ValueError(f"Unsupported topic '{topic}'. Available topics: {available_topics}")

            template_name = template_mapping[topic]

        # Load the template
        template_content = self.load_template(template_name)

        # Get the output format specification
        output_format_spec = self.get_output_format_spec()

        # Replace placeholders
        prompt = template_content.replace("{video_url}", video_url)
        prompt = prompt.replace("{topic}", topic)
        prompt = prompt.replace("{output_format_spec}", output_format_spec)

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
