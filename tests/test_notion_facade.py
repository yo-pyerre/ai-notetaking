"""
Unit tests for the Notion API client.

Tests cover authentication, property mapping, content block creation,
and error handling for the Notion integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.notion_facade import (
    NotionClient,
    NotionAuthenticationError,
    NotionPageCreationError
)
from src.models import Note, TopicConfig, NotionSchema


class TestNotionClient:
    """Test suite for NotionClient class."""

    def test_init_with_api_key(self):
        """Test client initialization with provided API key."""
        with patch('src.notion_facade.NotionClientAPI') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = NotionClient(api_key="test_key")

            assert client.api_key == "test_key"
            mock_client_class.assert_called_once_with(auth="test_key")

    def test_init_with_env_var(self):
        """Test client initialization using environment variable."""
        with patch('src.notion_facade.os.getenv', return_value="env_key"), \
             patch('src.notion_facade.NotionClientAPI') as mock_client_class:

            mock_client = Mock()
            mock_client_class.return_value = mock_client

            client = NotionClient()

            assert client.api_key == "env_key"
            mock_client_class.assert_called_once_with(auth="env_key")

    def test_init_no_api_key(self):
        """Test client initialization fails without API key."""
        with patch('src.notion_facade.os.getenv', return_value=None):
            with pytest.raises(NotionAuthenticationError, match="Notion API key not found"):
                NotionClient()

    def test_init_client_creation_failure(self):
        """Test client initialization fails when Notion client creation fails."""
        with patch('src.notion_facade.os.getenv', return_value="test_key"), \
             patch('src.notion_facade.NotionClientAPI', side_effect=Exception("Connection failed")):

            with pytest.raises(NotionAuthenticationError, match="Failed to initialize Notion client"):
                NotionClient()

    @patch('src.notion_facade.NotionClientAPI')
    def test_create_learning_page_success(self, mock_client_class):
        """Test successful page creation."""
        # Setup
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.pages.create.return_value = {"url": "https://notion.so/test-page"}

        client = NotionClient(api_key="test_key")

        note = Note(
            title="Test Recipe",
            summary="A delicious test recipe",
            key_points=["Step 1", "Step 2"],
            database_fields={"Cuisine": "Italian", "Difficulty": "Easy"}
        )

        schema = NotionSchema(
            required_fields=["Title", "Source", "DateAdded", "Type"],
            custom_fields=["Cuisine", "Difficulty"]
        )

        topic_config = TopicConfig(
            notion_database_id="test_db_id",
            anki_deck_name="Test Deck",
            prompt_template="test.txt",
            notion_schema=schema,
            anki_tags=["test"]
        )

        # Execute
        result = client.create_learning_page(note, topic_config, "https://example.com")

        # Assert
        assert result == "https://notion.so/test-page"
        mock_client.pages.create.assert_called_once()

        call_args = mock_client.pages.create.call_args
        assert call_args[1]["parent"]["database_id"] == "test_db_id"
        assert "properties" in call_args[1]
        assert "children" in call_args[1]

    @patch('src.notion_facade.NotionClientAPI')
    def test_create_learning_page_failure(self, mock_client_class):
        """Test page creation failure handling."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.pages.create.side_effect = Exception("API Error")

        client = NotionClient(api_key="test_key")

        note = Note(title="Test", summary="Test summary", key_points=[])
        schema = NotionSchema(required_fields=["Title"], custom_fields=[])
        topic_config = TopicConfig(
            notion_database_id="test_db_id",
            anki_deck_name="Test Deck",
            prompt_template="test.txt",
            notion_schema=schema,
            anki_tags=["test"]
        )

        with pytest.raises(NotionPageCreationError, match="Failed to create Notion page"):
            client.create_learning_page(note, topic_config)


