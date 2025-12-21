"""
ResponseParser - Parses AI-generated JSON responses into structured data models.

This module handles the parsing and validation of responses from external AI services,
converting them into validated Pydantic models for use by Notion and Anki generators.
"""

import json
from typing import Dict, Any, Union
from pydantic import ValidationError

from src.models import AIResponse, Note, Flashcard


class ResponseParser:
    """
    Parser for AI-generated JSON responses.

    Handles JSON parsing, validation, and conversion to structured data models.
    Provides comprehensive error handling for malformed or invalid responses.
    """

    def __init__(self):
        """Initialize the ResponseParser."""
        pass

    def parse_response(self, json_string: str) -> AIResponse:
        """
        Parse a JSON response string into an AIResponse object.

        Args:
            json_string: JSON string containing the AI response

        Returns:
            AIResponse: Validated response object with Note and Flashcards

        Raises:
            ValueError: If JSON is invalid or response structure is malformed
        """
        # Step 1: Validate and parse JSON
        try:
            raw_data = self.validate_json(json_string)
        except ValueError as e:
            raise ValueError(f"Failed to parse AI response: {e}") from e

        # Step 2: Convert to structured data models
        try:
            structured_data = self.create_structured_data(raw_data)
        except ValueError as e:
            raise ValueError(f"Response structure validation failed: {e}") from e

        return structured_data

    def validate_json(self, json_string: str) -> Dict[str, Any]:
        """
        Validate and parse JSON string.

        Args:
            json_string: JSON string to validate

        Returns:
            Dict containing parsed JSON data

        Raises:
            ValueError: If JSON is malformed or invalid
        """
        if not json_string or not json_string.strip():
            raise ValueError("Empty or whitespace-only JSON response")

        try:
            parsed_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}") from e

        if not isinstance(parsed_data, dict):
            raise ValueError("Response must be a JSON object")

        return parsed_data

    def create_structured_data(self, raw_data: Dict[str, Any]) -> AIResponse:
        """
        Convert raw dictionary data into validated AIResponse model.

        Args:
            raw_data: Dictionary containing parsed JSON data

        Returns:
            AIResponse: Validated response object

        Raises:
            ValueError: If data doesn't match expected structure
        """
        try:
            # Validate that required top-level fields exist
            if "note" not in raw_data:
                raise ValueError("Missing required 'note' field in response")
            if "flashcards" not in raw_data:
                raise ValueError("Missing required 'flashcards' field in response")

            # Validate note structure
            note_data = raw_data["note"]
            if not isinstance(note_data, dict):
                raise ValueError("'note' field must be an object")

            # Validate flashcards structure
            flashcards_data = raw_data["flashcards"]
            if not isinstance(flashcards_data, list):
                raise ValueError("'flashcards' field must be an array")

            # Validate note field types explicitly
            if "title" not in note_data:
                raise ValueError("Note missing required 'title' field")
            if "summary" not in note_data:
                raise ValueError("Note missing required 'summary' field")

            if not isinstance(note_data["title"], str):
                raise ValueError("Note 'title' field must be a string")
            if not isinstance(note_data["summary"], str):
                raise ValueError("Note 'summary' field must be a string")

            # Validate flashcards field types explicitly
            for i, flashcard in enumerate(flashcards_data):
                if not isinstance(flashcard, dict):
                    raise ValueError(f"Flashcard at index {i} must be an object")
                if "front" not in flashcard:
                    raise ValueError(f"Flashcard at index {i} missing required 'front' field")
                if "back" not in flashcard:
                    raise ValueError(f"Flashcard at index {i} missing required 'back' field")

                if not isinstance(flashcard["front"], str):
                    raise ValueError(f"Flashcard at index {i} 'front' field must be a string")
                if not isinstance(flashcard["back"], str):
                    raise ValueError(f"Flashcard at index {i} 'back' field must be a string")

            # Create Pydantic models - this will validate all fields and types
            ai_response = AIResponse(**raw_data)

            return ai_response

        except ValidationError as e:
            # Convert Pydantic validation errors to user-friendly messages
            error_details = []
            for error in e.errors():
                field_path = ".".join(str(loc) for loc in error["loc"])
                error_msg = error["msg"]
                error_details.append(f"Field '{field_path}': {error_msg}")

            raise ValueError(f"Response structure validation failed: {'; '.join(error_details)}") from e

        except Exception as e:
            if isinstance(e, ValueError):
                raise  # Re-raise our own ValueErrors
            raise ValueError(f"Response structure validation failed: {str(e)}") from e
