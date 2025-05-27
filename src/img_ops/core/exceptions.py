"""
Custom exceptions for the core application logic.

Defining custom exceptions allows for more specific error handling
and clearer communication of issues within the application.
"""


class ImgOpsError(Exception):
    """Base class for exceptions in this application."""
    pass


class FileProcessingError(ImgOpsError):
    """Raised when an error occurs during file processing."""

    def __init__(self, filepath: str, message: str):
        self.filepath = filepath
        self.message = f"Error processing file '{filepath}': {message}"
        super().__init__(self.message)


class MetadataError(ImgOpsError):
    """Raised for errors related to metadata handling."""

    def __init__(self, filepath: str, message: str):
        self.filepath = filepath
        self.message = f"Metadata error for file '{filepath}': {message}"
        super().__init__(self.message)


class ConfigError(ImgOpsError):
    """Raised for errors related to configuration."""
    pass

# Add other custom exceptions as needed
