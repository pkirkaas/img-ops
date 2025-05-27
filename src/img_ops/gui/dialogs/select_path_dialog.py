"""
Defines the SelectPathDialog for choosing a single folder or image file.
"""
import os
from PySide6.QtWidgets import (
    QDialog,
    QTreeView,
    QFileSystemModel,
    QVBoxLayout,
    QHBoxLayout,  # Added
    QDialogButtonBox,
    QSizePolicy,
    QLabel,  # For the TestWindow example
    QPushButton,  # Added
    QLineEdit,  # Added
    QSplitter,  # Added
    QListWidget,  # Added
    QListWidgetItem,  # Added
    QStyle  # Added for standard icons
)
from PySide6.QtCore import Qt, QDir, QModelIndex, Slot, QStandardPaths
from typing import Optional, List, Union  # Added Union
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
        self.setMinimumSize(700, 500)  # Increased default size
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

        self._selected_path: Optional[str] = None
        self._history: List[str] = []
        self._history_index: int = -1

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)

        # --- Top Navigation Bar ---
        nav_bar_layout = QHBoxLayout()

        self.back_button = QPushButton()
        self.back_button.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ArrowBack))
        self.back_button.setToolTip("Back")
        self.back_button.clicked.connect(self._navigate_back)
        self.back_button.setEnabled(False)  # Initially no history
        nav_bar_layout.addWidget(self.back_button)

        self.up_button = QPushButton()
        self.up_button.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ArrowUp))
        self.up_button.setToolTip("Up to parent directory")
        self.up_button.clicked.connect(self._navigate_up)
        nav_bar_layout.addWidget(self.up_button)

        self.path_line_edit = QLineEdit(self)
        self.path_line_edit.setReadOnly(True)  # For now, just display
        # self.path_line_edit.returnPressed.connect(self._navigate_to_entered_path) # Future: allow typing path
        nav_bar_layout.addWidget(self.path_line_edit, stretch=1)

        main_layout.addLayout(nav_bar_layout)

        # --- Main Content Area (Splitter) ---
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)
        main_layout.addWidget(self.splitter, stretch=1)

        # --- Places Panel (Left) ---
        self.places_list_widget = QListWidget(self)
        self.places_list_widget.setFixedWidth(150)  # Adjust as needed
        self.places_list_widget.itemClicked.connect(self._on_place_selected)
        self._populate_places()
        self.splitter.addWidget(self.places_list_widget)

        # --- File System Model and Tree View (Right) ---
        self.model = QFileSystemModel(self)
        # Set model root to "" to represent "This PC" / all drives level
        self.model.setRootPath("")
        self.model.setNameFilters(DEFAULT_IMAGE_EXTENSIONS_PATTERNS)
        self.model.setNameFilterDisables(False)

        self.tree_view = QTreeView(self)
        self.tree_view.setModel(self.model)
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree_view.setSelectionMode(
            QTreeView.SelectionMode.SingleSelection)
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)

        self.splitter.addWidget(self.tree_view)
        self.splitter.setSizes([150, 550])  # Initial sizes for splitter panes

        # --- Dialog Buttons (Bottom) ---
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        # --- Initial Path Setup & Connections ---
        if initial_path:
            start_dir = str(Path(initial_path).resolve())
        else:
            start_dir = ""  # Default to "This PC"

        # Initial path, don't add to history yet
        self._set_current_path_in_view(start_dir, add_to_history=False)
        # Select the initial path if it's valid and visible
        initial_index = self.model.index(start_dir)
        if initial_index.isValid():
            self.tree_view.setCurrentIndex(initial_index)
            # _on_selection_changed (triggered by setCurrentIndex) is responsible for setting
            # self._selected_path and updating the OK button state. This line is removed:
            # self._selected_path = self.model.filePath(initial_index) # Set initial selection

        self.tree_view.selectionModel().currentChanged.connect(self._on_selection_changed)
        self.tree_view.doubleClicked.connect(self._on_double_clicked)

        self._update_ok_button_state()
        self._update_nav_buttons_state()  # Update Up and Back buttons

    def _populate_places(self):
        """Populates the 'Places' list widget with common locations."""
        places = [
            ("Home", QDir.homePath(), QStyle.StandardPixmap.SP_DirHomeIcon),
            ("Desktop", QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DesktopLocation), QStyle.StandardPixmap.SP_DesktopIcon),
            # ("Documents", QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation), QStyle.StandardPixmap.SP_DirDocIcon),
            # ("Downloads", QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DownloadsLocation), QStyle.StandardPixmap.SP_DirLinkIcon), # Using link as placeholder
            # ("Pictures", QStandardPaths.writableLocation(QStandardPaths.StandardLocation.PicturesLocation), QStyle.StandardPixmap.SP_DirLinkIcon), # Using link as placeholder
            # Special case for drives
            ("This PC", "", QStyle.StandardPixmap.SP_ComputerIcon)
        ]
        for name, path, icon_enum in places:
            item = QListWidgetItem(name)
            item.setIcon(self.style().standardIcon(icon_enum))
            # Store path in UserRole
            item.setData(Qt.ItemDataRole.UserRole, path)
            self.places_list_widget.addItem(item)

        # Add Drives for "This PC"
        # This part can be complex if we want to list them under "This PC" item.
        # For simplicity now, just list drives directly after "This PC".
        for drive in QDir.drives():  # QFileInfo objects
            drive_path = drive.absoluteFilePath()
            item = QListWidgetItem(
                f"Drive {drive.filePath().upper()}")  # e.g. "Drive C:/"
            item.setIcon(self.style().standardIcon(
                QStyle.StandardPixmap.SP_DriveHDIcon))
            item.setData(Qt.ItemDataRole.UserRole, drive_path)
            self.places_list_widget.addItem(item)

    @Slot(QListWidgetItem)
    def _on_place_selected(self, item: QListWidgetItem):
        """Handles selection changes in the 'Places' list."""
        path_data = item.data(
            Qt.ItemDataRole.UserRole)  # This is the path string, or "" for This PC

        # Distinguish "This PC" (which has path_data == "") from other valid paths.
        if item.text() == "This PC":
            self._set_current_path_in_view("", is_this_pc_navigation=True)
        elif path_data is not None:  # For other places with actual paths
            self._set_current_path_in_view(path_data)

    def _add_to_history(self, path_str: str):
        """Adds a path to the navigation history."""
        # If we are navigating forward after going back, truncate future history
        if self._history_index < len(self._history) - 1:
            self._history = self._history[:self._history_index + 1]

        # Avoid adding consecutive duplicates to history
        # path_str here is the canonical path from the model (e.g., "" for This PC)
        if not self._history or self._history[-1] != path_str:
            self._history.append(path_str)
        self._history_index = len(self._history) - 1

    def _set_current_path_in_view(self, path_str: str, add_to_history: bool = True, is_this_pc_navigation: bool = False):
        """
        Sets the QTreeView's root index to the given path and updates UI elements.
        Manages navigation history.
        `is_this_pc_navigation` is a flag to ensure "This PC" (empty path) is handled correctly.
        """
        current_model_root_path = self.model.filePath(
            self.tree_view.rootIndex())

        # If the target path is the same as the current root, and it's not an explicit "This PC" re-selection, do nothing.
        if path_str == current_model_root_path and not (path_str == "" and is_this_pc_navigation):
            # If path_str is "" and current_model_root_path is also "", but it wasn't a "This PC" click,
            # it might be a no-op from _navigate_up when already at "This PC".
            # If it *was* a "This PC" click (is_this_pc_navigation=True), we should proceed to update UI.
            if not (path_str == "" and current_model_root_path == "" and is_this_pc_navigation):
                # If it's a non-empty path that matches, definitely no-op.
                if path_str != "":
                    return
                # If both are "" but not a "This PC" click, it's a no-op (e.g. up from C:/ then up again)
                elif not is_this_pc_navigation:
                    return

        # For path_str="", this gives the "Computer" level
        target_model_index = self.model.index(path_str)

        if not target_model_index.isValid() and path_str != "":  # "" is a valid index for the model root
            # print(f"Warning: Path '{path_str}' is not valid in the model.")
            return

        self.tree_view.setRootIndex(target_model_index)
        # If we just navigated to "This PC" (empty string path)
        if path_str == "":
            # Force the view to completely refresh from the model at this new root
            self.tree_view.reset()

        # Use the canonical path from the model for display and history
        # For "This PC", model.filePath(model.index("")) returns ""
        canonical_path_from_model = self.model.filePath(target_model_index)

        # This means path_str was "" (This PC)
        if not canonical_path_from_model:
            self.path_line_edit.setText("This PC")
        else:
            self.path_line_edit.setText(canonical_path_from_model)

        if add_to_history:
            # Store "" for "This PC"
            self._add_to_history(canonical_path_from_model)

        self._update_nav_buttons_state()
        self.tree_view.clearSelection()
        self._selected_path = None
        self._update_ok_button_state()

    @Slot()
    def _navigate_up(self):
        """Navigates the tree view to the parent of its current root directory."""
        current_root_index = self.tree_view.rootIndex()
        parent_index = current_root_index.parent()

        # filePath of model.index("") is ""
        # filePath of parent of model.index("C:/") is ""
        # filePath of parent of model.index("") is "" (parent of root is also root for QFileSystemModel)

        parent_path_str = self.model.filePath(parent_index)
        current_path_str = self.model.filePath(current_root_index)

        if parent_index.isValid() and parent_path_str != current_path_str:
            # If parent_path_str is "", it means we are navigating up to "This PC"
            self._set_current_path_in_view(
                parent_path_str, is_this_pc_navigation=(parent_path_str == ""))
        # If parent is not valid or same as current, we are at the top ("This PC"), do nothing.

    @Slot()
    def _navigate_back(self):
        """Navigates to the previous path in history."""
        if self._history_index > 0:
            self._history_index -= 1
            path_to_go = self._history[self._history_index]
            self._set_current_path_in_view(
                path_to_go, add_to_history=False)  # Don't re-add to history

    def _update_nav_buttons_state(self):
        """Updates the enabled state of Up and Back buttons."""
        # Up button
        current_root_index = self.tree_view.rootIndex()
        # Enable "Up" if the parent of the current root is valid AND not the same as current root
        # (QFileSystemModel's root "" has parent "" which is valid but not navigable up)
        parent_of_root = current_root_index.parent()
        can_go_up = parent_of_root.isValid() and self.model.filePath(
            parent_of_root) != self.model.filePath(current_root_index)
        self.up_button.setEnabled(can_go_up)

        # Back button
        self.back_button.setEnabled(self._history_index > 0)
        # Forward button (if implemented) would be: self._history_index < len(self._history) - 1

    @Slot(QModelIndex, QModelIndex)
    def _on_selection_changed(self, current: QModelIndex, previous: QModelIndex):
        """
        Handles changes in the tree view's current selection.
        Updates the internal selected path.
        """
        if current.isValid():
            file_path = self.model.filePath(current)
            file_info = self.model.fileInfo(current)
            # We need to check if the selected item is an image file or a directory.
            # The filter should ensure only images or dirs are visible.
            if file_info.isDir() or (file_info.isFile() and self._is_image_file(file_path)):
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
            path_str = self.model.filePath(index)
            file_info = self.model.fileInfo(index)
            if file_info.isDir():
                self._set_current_path_in_view(path_str)
            elif file_info.isFile() and self._is_image_file(path_str):
                self._selected_path = path_str  # Update selected path
                self._update_ok_button_state()  # Enable OK if not already
                self.accept()  # Accept dialog on double-clicking a file

    def _is_image_file(self, file_path: str) -> bool:
        """Checks if a file path matches one of the image extensions."""
        if not file_path:
            return False
        # Check against the patterns (case-insensitive for extension part)
        path_obj = Path(file_path)
        file_ext_lower = path_obj.suffix.lower()  # e.g. ".jpg"

        for pattern in DEFAULT_IMAGE_EXTENSIONS_PATTERNS:
            # pattern is like "*.jpg"
            pattern_ext_lower = pattern[1:].lower()  # e.g. ".jpg"
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
        dialog = SelectPathDialog(
            initial_path=initial_path, title=title, parent=parent)
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

            # Get central widget if button is central
            layout = QVBoxLayout(self.button.parentWidget())
            if not layout:  # If button was not set as central widget directly
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

            path = SelectPathDialog.get_path(
                self, initial_path=pictures_path, title="Choose an Image or Folder")
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
