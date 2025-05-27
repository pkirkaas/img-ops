"""
Defines the SelectedPathsWidget for displaying and managing a list of
selected file system paths (folders or image files).
"""
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QMenu,
    QMessageBox
)
from PySide6.QtCore import Qt, Slot, Signal, QPoint # Added QPoint
from PySide6.QtGui import QAction, QCursor

from typing import Set, List, Optional
from pathlib import Path

from ..state import AppState
from ..dialogs.select_path_dialog import SelectPathDialog, DEFAULT_IMAGE_EXTENSIONS_PATTERNS
from ...core.file_system import check_nested #, filter_imgs # filter_imgs might not be needed if SelectPathDialog handles it

class SelectedPathsWidget(QWidget):
  """
  A widget that displays a list of selected file system paths.
  Paths can be folders or individual image files.
  Supports adding paths via a dialog and removing paths via a context menu.
  Synchronizes with the global AppState.
  """

  # Signal to request a change in the global selection state
  # This is somewhat redundant if we directly call app_state methods,
  # but can be useful if other parts of this widget need to react internally first.
  # For now, we'll aim to directly modify AppState.
  # selection_update_requested = Signal(set) # set of paths

  def __init__(self, parent: Optional[QWidget] = None):
    """
    Initializes the SelectedPathsWidget.

    Args:
      parent (Optional[QWidget], optional): The parent widget. Defaults to None.
    """
    super().__init__(parent)

    self._app_state: Optional[AppState] = None
    self._current_displayed_paths: Set[str] = set()

    self.list_widget = QListWidget(self)
    self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) # Multi-select
    self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.list_widget.customContextMenuRequested.connect(self._show_context_menu)

    main_layout = QVBoxLayout(self)
    main_layout.addWidget(self.list_widget)
    self.setLayout(main_layout)

  def set_app_state(self, app_state: AppState):
    """
    Connects the widget to the global application state.

    Args:
      app_state (AppState): The application state manager.
    """
    self._app_state = app_state
    if self._app_state:
      self._app_state.selected_paths_changed.connect(self._on_global_selection_changed)
      # Initialize with current global selection
      self._on_global_selection_changed(self._app_state.selected_paths)

  @Slot(set)
  def _on_global_selection_changed(self, new_paths: Set[str]):
    """
    Updates the list widget when the global selection in AppState changes.

    Args:
      new_paths (Set[str]): The new set of globally selected paths.
    """
    if new_paths == self._current_displayed_paths:
      return # No change needed

    self.list_widget.clear()
    sorted_paths = sorted(list(new_paths))
    for path_str in sorted_paths:
      # Filter to ensure only folders or valid image files are displayed
      # This check should ideally be done before adding to AppState,
      # but as a safeguard here or if AppState can contain other things.
      p = Path(path_str)
      if p.is_dir() or self._is_image_file(path_str):
        item = QListWidgetItem(path_str)
        self.list_widget.addItem(item)
    
    self._current_displayed_paths = new_paths.copy()

  def _is_image_file(self, file_path_str: str) -> bool:
    """
    Checks if a file path string likely points to an image file based on its extension.
    """
    path_obj = Path(file_path_str)
    if not path_obj.is_file():
        return False
        
    file_ext_lower = path_obj.suffix.lower()
    for pattern in DEFAULT_IMAGE_EXTENSIONS_PATTERNS: # From SelectPathDialog
        pattern_ext_lower = pattern[1:].lower() # e.g., ".jpg" from "*.jpg"
        if file_ext_lower == pattern_ext_lower:
            return True
    return False

  @Slot()
  def _add_path_action(self):
    """
    Handles the 'Add Path...' action from the context menu.
    Opens the SelectPathDialog to choose a new path.
    """
    if not self._app_state:
      return

    selected_path = SelectPathDialog.get_path(parent=self, title="Add Path to Selection")
    if selected_path:
      # Check for nesting before adding
      current_paths_list = list(self._current_displayed_paths)
      
      # Temporarily add the new path for the check_nested validation
      paths_to_check = current_paths_list + [selected_path]
      
      try:
        # Ensure the new path itself is valid (folder or image)
        p_new = Path(selected_path)
        if not (p_new.is_dir() or (p_new.is_file() and self._is_image_file(selected_path))):
            QMessageBox.warning(self, "Invalid Path Type",
                                f"The selected path is not a folder or a recognized image file:\n{selected_path}")
            return

        check_nested(paths_to_check) # This will raise ValueError if nesting occurs
        self._app_state.add_selected_path(selected_path) # This will trigger _on_global_selection_changed
      except FileNotFoundError as e:
        QMessageBox.warning(self, "Path Not Found", f"The selected path could not be found:\n{e}")
      except ValueError as e: # Raised by check_nested for nesting violation
        QMessageBox.warning(self, "Nesting Violation", f"Could not add path due to nesting:\n{selected_path}\n\nDetails: {e}")
      except Exception as e:
        QMessageBox.critical(self, "Error Adding Path", f"An unexpected error occurred:\n{e}")


  @Slot()
  def _remove_selected_paths_action(self):
    """
    Handles the 'Remove' action for selected items in the list widget.
    """
    if not self._app_state:
      return

    items_to_remove = self.list_widget.selectedItems()
    if not items_to_remove:
      return

    for item in items_to_remove:
      path_to_remove = item.text()
      self._app_state.remove_selected_path(path_to_remove)
      # The _on_global_selection_changed slot will handle updating the list_widget

  @Slot(QPoint)
  def _show_context_menu(self, pos: QPoint):
    """
    Shows the context menu for the list widget.
    """
    context_menu = QMenu(self)
    
    add_action = QAction("Add Path...", self)
    add_action.triggered.connect(self._add_path_action)
    context_menu.addAction(add_action)

    # Add "Remove" only if items are selected
    if self.list_widget.selectedItems():
      remove_action = QAction("Remove Selected", self)
      remove_action.triggered.connect(self._remove_selected_paths_action)
      context_menu.addAction(remove_action)
      
      # Could add "Remove All" here too
      # clear_all_action = QAction("Remove All Paths", self)
      # clear_all_action.triggered.connect(self._app_state.clear_selected_paths) # If app_state is available
      # context_menu.addAction(clear_all_action)

    context_menu.exec(self.list_widget.mapToGlobal(pos))


