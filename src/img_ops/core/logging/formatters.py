"""
Custom log formatters for the img_ops application.

This module can contain custom `logging.Formatter` subclasses if specific
formatting needs arise that are not covered by the standard format strings,
such as adding colors to console output or complex structured logging.

For Phase 1, we primarily use standard format strings defined in config.py.
This file is a placeholder for future enhancements.
"""
import logging

# Example of a custom formatter (e.g., for adding colors to console)
# This is a basic example and might need a library like 'colorlog' for robust cross-platform colors.
class ConsoleColorFormatter(logging.Formatter):
    """
    A custom formatter to add colors to console log messages based on level.
    Note: ANSI escape codes might not work on all terminals (e.g., Windows cmd by default).
    Consider using a library like 'colorlog' for better cross-platform support if needed.
    """
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    # The background is set with 40 plus the number of the color, and the foreground with 30
    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm" # Bold
    BOLD_SEQ = "\033[1m"

    COLORS = {
        'WARNING': YELLOW,
        'INFO': GREEN, # White or Green often used for INFO
        'DEBUG': BLUE, # Blue or Cyan for DEBUG
        'CRITICAL': MAGENTA, # Magenta or Yellow for CRITICAL
        'ERROR': RED
    }

    def __init__(self, fmt="%(levelname)-8s %(name)s: %(message)s", datefmt=None, style='%', use_colors=True):
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the log record, adding color if enabled and applicable.
        """
        levelname = record.levelname
        if self.use_colors and levelname in self.COLORS:
            # Apply color to the levelname part of the message
            # A more sophisticated approach would parse the format string or color the whole line.
            # This simple version just colors the levelname.
            
            # Original message formatted by the base class
            s = super().format(record)
            
            # Colorize the levelname part (assuming it's at the start or clearly identifiable)
            # This is a naive replacement; a robust solution would involve more complex parsing
            # or formatting the parts of the record before combining them.
            # For example, if fmt is "%(levelname)-8s %(message)s"
            # record.levelname will be "INFO", "ERROR" etc.
            
            # Let's try to color just the levelname in the formatted string
            # This is still a bit naive as it assumes levelname appears as is.
            colored_levelname = self.COLOR_SEQ % (30 + self.COLORS[levelname]) + levelname + self.RESET_SEQ
            
            # Replace the first occurrence of levelname. This might not be perfect for all formats.
            # A better way is to override specific parts of the record before super().format()
            # or build the string piece by piece.
            
            # For simplicity, let's assume the format string starts with levelname or similar
            # and we can prepend/append color codes if we format parts ourselves.
            
            # Alternative: format the message and then color the levelname part
            # This is still not ideal. The best way is to have a format string that
            # allows inserting color codes, or use a library designed for this.
            
            # Let's try a simpler approach for the example: color the whole line.
            # This is often acceptable for console output.
            # s = super().format(record) # Get the formatted string
            # colored_s = self.COLOR_SEQ % (30 + self.COLORS[levelname]) + s + self.RESET_SEQ
            # return colored_s
            
            # A more targeted approach:
            # Temporarily change record.levelname for formatting if the format string uses %(levelname)s
            original_levelname = record.levelname
            record.levelname = f"{self.COLOR_SEQ % (30 + self.COLORS[levelname])}{original_levelname}{self.RESET_SEQ}"
            formatted_message = super().format(record)
            record.levelname = original_levelname # Restore original for other handlers
            return formatted_message
            
        else:
            return super().format(record)

# To use this formatter, you would add it to your config.py:
# 'formatters': {
#     'console_color': {
#         '()': 'img_ops.core.logging.formatters.ConsoleColorFormatter', # Use '()' for custom class
#         'format': '[%(levelname)-8s] %(name)s: %(message)s', # Example format
#         'use_colors': True # Optional: control color usage
#     }
# },
# 'handlers': {
#     'console': {
#         'class': 'logging.StreamHandler',
#         'level': 'INFO',
#         'formatter': 'console_color', # Use the custom formatter
#         ...
#     }
# }

if __name__ == '__main__':
    # Example of using the ConsoleColorFormatter
    logger = logging.getLogger('color_test')
    logger.setLevel(logging.DEBUG)
    
    # Basic console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # Using the custom formatter
    formatter = ConsoleColorFormatter(fmt='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s', 
                                      datefmt='%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    # Test without colors
    formatter_no_color = ConsoleColorFormatter(fmt='%(asctime)s [%(levelname)-8s] %(name)s: %(message)s', 
                                               datefmt='%H:%M:%S', use_colors=False)
    ch_no_color = logging.StreamHandler()
    ch_no_color.setFormatter(formatter_no_color)
    
    logger_no_color = logging.getLogger('no_color_test')
    logger_no_color.addHandler(ch_no_color)
    logger_no_color.setLevel(logging.DEBUG)

    print("\n--- Test without colors ---")
    logger_no_color.info("Info without color.")
    logger_no_color.error("Error without color.")