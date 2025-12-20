# AI Learning Pipeline - Project Plan

## Project Overview

A two-stage CLI tool for processing educational video content into structured notes (Notion) and flashcards (Anki). Note generation is handled by external multimodal AI (e.g., Google Cloud Studio), while this pipeline manages prompt generation, response processing, and data organization.

**Core Principle**: Topic-aware processing with configurable databases and prompt templates.

---

## Architecture

─────────────
┌──────────────────────

│ Media to be processed e.g.
| Youtube URL, local media, podcasts 

└──────┬──────────────┘

▼

┌─────────────────────┐

│ generate_prompt.py  │  ← Reads topic config + templates

│  - Load template    │

│  - Inject media     │

│  - Add format spec  │

└──────┬──────────────┘

│

▼

[prompt.txt] ──→ (Manual: Paste to Cloud Studio)

│

▼

[Text response]

│

▼

┌──────────────────────┐

│ process_output.py    │  ← Reads topic config

│  - Parse response    │

│  - Map to database   │

│  - Upload to Notion  
| and/or generate Anki │

└──────┬───────────────┘

│

▼

┌──────────────────────┐

│ ✓ Notion Updated     │

│ ✓ Anki Deck Created  │

└──────────────────────┘

---

## Directory Structure

├── .env                          # API keys, secrets

├── .env.example                  # Template for .env

├── .gitignore

├── requirements.txt

├── README.md

│

├── config/

│   ├── TBD

│

├── templates/

│   ├── base_prompt.txt          # Default prompt template

│   ├── cooking.txt              # Cooking-specific template

│   └── general.txt              # General educational content

│   |── ...

├── src/

│   ├── init.py

│   ├── models.py                # Data classes (Note, Flashcard, etc.)

│   ├── config_loader.py         # Load and validate configs

│   ├── prompt_generator.py      # Generate prompts from templates

│   ├── response_parser.py       # Parse and validate AI JSON responses

│   ├── notion_client.py         # Notion API interactions

│   └── anki_generator.py        # Generate Anki decks

│

├── scripts/

│   ├── generate_prompt.py       # CLI: Generate prompt

│   └── process_output.py        # CLI: Process AI response

│

├── output/

│   ├── prompts/                 # Generated prompts (timestamped)

│   ├── responses/               # AI responses (for reference)

│   └── anki/                    # Generated .apkg files

│

└── tests/

├── test_config_loader.py

├── test_response_parser.py

└── fixtures/

└── sample_response.json

---

## Tech Stack

```txt
# requirements.txt
python-dotenv==1.0.0
pyyaml==6.0.1
notion-client==2.2.1
genanki==0.13.0
pydantic==2.5.0          # For data validation
click==8.1.7             # For CLI interface
rich==13.7.0             # For pretty CLI output

Python Version: 3.10+
```

## Configuration Files

### .env
```
NOTION_API_KEY=secret_xxxxx
DEFAULT_TOPIC=general
```

### config/topics.yaml

```
topics:
  cooking:
    notion_database_id: "abc123def456"
    anki_deck_name: "Cooking & Recipes"
    prompt_template: "cooking.txt"
    notion_schema:
      required_fields:
        - Title
        - Source
        - DateAdded
        - Type
      custom_fields:
        - Cuisine          # select
        - Difficulty       # select
        - Ingredients      # rich_text
        - Instructions     # rich_text
        - CookTime         # number
    anki_tags:
      - cooking
      - recipes
  
  general:
    notion_database_id: "xyz789uvw012"
    anki_deck_name: "General Learning"
    prompt_template: "general.txt"
    notion_schema:
      required_fields:
        - Title
        - Source
        - DateAdded
        - Type
        - Summary
      custom_fields: []
    anki_tags:
      - learning

# Add more topics as needed
```

### config/defaults.yaml

```
anki:
  model_id: 1607392319  # Basic model ID
  deck_id_base: 2000000000

output:
  prompts_dir: "output/prompts"
  responses_dir: "output/responses"
  anki_dir: "output/anki"

notion:
  default_page_icon: "📚"
  ```

### src/models.py

```
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
from datetime import datetime

class Flashcard(BaseModel):
    front: str
    back: str
    tags: List[str] = []

class Note(BaseModel):
    title: str
    summary: str
    key_points: List[str] = []
    database_fields: Dict[str, Any] = {}  # Topic-specific fields

Add more as needed
```

## Implementation Phases

Phase 1: Configuration & Core Infrastructure


Task 1.1: Set up project structure


- Create directory structure as specified

- Initialize virtual environment

- Create requirements.txt and install dependencies

- Set up .env.example and .gitignore

Task 1.2: Implement configuration loader


- src/config_loader.py: Load topics.yaml and defaults.yaml

- Validate required fields using Pydantic

- Provide helper functions: get_topic_config(topic_name), list_topics()

- Handle missing configs gracefully with error messages

Task 1.3: Create data models


- Implement base Pydantic models in src/models.py

- Add validation rules (non-empty strings, valid URLs, etc.)

Acceptance Criteria:


- Can load topics config and access cooking database ID

- Invalid configs raise clear error messages

- All models validate correctly

### Phase 2: Prompt Generation


Task 2.1: Create prompt templates


- templates/base_prompt.txt: Generic structure with placeholders

- templates/cooking.txt: Cooking-specific instructions

- templates/general.txt: General educational content

- Use placeholders: {video_url}, {topic}, {output_format_spec}

