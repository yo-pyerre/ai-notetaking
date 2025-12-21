"""
Shared test fixtures and configuration for AI Notetaking Pipeline tests.
"""

from pathlib import Path
import pytest
from typing import Generator

from src.prompt_generator import PromptGenerator


@pytest.fixture
def sample_templates_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory with sample templates for testing."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Create sample cooking template
    cooking_template = templates_dir / "cooking.txt"
    cooking_template.write_text("""You are an expert culinary educator specializing in cooking techniques, recipes, and kitchen skills. Analyze this cooking video and create structured learning materials for aspiring cooks and chefs.

VIDEO URL: {video_url}
TOPIC: {topic}

Your specialized focus for cooking content:
- Identify specific cooking techniques, methods, and skills demonstrated
- Extract ingredient lists, measurements, and preparation steps

Please provide your response in the following JSON format:

{output_format_spec}

Cooking-Specific Guidelines:
- Break down complex techniques into step-by-step instructions
- Include timing information for each cooking stage
""")

    # Create sample general template
    general_template = templates_dir / "general.txt"
    general_template.write_text("""You are an expert educational content analyst specializing in general knowledge and learning materials. Analyze this educational video and create structured learning materials for students and lifelong learners.

VIDEO URL: {video_url}
TOPIC: {topic}

Your specialized focus for general educational content:
- Identify key concepts, theories, and principles explained
- Extract important facts, definitions, and terminology

Please provide your response in the following JSON format:

{output_format_spec}

General Education Guidelines:
- Break down complex ideas into understandable components
- Include definitions for technical terms and jargon
""")

    # Create custom template for testing
    custom_template = templates_dir / "custom.txt"
    custom_template.write_text("Custom template: {video_url} - {topic}")

    yield templates_dir


@pytest.fixture
def prompt_generator(sample_templates_dir: Path) -> PromptGenerator:
    """Create PromptGenerator instance with test templates."""
    return PromptGenerator(str(sample_templates_dir))


@pytest.fixture
def test_video_url() -> str:
    """Standard test video URL."""
    return "https://www.youtube.com/watch?v=test123"


@pytest.fixture
def expected_cooking_prompt_start() -> str:
    """Expected start of cooking prompt for testing."""
    return "You are an expert culinary educator specializing in cooking techniques"


@pytest.fixture
def expected_general_prompt_start() -> str:
    """Expected start of general prompt for testing."""
    return "You are an expert educational content analyst specializing in general knowledge"
