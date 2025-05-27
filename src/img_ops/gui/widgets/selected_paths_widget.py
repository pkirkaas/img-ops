"""
Defines the SelectedPathsWidget for displaying and managing a list of
selected file system paths (folders or image files).
"""
from PySide6.QtWidgets import (
    QApplication, # Added for processEvents
    QWidget,
    QVBoxLayout,
    QListWidget, # Re-added for _list_files_action dialog
    # QListWidgetItem, # Still not needed directly
    QTableWidget, QTableWidgetItem, QHeaderView, # Added for table
    QAbstractItemView,
    QMenu,
    QMessageBox,
    QLabel, QPushButton, QHBoxLayout, # Added for new UI elements
    QStyle, QDialog, QProgressDialog # Added QStyle for icons, QDialog for list, QProgressDialog
)
from PySide6.QtCore import Qt, Slot, Signal, QPoint, QFileInfo, QObject # Added QFileInfo and QObject
from PySide6.QtGui import QAction, QCursor, QIcon # Added QIcon

from typing import Set, List, Optional
from pathlib import Path

from ..state import AppState
from ..dialogs.select_path_dialog import SelectPathDialog, DEFAULT_IMAGE_EXTENSIONS_PATTERNS
from ...core.file_system import check_nested, get_all_image_files_in_paths # Added get_all_image_files_in_paths
from ...core.file_info_cache import FileInfoCache # For PHash button

