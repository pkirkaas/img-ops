"""
Settings Configuration Widget.

This widget allows editing of the currently active application configuration's
details, such as description, method, and similarity percentage.
Path management is handled by the sibling SelectedPathsWidget.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QComboBox, QDoubleSpinBox, QPushButton, QGroupBox, QLabel,
    QMessageBox # Added QMessageBox import
)
from PySide6.QtCore import Slot, Signal, Qt # Added Qt import
from typing import Optional

from ...core.app_config import AppConfigManager, AppConfiguration
from ...core.exceptions import ConfigError
from ..state import AppState # For accessing selected_paths if needed, though MainWindow will coordinate
from ..utils import show_selectable_message_box

class SettingsConfigWidget(QWidget):
    """
    Widget to edit details of the currently active application configuration.
    """
    # Signal emitted when changes are applied, MainWindow can listen to update other UI if needed
    configuration_updated = Signal(AppConfiguration) 

    def __init__(self, 
                 config_manager: AppConfigManager,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._config_manager = config_manager
        self._current_config: Optional[AppConfiguration] = None

        self._setup_ui()
        self._connect_signals()
        self.setEnabled(False) # Disabled until a config is loaded

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        details_group = QGroupBox("Current Configuration Settings")
        main_layout.addWidget(details_group)
        
        form_layout = QFormLayout(details_group)

        self.name_label = QLineEdit() # Display only, not for editing name here
        self.name_label.setReadOnly(True)
        self.name_label.setStyleSheet("background-color: #f0f0f0;") # Indicate read-only
        form_layout.addRow("Name:", self.name_label)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Configuration description")
        self.description_edit.setFixedHeight(80)
        form_layout.addRow("Description:", self.description_edit)

        self.method_combo = QComboBox()
        self.method_combo.addItems(['phash', 'ssim', 'orb', 'sift', 'surf', 'histogram'])
        self.method_combo.setToolTip("Select the similarity comparison method")
        form_layout.addRow("Method:", self.method_combo)

        self.percent_spin = QDoubleSpinBox()
        self.percent_spin.setRange(0.0, 100.0)
        self.percent_spin.setDecimals(1)
        self.percent_spin.setSuffix("%")
        self.percent_spin.setToolTip("Similarity threshold percentage (0-100)")
        form_layout.addRow("Similarity %:", self.percent_spin)
        
        # Paths are managed by SelectedPathsWidget, this widget only shows a note
        paths_info_label = QLabel("<i>Paths for this configuration are managed in the adjacent 'Selected Paths' panel.</i>")
        paths_info_label.setWordWrap(True)
        form_layout.addRow(paths_info_label)

        self.apply_button = QPushButton("Apply Changes to Configuration")
        self.apply_button.setToolTip("Save changes to the current configuration profile")
        main_layout.addWidget(self.apply_button)

    def _connect_signals(self):
        self.apply_button.clicked.connect(self._apply_changes)

    def load_configuration(self, config: Optional[AppConfiguration]):
        self._current_config = config
        if config:
            self.name_label.setText(config.name)
            self.description_edit.setPlainText(config.description)
            
            method_index = self.method_combo.findText(config.method, Qt.MatchFlag.MatchFixedString)
            if method_index >= 0:
                self.method_combo.setCurrentIndex(method_index)
            else:
                self.method_combo.setCurrentIndex(0) # Default to first if not found

            self.percent_spin.setValue(config.percent)
            self.setEnabled(True)
        else:
            self.name_label.clear()
            self.description_edit.clear()
            self.method_combo.setCurrentIndex(0)
            self.percent_spin.setValue(0.0)
            self.setEnabled(False)

    @Slot()
    def _apply_changes(self):
        if not self._current_config:
            show_selectable_message_box(self, QMessageBox.Warning, "No Configuration", "No configuration is currently active to apply changes to.")
            return

        # Name is not editable here. Paths are handled by SelectedPathsWidget via AppState.
        # We only update description, method, and percent for the self._current_config object.
        # MainWindow is responsible for getting the updated paths from AppState.
        
        try:
            # Create a temporary dict to validate new values if needed, or update directly
            # For now, direct update and rely on MainWindow to fetch paths from AppState
            
            updated_description = self.description_edit.toPlainText().strip()
            updated_method = self.method_combo.currentText()
            updated_percent = self.percent_spin.value()

            # Validate directly by trying to set them on a copy (optional, Pydantic handles on AppConfig)
            # temp_config_data = self._current_config.dict()
            # temp_config_data["description"] = updated_description
            # temp_config_data["method"] = updated_method
            # temp_config_data["percent"] = updated_percent
            # AppConfiguration(**temp_config_data) # This would raise validation error

            # Update the actual current_config object (held by MainWindow)
            self._current_config.description = updated_description
            self._current_config.method = updated_method
            self._current_config.percent = updated_percent
            # Note: self._current_config.paths will be updated by MainWindow listening to AppState

            self._config_manager.save_to_file() # Save all configurations
            
            show_selectable_message_box(
                self, 
                QMessageBox.Information, 
                "Configuration Updated", 
                f"Changes to configuration '{self._current_config.name}' have been applied and saved."
            )
            self.configuration_updated.emit(self._current_config)

        except ConfigError as e:
            show_selectable_message_box(self, QMessageBox.Critical, "Save Error", f"Failed to save configuration changes:\n{str(e)}")
        except Exception as e: # Catch Pydantic validation errors if any were to occur
            show_selectable_message_box(self, QMessageBox.Critical, "Validation Error", f"Invalid data for configuration:\n{str(e)}")