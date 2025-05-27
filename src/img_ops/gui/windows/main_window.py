"""
Defines the MainWindow class for the img-ops application.
"""
from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QDialog,
                            QMessageBox, QToolBar) # Added QToolBar
from PySide6.QtCore import Qt, Slot # Added Slot
from ..widgets.resize_container import ResizeContainer
# from ..widgets.tree_select import TreeSelect # Removed
from ..widgets.image_viewer import ImageViewer
# from ..widgets.show_selected import ShowSelected # Removed
from ..widgets.app_config_widget import AppConfigWidget
from ..widgets.current_config_display import CurrentConfigDisplay
from ..widgets.selected_paths_widget import SelectedPathsWidget # New import
from ..widgets.select_configuration_widget import SelectConfigurationWidget # Import new widget
from ..state import AppState
from ...core.app_config import AppConfiguration, get_config_manager
from ...core.file_info_cache import FileInfoCache
from ..dialogs.cache_status_dialog import CacheStatusDialog
from ..utils import show_selectable_message_box # Import the centralized helper


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
    self.app_config = self.config_manager.get_default_configuration() # Initial active config
    self.app_state.set_selected_paths(set(self.app_config.paths)) # Initialize AppState

    # Initialize FileInfoCache
    # In a real application, you might want to manage the lifecycle of this cache
    # more carefully, e.g., as a singleton or passed via dependency injection.
    # For now, we create an instance here.
    try:
      self.file_info_cache = FileInfoCache() # Uses default DB path
    except Exception as e:
      self.file_info_cache = None # Indicate cache is not available
      show_selectable_message_box(
          self,
          QMessageBox.Icon.Critical,
          "Cache Initialization Error",
          f"Failed to initialize the file information cache: {e}\n\nCache functionality will be disabled."
      )
    
    # Set the initialized cache on the AppState instance
    if self.file_info_cache:
        self.app_state.set_file_info_cache(self.file_info_cache)
    else:
        # If cache initialization failed, app_state.file_info_cache will remain None
        # Widgets trying to use it should handle this gracefully (as SelectedPathsWidget does)
        print("MainWindow: FileInfoCache was not initialized, so not setting it on AppState.")


    # --- Toolbar Setup ---
    self.toolbar = QToolBar("Main Toolbar")
    self.toolbar.setMovable(False) # Optional: prevent toolbar from being moved
    self.addToolBar(self.toolbar)

    self.select_config_widget_toolbar = SelectConfigurationWidget(
        config_manager=self.config_manager,
        app_state=self.app_state, # Pass app_state
        parent=self # Parent to the main window for lifecycle management
    )
    self.toolbar.addWidget(self.select_config_widget_toolbar)

    # --- Central widget setup with ResizeContainers ---
    v_splitter_main = ResizeContainer(orientation=Qt.Orientation.Vertical, parent=self)
    self.setCentralWidget(v_splitter_main)

    # The v_splitter_main will now hold the main content area directly.
    # We'll create a horizontal splitter for the ImageViewer and SelectedPathsWidget.
    
    main_content_splitter = ResizeContainer(orientation=Qt.Orientation.Horizontal, background_color="lightcoral", parent=v_splitter_main)

    # Create and add the ImageViewer to the left pane
    self.image_viewer_main = ImageViewer(parent=main_content_splitter)
    image_path = r"Z:\Photos\FavG\465826_6adaadb6_crop.jpg" # Example path
    self.image_viewer_main.set_image_from_path(image_path)
    main_content_splitter.addWidget(self.image_viewer_main)

    # Create and add the SelectedPathsWidget to the right pane
    self.selected_paths_widget_main = SelectedPathsWidget(parent=main_content_splitter)
    self.selected_paths_widget_main.set_app_state(self.app_state)
    main_content_splitter.addWidget(self.selected_paths_widget_main)
    
    main_content_splitter.setWidgetSizes([300, 200]) # Adjust initial sizes as needed

    v_splitter_main.addWidget(main_content_splitter) # Add the main content area
    # v_splitter_main will only have one child now, so setWidgetSizes might not be strictly needed
    # or should be adjusted if more direct children are added to v_splitter_main later.
    # For now, let the ResizeContainer manage its single child's size.

    # Add configuration display widget to the status bar area
    self.config_display = CurrentConfigDisplay(parent=self)
    config_file_path_str = self.config_manager.config_file_path if self.config_manager.config_file_path else None
    self.config_display.update_display(self.app_config, config_file_path_str) # Populate the display
    self.statusBar().addPermanentWidget(self.config_display, stretch=1)

    self._create_menus()
    self._create_status_bar()
    
    # Connect additional signals for enhanced functionality
    self._connect_signals()
    
    # Initial load of paths from the default/active config into SelectedPathsWidget (via AppState)
    self._load_paths_from_current_config()
  
  def _load_paths_from_current_config(self):
    """
    Updates AppState (and thus SelectedPathsWidget) with paths from the current self.app_config.
    """
    if self.app_config:
        self.app_state.set_selected_paths(set(self.app_config.paths))
        # print(f"Loaded paths from '{self.app_config.name}' into SelectedPathsWidget: {self.app_config.paths}")
    else:
        self.app_state.clear_selected_paths() # Clear if no config active
        # print("No active config, cleared paths in SelectedPathsWidget.")

  def _connect_signals(self):
    """
    Connect additional signals between widgets and state for enhanced functionality.
    """
    # When AppState's selected paths change (e.g., from SelectedPathsWidget),
    # update the current app_config and save it.
    self.app_state.selected_paths_changed.connect(self._on_app_state_paths_changed)
    
    # Connect the toolbar config selector widget
    self.select_config_widget_toolbar.configuration_selected.connect(self._on_toolbar_config_selected)
  
  @Slot(str)
  def _on_toolbar_config_selected(self, config_name: str):
    """
    Handles configuration selection from the toolbar widget.
    Updates the main application's active configuration and loads its paths.
    """
    new_config = self.config_manager.get_configuration(config_name)
    if new_config:
        if self.app_config is None or self.app_config.name != new_config.name:
            self.app_config = new_config
            config_file_path_str = self.config_manager.config_file_path if self.config_manager.config_file_path else None
            self.config_display.update_display(self.app_config, config_file_path_str)
            self.statusBar().showMessage(f"Configuration '{self.app_config.name}' activated.", 3000)
            
            self._load_paths_from_current_config() # Load paths for the new config
            print(f"MainWindow: Active configuration changed to '{self.app_config.name}' via toolbar.")
    else:
        show_selectable_message_box(
            self,
            QMessageBox.Icon.Warning,
            "Configuration Error",
            f"Could not load selected configuration: {config_name}"
        )
        # Optionally, revert the combobox in select_config_widget_toolbar to the previous valid config
        if self.app_config:
             self.select_config_widget_toolbar.set_selected_configuration(self.app_config.name)

  @Slot(set)
  def _on_app_state_paths_changed(self, new_paths_set: set):
    """
    Called when AppState.selected_paths changes (e.g., user modified in SelectedPathsWidget).
    Updates the current self.app_config.paths and saves the configuration.
    Also updates the status bar.
    """
    if self.app_config:
        new_paths_list = sorted(list(new_paths_set))
        if self.app_config.paths != new_paths_list: # Check if there's an actual change
            self.app_config.paths = new_paths_list
            try:
                self.config_manager.save_to_file() # Save the updated configuration
                # print(f"Saved updated paths for config '{self.app_config.name}' to file.")
                # Update the status bar based on the new path count
                self._update_status_bar_path_count(len(new_paths_list))

            except ConfigError as e:
                show_selectable_message_box(
                    self,
                    QMessageBox.Icon.Critical,
                    "Save Error",
                    f"Failed to save configuration changes for '{self.app_config.name}':\n{e}"
                )
        else: # Even if list content is same, count might be what status bar needs
            self._update_status_bar_path_count(len(new_paths_list))

    else: # No active config, just update status bar
        self._update_status_bar_path_count(len(new_paths_set))


  def _update_status_bar_path_count(self, count: int):
    """Updates the status bar message based on the number of paths."""
    if count == 0:
      self.statusBar().showMessage("Ready - No paths selected")
    elif count == 1:
      self.statusBar().showMessage(f"1 path selected")
    else:
      self.statusBar().showMessage(f"{count} paths selected")

  # _on_selection_changed was removed as its functionality is now handled by
  # _on_app_state_paths_changed calling _update_status_bar_path_count.

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

    # Cache menu
    cache_menu = menu_bar.addMenu("&Cache")
    clear_cache_action = cache_menu.addAction("&Clear Cache")
    clear_cache_action.triggered.connect(self._clear_file_cache)
    clean_cache_action = cache_menu.addAction("C&lean Cache")
    clean_cache_action.triggered.connect(self._clean_file_cache)
    cache_status_action = cache_menu.addAction("Cache &Status...")
    cache_status_action.triggered.connect(self._show_cache_status_dialog)

    # Disable cache menu items if cache is not available
    if not self.file_info_cache:
        cache_menu.setEnabled(False)


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

    # Connect the AppConfigWidget's signal to refresh the toolbar's selector
    # This ensures if a config is added/deleted/renamed in the dialog, the toolbar updates.
    app_config_widget.configuration_changed.connect(
        lambda changed_config_name: self.select_config_widget_toolbar.refresh_configurations(
            select_config_name=self.app_config.name # Try to keep current selection if possible
        )
    )
    
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
                config_file_path_str = self.config_manager.config_file_path if self.config_manager.config_file_path else None
                self.config_display.update_display(self.app_config, config_file_path_str)
                self.statusBar().showMessage(f"Configuration '{self.app_config.name}' loaded.", 3000)
                # Update the toolbar selector and load paths
                self.select_config_widget_toolbar.refresh_configurations(select_config_name=self.app_config.name)
                self._load_paths_from_current_config()
              else:
                # Fallback to default if the selected one somehow isn't found
                self.app_config = self.config_manager.get_default_configuration()
                config_file_path_str = self.config_manager.config_file_path if self.config_manager.config_file_path else None
                self.config_display.update_display(self.app_config, config_file_path_str)
                self.select_config_widget_toolbar.refresh_configurations(select_config_name=self.app_config.name)
                self._load_paths_from_current_config()
                show_selectable_message_box(self, QMessageBox.Icon.Warning, "Configuration Error", f"Could not load configuration: {updated_config_name}. Reverted to default.")
            else: # If no specific config was selected, refresh with current (possibly default)
                self.app_config = self.config_manager.get_configuration(self.app_config.name) or self.config_manager.get_default_configuration()
                config_file_path_str = self.config_manager.config_file_path if self.config_manager.config_file_path else None
                self.config_display.update_display(self.app_config, config_file_path_str)
                self.select_config_widget_toolbar.refresh_configurations(select_config_name=self.app_config.name)
                self._load_paths_from_current_config()

            # The AppConfigWidget should call self.config_manager.save_to_file() internally upon acceptance.
            # If not, we might need to call it here:
            # self.config_manager.save_to_file()
            # For now, assuming the widget handles saving.

        except Exception as e:
            show_selectable_message_box(
                self,
                QMessageBox.Warning,
                "Configuration Error",
                f"Failed to update or apply configuration: {str(e)}"
            )

  def _clear_file_cache(self):
    """
    Handles the 'Clear Cache' menu action.
    Confirms with the user and then clears the file info cache.
    """
    if not self.file_info_cache:
      show_selectable_message_box(self, QMessageBox.Icon.Warning, "Cache Not Available", "File info cache is not initialized.")
      return

    reply = QMessageBox.question(
        self,
        "Confirm Clear Cache",
        "Are you sure you want to permanently delete all entries from the phash cache?\n"
        "This action cannot be undone.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.Yes:
      try:
        self.file_info_cache.clear_cache()
        self.statusBar().showMessage("File info cache cleared.", 3000)
        show_selectable_message_box(self, QMessageBox.Icon.Information, "Cache Cleared", "All entries have been removed from the cache.")
      except Exception as e:
        show_selectable_message_box(self, QMessageBox.Icon.Critical, "Error Clearing Cache", f"Could not clear the cache: {e}")

  def _clean_file_cache(self):
    """
    Handles the 'Clean Cache' menu action.
    Runs the clean_cache method of the FileInfoCache.
    """
    if not self.file_info_cache:
      show_selectable_message_box(self, QMessageBox.Icon.Warning, "Cache Not Available", "File info cache is not initialized.")
      return
    try:
      self.file_info_cache.clean_cache()
      self.statusBar().showMessage("File info cache cleaned.", 3000)
      show_selectable_message_box(self, QMessageBox.Icon.Information, "Cache Cleaned", "Invalid or outdated entries have been removed from the cache.")
    except Exception as e:
      show_selectable_message_box(self, QMessageBox.Icon.Critical, "Error Cleaning Cache", f"Could not clean the cache: {e}")

  def _show_cache_status_dialog(self):
    """
    Handles the 'Cache Status' menu action.
    Displays a dialog with cache statistics.
    """
    if not self.file_info_cache:
      show_selectable_message_box(self, QMessageBox.Icon.Warning, "Cache Not Available", "File info cache is not initialized. Cannot show status.")
      return

    dialog = CacheStatusDialog(cache_instance=self.file_info_cache, parent=self)
    dialog.exec()
  
  def closeEvent(self, event):
    """
    Ensure the cache connection is closed when the main window closes.
    """
    if self.file_info_cache:
        try:
            self.file_info_cache.close()
        except Exception as e:
            print(f"Error closing file info cache: {e}") # Log this
    super().closeEvent(event)


if __name__ == '__main__':
  # This part is for testing the MainWindow independently
  import sys
  from PySide6.QtWidgets import QApplication
  app = QApplication(sys.argv)
  main_win = MainWindow()
  main_win.show()
  sys.exit(app.exec())