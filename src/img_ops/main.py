"""Main entry point for the img_ops package."""

import sys
from typing import List, Optional


def start(args: Optional[List[str]] = None) -> int:
    """
    Entry point for the 'poetry run start' command.
    Prints a message indicating the script is running.
    
    Args:
        args: Command-line arguments (not used in this simple implementation)
        
    Returns:
        Exit code (0 for success)
    """
    try:
        # Print the main message
        print("In img_ops.main:start with Python & Poetry")
        return 0
    except Exception as e:
        # Simple error handling
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(start())