if __name__ == '__main__':
  import sys
  from PySide6.QtWidgets import QApplication, QMainWindow

  # Dummy AppState for testing
  class DummyAppState(QObject):
    selected_paths_changed = Signal(set)
    def __init__(self):
      super().__init__()
      self._selected_paths = set()
    @property
    def selected_paths(self): return self._selected_paths.copy()
    def add_selected_path(self, path):
      if path not in self._selected_paths:
        self._selected_paths.add(path)
        self.selected_paths_changed.emit(self._selected_paths)
    def remove_selected_path(self, path):
      if path in self._selected_paths:
        self._selected_paths.remove(path)
        self.selected_paths_changed.emit(self._selected_paths)

  app = QApplication(sys.argv)
  main_win = QMainWindow()
  main_win.setWindowTitle("Test SelectedPathsWidget")
  
  test_app_state = DummyAppState()
  
  selected_paths_w = SelectedPathsWidget()
  selected_paths_w.set_app_state(test_app_state) # Connect to dummy state
  
  main_win.setCentralWidget(selected_paths_w)
  main_win.resize(400, 300)
  main_win.show()

  # Example: Simulate external changes to app_state
  # test_app_state.add_selected_path(str(Path.home()))
  # test_app_state.add_selected_path(str(Path.home() / "Documents")) # This would be a nesting violation if checked by add_path_action

  sys.exit(app.exec())