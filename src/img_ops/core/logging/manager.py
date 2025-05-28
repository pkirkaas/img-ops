"""
LogManager for central logging configuration and access.
"""
import logging
import logging.config
import os
from pathlib import Path
from typing import Optional, Dict, Any

from .config import DEFAULT_LOG_CONFIG, LOGS_DIR

# --- Singleton Pattern ---
_log_manager_instance = None

def get_log_manager():
    """
    Returns the singleton instance of LogManager.
    Initializes it if it hasn't been initialized yet.
    """
    global _log_manager_instance
    if _log_manager_instance is None:
        _log_manager_instance = LogManager()
    return _log_manager_instance
# --- End Singleton Pattern ---

class LogManager:
    """
    Manages the application's logging configuration.
    Provides a centralized way to get logger instances.
    """
    _instance: Optional['LogManager'] = None # For singleton access via LogManager.instance()

    def __init__(self):
        """
        Initializes the LogManager.
        This constructor should ideally only be called once (enforced by get_log_manager).
        """
        if LogManager._instance is not None:
            # This can happen if someone tries to instantiate LogManager() directly
            # after get_log_manager() has already created the instance.
            # We can either raise an error or just return the existing instance.
            # For simplicity, we'll rely on get_log_manager for singleton behavior.
            pass

        self._configured = False
        self._log_config: Dict[str, Any] = {}
        self._gui_handler: Optional[logging.Handler] = None # For Phase 2

        # Set the singleton instance if this is the first creation
        if LogManager._instance is None:
            LogManager._instance = self
        
        self.configure() # Auto-configure with defaults on first instantiation

    @staticmethod
    def instance() -> 'LogManager':
        """Provides access to the singleton instance of LogManager."""
        return get_log_manager()

    def _ensure_logs_dir_exists(self):
        """
        Ensures that the directory specified by LOGS_DIR in the config exists.
        """
        # LOGS_DIR is relative to the project root.
        # Assuming the project root is the current working directory when the app starts,
        # or that this script is run from a context where Path(".") makes sense.
        # For more robustness, one might pass the project root path during configuration.
        project_root = Path(".") # This might need adjustment based on execution context
        logs_path = project_root / LOGS_DIR
        try:
            logs_path.mkdir(parents=True, exist_ok=True)
            # print(f"Log directory ensured: {logs_path.resolve()}") # For debugging
        except OSError as e:
            # Fallback: log to console if directory creation fails
            print(f"Warning: Could not create log directory {logs_path}. Logging to console only. Error: {e}")
            # Potentially disable file handler in config if this happens
            if 'file_rotating' in self._log_config.get('handlers', {}):
                # This is a bit tricky as the config is already loaded.
                # A better approach might be to try creating dir, then load config,
                # and if dir creation failed, modify config before dictConfig.
                # For now, this warning is the primary action.
                pass


    def configure(self, config: Optional[Dict[str, Any]] = None, app_name: str = "img_ops"):
        """
        Configures the logging system using a dictionary-based configuration.
        If no config is provided, uses DEFAULT_LOG_CONFIG.

        Args:
            config (Optional[Dict[str, Any]]): A logging configuration dictionary.
                                               Defaults to DEFAULT_LOG_CONFIG.
            app_name (str): The base name for loggers (e.g., 'img_ops').
        """
        if self._configured and config is None:
            # Already configured with defaults, and no new config provided, so do nothing.
            return

        self._log_config = config if config is not None else DEFAULT_LOG_CONFIG.copy()
        
        # Ensure logs directory exists before setting up file handlers
        self._ensure_logs_dir_exists()

        try:
            logging.config.dictConfig(self._log_config)
            self._configured = True
            # print("LogManager: Logging configured successfully.") # For debugging
        except Exception as e:
            # Fallback to basic console logging if configuration fails
            logging.basicConfig(level=logging.INFO)
            logging.error(f"LogManager: Failed to configure logging with dictConfig: {e}. Falling back to basicConfig.", exc_info=True)
            self._configured = False # Mark as not (properly) configured

        # Set the root logger for the application if not already set by dictConfig
        # The root logger for the app (e.g., 'img_ops') can be obtained via get_logger(app_name)
        # Its level and handlers are typically defined in the 'loggers' section of the config.

    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Retrieves a logger instance. If name is None, returns the root logger
        for the application (e.g., 'img_ops').

        Args:
            name (Optional[str]): The name of the logger. Typically __name__ from the calling module.
                                  If None, returns the application's root logger.

        Returns:
            logging.Logger: The configured logger instance.
        """
        if not self._configured:
            # Attempt to configure with defaults if not done yet.
            # This ensures that even if configure() wasn't explicitly called,
            # get_logger() will try to set up a working logging system.
            self.configure()
            if not self._configured: # If configuration still failed
                # Return a basic logger as a last resort
                return logging.getLogger(name or "img_ops_fallback")


        # If name is like 'img_ops.module.submodule', it will inherit from 'img_ops' logger if configured.
        # If name is just 'module.submodule', it will be relative to the global root logger.
        # It's common practice to use __name__ which gives 'img_ops.core.logging.manager' for this file.
        
        # The 'loggers' section in DEFAULT_LOG_CONFIG configures the '' (root) logger.
        # If you want a specific base logger for the app, like 'img_ops',
        # you'd add an entry for 'img_ops' in the 'loggers' section.
        # For now, using __name__ will create loggers like 'img_ops.core.module',
        # which will by default propagate to the configured root logger ('').
        
        if name:
            # Ensure the name is prefixed with the app's base if it's not already
            # This helps in organizing loggers under a common application namespace.
            # However, standard practice is to use __name__ directly.
            # Let's stick to standard practice: logger = logging.getLogger(__name__)
            # The configuration for 'img_ops' or '' (root) will catch these.
            return logging.getLogger(name)
        else:
            # Return the application's "root" logger, which might be the global root ''
            # or a specific one like 'img_ops' if defined as such.
            # For now, let's assume the global root logger is the main one for the app.
            return logging.getLogger() # Returns the root logger ('')

    def add_gui_handler(self, handler: logging.Handler):
        """
        Adds a GUI-specific handler to the root logger or a designated app logger.
        (To be implemented in Phase 2)

        Args:
            handler (logging.Handler): The GUI handler instance.
        """
        self._gui_handler = handler
        # Example: Get the application's root logger and add the handler
        # app_root_logger = self.get_logger() # Gets the '' logger
        # app_root_logger.addHandler(self._gui_handler)
        # print(f"LogManager: GUI handler {handler} added to logger {app_root_logger.name}.")
        pass # Placeholder for Phase 2

    def set_level(self, level_name: str, logger_name: Optional[str] = None):
        """
        Sets the logging level for a specific logger or the root logger.

        Args:
            level_name (str): The logging level (e.g., 'DEBUG', 'INFO').
            logger_name (Optional[str]): The name of the logger. If None, sets for the root logger.
        """
        level = getattr(logging, level_name.upper(), logging.INFO)
        logger_to_configure = self.get_logger(logger_name)
        logger_to_configure.setLevel(level)
        # print(f"LogManager: Level for logger '{logger_to_configure.name}' set to {level_name}.")

        # Also update levels for its handlers if desired, or reconfigure.
        # For simplicity, this basic version just sets the logger's level.
        # More complex scenarios might involve iterating handlers or re-applying dictConfig.

# Initialize the singleton instance when the module is imported
# This ensures LogManager() is called once and configure() runs with defaults.
get_log_manager()

# Convenience function to get a logger directly
def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Convenience function to get a logger instance from the LogManager.
    """
    return get_log_manager().get_logger(name)

