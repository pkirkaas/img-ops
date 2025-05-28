"""
Default configuration for the logging system.
"""
import logging

# Define a base directory for logs, e.g., in the user's app data directory or project root.
# For simplicity during development, we can place it in the project root.
# In a real application, consider using platformdirs or similar.
LOGS_DIR = "logs" # Relative to project root for now

DEFAULT_LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(module)s:%(lineno)d - %(levelname)s - %(message)s'
        },
        # A more console-friendly format, potentially with colors later
        'console_friendly': {
            'format': '[%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO', # Default level for console
            'formatter': 'console_friendly',
            'stream': 'ext://sys.stdout' # Default to stdout
        },
        'file_rotating': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG', # Default level for file logs
            'formatter': 'detailed',
            'filename': f'{LOGS_DIR}/img_ops_app.log', # Log file path
            'maxBytes': 10*1024*1024,  # 10 MB
            'backupCount': 5, # Keep 5 backup files
            'encoding': 'utf-8'
        }
        # GUI handler will be added in Phase 2
    },
    'loggers': {
        # Root logger configuration - catches all logs not caught by specific loggers
        '': { # Empty string for root logger
            'handlers': ['console', 'file_rotating'],
            'level': 'DEBUG', # Capture all DEBUG and higher messages at the root
            'propagate': False # Prevent root logger from passing messages to its own handlers again if already handled
        },
        # Example of a specific logger configuration (can be added as needed)
        # 'img_ops.core.specific_module': {
        #     'handlers': ['console'],
        #     'level': 'INFO',
        #     'propagate': False
        # }
    }
    # 'root' is an alias for the logger with name '' (empty string).
    # It's often clearer to configure the root logger using '' as the name.
}

# Ensure the logs directory exists
# This will be handled by the LogManager when it initializes.