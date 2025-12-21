"""
Configuration loader for AI Learning Pipeline.

Loads and validates configuration files using Pydantic models.
Provides helper functions for accessing topic configurations.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional

from src.models import TopicsConfig, DefaultsConfig, TopicConfig


class ConfigLoader:
    """Loads and manages configuration for the AI Notetaking Pipeline."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize the configuration loader.

        Args:
            config_dir: Path to the configuration directory (default: "config")
        """
        self.config_dir = Path(config_dir)
        self._topics_config: Optional[TopicsConfig] = None
        self._defaults_config: Optional[DefaultsConfig] = None

    def load_topics_config(self) -> TopicsConfig:
        """
        Load topics configuration from YAML file.

        Returns:
            TopicsConfig: Validated topics configuration

        Raises:
            FileNotFoundError: If topics.yaml is not found
            ValueError: If configuration is invalid
        """
        topics_file = self.config_dir / "topics.yaml"
        if not topics_file.exists():
            raise FileNotFoundError(f"Topics configuration file not found: {topics_file}")

        try:
            with open(topics_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            self._topics_config = TopicsConfig(**data)
            return self._topics_config
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in topics configuration: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load topics configuration: {e}")

    def load_defaults_config(self) -> DefaultsConfig:
        """
        Load defaults configuration from YAML file.

        Returns:
            DefaultsConfig: Validated defaults configuration

        Raises:
            FileNotFoundError: If defaults.yaml is not found
            ValueError: If configuration is invalid
        """
        defaults_file = self.config_dir / "defaults.yaml"
        if not defaults_file.exists():
            raise FileNotFoundError(f"Defaults configuration file not found: {defaults_file}")

        try:
            with open(defaults_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            self._defaults_config = DefaultsConfig(**data)
            return self._defaults_config
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in defaults configuration: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load defaults configuration: {e}")

    def get_topic_config(self, topic_name: str) -> TopicConfig:
        """
        Get configuration for a specific topic.

        Args:
            topic_name: Name of the topic

        Returns:
            TopicConfig: Configuration for the topic

        Raises:
            ValueError: If topic is not found
        """
        if self._topics_config is None:
            self.load_topics_config()

        if topic_name not in self._topics_config.topics:
            available_topics = list(self._topics_config.topics.keys())
            raise ValueError(f"Topic '{topic_name}' not found. Available topics: {available_topics}")

        return self._topics_config.topics[topic_name]

    def list_topics(self) -> List[str]:
        """
        List all available topic names.

        Returns:
            List[str]: List of topic names
        """
        if self._topics_config is None:
            self.load_topics_config()

        return list(self._topics_config.topics.keys())

    def get_defaults(self) -> DefaultsConfig:
        """
        Get default configuration values.

        Returns:
            DefaultsConfig: Default configuration
        """
        if self._defaults_config is None:
            self.load_defaults_config()

        return self._defaults_config