if __name__ == '__main__':
    # Example Usage:
    # The LogManager is automatically configured with defaults when this module is imported.
    
    # Get the application's root logger
    root_logger = get_logger() # Equivalent to get_logger(None)
    root_logger.debug("This is a root debug message.") # Should appear in file, not console by default
    root_logger.info("This is a root info message.")   # Should appear in both
    root_logger.warning("This is a root warning message.")
    root_logger.error("This is a root error message.")
    root_logger.critical("This is a root critical message.")

    # Get a specific logger for a module
    module_logger = get_logger("my_module")
    module_logger.debug("This is a my_module debug message.") # To file
    module_logger.info("This is a my_module info message.")   # To file and console

    # Example of using a logger from another part of the app (simulated)
    # In another_module.py:
    # from img_ops.core.logging.manager import get_logger
    # logger = get_logger(__name__) # __name__ would be 'another_module' or 'img_ops.another_module'
    # logger.info("Message from another module.")

    another_module_logger = get_logger("img_ops.another_module")
    another_module_logger.info("Info from img_ops.another_module")
    another_module_logger.debug("Debug from img_ops.another_module")

    # Test changing log level
    print("\nSetting root logger level to DEBUG for console (via handler)...")
    # To change console level, we need to access the handler
    # This is a bit more direct manipulation than ideal for a simple set_level
    # A more robust set_level would find handlers and update them.
    console_handler_found = False
    for handler in root_logger.handlers:
        if handler.name == 'console': # We need to add names to handlers in config for this
            # Or check type: isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout
            # For now, let's assume the first StreamHandler is console if no names.
            # This is fragile. The config should name handlers if we want to target them.
            # Let's update config.py to add names to handlers.
            # For this example, let's just set the root logger level, which affects propagation.
            # The handler's own level still applies.
            pass # See note above.

    # A simpler way for this example: reconfigure with a modified config
    # Or, for a quick test, just get the root logger and set its level.
    # The handlers also have levels.
    # get_log_manager().set_level("DEBUG") # Sets root logger level
    # root_logger.info("Root info after trying to set level (check console and file).")
    # root_logger.debug("Root debug after trying to set level (check console and file).")

    print("\nTo properly change console output level, you'd typically reconfigure or adjust handler levels.")
    print(f"Check logs in: {Path(LOGS_DIR).resolve()}")