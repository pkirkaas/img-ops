"""
Defines the MainWindow class for the img-ops application.
"""
from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QDialog,
                            QMessageBox)
from PySide6.QtCore import Qt
from ..widgets.resize_container import ResizeContainer
from ..widgets.tree_select import TreeSelect
from ..widgets.image_viewer import ImageViewer
from ..widgets.show_selected import ShowSelected
from ..widgets.app_config_widget import AppConfigWidget
from ..widgets.current_config_display import CurrentConfigDisplay
from ..state import AppState
from ...core.app_config import AppConfiguration, get_config_manager

class MainWindow(QMainWindow):
  """
  The main application window.

  This window will host the primary user interface elements,
  such as image viewers, file browsers, and control panels.
  """
  def __init__(self, parent=None):
    """
    Initializes the MainWindow, setting up the main application frame,
    initial size, title, and basic UI elements like menus and a status bar.
    This window serves as the primary container for other widgets.

    Args:
      parent (QWidget, optional): The parent widget. Defaults to None.
    """
    super().__init__(parent)

    self.setWindowTitle("Img-Ops - Image Operations")
    self.setGeometry(100, 100, 900, 400) # x, y, width, height

    # Initialize the application state
    self.app_state = AppState(self)

    # Initialize configuration management
    self.config_manager = get_config_manager()
    self.app_config = self.config_manager.get_default_configuration()

    # --- Central widget setup with ResizeContainers ---
    v_splitter_main = ResizeContainer(orientation=Qt.Orientation.Vertical, parent=self)
    self.setCentralWidget(v_splitter_main)

    # Top horizontal container
    h_splitter_top = ResizeContainer(orientation=Qt.Orientation.Horizontal, background_color="lightblue", parent=v_splitter_main)
    
    # Create and add the TreeSelect widget to the top-left pane
    # It will default to showing the system root ("This PC" / "/")
    self.tree_select_widget = TreeSelect(parent=h_splitter_top)
    self.tree_select_widget.set_app_state(self.app_state)
    h_splitter_top.addWidget(self.tree_select_widget)
    
    # Create and add the ShowSelected widget to the top-right pane
    self.show_selected_widget = ShowSelected(parent=h_splitter_top)
    self.show_selected_widget.set_app_state(self.app_state)
    h_splitter_top.addWidget(self.show_selected_widget)
    
    h_splitter_top.setWidgetSizes([150, 150]) # Initial sizes for top horizontal panes

    # Bottom horizontal container
    h_splitter_bottom = ResizeContainer(orientation=Qt.Orientation.Horizontal, background_color="lightcoral", parent=v_splitter_main)

    # Create and add the ImageViewer to the bottom-left pane
    self.image_viewer_bl = ImageViewer(parent=h_splitter_bottom)
    # It's good practice to ensure the path separator is correct for the OS,
    # though Python's open and QPixmap are often flexible.
    # For Windows paths given with backslashes in strings, they might need escaping
    # or use raw strings r"Z:\..." or forward slashes "Z:/...".
    # QPixmap should handle "Z:\Photos\FavG\465826_6adaadb6_crop.jpg" correctly on Windows.
    image_path = r"Z:\Photos\FavG\465826_6adaadb6_crop.jpg"
    self.image_viewer_bl.set_image_from_path(image_path)
    h_splitter_bottom.addWidget(self.image_viewer_bl)

    label_br = QLabel("Bottom-Right Pane", h_splitter_bottom)
    label_br.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label_br.setStyleSheet("background-color: #fce4ec; border: 1px solid #f8bbd0; padding: 5px;")
    h_splitter_bottom.addWidget(label_br)

    h_splitter_bottom.setWidgetSizes([150, 150]) # Initial sizes for bottom horizontal panes

    # Add horizontal splitters to the main vertical splitter
    v_splitter_main.addWidget(h_splitter_top)
    v_splitter_main.addWidget(h_splitter_bottom)
    v_splitter_main.setWidgetSizes([200, 200]) # Initial sizes for vertical split

    # Add configuration display widget to the status bar area
    self.config_display = CurrentConfigDisplay(parent=self)
    self.config_display.update_display(self.app_config) # Populate the display
    self.statusBar().addPermanentWidget(self.config_display, stretch=1)

    self._create_menus()
    self._create_status_bar()
    
    # Connect additional signals for enhanced functionality
    self._connect_signals()
  
  def _connect_signals(self):
    """
    Connect additional signals between widgets and state for enhanced functionality.
    """
    # Connect tree selection changes to update status bar
    self.app_state.selected_paths_changed.connect(self._on_selection_changed)
  
  def _on_selection_changed(self, selected_paths):
    """
    Handle changes to the selected paths by updating the status bar.
    
    Args:
      selected_paths (Set[str]): The new set of selected file paths.
    """
    count = len(selected_paths)
    if count == 0:
      self.statusBar().showMessage("Ready")
    elif count == 1:
      self.statusBar().showMessage(f"1 file selected")
    else:
      self.statusBar().showMessage(f"{count} files selected")

  def _create_menus(self):
    """
    Creates the main menu bar and its actions.
    """
    menu_bar = self.menuBar()

    # File menu
    file_menu = menu_bar.addMenu("&File")
    open_action = file_menu.addAction("&Open...")

    # Settings menu with configuration option
    settings_menu = menu_bar.addMenu("&Settings")
    config_action = settings_menu.addAction("&Configuration...")
    config_action.triggered.connect(self._show_config_dialog)
    # open_action.triggered.connect(self.open_file_dialog)
    exit_action = file_menu.addAction("E&xit")
    exit_action.triggered.connect(self.close)

    help_menu = menu_bar.addMenu("&Help")
    about_action = help_menu.addAction("&About")
    # about_action.triggered.connect(self.show_about_dialog)

  def _create_status_bar(self):
    """
    Creates the status bar.
    """
    self.statusBar().showMessage("Ready")

  # Placeholder methods for actions (to be implemented)
  # def open_file_dialog(self):
  #   print("Placeholder: Open file dialog triggered.")

  # def show_about_dialog(self):
  #   print("Placeholder: Show about dialog triggered.")

  def _show_config_dialog(self):
    """
    Shows the configuration dialog and handles the result.

    Creates an AppConfigWidget dialog, shows it modally, and if accepted,
    updates the current configuration and refreshes the display.
    """
    # Create a QDialog to host the AppConfigWidget
    config_dialog = QDialog(self)
    config_dialog.setWindowTitle("Application Configuration")
    config_dialog.setMinimumSize(700, 500) # Adjust size as needed

    # Create the AppConfigWidget instance
    # Pass config_dialog as parent so AppConfigWidget can call accept/reject on it
    app_config_widget = AppConfigWidget(config_manager=self.config_manager,
                                        current_config_name=self.app_config.name,
                                        parent=config_dialog)

    # Set up layout for the QDialog
    dialog_layout = QVBoxLayout(config_dialog)
    dialog_layout.addWidget(app_config_widget)
    config_dialog.setLayout(dialog_layout)
    
    # Show the dialog modally
    if config_dialog.exec() == QDialog.DialogCode.Accepted:
        try:
            # The AppConfigWidget handles saving via its OK button.
            # We retrieve the name of the configuration that was selected or active
            # when the dialog was accepted.
            updated_config_name = app_config_widget.get_selected_config_name()
            if updated_config_name:
              self.app_config = self.config_manager.get_configuration(updated_config_name)
              if self.app_config:
                self.config_display.update_display(self.app_config)
                self.statusBar().showMessage(f"Configuration '{self.app_config.name}' loaded.", 3000)
              else:
                # Fallback to default if the selected one somehow isn't found
                self.app_config = self.config_manager.get_default_configuration()
                self.config_display.update_display(self.app_config)
                QMessageBox.warning(self, "Configuration Error", f"Could not load configuration: {updated_config_name}. Reverted to default.")
            else: # If no specific config was selected, refresh with current (possibly default)
                self.app_config = self.config_manager.get_configuration(self.app_config.name) or self.config_manager.get_default_configuration()
                self.config_display.update_display(self.app_config)

            # The AppConfigWidget should call self.config_manager.save_to_file() internally upon acceptance.
            # If not, we might need to call it here:
            # self.config_manager.save_to_file()
            # For now, assuming the widget handles saving.

        except Exception as e:
            QMessageBox.warning(
                self,
                "Configuration Error",
                f"Failed to update or apply configuration: {str(e)}"
            )

if __name__ == '__main__':
  # This part is for testing the MainWindow independently
  import sys
  from PySide6.QtWidgets import QApplication
  app = QApplication(sys.argv)
  main_win = MainWindow()
  main_win.show()
  sys.exit(app.exec())