class TestPropertyMapping:
    """Test property mapping functionality."""

    @patch('src.notion_facade.NotionClientAPI')
    def test_map_properties_basic(self, mock_client_class):
        """Test basic property mapping for required fields."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        note = Note(
            title="Test Title",
            summary="Test summary",
            key_points=["Point 1", "Point 2"]
        )

        schema = NotionSchema(
            required_fields=["Title", "Source", "DateAdded", "Type"],
            custom_fields=[]
        )

        with patch('src.notion_facade.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"

            properties = client._map_properties(note, schema, "https://example.com")

        assert properties["Title"]["title"][0]["text"]["content"] == "Test Title"
        assert properties["Source"]["url"] == "https://example.com"
        assert properties["DateAdded"]["date"]["start"] == "2023-01-01T00:00:00"
        assert properties["Type"]["select"]["name"] == "Learning Note"

    @patch('src.notion_facade.NotionClientAPI')
    def test_map_properties_with_summary_field(self, mock_client_class):
        """Test property mapping when Summary is a required field."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        note = Note(
            title="Test Title",
            summary="Test summary",
            key_points=[]
        )

        schema = NotionSchema(
            required_fields=["Title", "Summary"],
            custom_fields=[]
        )

        properties = client._map_properties(note, schema)

        assert properties["Summary"]["rich_text"][0]["text"]["content"] == "Test summary"

    @patch('src.notion_facade.NotionClientAPI')
    def test_map_properties_custom_fields(self, mock_client_class):
        """Test mapping of custom fields from database_fields."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        note = Note(
            title="Test Title",
            summary="Test summary",
            key_points=[],
            database_fields={
                "Cuisine": "Italian",
                "Difficulty": "Easy",
                "CookTime": 30
            }
        )

        schema = NotionSchema(
            required_fields=["Title"],
            custom_fields=["Cuisine", "Difficulty", "CookTime"]
        )

        properties = client._map_properties(note, schema)

        assert properties["Cuisine"]["select"]["name"] == "Italian"
        assert properties["Difficulty"]["select"]["name"] == "Easy"
        assert properties["CookTime"]["number"] == 30


class TestCustomFieldMapping:
    """Test custom field type mapping."""

    @patch('src.notion_facade.NotionClientAPI')
    def test_map_select_fields(self, mock_client_class):
        """Test mapping of select-type custom fields."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        # Test Cuisine field
        result = client._map_custom_field("Cuisine", "Italian")
        assert result == {"select": {"name": "Italian"}}

        # Test Difficulty field
        result = client._map_custom_field("Difficulty", "Hard")
        assert result == {"select": {"name": "Hard"}}

    @patch('src.notion_facade.NotionClientAPI')
    def test_map_rich_text_fields(self, mock_client_class):
        """Test mapping of rich text custom fields."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        # Test string value
        result = client._map_custom_field("Ingredients", "Flour, sugar, eggs")
        assert result["rich_text"][0]["text"]["content"] == "Flour, sugar, eggs"

        # Test list value
        ingredients_list = ["Flour", "Sugar", "Eggs"]
        result = client._map_custom_field("Ingredients", ingredients_list)
        assert "• Flour" in result["rich_text"][0]["text"]["content"]
        assert "• Sugar" in result["rich_text"][0]["text"]["content"]
        assert "• Eggs" in result["rich_text"][0]["text"]["content"]

    @patch('src.notion_facade.NotionClientAPI')
    def test_map_number_field(self, mock_client_class):
        """Test mapping of number-type custom fields."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        # Test valid number
        result = client._map_custom_field("CookTime", 45)
        assert result == {"number": 45}

        # Test string that can be converted
        result = client._map_custom_field("CookTime", "30")
        assert result == {"number": 30}

        # Test invalid value
        result = client._map_custom_field("CookTime", "not-a-number")
        assert result == {"number": 0}

    @patch('src.notion_facade.NotionClientAPI')
    def test_map_unknown_field_type(self, mock_client_class):
        """Test mapping of unknown field types defaults to rich text."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        result = client._map_custom_field("UnknownField", "some value")
        assert result["rich_text"][0]["text"]["content"] == "some value"


class TestContentBlocks:
    """Test content block creation."""

    @patch('src.notion_facade.NotionClientAPI')
    def test_create_content_blocks_with_summary_and_points(self, mock_client_class):
        """Test content block creation with both summary and key points."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        note = Note(
            title="Test Title",
            summary="This is a summary",
            key_points=["Point 1", "Point 2", "Point 3"]
        )

        blocks = client._create_content_blocks(note)

        # Should have summary paragraph + 3 bullet points
        assert len(blocks) == 4

        # First block should be summary paragraph
        assert blocks[0]["type"] == "paragraph"
        assert blocks[0]["paragraph"]["rich_text"][0]["text"]["content"] == "This is a summary"

        # Remaining blocks should be bullet points
        for i, point in enumerate(note.key_points, 1):
            assert blocks[i]["type"] == "bulleted_list_item"
            assert blocks[i]["bulleted_list_item"]["rich_text"][0]["text"]["content"] == point

    @patch('src.notion_facade.NotionClientAPI')
    def test_create_content_blocks_summary_only(self, mock_client_class):
        """Test content block creation with summary only."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        note = Note(
            title="Test Title",
            summary="Summary only",
            key_points=[]
        )

        blocks = client._create_content_blocks(note)

        assert len(blocks) == 1
        assert blocks[0]["type"] == "paragraph"
        assert blocks[0]["paragraph"]["rich_text"][0]["text"]["content"] == "Summary only"

    @patch('src.notion_facade.NotionClientAPI')
    def test_create_content_blocks_points_only(self, mock_client_class):
        """Test content block creation with key points only."""
        mock_client_class.return_value = Mock()
        client = NotionClient(api_key="test_key")

        note = Note(
            title="Test Title",
            summary="",
            key_points=["Point A", "Point B"]
        )

        blocks = client._create_content_blocks(note)

        # Should only have bullet points (no summary block since summary is empty)
        assert len(blocks) == 2
        assert blocks[0]["type"] == "bulleted_list_item"
        assert blocks[1]["type"] == "bulleted_list_item"