class SelectedPathsWidget(QWidget):
  """
  A widget that displays a list of selected file system paths (folders or image files).
  Supports adding, removing, validating, listing contents, and PHashing paths.
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

    main_layout = QVBoxLayout(self)
    self.setLayout(main_layout)

    # Title Label
    self.title_label = QLabel("Which Paths to Scan for Similarity?", self)
    main_layout.addWidget(self.title_label)

    # Table Widget for Paths
    self.paths_table = QTableWidget(self)
    self.paths_table.setColumnCount(1)
    self.paths_table.setHorizontalHeaderLabels(["Paths"])
    self.paths_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    self.paths_table.verticalHeader().setVisible(False)
    self.paths_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    self.paths_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    self.paths_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Read-only
    self.paths_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.paths_table.customContextMenuRequested.connect(self._show_context_menu)
    main_layout.addWidget(self.paths_table)

    # Button Row
    button_layout = QHBoxLayout()
    self.validate_button = QPushButton("Validate", self)
    self.list_button = QPushButton("List Files", self)
    self.phash_button = QPushButton("PHash Files", self)

    self.validate_button.clicked.connect(self._validate_paths_action)
    self.list_button.clicked.connect(self._list_files_action)
    self.phash_button.clicked.connect(self._phash_files_action)

    button_layout.addWidget(self.validate_button)
    button_layout.addWidget(self.list_button)
    button_layout.addWidget(self.phash_button)
    main_layout.addLayout(button_layout)


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

  def _get_path_icon(self, path_str: str) -> QIcon:
    """
    Returns an icon based on the path type (drive, folder, image file, other file).
    """
    p_info = QFileInfo(path_str)
    style = self.style()

    if not p_info.exists():
        # This case should ideally be prevented by validation before adding to AppState
        return style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)

    # Check for drive root (e.g., "C:/", "/")
    # A drive root is also a directory, so check this first.
    # QFileInfo.isRoot() is true for "/" on Unix. For Windows "C:/", it's true if it's the current directory.
    # A more reliable check for drive-like paths:
    path_obj = Path(path_str)
    # Check if it's an absolute path, its parent is itself (e.g. Path("C:/").parent == Path("C:/")),
    # and its anchor (drive letter + root) is the path itself.
    if path_obj.is_absolute() and path_obj.parent == path_obj and str(path_obj.anchor) == str(path_obj):
        return style.standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon)

    if p_info.isDir():
        return style.standardIcon(QStyle.StandardPixmap.SP_DirIcon)

    if p_info.isFile():
        if self._is_image_file(path_str):
            # Using a generic file icon for images for now, can be more specific
            return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        else:
            # Non-image file (should ideally be filtered out)
            return style.standardIcon(QStyle.StandardPixmap.SP_FileIcon) # Or SP_MessageBoxQuestion for unexpected file types

    return style.standardIcon(QStyle.StandardPixmap.SP_QuestionMark) # Default for unknown types


  @Slot(set)
  def _on_global_selection_changed(self, new_paths: Set[str]):
    """
    Updates the table widget when the global selection in AppState changes.

    Args:
      new_paths (Set[str]): The new set of globally selected paths.
    """
    if new_paths == self._current_displayed_paths:
      return # No change needed

    self.paths_table.setRowCount(0) # Clear table
    sorted_paths = sorted(list(new_paths))
    
    self.paths_table.setRowCount(len(sorted_paths))
    for row, path_str in enumerate(sorted_paths):
      p = Path(path_str)
      # Basic validation: ensure it's a dir or an image file (should be guaranteed by AppState ideally)
      if p.is_dir() or self._is_image_file(path_str):
        icon = self._get_path_icon(path_str)
        item = QTableWidgetItem(path_str)
        item.setIcon(icon)
        # Store the full path in UserRole if needed, though text() is likely the path itself
        item.setData(Qt.ItemDataRole.UserRole, path_str)
        self.paths_table.setItem(row, 0, item)
      else:
        # This path shouldn't be in the list if validation is working upstream
        # Or, we can add it with a warning icon
        item = QTableWidgetItem(f"[Invalid] {path_str}")
        item.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning))
        self.paths_table.setItem(row, 0, item)

    self._current_displayed_paths = new_paths.copy()
    # self.paths_table.resizeColumnsToContents() # Optional: adjust column width

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
      # Use app_state.selected_paths directly for the most up-to-date list
      current_paths_list = list(self._app_state.selected_paths) if self._app_state else []
      
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

    selected_rows = sorted(list(set(index.row() for index in self.paths_table.selectedIndexes())), reverse=True)
    if not selected_rows:
      return

    paths_to_remove = []
    for row in selected_rows:
        item = self.paths_table.item(row, 0)
        if item:
            paths_to_remove.append(item.text()) # Assuming item text is the path

    for path_to_remove in paths_to_remove:
      if self._app_state: # Check if app_state is available
          self._app_state.remove_selected_path(path_to_remove)
      # The _on_global_selection_changed slot will handle updating the table

  @Slot(QPoint)
  def _show_context_menu(self, pos: QPoint):
    """
    Shows the context menu for the table widget.
    """
    context_menu = QMenu(self)
    
    add_action = QAction("Add Path...", self)
    add_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)) # Example Icon
    add_action.triggered.connect(self._add_path_action)
    context_menu.addAction(add_action)

    # Add "Remove" only if items are selected
    if self.paths_table.selectedItems(): # Or check selectedIndexes()
      remove_action = QAction("Remove Selected", self)
      remove_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)) # Example Icon
      remove_action.triggered.connect(self._remove_selected_paths_action)
      context_menu.addAction(remove_action)
      
      context_menu.addSeparator()
      
      clear_all_action = QAction("Remove All Paths", self)
      clear_all_action.triggered.connect(self._clear_all_paths_action)
      context_menu.addAction(clear_all_action)


    context_menu.exec(self.paths_table.mapToGlobal(pos))

  @Slot()
  def _clear_all_paths_action(self):
    """Removes all paths from the selection."""
    if self._app_state:
        # Ask for confirmation
        reply = QMessageBox.question(self, "Confirm Clear",
                                     "Are you sure you want to remove all paths?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._app_state.clear_selected_paths()


  # --- Button Action Implementations ---
  @Slot()
  def _validate_paths_action(self):
    """Validates current paths for nesting and image types."""
    if not self._app_state or not self._app_state.selected_paths:
        QMessageBox.information(self, "Validate Paths", "No paths selected to validate.")
        return

    paths_to_check = list(self._app_state.selected_paths)
    errors = []
    try:
        check_nested(paths_to_check)
    except ValueError as e:
        errors.append(f"Nesting violation: {e}")
    
    for path_str in paths_to_check:
        p = Path(path_str)
        if p.is_file() and not self._is_image_file(path_str):
            errors.append(f"Not an image file: {path_str}")
        elif not p.exists(): # Should be caught earlier, but good to check
             errors.append(f"Path does not exist: {path_str}")


    if errors:
        QMessageBox.warning(self, "Validation Failed", "Found issues:\n\n" + "\n".join(errors))
    else:
        QMessageBox.information(self, "Validation Successful", "All selected paths are valid and not nested.")

  @Slot()
  def _list_files_action(self):
    """Lists all image files from the selected paths in a dialog."""
    if not self._app_state or not self._app_state.selected_paths:
        QMessageBox.information(self, "List Files", "No paths selected to list files from.")
        return

    current_paths = list(self._app_state.selected_paths)
    
    # Show a progress dialog as this might take time
    progress = QProgressDialog("Scanning files...", "Cancel", 0, 0, self) # Indeterminate
    progress.setWindowModality(Qt.WindowModality.WindowModal)
    progress.show()
    QApplication.processEvents() # Allow progress dialog to show

    try:
        all_image_files = get_all_image_files_in_paths(current_paths, DEFAULT_IMAGE_EXTENSIONS_PATTERNS)
    except Exception as e:
        progress.close()
        QMessageBox.critical(self, "Error Listing Files", f"An error occurred while gathering files:\n{e}")
        return
    finally:
        progress.close()


    dialog = QDialog(self)
    dialog.setWindowTitle(f"Image Files Found ({len(all_image_files)})")
    dialog.setMinimumWidth(600)
    dialog.setMinimumHeight(400)
    
    layout = QVBoxLayout(dialog)
    list_widget = QListWidget()
    if all_image_files:
        list_widget.addItems(sorted([str(f) for f in all_image_files]))
    else:
        list_widget.addItem("No image files found in the selected paths.")
        
    layout.addWidget(list_widget)
    
    button_box = QPushButton("OK", dialog)
    button_box.clicked.connect(dialog.accept)
    layout.addWidget(button_box)
    
    dialog.exec()


  @Slot()
  def _phash_files_action(self):
    """Computes and caches PHashes for all image files from selected paths."""
    if not self._app_state or not self._app_state.selected_paths:
        QMessageBox.information(self, "PHash Files", "No paths selected to PHash.")
        return
    
    if not self._app_state.file_info_cache: # Assuming cache is in app_state
        QMessageBox.critical(self, "PHash Error", "File info cache is not available.")
        return

    current_paths = list(self._app_state.selected_paths)
    
    # Initial progress for gathering files
    gather_progress = QProgressDialog("Gathering image files...", "Cancel", 0, 0, self)
    gather_progress.setWindowModality(Qt.WindowModality.WindowModal)
    gather_progress.show()
    QApplication.processEvents()

    try:
        all_image_files = get_all_image_files_in_paths(current_paths, DEFAULT_IMAGE_EXTENSIONS_PATTERNS)
    except Exception as e:
        gather_progress.close()
        QMessageBox.critical(self, "Error PHashing", f"Error gathering files for PHashing:\n{e}")
        return
    finally:
        gather_progress.close()

    if not all_image_files:
        QMessageBox.information(self, "PHash Files", "No image files found to PHash.")
        return

    cache: FileInfoCache = self._app_state.file_info_cache
    processed_count = 0
    error_count = 0

    phash_progress = QProgressDialog("Calculating PHashes...", "Cancel", 0, len(all_image_files), self)
    phash_progress.setWindowModality(Qt.WindowModality.WindowModal)
    phash_progress.setValue(0)
    phash_progress.show()

    for i, file_path_obj in enumerate(all_image_files):
        phash_progress.setValue(i)
        if phash_progress.wasCanceled():
            break
        
        file_path_str = str(file_path_obj)
        try:
            # This will compute and cache if necessary
            cache.get_phash(file_path_str) # Corrected method name
            processed_count +=1
        except Exception as e:
            # Log error or collect errors to show later
            print(f"Error PHashing {file_path_str}: {e}") # Simple console log for now
            error_count += 1
        QApplication.processEvents() # Keep UI responsive

    phash_progress.setValue(len(all_image_files))
    phash_progress.close()

    summary_message = f"PHashing complete.\nProcessed: {processed_count} files."
    if error_count > 0:
        summary_message += f"\nErrors encountered: {error_count} files (see console for details)."
    
    QMessageBox.information(self, "PHash Complete", summary_message)


if __name__ == '__main__':
  import sys
  from PySide6.QtWidgets import QApplication, QMainWindow
  import tempfile # For dummy cache

  # Dummy FileInfoCache for testing
  class DummyFileInfoCache:
    def __init__(self, db_path):
      self.db_path = db_path
      self._cache = {} # Simplified in-memory cache for phash
      print(f"DummyFileInfoCache initialized with db: {db_path}")

    def get_or_compute_phash(self, file_path_str: str) -> Optional[str]:
      if file_path_str in self._cache:
        print(f"PHash for {file_path_str} from cache: {self._cache[file_path_str]}")
        return self._cache[file_path_str]
      
      # Simulate PHash computation
      # In a real scenario, this would involve image loading and hashing
      if Path(file_path_str).exists() and Path(file_path_str).is_file():
          dummy_phash = f"phash_{Path(file_path_str).name}"
          self._cache[file_path_str] = dummy_phash
          print(f"Computed dummy PHash for {file_path_str}: {dummy_phash}")
          return dummy_phash
      print(f"Could not compute dummy PHash for {file_path_str}")
      return None

    def close(self):
        print("DummyFileInfoCache closed.")

  # Dummy AppState for testing
  class DummyAppState(QObject):
    selected_paths_changed = Signal(set)
    
    def __init__(self):
      super().__init__()
      self._selected_paths = set()
      # Create a temporary file for the dummy cache
      self._temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
      self.file_info_cache: Optional[DummyFileInfoCache] = DummyFileInfoCache(self._temp_db_file.name)
      print(f"Dummy AppState created with cache: {self._temp_db_file.name}")

    @property
    def selected_paths(self) -> Set[str]:
      return self._selected_paths.copy()

    def add_selected_path(self, path: str):
      if path not in self._selected_paths:
        self._selected_paths.add(path)
        self.selected_paths_changed.emit(self._selected_paths)
        print(f"Path added to dummy AppState: {path}")

    def remove_selected_path(self, path: str):
      if path in self._selected_paths:
        self._selected_paths.remove(path)
        self.selected_paths_changed.emit(self._selected_paths)
        print(f"Path removed from dummy AppState: {path}")

    def clear_selected_paths(self):
        self._selected_paths.clear()
        self.selected_paths_changed.emit(self._selected_paths)
        print("All paths cleared from dummy AppState.")
        
    def get_temp_db_path(self) -> str:
        return self._temp_db_file.name

    def cleanup(self):
        if self.file_info_cache:
            self.file_info_cache.close()
        self._temp_db_file.close()
        try:
            Path(self._temp_db_file.name).unlink(missing_ok=True)
            print(f"Temporary cache file {self._temp_db_file.name} deleted.")
        except Exception as e:
            print(f"Error deleting temporary cache file {self._temp_db_file.name}: {e}")


  app = QApplication(sys.argv)
  main_win = QMainWindow()
  main_win.setWindowTitle("Test SelectedPathsWidget")
  
  test_app_state = DummyAppState()
  
  selected_paths_w = SelectedPathsWidget()
  selected_paths_w.set_app_state(test_app_state)
  
  main_win.setCentralWidget(selected_paths_w)
  main_win.resize(600, 400) # Increased size for better visibility
  main_win.show()

  # Example: Add some initial paths for testing
  home_path_str = str(Path.home())
  test_app_state.add_selected_path(home_path_str)
  
  # Create a dummy file for PHash testing
  temp_dir = tempfile.TemporaryDirectory()
  dummy_image_file = Path(temp_dir.name) / "test_image.jpg"
  try:
      with open(dummy_image_file, "w") as f:
          f.write("dummy image content")
      test_app_state.add_selected_path(str(dummy_image_file))
      print(f"Added dummy image for testing: {dummy_image_file}")
  except Exception as e:
      print(f"Could not create dummy image file: {e}")


  exit_code = app.exec()
  
  # Cleanup dummy state
  test_app_state.cleanup()
  temp_dir.cleanup() # Clean up temporary directory

  sys.exit(exit_code)