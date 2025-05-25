"""
Application Configuration Management Widget.

This module provides a PySide6 widget for managing application configurations,
allowing users to view, create, edit, and delete configurations through a
comprehensive GUI interface.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
  QWidget,
  QVBoxLayout,
  QHBoxLayout,
  QListWidget,
  QListWidgetItem,
  QPushButton,
  QLineEdit,
  QTextEdit,
  QLabel,
  QComboBox,
  QSpinBox,
  QDoubleSpinBox,
  QGroupBox,
  QFormLayout,
  QMessageBox,
  QDialog,
  QDialogButtonBox,
  QFileDialog,
  QSplitter,
  QFrame
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont

from src.img_ops.core.app_config import AppConfigManager, AppConfiguration
from src.img_ops.core.exceptions import ConfigError


class ConfigEditDialog(QDialog):
  """
  Dialog for editing a single configuration.
  
  Provides a form-based interface for editing all configuration properties
  including name, description, paths, method, and similarity percentage.
  Includes validation and error handling for all input fields.
  """
  
  def __init__(self, config: Optional[AppConfiguration] = None, existing_names: List[str] = None, parent=None):
    """
    Initialize the configuration edit dialog.
    
    Args:
      config (AppConfiguration, optional): Configuration to edit. If None, creates new config.
      existing_names (List[str], optional): List of existing configuration names for validation.
      parent (QWidget, optional): Parent widget.
    """
    super().__init__(parent)
    
    self.config = config or AppConfiguration()
    self.existing_names = existing_names or []
    self.original_name = self.config.name if config else None
    
    self._setup_ui()
    self._populate_fields()
    self._connect_signals()
  
  def _setup_ui(self):
    """Set up the user interface components."""
    self.setWindowTitle("Edit Configuration" if self.config.name != "MyConf" else "New Configuration")
    self.setModal(True)
    self.setMinimumSize(500, 600)
    
    # Main layout
    layout = QVBoxLayout(self)
    
    # Basic information group
    basic_group = QGroupBox("Basic Information")
    basic_layout = QFormLayout(basic_group)
    
    # Name field
    self.name_edit = QLineEdit()
    self.name_edit.setMaxLength(100)
    self.name_edit.setPlaceholderText("Enter configuration name")
    basic_layout.addRow("Name:", self.name_edit)
    
    # Description field
    self.description_edit = QTextEdit()
    self.description_edit.setMaximumHeight(80)
    self.description_edit.setPlaceholderText("Enter configuration description")
    basic_layout.addRow("Description:", self.description_edit)
    
    layout.addWidget(basic_group)
    
    # Comparison settings group
    comparison_group = QGroupBox("Comparison Settings")
    comparison_layout = QFormLayout(comparison_group)
    
    # Method selection
    self.method_combo = QComboBox()
    self.method_combo.addItems(['phash', 'ssim', 'orb', 'sift', 'surf', 'histogram'])
    self.method_combo.setToolTip("Select the similarity comparison method")
    comparison_layout.addRow("Method:", self.method_combo)
    
    # Similarity percentage
    self.percent_spin = QDoubleSpinBox()
    self.percent_spin.setRange(0.0, 100.0)
    self.percent_spin.setDecimals(1)
    self.percent_spin.setSuffix("%")
    self.percent_spin.setToolTip("Similarity threshold percentage (0-100)")
    comparison_layout.addRow("Similarity %:", self.percent_spin)
    
    layout.addWidget(comparison_group)
    
    # Paths group
    paths_group = QGroupBox("File Paths")
    paths_layout = QVBoxLayout(paths_group)
    
    # Paths list
    self.paths_list = QListWidget()
    self.paths_list.setMinimumHeight(150)
    self.paths_list.setToolTip("List of file and directory paths to process")
    paths_layout.addWidget(self.paths_list)
    
    # Path buttons
    path_buttons_layout = QHBoxLayout()
    
    self.add_file_btn = QPushButton("Add File")
    self.add_file_btn.setToolTip("Add a single file to the configuration")
    path_buttons_layout.addWidget(self.add_file_btn)
    
    self.add_dir_btn = QPushButton("Add Directory")
    self.add_dir_btn.setToolTip("Add a directory to the configuration")
    path_buttons_layout.addWidget(self.add_dir_btn)
    
    self.remove_path_btn = QPushButton("Remove Selected")
    self.remove_path_btn.setToolTip("Remove the selected path from the list")
    self.remove_path_btn.setEnabled(False)
    path_buttons_layout.addWidget(self.remove_path_btn)
    
    self.clear_paths_btn = QPushButton("Clear All")
    self.clear_paths_btn.setToolTip("Remove all paths from the list")
    path_buttons_layout.addWidget(self.clear_paths_btn)
    
    paths_layout.addLayout(path_buttons_layout)
    layout.addWidget(paths_group)
    
    # Dialog buttons
    self.button_box = QDialogButtonBox(
      QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    )
    layout.addWidget(self.button_box)
    
    # Apply styling
    self._apply_styling()
def _apply_styling(self):
    """Apply consistent styling to the dialog components."""
    # Style group boxes
    group_style = """
      QGroupBox {
        font-weight: bold;
        border: 2px solid #cccccc;
        border-radius: 5px;
        margin-top: 1ex;
        padding-top: 10px;
      }
      QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
      }
    """
    
    for group in self.findChildren(QGroupBox):
      group.setStyleSheet(group_style)
    
    # Style the paths list
    self.paths_list.setStyleSheet("""
      QListWidget {
        background-color: #fafafa;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 10px;
      }
      QListWidget::item {
        padding: 2px;
        border-bottom: 1px solid #eee;
      }
      QListWidget::item:selected {
        background-color: #0078d4;
        color: white;
      }
    """)
  
def _populate_fields(self):
    """Populate form fields with configuration data."""
    self.name_edit.setText(self.config.name)
    self.description_edit.setPlainText(self.config.description)
    
    # Set method
    method_index = self.method_combo.findText(self.config.method)
    if method_index >= 0:
      self.method_combo.setCurrentIndex(method_index)
    
    self.percent_spin.setValue(self.config.percent)
    
    # Populate paths
    for path in self.config.paths:
      self.paths_list.addItem(path)
  
def _connect_signals(self):
    """Connect widget signals to their handlers."""
    # Dialog buttons
    self.button_box.accepted.connect(self._validate_and_accept)
    self.button_box.rejected.connect(self.reject)
    
    # Path management
    self.add_file_btn.clicked.connect(self._add_file_path)
    self.add_dir_btn.clicked.connect(self._add_directory_path)
    self.remove_path_btn.clicked.connect(self._remove_selected_path)
    self.clear_paths_btn.clicked.connect(self._clear_all_paths)
    
    # Enable/disable remove button based on selection
    self.paths_list.itemSelectionChanged.connect(self._on_path_selection_changed)
    
    # Validation on name change
    self.name_edit.textChanged.connect(self._validate_name)
  
@Slot()
def _add_file_path(self):
    """Add a file path through file dialog."""
    file_path, _ = QFileDialog.getOpenFileName(
      self,
      "Select File",
      "",
      "All Files (*.*)"
    )
    
    if file_path:
      self._add_path_to_list(file_path)
  
@Slot()
def _add_directory_path(self):
    """Add a directory path through directory dialog."""
    dir_path = QFileDialog.getExistingDirectory(
      self,
      "Select Directory"
    )
    
    if dir_path:
      self._add_path_to_list(dir_path)
  
  def _add_path_to_list(self, path: str):
    """
    Add a path to the paths list if it's not already present.
    
    Args:
      path (str): The file or directory path to add.
    """
    # Normalize path for comparison
    normalized_path = os.path.normpath(path)
    
    # Check if path already exists
    for i in range(self.paths_list.count()):
      existing_path = self.paths_list.item(i).text()
      if os.path.normpath(existing_path) == normalized_path:
        QMessageBox.information(self, "Duplicate Path", f"Path already exists:\n{path}")
        return
    
    # Add the path
    self.paths_list.addItem(path)
  
@Slot()
  def _remove_selected_path(self):
    """Remove the currently selected path from the list."""
    current_row = self.paths_list.currentRow()
    if current_row >= 0:
      self.paths_list.takeItem(current_row)
  
@Slot()
  def _clear_all_paths(self):
    """Clear all paths from the list after confirmation."""
    if self.paths_list.count() == 0:
      return
    
    reply = QMessageBox.question(
      self,
      "Clear All Paths",
      "Are you sure you want to remove all paths?",
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
      QMessageBox.StandardButton.No
    )
    
    if reply == QMessageBox.StandardButton.Yes:
      self.paths_list.clear()
  
@Slot()
  def _on_path_selection_changed(self):
    """Handle path selection changes."""
    has_selection = self.paths_list.currentRow() >= 0
    self.remove_path_btn.setEnabled(has_selection)
  
  @Slot(str)
  def _validate_name(self, name: str):
    """
    Validate the configuration name.
    
    Args:
      name (str): The name to validate.
    """
    # Check if name is empty
    if not name.strip():
      self.name_edit.setStyleSheet("border: 2px solid red;")
      return
    
    # Check if name already exists (excluding original name for edits)
    if name in self.existing_names and name != self.original_name:
      self.name_edit.setStyleSheet("border: 2px solid red;")
      return
    
    # Name is valid
    self.name_edit.setStyleSheet("")
  
def _validate_and_accept(self):
    """Validate all fields and accept the dialog if valid."""
    # Validate name
    name = self.name_edit.text().strip()
    if not name:
      QMessageBox.warning(self, "Invalid Name", "Configuration name cannot be empty.")
      self.name_edit.setFocus()
      return
    
    if name in self.existing_names and name != self.original_name:
      QMessageBox.warning(self, "Duplicate Name", f"Configuration name '{name}' already exists.")
      self.name_edit.setFocus()
      return
    
    # Update configuration
    try:
      self.config.name = name
      self.config.description = self.description_edit.toPlainText().strip()
      self.config.method = self.method_combo.currentText()
      self.config.percent = self.percent_spin.value()
      
      # Update paths
      paths = []
      for i in range(self.paths_list.count()):
        paths.append(self.paths_list.item(i).text())
      self.config.paths = paths
      
      # Validate the configuration (this will trigger Pydantic validation)
      AppConfiguration(**self.config.dict())
      
    except Exception as e:
      QMessageBox.critical(self, "Validation Error", f"Configuration validation failed:\n{str(e)}")
      return
    
    self.accept()
  
  def get_configuration(self) -> AppConfiguration:
    """
    Get the edited configuration.
    
    Returns:
      AppConfiguration: The configuration with updated values.
    """
    return self.config


class AppConfigWidget(QWidget):
  """
  Widget for managing application configurations.
  
  Provides a comprehensive interface for viewing, creating, editing, and deleting
  application configurations. Integrates with the AppConfigManager for persistence
  and emits signals when configurations are modified.
  
  Signals:
    configuration_changed: Emitted when any configuration is modified.
                          Args: config_name (str) - Name of the changed configuration
    configuration_selected: Emitted when a configuration is selected.
                           Args: config (AppConfiguration) - The selected configuration
  """
  
  # Signals
  configuration_changed = Signal(str)  # config_name
  configuration_selected = Signal(AppConfiguration)  # config
  
  def __init__(self, config_manager: Optional[AppConfigManager] = None, parent=None):
    """
    Initialize the AppConfigWidget.
    
    Args:
      config_manager (AppConfigManager, optional): Configuration manager instance.
                                                  If None, creates a new one.
      parent (QWidget, optional): Parent widget.
    """
    super().__init__(parent)
    
    self.config_manager = config_manager or AppConfigManager()
    self.current_config: Optional[AppConfiguration] = None
    
    self._setup_ui()
    self._connect_signals()
    self._refresh_config_list()
def _add_directory_path(self):
    """Add a directory path through directory dialog."""
    dir_path = QFileDialog.getExistingDirectory(
      self,
      "Select Directory"
    )

    if dir_path:
      self._add_path_to_list(dir_path)

@Slot()
def _remove_selected_path(self):
    """Remove the currently selected path from the list."""
    current_row = self.paths_list.currentRow()
    if current_row >= 0:
      self.paths_list.takeItem(current_row)

@Slot()
def _clear_all_paths(self):
    """Clear all paths from the list after confirmation."""
    if self.paths_list.count() == 0:
      return

    reply = QMessageBox.question(
      self,
      "Clear All Paths",
      "Are you sure you want to remove all paths?",
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
      QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
      self.paths_list.clear()

@Slot()
def _on_path_selection_changed(self):
    """Handle path selection changes."""
    has_selection = self.paths_list.currentRow() >= 0
    self.remove_path_btn.setEnabled(has_selection)

@Slot(str)
def _validate_name(self, name: str):
    """
    Validate the configuration name.

    Args:
      name (str): The name to validate.
    """
    # Check if name is empty
    if not name.strip():
      self.name_edit.setStyleSheet("border: 2px solid red;")
      return

    # Check if name already exists (excluding original name for edits)
    if name in self.existing_names and name != self.original_name:
      self.name_edit.setStyleSheet("border: 2px solid red;")
      return

    # Name is valid
    self.name_edit.setStyleSheet("")

def _validate_and_accept(self):
    """Validate all fields and accept the dialog if valid."""
    # Validate name
    name = self.name_edit.text().strip()
    if not name:
      QMessageBox.warning(self, "Invalid Name", "Configuration name cannot be empty.")
      self.name_edit.setFocus()
      return

    if name in self.existing_names and name != self.original_name:
      QMessageBox.warning(self, "Duplicate Name", f"Configuration name '{name}' already exists.")
      self.name_edit.setFocus()
      return

    # Update configuration
    try:
      self.config.name = name
      self.config.description = self.description_edit.toPlainText().strip()
      self.config.method = self.method_combo.currentText()
      self.config.percent = self.percent_spin.value()

      # Update paths
      paths = []
      for i in range(self.paths_list.count()):
        paths.append(self.paths_list.item(i).text())
      self.config.paths = paths

      # Validate the configuration (this will trigger Pydantic validation)
      AppConfiguration(**self.config.dict())

    except Exception as e:
      QMessageBox.critical(self, "Validation Error", f"Configuration validation failed:\n{str(e)}")
      return

    self.accept()

def get_configuration(self) -> AppConfiguration:
    """
    Get the edited configuration.

    Returns:
      AppConfiguration: The configuration with updated values.
    """
    return self.config

def _setup_ui(self):
    """Set up the user interface components."""
    # Main layout
    main_layout = QVBoxLayout(self)

    # Title
    title_label = QLabel("Application Configurations")
    title_font = QFont()
    title_font.setPointSize(14)
    title_font.setBold(True)
    title_label.setFont(title_font)
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(title_label)

    # Create splitter for resizable sections
    splitter = QSplitter(Qt.Orientation.Horizontal)

    # Left panel - Configuration list
    left_panel = QFrame()
    left_layout = QVBoxLayout(left_panel)

    # Configuration list
    list_label = QLabel("Configurations:")
    list_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
    left_layout.addWidget(list_label)

    self.config_list = QListWidget()
    self.config_list.setMinimumWidth(200)
    self.config_list.setToolTip("Select a configuration to view or edit")
    left_layout.addWidget(self.config_list)

    # List management buttons
    list_buttons_layout = QHBoxLayout()

    self.new_btn = QPushButton("New")
    self.new_btn.setToolTip("Create a new configuration")
    list_buttons_layout.addWidget(self.new_btn)

    self.edit_btn = QPushButton("Edit")
    self.edit_btn.setToolTip("Edit the selected configuration")
    self.edit_btn.setEnabled(False)
    list_buttons_layout.addWidget(self.edit_btn)

    self.delete_btn = QPushButton("Delete")
    self.delete_btn.setToolTip("Delete the selected configuration")
    self.delete_btn.setEnabled(False)
    list_buttons_layout.addWidget(self.delete_btn)

    left_layout.addLayout(list_buttons_layout)

    splitter.addWidget(left_panel)

    # Right panel - Configuration details
    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)

    details_label = QLabel("Configuration Details:")
    details_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
    right_layout.addWidget(details_label)

    # Details display
    self.details_text = QTextEdit()
    self.details_text.setReadOnly(True)
    self.details_text.setMinimumWidth(300)
    self.details_text.setPlaceholderText("Select a configuration to view details")
    right_layout.addWidget(self.details_text)

    splitter.addWidget(right_panel)

    # Set splitter proportions
    splitter.setSizes([200, 300])
    main_layout.addWidget(splitter)

    # Dialog buttons
    button_layout = QHBoxLayout()
    button_layout.addStretch()

    self.ok_btn = QPushButton("OK")
    self.ok_btn.setDefault(True)
    self.ok_btn.setMinimumWidth(80)
    button_layout.addWidget(self.ok_btn)

    self.cancel_btn = QPushButton("Cancel")
    self.cancel_btn.setMinimumWidth(80)
    button_layout.addWidget(self.cancel_btn)

    main_layout.addLayout(button_layout)

    # Apply styling
    self._apply_styling()

def _apply_styling(self):
    """Apply consistent styling to the widget components."""
    # Style the configuration list
    self.config_list.setStyleSheet("""
      QListWidget {
        background-color: #fafafa;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px;
        font-size: 11px;
      }
      QListWidget::item {
        padding: 5px;
        border-bottom: 1px solid #eee;
        border-radius: 2px;
      }
      QListWidget::item:selected {
        background-color: #0078d4;
        color: white;
      }
      QListWidget::item:hover {
        background-color: #e5f3ff;
      }
    """)

    # Style the details text
    self.details_text.setStyleSheet("""
      QTextEdit {
        background-color: #fafafa;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 10px;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 10px;
        line-height: 1.4;
      }
    """)

    # Style buttons
    button_style = """
      QPushButton {
        padding: 6px 12px;
        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: #f8f9fa;
        font-size: 11px;
      }
      QPushButton:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
      }
      QPushButton:pressed {
        background-color: #dee2e6;
      }
      QPushButton:disabled {
        background-color: #e9ecef;
        color: #6c757d;
        border-color: #dee2e6;
      }
    """

    for button in self.findChildren(QPushButton):
      button.setStyleSheet(button_style)

def _connect_signals(self):
    """Connect widget signals to their handlers."""
    # List selection
    self.config_list.itemSelectionChanged.connect(self._on_config_selection_changed)
    self.config_list.itemDoubleClicked.connect(self._edit_configuration)

    # Buttons
    self.new_btn.clicked.connect(self._create_new_configuration)
    self.edit_btn.clicked.connect(self._edit_configuration)
    self.delete_btn.clicked.connect(self._delete_configuration)

    self.ok_btn.clicked.connect(self._on_ok_clicked)
    self.cancel_btn.clicked.connect(self._on_cancel_clicked)

def _refresh_config_list(self):
    """Refresh the configuration list from the manager."""
    self.config_list.clear()

    config_names = self.config_manager.list_configuration_names()
    for name in sorted(config_names):
      item = QListWidgetItem(name)
      item.setData(Qt.ItemDataRole.UserRole, name)
      self.config_list.addItem(item)

    # Clear details if no configurations
    if not config_names:
      self.details_text.clear()
      self.current_config = None

@Slot()
def _on_config_selection_changed(self):
    """Handle configuration selection changes."""
    current_item = self.config_list.currentItem()
    has_selection = current_item is not None

    # Enable/disable buttons
    self.edit_btn.setEnabled(has_selection)
    self.delete_btn.setEnabled(has_selection)

    if has_selection:
      config_name = current_item.data(Qt.ItemDataRole.UserRole)
      config = self.config_manager.get_configuration(config_name)

      if config:
        self.current_config = config
        self._display_config_details(config)
        self.configuration_selected.emit(config)
    else:
      self.current_config = None
      self.details_text.clear()

def _display_config_details(self, config: AppConfiguration):
    """
    Display configuration details in the details panel.

    Args:
      config (AppConfiguration): Configuration to display.
    """
    details = []
    details.append(f"Name: {config.name}")
    details.append(f"Description: {config.description}")
    details.append(f"Method: {config.method}")
    details.append(f"Similarity: {config.percent}%")
    details.append("")

    if config.paths:
      details.append(f"Paths ({len(config.paths)}):")
      for i, path in enumerate(config.paths, 1):
        # Check if path exists
        exists_marker = "✓" if os.path.exists(path) else "✗"
        details.append(f"  {i}. {exists_marker} {path}")

      # Show path statistics
      existing_paths = config.get_existing_paths()
      missing_paths = config.get_missing_paths()
      details.append("")
      details.append(f"Existing paths: {len(existing_paths)}")
      details.append(f"Missing paths: {len(missing_paths)}")
    else:
      details.append("No paths configured")

    self.details_text.setPlainText("\n".join(details))

@Slot()
def _create_new_configuration(self):
    """Create a new configuration."""
    existing_names = self.config_manager.list_configuration_names()

    dialog = ConfigEditDialog(
      config=None,
      existing_names=existing_names,
      parent=self
    )

    if dialog.exec() == QDialog.DialogCode.Accepted:
      new_config = dialog.get_configuration()

      try:
        if self.config_manager.add_configuration(new_config):
          self.config_manager.save_to_file()
          self._refresh_config_list()
          self._select_config_by_name(new_config.name)
          self.configuration_changed.emit(new_config.name)
        else:
          QMessageBox.warning(self, "Error", f"Configuration '{new_config.name}' already exists.")
      except ConfigError as e:
        QMessageBox.critical(self, "Configuration Error", f"Failed to save configuration:\n{str(e)}")
      except Exception as e:
        QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred:\n{str(e)}")

@Slot()
def _edit_configuration(self):
    """Edit the selected configuration."""
    if not self.current_config:
      return

    existing_names = self.config_manager.list_configuration_names()

    # Create a copy for editing
    config_copy = AppConfiguration(**self.current_config.dict())

    dialog = ConfigEditDialog(
      config=config_copy,
      existing_names=existing_names,
      parent=self
    )

    if dialog.exec() == QDialog.DialogCode.Accepted:
      edited_config = dialog.get_configuration()

      try:
        # Remove old configuration if name changed
        old_name = self.current_config.name
        if edited_config.name != old_name:
          self.config_manager.remove_configuration(old_name)

        # Add/update configuration
        self.config_manager.configurations[edited_config.name] = edited_config
        self.config_manager.save_to_file()

        self._refresh_config_list()
        self._select_config_by_name(edited_config.name)
        self.configuration_changed.emit(edited_config.name)

      except ConfigError as e:
        QMessageBox.critical(self, "Configuration Error", f"Failed to save configuration:\n{str(e)}")
      except Exception as e:
        QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred:\n{str(e)}")

@Slot()
def _delete_configuration(self):
    """Delete the selected configuration."""
    if not self.current_config:
      return

    config_name = self.current_config.name

    reply = QMessageBox.question(
      self,
      "Delete Configuration",
      f"Are you sure you want to delete the configuration '{config_name}'?\n\nThis action cannot be undone.",
      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
      QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.Yes:
      try:
        if self.config_manager.remove_configuration(config_name):
          self.config_manager.save_to_file()
          self._refresh_config_list()
          self.configuration_changed.emit(config_name)
        else:
          QMessageBox.warning(self, "Error", f"Configuration '{config_name}' not found.")
      except ConfigError as e:
        QMessageBox.critical(self, "Configuration Error", f"Failed to delete configuration:\n{str(e)}")
      except Exception as e:
        QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred:\n{str(e)}")

def _select_config_by_name(self, name: str):
    """
    Select a configuration by name in the list.

    Args:
      name (str): Name of the configuration to select.
    """
    for i in range(self.config_list.count()):
      item = self.config_list.item(i)
      if item.data(Qt.ItemDataRole.UserRole) == name:
        self.config_list.setCurrentItem(item)
        break

@Slot()
def _on_ok_clicked(self):
    """Handle OK button click."""
    # Save any pending changes
    try:
      self.config_manager.save_to_file()
    except ConfigError as e:
      QMessageBox.critical(self, "Save Error", f"Failed to save configurations:\n{str(e)}")
      return

    # Close the widget (if used as dialog)
    if self.parent() and hasattr(self.parent(), 'accept'):
      self.parent().accept()

@Slot()
def _on_cancel_clicked(self):
    """Handle Cancel button click."""
    # Reload configurations to discard any unsaved changes
    try:
      self.config_manager.load_from_file()
      self._refresh_config_list()
    except ConfigError as e:
      # If reload fails, just close
      pass

    # Close the widget (if used as dialog)
    if self.parent() and hasattr(self.parent(), 'reject'):
      self.parent().reject()

def get_selected_configuration(self) -> Optional[AppConfiguration]:
    """
    Get the currently selected configuration.

    Returns:
      AppConfiguration or None: The selected configuration, or None if none selected.
    """
    return self.current_config

def set_selected_configuration(self, name: str) -> bool:
    """
    Set the selected configuration by name.

    Args:
      name (str): Name of the configuration to select.

    Returns:
      bool: True if configuration was found and selected, False otherwise.
    """
    config = self.config_manager.get_configuration(name)
    if config:
      self._select_config_by_name(name)
      return True
    return False

if __name__ == '__main__':
    # Test the widget independently
    import sys
    from PySide6.QtWidgets import QApplication, QDialog

    app = QApplication(sys.argv)

    # Create test configuration manager with some sample data
    config_manager = AppConfigManager()

    # Add some test configurations
    test_config1 = AppConfiguration(
        name="Test Config 1",
        description="First test configuration",
        method="phash",
        percent=85.0,
        paths=["/home/user/images", "/home/user/photos"]
    )

    test_config2 = AppConfiguration(
        name="Test Config 2",
        description="Second test configuration",
        method="ssim",
        percent=92.5,
        paths=["/home/user/documents"]
    )

    config_manager.add_configuration(test_config1)
    config_manager.add_configuration(test_config2)

    # Create and show widget in a dialog
    dialog = QDialog()
    dialog.setWindowTitle("Test App Config Widget")
    dialog.setMinimumSize(800, 600)

    layout = QVBoxLayout(dialog)
    widget = AppConfigWidget(config_manager=config_manager, parent=dialog)
    layout.addWidget(widget)

    # Connect signals for testing
    widget.configuration_changed.connect(
        lambda name: print(f"Configuration changed: {name}")
    )
    widget.configuration_selected.connect(
        lambda config: print(f"Configuration selected: {config.name}")
    )

    dialog.exec()