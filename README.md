# AI Notetaking Pipeline

A CLI tool that transforms educational video content into structured learning materials through automated processing with external multimodal AI services.

## 🎯 Overview

The AI Notetaking Pipeline is a two-stage CLI tool that:

1. **Stage 1**: Generates structured prompts for multimodal AI analysis of educational videos
2. **Stage 2**: Processes AI responses into dual outputs:
   - **Notion pages** for detailed, structured notes
   - **Anki decks** for spaced repetition learning

Perfect for self-learners who want to convert video content into actionable study materials without manual note-taking.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Notion API key
- External multimodal AI service (Google Cloud Studio, etc.)

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd ai-notetaking-pipeline
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Notion API key
   ```

3. **Configure topics:**
   - Edit `config/topics.yaml` with your Notion database IDs
   - Customize schemas for your learning domains

## 📋 Workflow

### Stage 1: Generate Prompt
Create a structured prompt for AI analysis:

```bash
python scripts/generate_prompt.py --url "https://youtube.com/watch?v=..." --topic cooking --output my-prompt.txt
```

**Options:**
- `--url, -u`: Video URL to analyze (required)
- `--topic, -t`: Topic domain (cooking, general) (required)
- `--output, -o`: Output file path (optional, defaults to `output/prompts/{topic}_prompt.txt`)
- `--preview, -p`: Preview prompt without saving

### Stage 2: Process AI Response
Convert AI analysis into learning materials:

```bash
python scripts/process_output.py --input response.json --topic cooking --source-url "https://youtube.com/watch?v=..."
```

**Options:**
- `--input, -i`: Path to JSON response from AI service (required)
- `--topic, -t`: Topic domain for processing (required)
- `--source-url, -s`: Original content URL for metadata (optional)
- `--notion-only`: Create only Notion page, skip Anki deck
- `--anki-only`: Create only Anki deck, skip Notion page

## 🎨 Supported Topics

### Cooking
- **Use case**: Recipe videos, cooking tutorials, technique demonstrations
- **Outputs**: Detailed recipes with ingredients, instructions, and technique breakdowns
- **Anki focus**: Cooking methods, ingredient substitutions, timing, safety tips

### General Learning
- **Use case**: Educational videos, lectures, how-to content
- **Outputs**: Structured notes with summaries and key concepts
- **Anki focus**: Important facts, concepts, and procedural knowledge

## ⚙️ Configuration

### Topic Configuration (`config/topics.yaml`)

Each topic defines:
- **Notion database ID**: Where structured notes are stored
- **Anki deck name**: Name for generated flashcard decks
- **Prompt template**: Template file for AI prompting
- **Schema**: Required and custom fields for Notion pages
- **Tags**: Anki tags for organization

### Adding New Topics

1. **Create template** in `templates/` directory
2. **Add configuration** to `config/topics.yaml`
3. **Create Notion database** with matching schema
4. **Test** with sample content

## 📊 Output Formats

### Notion Pages
- **Title**: Auto-generated from content analysis
- **Rich content blocks**: Formatted text, lists, and structured data
- **Custom properties**: Topic-specific metadata (difficulty, cuisine, etc.)
- **Source tracking**: Links back to original content

### Anki Decks
- **Unique deck IDs**: Prevent import conflicts
- **Tagged cards**: Organized by topic and content type
- **Source metadata**: Cards include original URL when provided
- **Standard format**: Compatible with Anki desktop and mobile

## 🛠️ Development

### Project Structure
```
├── src/                    # Core modules
│   ├── models.py          # Data models (Pydantic)
│   ├── config_loader.py   # Configuration management
│   ├── prompt_generator.py # Prompt creation logic
│   ├── response_parser.py  # AI response processing
│   ├── notion_facade.py   # Notion API client
│   └── anki_generator.py  # Anki deck creation
├── scripts/               # CLI entry points
├── config/                # YAML configurations
├── templates/             # Prompt templates
├── output/                # Generated files
└── tests/                 # Unit tests
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_prompt_generator.py
```

