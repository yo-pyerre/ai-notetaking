"""
Notion API client for creating pages from AI-processed learning content.

This module provides a clean interface for creating Notion pages with proper
database association, property mapping, and rich content formatting.
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from notion_client import Client
from pydantic import ValidationError

from src.models import Note, TopicConfig, NotionSchema


class NotionClientError(Exception):
    """Base exception for Notion client errors."""
    pass


class NotionAuthenticationError(NotionClientError):
    """Raised when Notion API authentication fails."""
    pass


class NotionPageCreationError(NotionClientError):
    """Raised when page creation fails."""
    pass


class NotionClient:
    """
    Client for interacting with the Notion API to create learning content pages.

    Handles authentication, property mapping, and content block creation for
    structured learning materials.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Notion client.

        Args:
            api_key: Notion integration API key. If not provided, reads from NOTION_TOKEN env var.

        Raises:
            NotionAuthenticationError: If API key is not available or invalid.
        """
        self.api_key = api_key or os.getenv('NOTION_TOKEN')
        if not self.api_key:
            raise NotionAuthenticationError(
                "Notion API key not found. Set NOTION_TOKEN environment variable or pass api_key parameter."
            )

        try:
            self.client = Client(auth=self.api_key)
        except Exception as e:
            raise NotionAuthenticationError(f"Failed to initialize Notion client: {e}")

    def create_learning_page(
        self,
        note: Note,
        topic_config: TopicConfig,
        source_url: Optional[str] = None
    ) -> str:
        """
        Create a new page in the specified Notion database from a learning note.

        Args:
            note: The structured learning note to convert to a Notion page.
            topic_config: Configuration for the topic, including database ID and schema.
            source_url: Optional URL of the source material.

        Returns:
            The URL of the created Notion page.

        Raises:
            NotionPageCreationError: If page creation fails.
        """
        try:
            # Map note data to Notion properties
            properties = self._map_properties(note, topic_config.notion_schema, source_url)

            # Create content blocks for the page
            children = self._create_content_blocks(note)

            # Create the page
            response = self.client.pages.create(
                parent={"database_id": topic_config.notion_database_id},
                properties=properties,
                children=children
            )

            return response["url"]

        except Exception as e:
            raise NotionPageCreationError(f"Failed to create Notion page: {e}")

    def _map_properties(
        self,
        note: Note,
        schema: NotionSchema,
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Map note data to Notion page properties according to the topic schema.

        Args:
            note: The learning note to map.
            schema: The Notion schema defining required and custom fields.
            source_url: Optional source URL.

        Returns:
            Dictionary of Notion property objects.
        """
        properties = {}

        # Handle title (always required)
        properties["Title"] = {
            "title": [
                {
                    "text": {
                        "content": note.title
                    }
                }
            ]
        }

        # Handle source URL if provided
        if source_url:
            properties["Source"] = {
                "url": source_url
            }

        # Handle DateAdded (current timestamp)
        properties["DateAdded"] = {
            "date": {
                "start": datetime.now().isoformat()
            }
        }

        # Handle Type (fixed value for learning content)
        properties["Type"] = {
            "select": {
                "name": "Learning Note"
            }
        }

        # Handle Summary if it's a required field (like for general topic)
        if "Summary" in schema.required_fields:
            properties["Summary"] = {
                "rich_text": [
                    {
                        "text": {
                            "content": note.summary
                        }
                    }
                ]
            }

        # Handle custom fields from note.database_fields
        for field_name in schema.custom_fields:
            if field_name in note.database_fields:
                field_value = note.database_fields[field_name]
                properties[field_name] = self._map_custom_field(field_name, field_value)

        return properties

    def _map_custom_field(self, field_name: str, value: Any) -> Dict[str, Any]:
        """
        Map a custom field value to the appropriate Notion property type.

        Args:
            field_name: Name of the field (used to infer type).
            value: The field value to map.

        Returns:
            Notion property object.
        """
        # For now, handle common field types based on naming conventions
        # This could be extended with a more sophisticated mapping system

        if field_name in ["Cuisine", "Difficulty"]:
            # Select fields
            return {
                "select": {
                    "name": str(value)
                }
            }
        elif field_name in ["Ingredients", "Instructions"]:
            # Rich text fields
            if isinstance(value, list):
                # Convert list to formatted text
                content = "\n".join(f"• {item}" for item in value)
            else:
                content = str(value)

            return {
                "rich_text": [
                    {
                        "text": {
                            "content": content
                        }
                    }
                ]
            }
        elif field_name == "CookTime":
            # Number field
            try:
                return {
                    "number": int(value)
                }
            except (ValueError, TypeError):
                return {
                    "number": 0
                }
        else:
            # Default to rich text for unknown fields
            return {
                "rich_text": [
                    {
                        "text": {
                            "content": str(value)
                        }
                    }
                ]
            }

    def _create_content_blocks(self, note: Note) -> List[Dict[str, Any]]:
        """
        Create Notion content blocks for the page body.

        Args:
            note: The learning note to convert to blocks.

        Returns:
            List of Notion block objects.
        """
        blocks = []

        # Add summary as a paragraph block (if not already in properties)
        if note.summary:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": note.summary
                            }
                        }
                    ]
                }
            })

        # Add key points as a bulleted list
        if note.key_points:
            for point in note.key_points:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": point
                                }
                            }
                        ]
                    }
                })

        return blocks
