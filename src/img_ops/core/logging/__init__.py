"""
Logging package for the img_ops application.

This package provides a centralized logging system based on Python's
standard `logging` module, enhanced with custom handlers and configurations
for file, console, and GUI outputs.

Key components:
- LogManager: Singleton for configuring and accessing loggers.
- get_logger: Convenience function to get a logger instance.
- LoggerMixin: A mixin class for easy logger access in any class.
- DEFAULT_LOG_CONFIG: Default logging configuration dictionary.

Basic Usage:

1. To get a logger in any module:
   ```python
   from img_ops.core.logging import get_logger
   logger = get_logger(__name__)
   logger.info("This is an informational message.")
   logger.error("This is an error message.", exc_info=True)
   ```

2. To use the LoggerMixin in a class:
   ```python
   from img_ops.core.logging import LoggerMixin

   class MyService(LoggerMixin):
       def do_work(self):
           self.logger.debug("Starting work...")
           # ... work ...
           self.logger.info("Work completed.")
   ```

The LogManager is automatically initialized with default settings when the
`img_ops.core.logging.manager` module is first imported. This typically
happens when `get_logger` or `LoggerMixin` is used.

Configuration can be customized by accessing the LogManager instance:
   ```python
   from img_ops.core.logging import get_log_manager
   log_manager = get_log_manager()
   # new_config = { ... }
   # log_manager.configure(new_config)
   ```
"""

# Import key components to make them available at the package level
from .manager import LogManager, get_log_manager, get_logger
from .mixins import LoggerMixin
from .config import DEFAULT_LOG_CONFIG, LOGS_DIR

# Ensure the LogManager singleton is initialized when this package is imported.
# The import of .manager itself already does this, so this is mostly for clarity
# or if someone imports `img_ops.core.logging` directly without submodule access.
_ = get_log_manager()

__all__ = [
    'LogManager',
    'get_log_manager',
    'get_logger',
    'LoggerMixin',
    'DEFAULT_LOG_CONFIG',
    'LOGS_DIR'
]