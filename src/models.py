from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

class Flashcard(BaseModel):
    model_config = ConfigDict(strict=True)

    front: str
    back: str
    tags: List[str] = []

class Note(BaseModel):
    model_config = ConfigDict(strict=True)

    title: str
    summary: str
    key_points: List[str] = []
    database_fields: Dict[str, Any] = {}  # Topic-specific fields

# Configuration Models
class NotionSchema(BaseModel):
    required_fields: List[str]
    custom_fields: List[str]

class TopicConfig(BaseModel):
    notion_database_id: str
    anki_deck_name: str
    prompt_template: str
    notion_schema: NotionSchema
    anki_tags: List[str]

class TopicsConfig(BaseModel):
    topics: Dict[str, TopicConfig]

class AnkiDefaults(BaseModel):
    model_id: int
    deck_id_base: int

class OutputDefaults(BaseModel):
    prompts_dir: str
    responses_dir: str
    anki_dir: str

class NotionDefaults(BaseModel):
    default_page_icon: str

class DefaultsConfig(BaseModel):
    anki: AnkiDefaults
    output: OutputDefaults
    notion: NotionDefaults

# API Response Models
class AIResponse(BaseModel):
    note: Note
    flashcards: List[Flashcard]

# Add more as needed
