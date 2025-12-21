"""
Unit tests for PromptGenerator class.

Tests cover template loading, JSON schema generation, prompt generation,
placeholder replacement, and file operations.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from src.prompt_generator import PromptGenerator


class TestPromptGenerator:
    """Test suite for PromptGenerator class."""

    def test_init_default_templates_dir(self):
        """Test default templates directory initialization."""
        generator = PromptGenerator()
        assert generator.templates_dir == Path("templates")

    def test_init_custom_templates_dir(self):
        """Test custom templates directory initialization."""
        custom_dir = "/custom/templates"
        generator = PromptGenerator(custom_dir)
        assert generator.templates_dir == Path(custom_dir)

    def test_load_template_success(self, tmp_path: Path):
        """Test successful template loading."""
        # Create test template
        template_file = tmp_path / "test_template.txt"
        test_content = "Test template content with {placeholder}"
        template_file.write_text(test_content)

        generator = PromptGenerator(str(tmp_path))
        result = generator.load_template("test_template.txt")

        assert result == test_content

    def test_load_template_file_not_found(self):
        """Test template loading when file doesn't exist."""
        generator = PromptGenerator("/nonexistent/directory")

        with pytest.raises(FileNotFoundError, match="Template file not found"):
            generator.load_template("missing.txt")

    def test_load_template_special_characters(self, tmp_path: Path):
        """Test template loading with special characters and unicode."""
        template_file = tmp_path / "unicode_template.txt"
        test_content = "Template with émojis 🎉 and spëcial chärs"
        template_file.write_text(test_content, encoding='utf-8')

        generator = PromptGenerator(str(tmp_path))
        result = generator.load_template("unicode_template.txt")

        assert result == test_content

    def test_get_output_format_spec_structure(self):
        """Test that output format spec has correct JSON structure."""
        generator = PromptGenerator()
        spec = generator.get_output_format_spec()

        # Check for JSON code block markers
        assert "```json" in spec
        assert "```" in spec

        # Check for required structure elements
        assert '"note":' in spec
        assert '"flashcards":' in spec
        assert '"title"' in spec
        assert '"summary"' in spec
        assert '"key_points"' in spec
        assert '"database_fields"' in spec
        assert '"front"' in spec
        assert '"back"' in spec
        assert '"tags"' in spec

    def test_get_output_format_spec_sample_data(self):
        """Test that output format spec contains expected sample data."""
        generator = PromptGenerator()
        spec = generator.get_output_format_spec()

        # Check for sample content
        assert '"Sample Title"' in spec
        assert '"Key point 1"' in spec
        assert '"Question?"' in spec
        assert '"tag1"' in spec

    def test_get_output_format_spec_explanation(self):
        """Test that output format spec includes field explanations."""
        generator = PromptGenerator()
        spec = generator.get_output_format_spec()

        # Check for explanation text
        assert "note\":" in spec  # Note field explanation
        assert "flashcards\":" in spec  # Flashcards field explanation
        assert "title\":" in spec  # Title field explanation

    def test_generate_prompt_cooking_topic(self, prompt_generator: PromptGenerator, test_video_url: str):
        """Test prompt generation for cooking topic."""
        result = prompt_generator.generate_prompt(test_video_url, "cooking")

        # Check that placeholders were replaced
        assert test_video_url in result
        assert "cooking" in result

        # Check that JSON schema was injected
        assert "```json" in result
        assert '"note":' in result
        assert '"flashcards":' in result

        # Check for cooking-specific content
        assert "culinary educator" in result
        assert "cooking techniques" in result

    def test_generate_prompt_general_topic(self, prompt_generator: PromptGenerator, test_video_url: str):
        """Test prompt generation for general topic."""
        result = prompt_generator.generate_prompt(test_video_url, "general")

        # Check that placeholders were replaced
        assert test_video_url in result
        assert "general" in result

        # Check that JSON schema was injected
        assert "```json" in result
        assert '"note":' in result

        # Check for general-specific content
        assert "educational content analyst" in result
        assert "general knowledge" in result

    def test_generate_prompt_invalid_topic(self, prompt_generator: PromptGenerator, test_video_url: str):
        """Test prompt generation with invalid topic."""
        with pytest.raises(ValueError, match="Unsupported topic 'invalid'"):
            prompt_generator.generate_prompt(test_video_url, "invalid")

    def test_generate_prompt_custom_template(self, sample_templates_dir: Path, test_video_url: str):
        """Test prompt generation with custom template override."""
        generator = PromptGenerator(str(sample_templates_dir))

        result = generator.generate_prompt(test_video_url, "cooking", "custom.txt")

        # Should use custom template content
        assert "Custom template:" in result
        assert test_video_url in result
        assert "cooking" in result

    def test_generate_prompt_special_characters_in_url(self, prompt_generator: PromptGenerator):
        """Test prompt generation with special characters in URL."""
        special_url = "https://example.com/video?param=value&other=🎉"
        result = prompt_generator.generate_prompt(special_url, "cooking")

        assert special_url in result

    def test_generate_prompt_missing_placeholders_in_template(self, tmp_path: Path, test_video_url: str):
        """Test prompt generation when template doesn't have all placeholders."""
        # Create template without {output_format_spec}
        template_file = tmp_path / "incomplete.txt"
        template_file.write_text("URL: {video_url} Topic: {topic}")

        generator = PromptGenerator(str(tmp_path))
        result = generator.generate_prompt(test_video_url, "cooking", "incomplete.txt")

        assert test_video_url in result
        assert "cooking" in result
        # Should still work even without all placeholders

    def test_save_prompt_creates_file(self, tmp_path: Path):
        """Test that save_prompt creates the output file."""
        generator = PromptGenerator()
        test_content = "Test prompt content"
        output_path = tmp_path / "test_output.txt"

        generator.save_prompt(test_content, str(output_path))

        assert output_path.exists()
        assert output_path.read_text() == test_content

    def test_save_prompt_creates_directories(self, tmp_path: Path):
        """Test that save_prompt creates necessary directories."""
        generator = PromptGenerator()
        output_path = tmp_path / "nested" / "directories" / "output.txt"

        generator.save_prompt("content", str(output_path))

        assert output_path.exists()
        assert output_path.parent.exists()
        assert output_path.read_text() == "content"

    def test_save_prompt_utf8_encoding(self, tmp_path: Path):
        """Test that save_prompt uses UTF-8 encoding."""
        generator = PromptGenerator()
        unicode_content = "Content with unicode: émojis 🎉"
        output_path = tmp_path / "unicode_output.txt"

        generator.save_prompt(unicode_content, str(output_path))

        # Read back with UTF-8 to verify encoding
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert content == unicode_content

    @patch('pathlib.Path.mkdir')
    def test_save_prompt_handles_mkdir_error(self, mock_mkdir, tmp_path: Path):
        """Test save_prompt when directory creation fails."""
        mock_mkdir.side_effect = OSError("Permission denied")

        generator = PromptGenerator()
        output_path = tmp_path / "output.txt"

        # Should still attempt to write file
        with pytest.raises(OSError):
            generator.save_prompt("content", str(output_path))

    def test_generate_prompt_integration(self, prompt_generator: PromptGenerator, test_video_url: str):
        """Integration test for complete prompt generation workflow."""
        result = prompt_generator.generate_prompt(test_video_url, "cooking")

        # Verify all components are present
        assert test_video_url in result
        assert "cooking" in result
        assert "```json" in result
        assert '"note":' in result
        assert '"flashcards":' in result
        assert "culinary educator" in result

        # Verify structure
        lines = result.split('\n')
        assert len(lines) > 10  # Should be a substantial prompt

    def test_template_mapping_internal_logic(self):
        """Test the internal topic-to-template mapping logic."""
        generator = PromptGenerator()

        # Test with valid topics
        try:
            generator.generate_prompt("https://test.com", "cooking")
        except FileNotFoundError:
            pass  # Expected since we're not testing file operations

        # Test with invalid topic
        with pytest.raises(ValueError):
            generator.generate_prompt("https://test.com", "invalid_topic")

    # Additional edge case tests could be added here:
    # - Very long URLs
    # - Empty template content
    # - Template with only placeholders
    # - Concurrent access to templates
    # - File system edge cases
