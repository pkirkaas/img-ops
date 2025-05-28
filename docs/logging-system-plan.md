# Logging System Implementation Plan

## Overview
Implementation of an enhanced Python logging system with custom handlers for GUI integration, providing unified logging across CLI, GUI, and core components.

## Architecture

### Core Components

```
src/img_ops/core/logging/
├── __init__.py           # Public API exports
├── manager.py            # LogManager singleton
├── handlers.py           # Custom handlers (GUI, enhanced file)
├── formatters.py         # Custom formatters
├── mixins.py            # LoggerMixin for easy access
├── config.py            # Configuration management
└── gui_integration.py   # Qt-specific GUI integration
```

### Design Principles

1. **Single Point of Access**: All components use the same logging interface
2. **Configurable Outputs**: File, console, and GUI outputs with independent configuration
3. **Thread Safety**: Built on Python's thread-safe logging infrastructure
4. **Qt Integration**: Custom handlers that emit Qt signals for GUI updates
5. **Structured Logging**: Support for rich context data and JSON formatting
6. **Performance**: Async GUI updates to prevent blocking

## Implementation Phases

### Phase 1: Core Infrastructure
- LogManager singleton with basic configuration
- Enhanced file handler with rotation
- Console handler with colored output
- Basic configuration system
- LoggerMixin for easy integration

### Phase 2: GUI Integration
- GUILogHandler with Qt signal emission
- GUI log viewer widget
- Status bar integration
- Error notification system

### Phase 3: Advanced Features
- Structured logging with JSON support
- Log filtering and searching
- Configuration file support
- Performance monitoring integration

### Phase 4: Polish & Enhancement
- Log export functionality
- Advanced GUI log viewer
- Log analytics and reporting
- Integration with existing error dialogs

## Key Features

### 1. LogManager (Singleton)
```python
class LogManager:
    """Central logging configuration and management."""
    
    def __init__(self):
        self._loggers = {}
        self._handlers = {}
        self._gui_handler = None
        self._configured = False
    
    def configure(self, config=None):
        """Configure all logging handlers and formatters."""
        
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger for the given name."""
        
    def add_gui_handler(self, handler):
        """Add GUI handler for real-time log display."""
        
    def set_level(self, level: str):
        """Set global logging level."""
```

### 2. GUILogHandler
```python
class GUILogHandler(logging.Handler, QObject):
    """Custom handler that emits Qt signals for GUI integration."""
    
    log_emitted = Signal(object)  # LogRecord object
    
    def emit(self, record):
        """Emit log record as Qt signal."""
        self.log_emitted.emit(record)
```

### 3. LoggerMixin
```python
class LoggerMixin:
    """Mixin to provide easy logger access to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__ + '.' + self.__class__.__name__)
```

### 4. Configuration System
```python
DEFAULT_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s: %(message)s'
        },
        'json': {
            'class': 'logging_system.formatters.JSONFormatter'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/img_ops.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'gui': {
            'class': 'logging_system.handlers.GUILogHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'img_ops': {
            'level': 'INFO',
            'handlers': ['file', 'console', 'gui']
        }
    }
}
```

## Integration Examples

### 1. Core Component Usage
```python
from img_ops.core.logging import LoggerMixin

class ImageProcessor(LoggerMixin):
    def process_image(self, path: str):
        self.logger.info("Starting image processing", extra={
            'path': path,
            'operation': 'process_image'
        })
        
        try:
            # Processing logic
            result = self._do_processing(path)
            self.logger.info("Image processed successfully", extra={
                'path': path,
                'result_size': len(result)
            })
            return result
        except Exception as e:
            self.logger.error("Image processing failed", extra={
                'path': path,
                'error': str(e)
            }, exc_info=True)
            raise
```

### 2. GUI Component Integration
```python
from img_ops.core.logging import get_logger, LogManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        
        # Connect to GUI log handler
        log_manager = LogManager.instance()
        if log_manager.gui_handler:
            log_manager.gui_handler.log_emitted.connect(self.on_log_message)
    
    def on_log_message(self, record):
        """Handle log messages for GUI display."""
        if record.levelno >= logging.WARNING:
            self.status_bar.showMessage(record.getMessage(), 5000)
        
        if record.levelno >= logging.ERROR:
            self.show_error_notification(record)
```

### 3. CLI Component Usage
```python
from img_ops.core.logging import get_logger

def main():
    logger = get_logger(__name__)
    logger.info("CLI application starting")
    
    try:
        # CLI logic
        process_files()
        logger.info("CLI processing completed successfully")
    except Exception as e:
        logger.error("CLI processing failed", exc_info=True)
        sys.exit(1)
```

## GUI Integration Features

### 1. Log Viewer Widget
- Real-time log display
- Filtering by level and component
- Search functionality
- Export capabilities

### 2. Status Bar Integration
- Show recent warnings/errors
- Click to open full log viewer
- Progress indication for long operations

### 3. Error Notification System
- Toast notifications for errors
- Integration with existing error dialogs
- Selectable/copyable error text

### 4. Debug Panel
- Real-time log streaming
- Component-specific filtering
- Performance metrics display

## Configuration Options

### 1. Log Levels
- DEBUG: Detailed diagnostic information
- INFO: General operational messages
- WARNING: Warning messages for recoverable issues
- ERROR: Error messages for serious problems
- CRITICAL: Critical errors that may cause application failure

### 2. Output Destinations
- **File**: Rotating log files with configurable size and retention
- **Console**: Colored terminal output for CLI usage
- **GUI**: Real-time display in GUI widgets with notifications

### 3. Formatting Options
- **Simple**: Level and message only
- **Detailed**: Timestamp, component, level, and message
- **JSON**: Structured format for machine parsing
- **Custom**: Application-specific formatting

## Performance Considerations

### 1. Async GUI Updates
- GUI handler uses Qt signals to prevent blocking
- Log processing happens on separate thread
- GUI updates are batched for performance

### 2. Memory Management
- Rotating file handlers prevent disk space issues
- GUI log viewer has configurable history limits
- Structured logging avoids string formatting overhead

### 3. Filtering
- Early filtering at handler level
- Component-based logger hierarchy
- Configurable log levels per output

## Testing Strategy

### 1. Unit Tests
- Test each handler independently
- Verify configuration loading
- Test log formatting and filtering

### 2. Integration Tests
- Test GUI signal emission
- Verify multi-threaded logging
- Test configuration changes at runtime

### 3. Performance Tests
- Measure logging overhead
- Test with high-volume logging
- Verify GUI responsiveness

## Migration Plan

### 1. Phase 1: Infrastructure
- Implement core logging components
- Replace existing print statements in core modules
- Add basic file and console logging

### 2. Phase 2: GUI Integration
- Implement GUI handlers
- Add log viewer widget
- Integrate with existing error dialogs

### 3. Phase 3: Enhancement
- Add structured logging
- Implement advanced GUI features
- Add configuration management

### 4. Phase 4: Optimization
- Performance tuning
- Advanced filtering
- Analytics and reporting

## Benefits

1. **Unified Logging**: Single interface across all components
2. **Professional Quality**: Built on proven logging infrastructure
3. **GUI Integration**: Real-time log display and notifications
4. **Configurable**: Flexible output and formatting options
5. **Maintainable**: Standard Python logging patterns
6. **Extensible**: Easy to add new handlers and formatters
7. **Performance**: Thread-safe and optimized for desktop applications
8. **Debugging**: Rich context and structured logging support

This logging system will provide a solid foundation for debugging, monitoring, and user feedback throughout the application.