"""
Tests for Anki deck generation functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os

from src.anki_generator import (
    generate_deck_id,
    create_anki_deck,
    save_deck_package,
    generate_deck_from_flashcards
)
from src.models import Flashcard


class TestDeckIdGeneration:
    """Test deck ID generation functionality."""

    def test_generate_deck_id_deterministic(self):
        """Test that same inputs produce same deck ID."""
        deck_name = "Test Deck"
        timestamp = "2025-01-17T10:30:00"

        id1 = generate_deck_id(deck_name, timestamp)
        id2 = generate_deck_id(deck_name, timestamp)

        assert id1 == id2
        assert isinstance(id1, int)
        assert id1 > 0

    def test_generate_deck_id_unique_for_different_inputs(self):
        """Test that different inputs produce different deck IDs."""
        id1 = generate_deck_id("Deck 1", "2025-01-17T10:30:00")
        id2 = generate_deck_id("Deck 2", "2025-01-17T10:30:00")
        id3 = generate_deck_id("Deck 1", "2025-01-17T10:31:00")

        assert id1 != id2
        assert id1 != id3
        assert id2 != id3

    @patch('src.anki_generator.get_defaults')
    def test_generate_deck_id_uses_config_base(self, mock_get_defaults):
        """Test that deck ID uses configured base value."""
        # Mock config
        mock_config = MagicMock()
        mock_config.anki.deck_id_base = 3000000000
        mock_get_defaults.return_value = mock_config

        deck_id = generate_deck_id("Test", "2025-01-17T10:30:00")

        # Should be base + hash modulo
        assert deck_id >= 3000000000
        assert deck_id < 3001000000  # Base + 1M


class TestDeckCreation:
    """Test deck creation functionality."""

    def test_create_anki_deck_basic(self):
        """Test basic deck creation with flashcards."""
        flashcards = [
            Flashcard(front="Question 1", back="Answer 1", tags=["tag1"]),
            Flashcard(front="Question 2", back="Answer 2", tags=["tag2"])
        ]

        deck = create_anki_deck(flashcards, "Test Deck")

        assert deck.name == "Test Deck"
        assert deck.deck_id is not None
        # Should have 2 flashcards
        assert len(deck.notes) == 2

    def test_create_anki_deck_with_tags(self):
        """Test deck creation with additional tags."""
        flashcards = [
            Flashcard(front="Q", back="A", tags=["card_tag"])
        ]

        deck = create_anki_deck(flashcards, "Test Deck", tags=["deck_tag"])

        # Card should have both card and deck tags
        note = deck.notes[0]
        assert "card_tag" in note.tags
        assert "deck_tag" in note.tags

    def test_create_anki_deck_with_source_url(self):
        """Test deck creation includes metadata card when source URL provided."""
        flashcards = [
            Flashcard(front="Q", back="A")
        ]

        deck = create_anki_deck(flashcards, "Test Deck", source_url="https://example.com")

        # Should have metadata card + 1 flashcard = 2 total
        assert len(deck.notes) == 2

        # First note should be metadata
        metadata_note = deck.notes[0]
        assert "Source" in metadata_note.fields[0]
        assert "https://example.com" in metadata_note.fields[1]
        assert "metadata" in metadata_note.tags

    def test_create_anki_deck_empty_flashcards(self):
        """Test deck creation with empty flashcard list."""
        deck = create_anki_deck([], "Empty Deck")

        assert deck.name == "Empty Deck"
        assert len(deck.notes) == 0

    @patch('src.anki_generator.datetime')
    @patch('src.anki_generator.generate_deck_id')
    def test_create_anki_deck_uses_timestamp(self, mock_gen_id, mock_datetime):
        """Test that deck creation uses current timestamp for ID generation."""
        mock_datetime.now.return_value.isoformat.return_value = "2025-01-17T10:30:00"
        mock_gen_id.return_value = 12345

        flashcards = [Flashcard(front="Q", back="A")]
        deck = create_anki_deck(flashcards, "Test")

        mock_gen_id.assert_called_once_with("Test", "2025-01-17T10:30:00")
        assert deck.deck_id == 12345


class TestDeckPackaging:
    """Test deck packaging and saving functionality."""

    def test_save_deck_package_creates_file(self):
        """Test that save_deck_package creates a .apkg file."""
        # Create a simple deck
        flashcards = [Flashcard(front="Test Q", back="Test A")]
        deck = create_anki_deck(flashcards, "Test Deck")

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = save_deck_package(deck, "test_topic", temp_dir)

            # Check file was created
            assert os.path.exists(filepath)
            assert filepath.endswith(".apkg")

            # Check filename format
            filename = os.path.basename(filepath)
            assert filename.startswith("test_topic_")
            assert filename.endswith(".apkg")

    def test_save_deck_package_creates_directory(self):
        """Test that save creates output directory if it doesn't exist."""
        flashcards = [Flashcard(front="Q", back="A")]
        deck = create_anki_deck(flashcards, "Test")

        with tempfile.TemporaryDirectory() as base_dir:
            output_dir = os.path.join(base_dir, "nonexistent", "anki")
            filepath = save_deck_package(deck, "test", output_dir)

            assert os.path.exists(filepath)
            assert os.path.exists(output_dir)

    @patch('src.anki_generator.get_defaults')
    def test_save_deck_package_uses_default_dir(self, mock_get_defaults):
        """Test that save uses default output directory when none specified."""
        mock_config = MagicMock()
        mock_config.output.anki_dir = "/default/anki/dir"
        mock_get_defaults.return_value = mock_config

        flashcards = [Flashcard(front="Q", back="A")]
        deck = create_anki_deck(flashcards, "Test")

        with patch('src.anki_generator.Path.mkdir'):
            with patch('genanki.Package.write_to_file') as mock_write:
                filepath = save_deck_package(deck, "test")

                # Should use default dir (handle both Unix and Windows path separators)
                assert "/default/anki/dir" in filepath.replace("\\", "/")
                assert "test_" in filepath
                assert filepath.endswith(".apkg")


