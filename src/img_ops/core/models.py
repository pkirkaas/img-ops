"""
Core data models for the application.

This module will define data structures used throughout the
core logic, such as representations for image files,
configuration data, etc.
"""
from dataclasses import dataclass


@dataclass
class ImageFile:
    """
    Represents an image file and its properties.
    """
    path: str
    # Add other relevant properties like size, dimensions, metadata_obj, etc.


@dataclass
class ConfigData:
    """
    Represents application configuration settings.
    """
    # Add configuration fields as needed
    pass

# Add other core models as the application evolves
