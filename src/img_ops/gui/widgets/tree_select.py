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
    QDialogButtonBox,
    QHBoxLayout  # Added for button layout
)
from PySide6.QtCore import Qt, QModelIndex, QDir, Signal
from typing import Dict, Set, List

# Import the new function
from src.img_ops.core.file_system import extract_paths


class CheckableFileSystemModel(QFileSystemModel):
    """
    A QFileSystemModel subclass that supports checkable items.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # Store check states by file path
        self.check_states: Dict[str, Qt.CheckState] = {}

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
            self.dataChanged.emit(
                index, index, [Qt.ItemDataRole.CheckStateRole])

            # Propagate check state to children if it's a directory (one-way propagation)
            if self.isDir(index) and current_check_state == Qt.CheckState.Checked:
                self._propagate_check_to_children(index, current_check_state)
            # Note: Unchecking a parent does not automatically uncheck children in this current implementation.
            # For full parent-child check synchronization or tri-state behavior,
            # this logic would need to be extended (e.g., iterating children on uncheck,
            # or implementing tri-state for parent to reflect mixed child states).
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
                self.dataChanged.emit(child_index, child_index, [
                                      Qt.ItemDataRole.CheckStateRole])
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

    Signals:
      selection_changed: Emitted when the selection (checked items) changes.
                        Args: selected_paths (Set[str]) - The new set of selected paths
    """

    # Signal emitted when selection changes
    selection_changed = Signal(set)  # Set[str] of selected file paths

    def __init__(self, initial_display_path: str = "", parent: QWidget = None):
        """
        Initializes the TreeSelect widget.

        Args:
          initial_display_path (str, optional): The path to initially display in the tree.
                                                Defaults to "" which shows system drives
                                                (e.g., "This PC" on Windows, "/" on Linux).
          parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        self.model = CheckableFileSystemModel(self)
        # Set the model's root to the conceptual file system root.
        # This allows navigation anywhere if initial_display_path is deep.
        self.model.setRootPath("")

        # Connect to model's dataChanged signal to emit our selection_changed signal
        self.model.dataChanged.connect(self._on_model_data_changed)

        self.tree_view = QTreeView(self)
        self.tree_view.setModel(self.model)
        # Set what the view initially displays.
        # If initial_display_path is "", model.index("") correctly points to "This PC" / drives.
        self.tree_view.setRootIndex(self.model.index(initial_display_path))
        # Optional: for smoother expand/collapse
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Hide all columns except the name (column 0)
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)

        # When an item is expanded, ensure its children are loaded if not already
        self.tree_view.expanded.connect(self._handle_expanded)
        # Connect a signal to update the "Up" button when the root index changes (e.g. by double click)
        # However, QTreeView doesn't have a direct rootIndexChanged signal.
        # We will manage this via our navigation methods.

        self.up_button = QPushButton("Up", self)
        self.up_button.clicked.connect(self._navigate_up)

        self.show_selected_button = QPushButton("Show Selected", self)
        self.show_selected_button.clicked.connect(
            self._show_selected_items_dialog)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.up_button)
        button_layout.addWidget(self.show_selected_button)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tree_view)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self._update_up_button_state()  # Set initial state

        # Reference to the app state (will be set by the main window)
        self._app_state = None

    def _navigate_up(self):
        """
        Navigates the tree view's root to its parent directory.
        """
        current_root = self.tree_view.rootIndex()
        parent_of_current_root = current_root.parent()

        if parent_of_current_root.isValid():
            self.tree_view.setRootIndex(parent_of_current_root)
            self._update_up_button_state()
        # If parent is not valid, we are at the top-most level the view can show
        # (which is the model's actual root, e.g., "This PC").

    def _update_up_button_state(self):
        """
        Enables or disables the 'Up' button based on the current view root.
        """
        current_root = self.tree_view.rootIndex()
        # The button is enabled if the parent of the current view root is a valid model index.
        # This means we are not at the absolute root of what QFileSystemModel can show (e.g. "This PC").
        can_go_up = current_root.parent().isValid()
        self.up_button.setEnabled(can_go_up)

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
        If directories are selected, it will list all files within those directories recursively.
        """
        checked_items_paths: Set[str] = self.model.get_checked_items()

        if not checked_items_paths:
            QMessageBox.information(
                self, "Selected Items", "No items are currently selected.")
            return

        # Use extract_paths to get all individual files
        # Convert set to list for extract_paths function
        all_file_paths: List[str] = extract_paths(list(checked_items_paths))

        if not all_file_paths:
            QMessageBox.information(
                self, "Selected Items", "No files found in the selected items (perhaps only empty directories were selected or paths were invalid).")
            return

        # Using a custom dialog for better text display
        dialog = QDialog(self)
        # Changed title to reflect it shows files
        dialog.setWindowTitle("Selected Files")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(300)

        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit(dialog)
        text_edit.setReadOnly(True)
        # Display the processed list of files
        text_edit.setText("\n".join(sorted(all_file_paths)))
        layout.addWidget(text_edit)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok, dialog)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.exec()

    def setDisplayPath(self, path: str):
        """
        Sets the path that the TreeView should display as its root.
        The underlying QFileSystemModel still retains its full system access if initialized with rootPath("").
        """
        target_index = self.model.index(path)
        if target_index.isValid():
            self.tree_view.setRootIndex(target_index)
            self._update_up_button_state()
        else:
            print(
                f"Warning: TreeSelect.setDisplayPath - Path '{path}' is not valid in the model.")

    def set_app_state(self, app_state):
        """
        Connect this widget to the application state.

        Args:
          app_state (AppState): The application state manager.
        """
        self._app_state = app_state

        # Initialize the app state with current selection
        if self._app_state:
            current_selection = self.model.get_checked_items()
            self._app_state.set_selected_paths(current_selection)

    def _on_model_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles: list):
        """
        Handle changes to the model data, specifically check state changes.

        Args:
          top_left (QModelIndex): The top-left index of the changed data.
          bottom_right (QModelIndex): The bottom-right index of the changed data.
          roles (list): The roles that changed.
        """
        # Check if the CheckStateRole was changed
        if Qt.ItemDataRole.CheckStateRole in roles:
            # Get the current selection and emit the signal
            current_selection = self.model.get_checked_items()
            self.selection_changed.emit(current_selection)

            # Update the app state if connected
            if self._app_state:
                self._app_state.set_selected_paths(current_selection)

    def get_selected_items(self) -> Set[str]:
        """
        Get the currently selected (checked) items.

        Returns:
          Set[str]: The set of currently selected file paths.
        """
        return self.model.get_checked_items()


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    # Test with default root (system drives / "This PC")
    main_widget = TreeSelect()
    main_widget.setWindowTitle(f"Test TreeSelect - Default Root")
    # Example of setting a specific display path after initialization:
    # test_display_path = QDir.homePath()
    # main_widget.setDisplayPath(test_display_path)
    # main_widget.setWindowTitle(f"Test TreeSelect - Root: {test_display_path}")
    main_widget.resize(600, 400)
    main_widget.show()

    sys.exit(app.exec())
