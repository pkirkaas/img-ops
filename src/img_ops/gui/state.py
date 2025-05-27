"""
Application state management for the img-ops GUI.

This module provides centralized state management using Qt's signal/slot mechanism
for communication between widgets and the main application.
"""
from PySide6.QtCore import QObject, Signal
from typing import Set, List, Optional  # Added Optional

from ..core.file_info_cache import FileInfoCache  # Import for type hinting


class AppState(QObject):
    """
    Central application state manager.

    This class maintains the shared state of the application and provides
    signals for notifying widgets when state changes occur. It acts as a
    central hub for communication between different parts of the GUI.

    Signals:
      selected_paths_changed: Emitted when the set of selected file paths changes.
                             Args: selected_paths (Set[str]) - The new set of selected paths

      current_directory_changed: Emitted when the current directory changes.
                                Args: directory_path (str) - The new current directory path
    """

    # Signals for state changes
    selected_paths_changed = Signal(set)  # Set[str] of selected file paths
    current_directory_changed = Signal(str)  # Current directory path

    def __init__(self, parent=None):
        """
        Initialize the application state.

        Args:
          parent (QObject, optional): The parent object. Defaults to None.
        """
        super().__init__(parent)

        # Internal state storage
        self._selected_paths: Set[str] = set()
        self._current_directory: str = ""
        # Added FileInfoCache attribute
        self.file_info_cache: Optional[FileInfoCache] = None

    @property
    def selected_paths(self) -> Set[str]:
        """
        Get the current set of selected file paths.

        Returns:
          Set[str]: The currently selected file paths.
        """
        return self._selected_paths.copy()

    @property
    def current_directory(self) -> str:
        """
        Get the current directory path.

        Returns:
          str: The current directory path.
        """
        return self._current_directory

    def set_selected_paths(self, paths: Set[str]):
        """
        Update the selected file paths and emit the change signal.

        Args:
          paths (Set[str]): The new set of selected file paths.
        """
        if paths != self._selected_paths:
            self._selected_paths = paths.copy()
            self.selected_paths_changed.emit(self._selected_paths)

    def add_selected_path(self, path: str):
        """
        Add a single path to the selected paths.

        Args:
          path (str): The file path to add to the selection.
        """
        if path not in self._selected_paths:
            self._selected_paths.add(path)
            self.selected_paths_changed.emit(self._selected_paths)

    def remove_selected_path(self, path: str):
        """
        Remove a single path from the selected paths.

        Args:
          path (str): The file path to remove from the selection.
        """
        if path in self._selected_paths:
            self._selected_paths.remove(path)
            self.selected_paths_changed.emit(self._selected_paths)

    def clear_selected_paths(self):
        """
        Clear all selected paths.
        """
        if self._selected_paths:
            self._selected_paths.clear()
            self.selected_paths_changed.emit(self._selected_paths)

    def set_current_directory(self, directory_path: str):
        """
        Update the current directory and emit the change signal.

        Args:
          directory_path (str): The new current directory path.
        """
        if directory_path != self._current_directory:
            self._current_directory = directory_path
            self.current_directory_changed.emit(self._current_directory)

    def get_selected_paths_list(self) -> List[str]:
        """
        Get the selected paths as a sorted list.

        Returns:
          List[str]: The selected file paths as a sorted list.
        """
        return sorted(list(self._selected_paths))

    def set_file_info_cache(self, cache: FileInfoCache):
        """
        Sets the FileInfoCache instance for the application.

        Args:
          cache (FileInfoCache): The file information cache instance.
        """
        if self.file_info_cache is not cache:  # Avoid unnecessary reassignment if it's the same object
            self.file_info_cache = cache
            # Optionally, emit a signal if other parts of the app need to know the cache is ready/changed.
            # self.file_info_cache_changed.emit(self.file_info_cache)
            # For debugging
            print(f"AppState: FileInfoCache instance set: {cache}")
