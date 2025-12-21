"""
Anki deck generation for the AI Learning Pipeline.

This module handles creating Anki decks from flashcards with proper formatting
and unique deck ID generation.
"""

import genanki
from pathlib import Path
from typing import List
from datetime import datetime
import hashlib

from src.models import Flashcard
from src.config_loader import get_defaults


def generate_deck_id(deck_name: str, timestamp: str) -> int:
    """
    Generate a unique deck ID based on deck name and timestamp.

    Uses SHA256 hash to create deterministic but unique IDs for each deck.
    This ensures decks with the same name but different creation times get different IDs.

    Args:
        deck_name: Name of the Anki deck
        timestamp: ISO timestamp string

    Returns:
        Unique deck ID as integer
    """
    # Create hash from deck name and timestamp
    hash_input = f"{deck_name}_{timestamp}"
    hash_obj = hashlib.sha256(hash_input.encode('utf-8'))

    # Convert first 8 bytes of hash to integer and add to base
    hash_bytes = hash_obj.digest()[:8]
    hash_int = int.from_bytes(hash_bytes, byteorder='big')

    # Get base deck ID from config and add hash
    defaults = get_defaults()
    base_id = defaults.anki.deck_id_base

    # Ensure ID is within Anki's valid range (positive integers)
    return base_id + (hash_int % 1000000)


def create_anki_deck(
    flashcards: List[Flashcard],
    deck_name: str,
    tags: List[str] = None,
    source_url: str = None
) -> genanki.Deck:
    """
    Create an Anki deck from flashcards.

    Args:
        flashcards: List of Flashcard objects to include in deck
        deck_name: Name of the deck
        tags: Additional tags to apply to all cards
        source_url: Source URL for metadata card

    Returns:
        genanki.Deck object ready for packaging
    """
    if tags is None:
        tags = []

    # Generate unique deck ID
    timestamp = datetime.now().isoformat()
    deck_id = generate_deck_id(deck_name, timestamp)

    # Create deck
    deck = genanki.Deck(deck_id, deck_name)

    # Get default model from config
    defaults = get_defaults()
    model = genanki.Model(
        defaults.anki.model_id,
        'Basic',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{Front}}<hr id="answer">{{Back}}',
            },
        ]
    )

    # Add metadata card if source URL provided
    if source_url:
        metadata_card = genanki.Note(
            model=model,
            fields=['Source', f'Generated from: {source_url}'],
            tags=['metadata'] + tags
        )
        deck.add_note(metadata_card)

    # Add flashcards
    for flashcard in flashcards:
        # Combine flashcard tags with deck tags
        card_tags = list(set(flashcard.tags + tags))

        note = genanki.Note(
            model=model,
            fields=[flashcard.front, flashcard.back],
            tags=card_tags
        )
        deck.add_note(note)

    return deck


def save_deck_package(
    deck: genanki.Deck,
    topic: str,
    output_dir: str = None
) -> str:
    """
    Save Anki deck as .apkg file.

    Args:
        deck: genanki.Deck object to package
        topic: Topic name for filename generation
        output_dir: Output directory (uses config default if None)

    Returns:
        Path to the saved .apkg file
    """
    if output_dir is None:
        defaults = get_defaults()
        output_dir = defaults.output.anki_dir

    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{topic}_{timestamp}.apkg"
    filepath = output_path / filename

    # Package and save deck
    genanki.Package(deck).write_to_file(filepath)

    return str(filepath)


def generate_deck_from_flashcards(
    flashcards: List[Flashcard],
    topic: str,
    deck_name: str,
    tags: List[str] = None,
    source_url: str = None,
    output_dir: str = None
) -> str:
    """
    Complete workflow: create deck from flashcards and save as .apkg file.

    Args:
        flashcards: List of flashcards to include
        topic: Topic name for organization
        deck_name: Name of the Anki deck
        tags: Tags to apply to cards
        source_url: Source URL for metadata
        output_dir: Output directory override

    Returns:
        Path to the generated .apkg file
    """
    # Create deck
    deck = create_anki_deck(flashcards, deck_name, tags, source_url)

    # Save package
    filepath = save_deck_package(deck, topic, output_dir)

    return filepath
