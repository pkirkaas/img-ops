"""
Defines the SelectPathDialog for choosing a single folder or image file.
"""
import os
from PySide6.QtWidgets import (
    QDialog,
    QTreeView,
    QFileSystemModel,
    QVBoxLayout,
    QDialogButtonBox,
    QSizePolicy,
    QLabel # For the TestWindow example
)
from PySide6.QtCore import Qt, QDir, QModelIndex, Slot
from typing import Optional, List, Union # Added Union
from pathlib import Path

# Common image file extensions for filtering
# This list can be expanded or sourced from a central configuration if needed.
DEFAULT_IMAGE_EXTENSIONS_PATTERNS: List[str] = [
    "*.jpg", "*.jpeg", "*.jpe", "*.jif", "*.jfif", "*.jfi",
    "*.png",
    "*.gif",
    "*.bmp", "*.dib",
    "*.tiff", "*.tif",
    "*.webp",
    "*.svg",
    "*.ico",
    # Raw formats (add more as needed)
    "*.raw", "*.arw", "*.cr2", "*.cr3", "*.dng", "*.nef", "*.orf",
    "*.heif", "*.heic",
    "*.avif",
    "*.jxl"
]

class SelectPathDialog(QDialog):
  """
  A dialog that allows the user to select a single folder or an image file
  from a file system tree view.
  """
  def __init__(self,
               initial_path: Optional[Union[str, Path]] = None,
               title: str = "Select Path",
               parent=None):
    """
    Initializes the SelectPathDialog.

    Args:
      initial_path (Optional[Union[str, Path]], optional): The path to initially display.
                                                            Defaults to the user's home directory.
      title (str, optional): The title of the dialog window. Defaults to "Select Path".
      parent (QWidget, optional): The parent widget. Defaults to None.
    """
    super().__init__(parent)
    self.setWindowTitle(title)
    self.setMinimumSize(500, 400) # Make it resizable
    self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    self._selected_path: Optional[str] = None

    # --- File System Model and Tree View ---
    self.model = QFileSystemModel(self)
    self.model.setRootPath(QDir.rootPath()) # Allow navigation anywhere
    
    # Set filters: show directories and specified image files
    # QFileSystemModel.setNameFilters() expects a list of wildcard patterns.
    # It filters out files that do not match any of the patterns.
    # Directories are always shown unless QFileSystemModel.Filter.NoDirs is set.
    self.model.setNameFilters(DEFAULT_IMAGE_EXTENSIONS_PATTERNS)
    # QFileSystemModel.setNameFilterDisables(False) means that files not matching the filter are hidden.
    # This is the default behavior, so explicitly setting it isn't strictly necessary
    # but reinforces the intent.
    self.model.setNameFilterDisables(False) 
    # We want to show directories, so we don't set QDir.NoDirs.
    # We only want to filter files, not hide directories that don't contain images.
    # The filtering is applied to what files are *listed* within directories.

    self.tree_view = QTreeView(self)
    self.tree_view.setModel(self.model)
    self.tree_view.setAnimated(True)
    self.tree_view.setIndentation(20)
    self.tree_view.setSortingEnabled(True)
    self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
    
    # Set selection mode to single selection
    self.tree_view.setSelectionMode(QTreeView.SelectionMode.SingleSelection)

    # Hide all columns except the name (column 0)
    for i in range(1, self.model.columnCount()):
        self.tree_view.hideColumn(i)

    # Set initial path to display
    if initial_path:
      start_dir = str(Path(initial_path).resolve())
    else:
      start_dir = QDir.homePath()
    
    self.tree_view.setRootIndex(self.model.index(start_dir))
    # Select the initial path if it's valid and visible
    # We might want to scroll to it as well.
    initial_index = self.model.index(start_dir)
    if initial_index.isValid():
        self.tree_view.setCurrentIndex(initial_index) # Selects the item
        self._selected_path = self.model.filePath(initial_index)


    # Connect signals
    self.tree_view.selectionModel().currentChanged.connect(self._on_selection_changed)
    self.tree_view.doubleClicked.connect(self._on_double_clicked)


    # --- Dialog Buttons ---
    self.button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
        self
    )
    self.button_box.accepted.connect(self.accept)
    self.button_box.rejected.connect(self.reject)
    # Initially disable OK until a valid selection is made
    self._update_ok_button_state()


    # --- Layout ---
    main_layout = QVBoxLayout(self)
    main_layout.addWidget(self.tree_view)
    main_layout.addWidget(self.button_box)
    self.setLayout(main_layout)

  @Slot(QModelIndex, QModelIndex)
  def _on_selection_changed(self, current: QModelIndex, previous: QModelIndex):
    """
    Handles changes in the tree view's current selection.
    Updates the internal selected path.
    """
    if current.isValid():
      file_path = self.model.filePath(current)
      # We need to check if the selected item is an image file or a directory.
      # The filter should ensure only images or dirs are visible.
      if self.model.isDir(current) or (self.model.isFile(current) and self._is_image_file(file_path)):
          self._selected_path = file_path
      else:
          # This case should ideally not happen if filters work correctly and only one item is selected
          self._selected_path = None 
    else:
      self._selected_path = None
    self._update_ok_button_state()

  @Slot(QModelIndex)
  def _on_double_clicked(self, index: QModelIndex):
    """
    Handles double-click events on items in the tree view.
    If a directory is double-clicked, navigate into it.
    If a file is double-clicked, accept the dialog with this file.
    """
    if index.isValid():
      if self.model.isDir(index):
        # Navigate into the directory by setting it as the new root for the view
        self.tree_view.setRootIndex(index)
      elif self.model.isFile(index) and self._is_image_file(self.model.filePath(index)):
        # If an image file is double-clicked, consider it selected and accept.
        self._selected_path = self.model.filePath(index)
        self._update_ok_button_state()
        if self.button_box.button(QDialogButtonBox.StandardButton.Ok).isEnabled():
            self.accept()


  def _is_image_file(self, file_path: str) -> bool:
    """Checks if a file path matches one of the image extensions."""
    if not file_path:
        return False
    # Check against the patterns (case-insensitive for extension part)
    path_obj = Path(file_path)
    file_ext_lower = path_obj.suffix.lower() # e.g. ".jpg"
    
    for pattern in DEFAULT_IMAGE_EXTENSIONS_PATTERNS:
        # pattern is like "*.jpg"
        pattern_ext_lower = pattern[1:].lower() # e.g. ".jpg"
        if file_ext_lower == pattern_ext_lower:
            return True
    return False

  def _update_ok_button_state(self):
    """
    Enables or disables the OK button based on whether a valid path is selected.
    """
    ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
    if ok_button:
      ok_button.setEnabled(self._selected_path is not None)

  def selected_path(self) -> Optional[str]:
    """
    Returns the absolute path of the item selected by the user.

    Returns:
      Optional[str]: The selected path if the dialog was accepted and a
                     valid item was selected, otherwise None.
    """
    if self.result() == QDialog.DialogCode.Accepted:
      return self._selected_path
    return None

  @staticmethod
  def get_path(parent=None, 
               initial_path: Optional[Union[str, Path]] = None,
               title: str = "Select Path") -> Optional[str]:
    """
    Static method to create, show the dialog, and return the selected path.

    Args:
      parent (QWidget, optional): Parent widget.
      initial_path (Optional[Union[str, Path]], optional): The path to initially display.
      title (str, optional): The title for the dialog window.

    Returns:
      Optional[str]: The selected path as a string, or None if canceled.
    """
    dialog = SelectPathDialog(initial_path=initial_path, title=title, parent=parent)
    if dialog.exec() == QDialog.DialogCode.Accepted:
      return dialog.selected_path()
    return None


