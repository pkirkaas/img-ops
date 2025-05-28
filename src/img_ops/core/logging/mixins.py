"""
Logging Mixin for easy logger access in classes.
"""
import logging
from typing import Optional # Added import for Optional
from .manager import get_logger as get_managed_logger # Renamed to avoid conflict

class LoggerMixin:
    """
    A mixin class that provides a 'logger' property to any class
    that inherits from it. The logger is automatically configured
    with the name of the class's module and class name.

    Example:
        ```python
        from img_ops.core.logging.mixins import LoggerMixin

        class MyClass(LoggerMixin):
            def do_something(self):
                self.logger.info("Doing something...")
                try:
                    # ... some operation ...
                    self.logger.debug("Operation successful.")
                except Exception as e:
                    self.logger.error(f"Operation failed: {e}", exc_info=True)

        my_instance = MyClass()
        my_instance.do_something()
        ```
    """

    _logger_instance: Optional[logging.Logger] = None

    @property
    def logger(self) -> logging.Logger:
        """
        Provides a logger instance for the class.
        The logger is named using the module and class name.
        It's cached after the first access.
        """
        if self._logger_instance is None:
            # Construct logger name, e.g., "img_ops.module.sub_module.ClassName"
            # This helps in filtering logs by component.
            logger_name = f"{self.__class__.__module__}.{self.__class__.__name__}"
            
            # If the module is part of the main app (e.g., starts with 'img_ops'),
            # it's fine. If it's a generic module, it might not be prefixed.
            # The get_managed_logger will handle getting the appropriate logger
            # from the configured LogManager.
            self.__class__._logger_instance = get_managed_logger(logger_name)
            # Using self.__class__._logger_instance to cache at class level
            # if all instances of this class should share the same logger instance.
            # If each instance should have its own logger (rarely needed unless logger name includes instance ID),
            # then use self._logger_instance = ...
            # For most cases, a class-level logger is appropriate.

        return self.__class__._logger_instance

if __name__ == '__main__':
    # Example of using LoggerMixin

    # This import should ideally be at the top of the file if used outside __main__
    # from .manager import get_log_manager 

    # Ensure the LogManager is configured (it is by default on import of manager.py)
    # log_manager = get_log_manager()
    # if not log_manager._configured:
    #     log_manager.configure()

    class ExampleWorker(LoggerMixin):
        def __init__(self, name):
            self.name = name
            # Logger is accessed via property, no need to init here unless you want to log in __init__
            self.logger.info(f"ExampleWorker '{self.name}' initialized.")

        def perform_task(self, task_data: str):
            self.logger.debug(f"'{self.name}' starting task with data: {task_data}")
            try:
                if task_data == "fail":
                    raise ValueError("Simulated task failure")
                result = task_data.upper()
                self.logger.info(f"'{self.name}' completed task. Result: {result}")
                return result
            except Exception as e:
                self.logger.error(f"'{self.name}' task failed: {task_data}", exc_info=True)
                # No need to re-raise for this example, error is logged.

    class AnotherComponent(LoggerMixin):
        def __init__(self):
            self.logger.info("AnotherComponent initialized.")

        def do_stuff(self):
            self.logger.debug("Doing stuff in AnotherComponent.")


    print("--- Testing LoggerMixin ---")
    worker1 = ExampleWorker("WorkerOne")
    worker1.perform_task("hello world")
    worker1.perform_task("fail")

    print("\n--- Testing AnotherComponent ---")
    comp = AnotherComponent()
    comp.do_stuff()
    
    # Verify logger names
    print(f"\nWorkerOne logger name: {worker1.logger.name}") # Should be something like '__main__.ExampleWorker' if run directly
                                                            # or 'img_ops.core.logging.mixins.ExampleWorker' if imported
    print(f"AnotherComponent logger name: {comp.logger.name}")

    print("\nCheck the log file (logs/img_ops_app.log) and console for output.")