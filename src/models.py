from pydantic import BaseModel, ConfigDict, field_validator
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

class NotionConfig(BaseModel):
    database_id: str
    required_fields: List[str]
    additional_instructions: Optional[str] = None

class AnkiConfig(BaseModel):
    deck_name: str
    tags: List[str]

class TopicConfig(BaseModel):
    notion: Optional[NotionConfig] = None
    anki: Optional[AnkiConfig] = None

class TopicsConfig(BaseModel):
    topics: Dict[str, TopicConfig]

class ResponseStructure(BaseModel):
    sample: Dict[str, Any]
    details: str

class ResponseStructures(BaseModel):
    notion: ResponseStructure
    anki: ResponseStructure