if __name__ == '__main__':
  import sys
  from PySide6.QtWidgets import QApplication, QPushButton, QMainWindow

  class TestWindow(QMainWindow):
    def __init__(self):
      super().__init__()
      self.setWindowTitle("Test SelectPathDialog")
      self.button = QPushButton("Open Select Path Dialog", self)
      self.button.clicked.connect(self.open_dialog)
      self.setCentralWidget(self.button)
      self.selected_label = QLabel("Selected: None", self)
      
      layout = QVBoxLayout(self.button.parentWidget()) # Get central widget if button is central
      if not layout: # If button was not set as central widget directly
          container = QWidget()
          layout = QVBoxLayout(container)
          self.setCentralWidget(container)

      layout.addWidget(self.button)
      layout.addWidget(self.selected_label)


    def open_dialog(self):
      # Example: Start in the user's Pictures directory if available
      pictures_path = QDir(QDir.homePath()).filePath("Pictures")
      if not QDir(pictures_path).exists():
          pictures_path = QDir.homePath()
      
      path = SelectPathDialog.get_path(self, initial_path=pictures_path, title="Choose an Image or Folder")
      if path:
        print(f"Selected path: {path}")
        self.selected_label.setText(f"Selected: {path}")
      else:
        print("Dialog canceled or no path selected.")
        self.selected_label.setText("Selected: None (Canceled)")

  app = QApplication(sys.argv)
  window = TestWindow()
  window.setGeometry(300, 300, 400, 200)
  window.show()
  sys.exit(app.exec())