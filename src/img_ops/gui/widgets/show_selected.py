"""
Defines the ShowSelected widget for displaying selected file paths.
"""
from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Slot
from typing import Set


class ShowSelected(QWidget):
    """
    A widget that displays the currently selected file paths in a multi-line text area.

    This widget automatically updates when the application state changes,
    showing each selected path on a separate line.
    """

    def __init__(self, parent=None):
        """
        Initialize the ShowSelected widget.

        Args:
          parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)

        # Create the UI components
        self._setup_ui()

        # Reference to the app state (will be set by the main window)
        self._app_state = None

    def _setup_ui(self):
        """
        Set up the user interface components.
        """
        # Create layout
        layout = QVBoxLayout(self)

        # Create title label
        title_label = QLabel("Selected Files:", self)
        title_label.setStyleSheet("""
      QLabel {
        font-weight: bold;
        font-size: 12px;
        color: #333;
        padding: 2px;
        background-color: #f0f0f0;
        border: 1px solid #ccc;
        border-radius: 3px;
      }
    """)
        layout.addWidget(title_label)

        # Create text display area
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText("No files selected")

        # Style the text display
        self.text_display.setStyleSheet("""
      QTextEdit {
        background-color: #fafafa;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 10px;
        line-height: 1.2;
      }
    """)

        layout.addWidget(self.text_display)

        # Set layout margins
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(3)

        self.setLayout(layout)

    def set_app_state(self, app_state):
        """
        Connect this widget to the application state.

        Args:
          app_state (AppState): The application state manager.
        """
        self._app_state = app_state

        # Connect to state change signals
        if self._app_state:
            self._app_state.selected_paths_changed.connect(
                self._on_selected_paths_changed)

            # Initialize with current state
            self._on_selected_paths_changed(self._app_state.selected_paths)

    @Slot(set)
    def _on_selected_paths_changed(self, selected_paths: Set[str]):
        """
        Handle changes to the selected paths.

        Args:
          selected_paths (Set[str]): The new set of selected file paths.
        """
        if not selected_paths:
            self.text_display.setPlainText("")
            return

        # Convert to sorted list and display each path on a separate line
        sorted_paths = sorted(list(selected_paths))
        display_text = "\n".join(sorted_paths)

        self.text_display.setPlainText(display_text)

        # Scroll to top to show the first entries
        cursor = self.text_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.text_display.setTextCursor(cursor)

    def clear_display(self):
        """
        Clear the display area.
        """
        self.text_display.setPlainText("")

    def get_displayed_paths(self) -> list:
        """
        Get the currently displayed paths as a list.

        Returns:
          list: The currently displayed file paths.
        """
        text = self.text_display.toPlainText().strip()
        if not text:
            return []
        return [line.strip() for line in text.split('\n') if line.strip()]


if __name__ == '__main__':
    # Test the widget independently
    import sys
    from PySide6.QtWidgets import QApplication
    from ..state import AppState

    app = QApplication(sys.argv)

    # Create test state
    app_state = AppState()

    # Create and show widget
    widget = ShowSelected()
    widget.set_app_state(app_state)
    widget.setWindowTitle("Test ShowSelected Widget")
    widget.resize(400, 300)
    widget.show()

    # Test with some sample data
    test_paths = {
        "/home/user/documents/file1.txt",
        "/home/user/pictures/image1.jpg",
        "/home/user/pictures/image2.png",
        "/home/user/downloads/archive.zip"
    }
    app_state.set_selected_paths(test_paths)

    sys.exit(app.exec())
