"""
Unit tests for ResponseParser class.

Tests cover JSON parsing, response validation, error handling,
and conversion to structured data models.
"""

import json
import pytest
from typing import Dict, Any

from response_parser import ResponseParser
from models import AIResponse, Note, Flashcard


class TestResponseParser:
    """Test suite for ResponseParser class."""

    def test_init(self):
        """Test ResponseParser initialization."""
        parser = ResponseParser()
        assert parser is not None

    def test_parse_valid_cooking_response(self):
        """Test parsing a valid cooking topic response."""
        valid_response = {
            "note": {
                "title": "Perfect Chocolate Chip Cookies",
                "summary": "Learn to bake perfect chocolate chip cookies with proper technique and timing.",
                "key_points": [
                    "Cream butter and sugars until light and fluffy",
                    "Mix dry ingredients separately before combining",
                    "Bake at 375°F for 9-11 minutes until golden brown"
                ],
                "database_fields": {
                    "difficulty": "intermediate",
                    "prep_time": "15 minutes",
                    "cook_time": "10 minutes",
                    "servings": 24
                }
            },
            "flashcards": [
                {
                    "front": "What is the ideal oven temperature for chocolate chip cookies?",
                    "back": "375°F (190°C)",
                    "tags": ["baking", "temperature", "cookies"]
                },
                {
                    "front": "Why should you cream butter and sugar until light and fluffy?",
                    "back": "Creates air pockets that help the cookies rise and become tender",
                    "tags": ["technique", "creaming", "texture"]
                }
            ]
        }

        parser = ResponseParser()
        result = parser.parse_response(json.dumps(valid_response))

        assert isinstance(result, AIResponse)
        assert result.note.title == "Perfect Chocolate Chip Cookies"
        assert len(result.flashcards) == 2
        assert result.flashcards[0].front.startswith("What is the ideal")
        assert result.flashcards[0].tags == ["baking", "temperature", "cookies"]

    def test_parse_valid_general_response(self):
        """Test parsing a valid general topic response."""
        valid_response = {
            "note": {
                "title": "Introduction to Machine Learning",
                "summary": "Overview of machine learning concepts, types, and applications.",
                "key_points": [
                    "Machine learning is a subset of artificial intelligence",
                    "Supervised learning uses labeled training data",
                    "Unsupervised learning finds patterns in unlabeled data"
                ],
                "database_fields": {
                    "subject": "Computer Science",
                    "level": "beginner",
                    "duration": "45 minutes"
                }
            },
            "flashcards": [
                {
                    "front": "What is the difference between supervised and unsupervised learning?",
                    "back": "Supervised learning uses labeled data with known outputs, while unsupervised learning finds patterns in unlabeled data",
                    "tags": ["machine_learning", "supervised", "unsupervised"]
                }
            ]
        }

        parser = ResponseParser()
        result = parser.parse_response(json.dumps(valid_response))

        assert isinstance(result, AIResponse)
        assert result.note.title == "Introduction to Machine Learning"
        assert len(result.flashcards) == 1
        assert "supervised" in result.flashcards[0].front.lower()

    def test_parse_minimal_valid_response(self):
        """Test parsing a minimal valid response with required fields only."""
        minimal_response = {
            "note": {
                "title": "Test Title",
                "summary": "Test summary"
            },
            "flashcards": []
        }

        parser = ResponseParser()
        result = parser.parse_response(json.dumps(minimal_response))

        assert isinstance(result, AIResponse)
        assert result.note.title == "Test Title"
        assert result.note.summary == "Test summary"
        assert result.note.key_points == []
        assert result.flashcards == []

    def test_parse_response_invalid_json(self):
        """Test parsing response with invalid JSON."""
        invalid_json = '{"note": {"title": "Test"}, "flashcards": []'  # Missing closing brace

        parser = ResponseParser()

        with pytest.raises(ValueError, match="Invalid JSON format"):
            parser.parse_response(invalid_json)

    def test_parse_response_malformed_structure(self):
        """Test parsing response with correct JSON but malformed structure."""
        malformed_response = {
            "note": "This should be an object, not a string",
            "flashcards": []
        }

        parser = ResponseParser()

        with pytest.raises(ValueError, match="Response structure validation failed"):
            parser.parse_response(json.dumps(malformed_response))

    def test_parse_response_missing_required_fields(self):
        """Test parsing response missing required note fields."""
        missing_title = {
            "note": {
                "summary": "Missing title field"
            },
            "flashcards": []
        }

        parser = ResponseParser()

        with pytest.raises(ValueError, match="Response structure validation failed"):
            parser.parse_response(json.dumps(missing_title))

    def test_parse_response_empty_flashcards(self):
        """Test parsing response with empty flashcards array."""
        response_with_empty_flashcards = {
            "note": {
                "title": "Test Title",
                "summary": "Test summary"
            },
            "flashcards": []
        }

        parser = ResponseParser()
        result = parser.parse_response(json.dumps(response_with_empty_flashcards))

        assert isinstance(result, AIResponse)
        assert result.flashcards == []

    def test_parse_response_special_characters(self):
        """Test parsing response with special characters and unicode."""
        special_response = {
            "note": {
                "title": "Título con acentos: naïve café",
                "summary": "Summary with émojis 🎉 and spëcial chärs",
                "key_points": [
                    "Point with symbols: α + β = γ",
                    "Point with quotes: \"Hello World\""
                ]
            },
            "flashcards": [
                {
                    "front": "Question with unicode: ¿Qué pasa?",
                    "back": "Answer with symbols: → ← ↑ ↓",
                    "tags": ["unicode", "special_chars"]
                }
            ]
        }

        parser = ResponseParser()
        result = parser.parse_response(json.dumps(special_response))

        assert isinstance(result, AIResponse)
        assert " naïve café" in result.note.title
        assert "🎉" in result.note.summary
        assert "¿Qué pasa?" in result.flashcards[0].front

    def test_parse_response_large_content(self):
        """Test parsing response with large content."""
        # Create a response with many flashcards and long content
        large_flashcards = []
        for i in range(50):
            large_flashcards.append({
                "front": f"Question {i} with substantial content that tests parsing limits",
                "back": f"Answer {i} with detailed explanation that contains enough text to test memory handling and processing capabilities",
                "tags": [f"tag{i}", "large_content"]
            })

        large_response = {
            "note": {
                "title": "Comprehensive Topic with Extensive Content",
                "summary": "A very detailed summary that covers multiple aspects of the topic with comprehensive information and thorough explanations.",
                "key_points": [f"Key point {i}: Detailed explanation of concept {i}" for i in range(20)]
            },
            "flashcards": large_flashcards
        }

        parser = ResponseParser()
        result = parser.parse_response(json.dumps(large_response))

        assert isinstance(result, AIResponse)
        assert len(result.flashcards) == 50
        assert len(result.note.key_points) == 20

    def test_parse_response_nested_json_strings(self):
        """Test parsing response where AI accidentally puts JSON as strings."""
        # Some AI models might return JSON with nested JSON strings
        nested_json_response = {
            "note": {
                "title": "Test Title",
                "summary": "Test summary"
            },
            "flashcards": [
                {
                    "front": "Question?",
                    "back": "Answer",
                    "tags": ["test"]
                }
            ]
        }

        # Convert to JSON string to simulate AI response format
        json_string = json.dumps(nested_json_response)

        parser = ResponseParser()
        result = parser.parse_response(json_string)

        assert isinstance(result, AIResponse)
        assert result.note.title == "Test Title"

    def test_validate_json_valid_input(self):
        """Test JSON validation with valid input."""
        valid_json = '{"test": "value"}'
        parser = ResponseParser()

        result = parser.validate_json(valid_json)
        assert result == {"test": "value"}

    def test_validate_json_invalid_input(self):
        """Test JSON validation with invalid input."""
        invalid_json = '{"test": "value"'  # Missing closing brace
        parser = ResponseParser()

        with pytest.raises(ValueError, match="Invalid JSON format"):
            parser.validate_json(invalid_json)

    def test_create_structured_data_valid_input(self):
        """Test conversion of raw dict to AIResponse model."""
        raw_data = {
            "note": {
                "title": "Test Note",
                "summary": "Test summary",
                "key_points": ["Point 1", "Point 2"],
                "database_fields": {"field": "value"}
            },
            "flashcards": [
                {
                    "front": "Front",
                    "back": "Back",
                    "tags": ["tag1", "tag2"]
                }
            ]
        }

        parser = ResponseParser()
        result = parser.create_structured_data(raw_data)

        assert isinstance(result, AIResponse)
        assert isinstance(result.note, Note)
        assert isinstance(result.flashcards[0], Flashcard)

    def test_create_structured_data_invalid_input(self):
        """Test conversion with invalid input data."""
        invalid_data = {
            "note": {
                "title": 123,  # Should be string
                "summary": "Test summary"
            },
            "flashcards": []
        }

        parser = ResponseParser()

        with pytest.raises(ValueError, match="Note 'title' field must be a string"):
            parser.create_structured_data(invalid_data)

    # Additional edge case tests could be added:
    # - Responses with null values
    # - Extremely nested structures
    # - Responses with circular references (though JSON doesn't support this)
    # - Responses with binary data encoded as strings
    # - Concurrent parsing (threading considerations)
