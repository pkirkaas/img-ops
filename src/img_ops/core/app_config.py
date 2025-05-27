"""
Application Configuration Management.

This module provides configuration management for the img-ops application using
Pydantic for data validation and PyYAML for file persistence. It supports
multiple named configurations with validation and file system operations.
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Union, Set
from pydantic import BaseModel, Field, validator, root_validator
from platformdirs import user_config_dir

from .exceptions import ConfigError


class AppConfiguration(BaseModel):
    """
    Single application configuration with validation and defaults.

    Represents a single named configuration for image operations including
    file paths, similarity comparison method, and filtering parameters.
    All fields have sensible defaults and are validated for correctness.

    Attributes:
      name: The name of the configuration (default: "MyConf")
      description: Description of the configuration (default: "MyConf desc")
      paths: List of file paths to process (default: empty list)
      method: Similarity comparison method (default: "phash")
      percent: Similarity percentage threshold 0-100 (default: 90)
    """

    name: str = Field(
        default="MyConf",
        description="The name of the configuration",
        min_length=1,
        max_length=100
    )

    description: str = Field(
        default="MyConf desc",
        description="Description of the configuration",
        max_length=500
    )

    paths: List[str] = Field(
        default_factory=list,
        description="List of file paths to process"
    )

    method: str = Field(
        default="phash",
        description="Similarity comparison method"
    )

    percent: float = Field(
        default=90.0,
        description="Similarity percentage threshold",
        ge=0.0,
        le=100.0
    )

    @validator('name')
    def validate_name(cls, v):
        """Validate configuration name."""
        if not v or not v.strip():
            raise ValueError("Configuration name cannot be empty")
        return v.strip()

    @validator('method')
    def validate_method(cls, v):
        """Validate similarity comparison method."""
        valid_methods = {'phash', 'ssim', 'orb', 'sift', 'surf', 'histogram'}
        if v.lower() not in valid_methods:
            raise ValueError(
                f"Method must be one of: {', '.join(valid_methods)}")
        return v.lower()

    @validator('paths')
    def validate_paths(cls, v):
        """Validate paths list for duplicates and format."""
        if not isinstance(v, list):
            raise ValueError("Paths must be a list")

        # Remove duplicates while preserving order
        seen: Set[str] = set()
        unique_paths = []
        for path in v:
            if not isinstance(path, str):
                raise ValueError(
                    f"All paths must be strings, got {type(path)}")

            # Normalize path for comparison
            normalized_path = os.path.normpath(path)
            if normalized_path not in seen:
                seen.add(normalized_path)
                unique_paths.append(path)

        return unique_paths

    def add_path(self, path: Union[str, Path]) -> bool:
        """
        Add a file path to the configuration.

        Args:
          path: File or directory path to add

        Returns:
          True if path was added, False if it already existed

        Raises:
          ValueError: If path is not a valid string or Path object
        """
        if not isinstance(path, (str, Path)):
            raise ValueError("Path must be a string or Path object")

        path_str = str(path)
        normalized_path = os.path.normpath(path_str)

        # Check if path already exists (normalized comparison)
        for existing_path in self.paths:
            if os.path.normpath(existing_path) == normalized_path:
                return False

        self.paths.append(path_str)
        return True

    def remove_path(self, path: Union[str, Path]) -> bool:
        """
        Remove a file path from the configuration.

        Args:
          path: File or directory path to remove

        Returns:
          True if path was removed, False if it wasn't found
        """
        if not isinstance(path, (str, Path)):
            raise ValueError("Path must be a string or Path object")

        path_str = str(path)
        normalized_path = os.path.normpath(path_str)

        # Find and remove matching path
        for i, existing_path in enumerate(self.paths):
            if os.path.normpath(existing_path) == normalized_path:
                self.paths.pop(i)
                return True

        return False

    def clear_paths(self) -> int:
        """
        Clear all paths from the configuration.

        Returns:
          Number of paths that were removed
        """
        count = len(self.paths)
        self.paths.clear()
        return count

    def get_existing_paths(self) -> List[str]:
        """
        Get list of paths that actually exist in the file system.

        Returns:
          List of paths that exist on disk
        """
        return [path for path in self.paths if os.path.exists(path)]

    def get_missing_paths(self) -> List[str]:
        """
        Get list of paths that don't exist in the file system.

        Returns:
          List of paths that don't exist on disk
        """
        return [path for path in self.paths if not os.path.exists(path)]


class AppConfigManager(BaseModel):
    """
    Manager for multiple application configurations with file persistence.

    Handles loading, saving, and managing multiple named configurations using
    PyYAML for file persistence. Provides methods for CRUD operations on
    configurations and automatic file system management.

    Attributes:
      configurations: Dictionary of named configurations
      config_file_path: Path to the configuration file
    """

    configurations: Dict[str, AppConfiguration] = Field(
        default_factory=dict,
        description="Dictionary of named configurations"
    )

    config_file_path: Optional[str] = Field(
        default=None,
        description="Path to the configuration file"
    )

    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

    def __init__(self, config_file_path: Optional[Union[str, Path]] = None, **data):
        """
        Initialize the configuration manager.

        Args:
          config_file_path: Optional path to configuration file. If None,
                           uses default location in user config directory.
          **data: Additional data for Pydantic model initialization
        """
        if config_file_path is None:
            # Use platform-appropriate config directory
            config_dir = user_config_dir("img-ops", "img-ops")
            config_file_path = os.path.join(config_dir, "app_config.yaml")

        super().__init__(config_file_path=str(config_file_path), **data)

        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)

        # Load existing configuration if file exists
        if os.path.exists(self.config_file_path):
            self.load_from_file()

    def add_configuration(self, config: AppConfiguration) -> bool:
        """
        Add a new configuration.

        Args:
          config: AppConfiguration instance to add

        Returns:
          True if configuration was added, False if name already exists

        Raises:
          ValueError: If config is not an AppConfiguration instance
        """
        if not isinstance(config, AppConfiguration):
            raise ValueError("config must be an AppConfiguration instance")

        if config.name in self.configurations:
            return False

        self.configurations[config.name] = config
        return True

    def get_configuration(self, name: str) -> Optional[AppConfiguration]:
        """
        Get a configuration by name.

        Args:
          name: Name of the configuration to retrieve

        Returns:
          AppConfiguration instance or None if not found
        """
        return self.configurations.get(name)

    def remove_configuration(self, name: str) -> bool:
        """
        Remove a configuration by name.

        Args:
          name: Name of the configuration to remove

        Returns:
          True if configuration was removed, False if not found
        """
        if name in self.configurations:
            del self.configurations[name]
            return True
        return False

    def list_configuration_names(self) -> List[str]:
        """
        Get list of all configuration names.

        Returns:
          List of configuration names
        """
        return list(self.configurations.keys())

    def get_or_create_configuration(self, name: str) -> AppConfiguration:
        """
        Get existing configuration or create new one with default values.

        Args:
          name: Name of the configuration

        Returns:
          AppConfiguration instance (existing or newly created)
        """
        if name in self.configurations:
            return self.configurations[name]

        # Create new configuration with provided name
        new_config = AppConfiguration(
            name=name, description=f"{name} configuration")
        self.configurations[name] = new_config
        return new_config

    def save_to_file(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        Save configurations to YAML file.

        Args:
          file_path: Optional path to save to. If None, uses default path.

        Raises:
          ConfigError: If there's an error writing the file
        """
        if file_path is None:
            file_path = self.config_file_path
        else:
            file_path = str(file_path)

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Convert to dictionary for YAML serialization
            data = {
                'configurations': {
                    name: config.dict() for name, config in self.configurations.items()
                }
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False,
                          sort_keys=True, indent=2)

        except Exception as e:
            raise ConfigError(
                f"Failed to save configuration to {file_path}: {e}")

    def load_from_file(self, file_path: Optional[Union[str, Path]] = None) -> None:
        """
        Load configurations from YAML file.

        Args:
          file_path: Optional path to load from. If None, uses default path.

        Raises:
          ConfigError: If there's an error reading or parsing the file
        """
        if file_path is None:
            file_path = self.config_file_path
        else:
            file_path = str(file_path)

        if not os.path.exists(file_path):
            # File doesn't exist, start with empty configurations
            self.configurations = {}
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if not data or 'configurations' not in data:
                self.configurations = {}
                return

            # Load configurations with validation
            configurations = {}
            for name, config_data in data['configurations'].items():
                try:
                    configurations[name] = AppConfiguration(**config_data)
                except Exception as e:
                    raise ConfigError(f"Invalid configuration '{name}': {e}")

            self.configurations = configurations

        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse YAML file {file_path}: {e}")
        except Exception as e:
            raise ConfigError(
                f"Failed to load configuration from {file_path}: {e}")

    def backup_configuration(self, backup_path: Union[str, Path]) -> None:
        """
        Create a backup of the current configuration.

        Args:
          backup_path: Path where to save the backup

        Raises:
          ConfigError: If backup fails
        """
        try:
            self.save_to_file(backup_path)
        except Exception as e:
            raise ConfigError(f"Failed to create backup: {e}")

    def restore_from_backup(self, backup_path: Union[str, Path]) -> None:
        """
        Restore configuration from a backup file.

        Args:
          backup_path: Path to the backup file

        Raises:
          ConfigError: If restore fails
        """
        if not os.path.exists(backup_path):
            raise ConfigError(f"Backup file does not exist: {backup_path}")

        try:
            self.load_from_file(backup_path)
        except Exception as e:
            raise ConfigError(f"Failed to restore from backup: {e}")

    def get_default_configuration(self) -> AppConfiguration:
        """
        Get or create a default configuration.

        Returns:
          Default AppConfiguration instance
        """
        return self.get_or_create_configuration("Default")


# Convenience function for getting a global config manager instance
_global_config_manager: Optional[AppConfigManager] = None


def get_config_manager(config_file_path: Optional[Union[str, Path]] = None) -> AppConfigManager:
    """
    Get the global configuration manager instance.

    Args:
      config_file_path: Optional path to configuration file for first initialization

    Returns:
      AppConfigManager instance
    """
    global _global_config_manager

    if _global_config_manager is None:
        _global_config_manager = AppConfigManager(
            config_file_path=config_file_path)

    return _global_config_manager