Sample prompt template
```
You are analyzing a cooking video from YouTube.

VIDEO URL: {video_url}

Please watch the entire video and extract:

1. RECIPE DETAILS
   - Title/Name of the dish
   - Cuisine type (e.g., Italian, Japanese, American)
   - Difficulty level (Beginner, Intermediate, Advanced)
   - Estimated cook time in minutes
   - Complete ingredients list with quantities
   - Step-by-step instructions

2. KEY LEARNING POINTS
   - Cooking techniques demonstrated
   - Tips and tricks mentioned
   - Common mistakes to avoid
   - Ingredient substitutions suggested

3. FLASHCARDS
   Create flashcards for:
   - Important cooking techniques
   - Key timing/temperature information
   - Ingredient knowledge
   - Troubleshooting tips
   
   Make cards specific and testable. Include context when needed.

REQUIRED OUTPUT FORMAT (JSON):
{output_format_spec}

Ensure all fields are populated. For ingredients and instructions, use clear formatting.
```

Task 2.2: Implement prompt generator


- src/prompt_generator.py:
	- Load template based on topic

	- Replace placeholders with actual values

	- Inject JSON output schema based on topic's Notion schema

	- Return formatted prompt string


Task 2.3: Build CLI for prompt generation


- scripts/generate_prompt.py:
	- Arguments: --url, --topic, --output (optional, defaults to stdout)

	- Load topic config

	- Generate prompt using prompt_generator

	- Save to output/prompts/{topic}_{timestamp}.txt

	- Print to stdout for easy copy-paste

	- Use rich for pretty formatting

Example usage
```
python scripts/generate_prompt.py \
  --url "https://youtube.com/watch?v=abc123" \
  --topic cooking \
  --output output/prompts/cooking_20250117.txt
```

### Phase 3: Response Processing - Parsing


Task 3.1: Implement response parser


- src/response_parser.py:
	- Read JSON file or string

	- Validate against AIResponse model

	- Extract notes and/or flashcards

	- Return structured data or raise validation errors


Task 3.2: Add error handling


- Handle malformed JSON

- Handle missing required fields

- Provide helpful error messages for fixing issues

- Option to parse "partially" and warn about issues

Acceptance Criteria:


- Successfully parses valid AI responses

- Clear error messages for invalid responses

- Unit tests with sample responses


---

### Phase 4: Response Processing - Notion Integration


Task 4.1: Implement Notion client wrapper


- src/notion_client.py:
	- Initialize with API key from .env

  - Integrate with Notion MCP

	- Map Note fields to Notion properties based on topic schema

	- Handle different Notion field types (title, rich_text, select, number, url, date)

	- Error handling for API failures


Task 4.2: Implement field mapping logic


- Map generic fields: Title, Source URL, DateAdded, Type

- Map topic-specific fields dynamically based on notion_schema retrieved from Notion MCP

- Convert data types appropriately (strings → rich_text blocks, lists → bulleted lists)

- Handle missing optional fields

Task 4.3: Build content blocks

- Convert summary to paragraph block

- Convert key_points to bulleted list

- Add Instructions and Ingredients as appropriate formatted blocks for cooking

- Preserve structure from AI response

Acceptance Criteria:


- Successfully creates Notion pages in correct database

- All fields map correctly

- Content blocks render properly

- Graceful handling of API rate limits


---

### Phase 5: Response Processing - Anki Generation


Task 5.1: Implement Anki generator


- src/anki_generator.py:
	- Function: create_deck(flashcards, deck_name, tags)

	- Use genanki to create deck with proper model

	- Add all flashcards with tags

	- Return deck object


Task 5.2: Save Anki packages


- Generate unique deck IDs

- Save to output/anki/{topic}_{timestamp}.apkg

- Include metadata note (source video, date created)

Acceptance Criteria:


- Generates valid .apkg files

- Files import successfully into Anki

- Cards have correct tags

- Deck names match config


---

### Phase 6: Main Processing Script


Task 6.1: Build main processor CLI


- scripts/process_output.py:
	- Arguments: --input, --topic, --notion-only, --anki-only

	- Load topic config

	- Parse AI response

	- Upload to Notion (unless --anki-only)

	- Generate Anki deck (unless --notion-only)

	- Print summary with links/file paths


Task 6.2: Add progress indicators


- Use rich.progress for status updates

- Show: Parsing → Uploading to Notion → Generating Anki → Complete

- Display success/error messages clearly

Example Usage:


	python scripts/process_output.py \
	  --input output/responses/cooking_20250117.json \
	  --topic cooking

Output:


	✓ Parsed AI response (1 note, 12 flashcards)
	✓ Created Notion page: "Homemade Pasta Techniques"
	   → https://notion.so/abc123
	✓ Generated Anki deck: output/anki/cooking_20250117.apkg
	   → 12 cards added to "Cooking & Recipes" deck
	
	Done! 🎉

Acceptance Criteria:


- Processes responses end-to-end

- Both Notion and Anki outputs work

- Clear feedback on success/failure

- Handles partial failures (e.g., Notion succeeds but Anki fails)


---

Phase 7: Documentation

Task 7.1: Write README


- Installation instructions

- Configuration setup guide

- Usage examples for both scripts

- How to add new topics

- Troubleshooting common issues

Task 7.2: Add logging


- Use Python logging module

- Log to logs/pipeline.log

- Include: timestamps, operations, errors

- Configurable log level via .env

