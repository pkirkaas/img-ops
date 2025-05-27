"""
Utility functions specific to the Command Line Interface (CLI).

This module can include helper functions for:
- Formatting output for the console.
- Handling user input or confirmations.
- Other CLI-specific tasks not part of the core logic.
"""


def format_success(message: str) -> str:
    """
    Formats a success message for CLI output.
    (Example: could add color using a library like 'rich')
    """
    return f"SUCCESS: {message}"


def format_error(message: str) -> str:
    """
    Formats an error message for CLI output.
    """
    return f"ERROR: {message}"


def confirm_action(prompt: str) -> bool:
    """
    Asks the user for confirmation.

    Args:
      prompt (str): The question to ask the user.

    Returns:
      bool: True if the user confirms, False otherwise.
    """
    response = input(f"{prompt} [y/N]: ").lower().strip()
    return response == "y"

# Add other CLI utility functions as needed.
