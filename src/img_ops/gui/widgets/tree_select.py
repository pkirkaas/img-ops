"""
Defines the TreeSelect widget for file system browsing with checkboxes.
"""
import os
from PySide6.QtWidgets import (
  QWidget,
  QTreeView,
  QFileSystemModel,
  QPushButton,
  QVBoxLayout,
  QMessageBox,
  QDialog,
  QTextEdit,
  QDialogButtonBox
)
from PySide6.QtCore import Qt, QModelIndex, QDir
from typing import Dict, Set

class CheckableFileSystemModel(QFileSystemModel):
  """
  A QFileSystemModel subclass that supports checkable items.
  """
  def __init__(self, parent=None):
    super().__init__(parent)
    self.check_states: Dict[str, Qt.CheckState] = {} # Store check states by file path

  def flags(self, index: QModelIndex) -> Qt.ItemFlag:
    """
    Returns the item flags for the given index.
    Adds Qt.ItemIsUserCheckable to default flags.
    """
    default_flags = super().flags(index)
    if index.isValid():
      return default_flags | Qt.ItemFlag.ItemIsUserCheckable
    return default_flags

  def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> any:
    """
    Returns the data stored under the given role for the item referred to by the index.
    Handles Qt.CheckStateRole.
    """
    if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
      file_path = self.filePath(index)
      return self.check_states.get(file_path, Qt.CheckState.Unchecked)
    return super().data(index, role)

  def setData(self, index: QModelIndex, value: any, role: int = Qt.ItemDataRole.EditRole) -> bool:
    """
    Sets the role data for the item at index to value.
    Handles Qt.CheckStateRole.
    """
    if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
      file_path = self.filePath(index)
      current_check_state = Qt.CheckState(value)
      self.check_states[file_path] = current_check_state
      self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
      
      # Propagate check state to children if it's a directory
      if self.isDir(index) and current_check_state == Qt.CheckState.Checked:
        self._propagate_check_to_children(index, current_check_state)
      # Note: Unchecking a parent does not automatically uncheck children in this simple version.
      # More complex logic would be needed for tri-state checkboxes or recursive unchecking.
      return True
    return super().setData(index, value, role)

  def _propagate_check_to_children(self, parent_index: QModelIndex, check_state: Qt.CheckState):
    """
    Recursively sets the check state for all children of a given parent index.
    """
    num_rows = self.rowCount(parent_index)
    for i in range(num_rows):
      child_index = self.index(i, 0, parent_index)
      child_file_path = self.filePath(child_index)
      if self.check_states.get(child_file_path) != check_state:
          self.check_states[child_file_path] = check_state
          self.dataChanged.emit(child_index, child_index, [Qt.ItemDataRole.CheckStateRole])
          if self.isDir(child_index):
              self._propagate_check_to_children(child_index, check_state)
  
  def get_checked_items(self) -> Set[str]:
    """
    Returns a set of file paths for all items that are currently checked.
    """
    checked_paths = set()
    for path, state in self.check_states.items():
      if state == Qt.CheckState.Checked:
        checked_paths.add(path)
    return checked_paths


class TreeSelect(QWidget):
  """
  A file system browser widget with a tree structure and checkboxes for selection.
  """
  def __init__(self, root_path: str = QDir.currentPath(), parent: QWidget = None):
    """
    Initializes the TreeSelect widget.

    Args:
      root_path (str, optional): The initial root path for the file browser.
                                 Defaults to QDir.currentPath().
      parent (QWidget, optional): The parent widget. Defaults to None.
    """
    super().__init__(parent)

    self.model = CheckableFileSystemModel(self)
    self.model.setRootPath(root_path)
    # self.model.setFilter(QDir.Filter.NoDotAndDotDot | QDir.Filter.AllEntries) # Show all

    self.tree_view = QTreeView(self)
    self.tree_view.setModel(self.model)
    self.tree_view.setRootIndex(self.model.index(root_path))
    self.tree_view.setAnimated(True) # Optional: for smoother expand/collapse
    self.tree_view.setIndentation(20)
    self.tree_view.setSortingEnabled(True)
    self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    # Hide all columns except the name (column 0)
    for i in range(1, self.model.columnCount()):
        self.tree_view.hideColumn(i)
    
    # When an item is expanded, ensure its children are loaded if not already
    self.tree_view.expanded.connect(self._handle_expanded)


    self.show_selected_button = QPushButton("Show Selected", self)
    self.show_selected_button.clicked.connect(self._show_selected_items_dialog)

    layout = QVBoxLayout(self)
    layout.addWidget(self.tree_view)
    layout.addWidget(self.show_selected_button)
    self.setLayout(layout)

  def _handle_expanded(self, index: QModelIndex):
    """
    When a directory is expanded, ensure its children are fetched.
    This is mostly handled by QFileSystemModel, but can be a point for custom logic.
    """
    if self.model.isDir(index) and not self.model.hasChildren(index):
        # QFileSystemModel usually lazy-loads. This ensures it tries.
        self.model.fetchMore(index)


  def _show_selected_items_dialog(self):
    """
    Displays a dialog box showing all currently selected (checked) items.
    """
    checked_items = self.model.get_checked_items()

    if not checked_items:
      QMessageBox.information(self, "Selected Items", "No items are currently selected.")
      return

    # Using a custom dialog for better text display
    dialog = QDialog(self)
    dialog.setWindowTitle("Selected File System Items")
    dialog.setMinimumWidth(500)
    dialog.setMinimumHeight(300)

    layout = QVBoxLayout(dialog)
    text_edit = QTextEdit(dialog)
    text_edit.setReadOnly(True)
    text_edit.setText("\n".join(sorted(list(checked_items))))
    layout.addWidget(text_edit)

    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, dialog)
    button_box.accepted.connect(dialog.accept)
    layout.addWidget(button_box)

    dialog.setLayout(layout)
    dialog.exec()

  def setRootPath(self, path: str):
    """
    Sets the root path for the file system browser.
    """
    self.model.setRootPath(path)
    self.tree_view.setRootIndex(self.model.index(path))


if __name__ == '__main__':
  import sys
  from PySide6.QtWidgets import QApplication

  app = QApplication(sys.argv)
  # Use a known directory for testing, e.g., the user's home directory or current dir
  test_path = QDir.homePath() 
  # test_path = "." # Or current directory

  main_widget = TreeSelect(root_path=test_path)
  main_widget.setWindowTitle(f"Test TreeSelect - Root: {test_path}")
  main_widget.resize(600, 400)
  main_widget.show()

  sys.exit(app.exec())