class TestCompleteWorkflow:
    """Test the complete flashcard to .apkg workflow."""

    def test_generate_deck_from_flashcards_complete_workflow(self):
        """Test the complete workflow from flashcards to saved file."""
        flashcards = [
            Flashcard(front="What is 2+2?", back="4", tags=["math"]),
            Flashcard(front="Capital of France?", back="Paris", tags=["geography"])
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = generate_deck_from_flashcards(
                flashcards=flashcards,
                topic="test_topic",
                deck_name="Test Deck",
                tags=["test"],
                source_url="https://example.com",
                output_dir=temp_dir
            )

            # Check file was created
            assert os.path.exists(filepath)
            assert filepath.endswith(".apkg")

            # Check path structure
            path_obj = Path(filepath)
            assert path_obj.parent.name == "test_topic" or str(path_obj.parent) == temp_dir
            assert path_obj.name.startswith("test_topic_")

    @patch('src.anki_generator.create_anki_deck')
    @patch('src.anki_generator.save_deck_package')
    def test_generate_deck_from_flashcards_integration(self, mock_save, mock_create):
        """Test integration of create and save functions."""
        mock_deck = MagicMock()
        mock_create.return_value = mock_deck
        mock_save.return_value = "/path/to/deck.apkg"

        flashcards = [Flashcard(front="Q", back="A")]

        result = generate_deck_from_flashcards(
            flashcards, "topic", "Deck Name", ["tag"], "url", "/output"
        )

        mock_create.assert_called_once_with(
            flashcards, "Deck Name", ["tag"], "url"
        )
        mock_save.assert_called_once_with(mock_deck, "topic", "/output")
        assert result == "/path/to/deck.apkg"
