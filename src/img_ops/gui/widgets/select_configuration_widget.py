"""
Select Configuration Widget.

This module provides a QComboBox widget for selecting an active application configuration.
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Signal, Slot
from typing import Optional

from ...core.app_config import AppConfigManager, AppConfiguration
# To potentially update global state or listen to changes
from ..state import AppState


class SelectConfigurationWidget(QWidget):
    """
    A widget with a QComboBox to select the active application configuration.
    """
    # Signal emitted when a configuration is selected by the user
    # Passes the name of the selected configuration
    configuration_selected = Signal(str)

    def __init__(self,
                 config_manager: AppConfigManager,
                 app_state: AppState,  # May not be strictly needed if MainWindow handles state update
                 parent: Optional[QWidget] = None):
        """
        Initializes the SelectConfigurationWidget.

        Args:
            config_manager (AppConfigManager): The application configuration manager.
            app_state (AppState): The global application state.
            parent (Optional[QWidget], optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._config_manager = config_manager
        self._app_state = app_state  # Store if needed for future interactions
        self._current_config_name: Optional[str] = None

        self._setup_ui()
        self.refresh_configurations()
        self._connect_signals()

    def _setup_ui(self):
        """Sets up the user interface components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Compact layout

        self.label = QLabel("Active Config:", self)
        layout.addWidget(self.label)

        self.config_combo = QComboBox(self)
        self.config_combo.setMinimumWidth(150)  # Ensure it's not too small
        self.config_combo.setToolTip(
            "Select the active application configuration")
        layout.addWidget(self.config_combo)

        self.setLayout(layout)

    def _connect_signals(self):
        """Connects widget signals to their handlers."""
        self.config_combo.currentTextChanged.connect(self._on_config_changed)
        # TODO: Consider connecting to a signal from AppConfigManager or AppState
        # if configurations can be added/removed/renamed dynamically elsewhere
        # and this widget needs to update. For now, manual refresh is an option.

    @Slot(str)
    def _on_config_changed(self, config_name: str):
        """
        Handles the selection change in the QComboBox.
        Emits a signal with the name of the newly selected configuration.
        """
        if config_name and config_name != self._current_config_name:
            self._current_config_name = config_name
            self.configuration_selected.emit(config_name)
            # print(f"SelectConfigurationWidget: '{config_name}' selected.") # For debugging

    def refresh_configurations(self, select_config_name: Optional[str] = None):
        """
        Reloads the list of configurations from the AppConfigManager.

        Args:
            select_config_name (Optional[str]): If provided, attempts to select this
                                                configuration after refreshing.
        """
        self.config_combo.blockSignals(
            True)  # Avoid emitting signal during refresh

        current_selection_before_refresh = self.config_combo.currentText()
        self.config_combo.clear()

        config_names = sorted(self._config_manager.list_configuration_names())
        self.config_combo.addItems(config_names)

        if select_config_name and select_config_name in config_names:
            self.config_combo.setCurrentText(select_config_name)
        elif current_selection_before_refresh in config_names:
            self.config_combo.setCurrentText(current_selection_before_refresh)
        elif config_names:  # Select first item if previous/target is not available
            self.config_combo.setCurrentIndex(0)

        self._current_config_name = self.config_combo.currentText()
        self.config_combo.blockSignals(False)

        # Manually emit if the selection actually changed due to refresh logic
        if self.config_combo.currentText() and self.config_combo.currentText() != current_selection_before_refresh:
            if self.config_combo.currentIndex() >= 0:  # Ensure there's a valid selection
                self.configuration_selected.emit(
                    self.config_combo.currentText())

    def get_selected_config_name(self) -> Optional[str]:
        """
        Returns the name of the currently selected configuration.
        """
        return self.config_combo.currentText() if self.config_combo.currentIndex() >= 0 else None

    def set_selected_configuration(self, config_name: str):
        """
        Programmatically sets the selected configuration in the combo box.
        This will also trigger the _on_config_changed slot and emit the signal.
        """
        if config_name in [self.config_combo.itemText(i) for i in range(self.config_combo.count())]:
            self.config_combo.setCurrentText(config_name)
        else:
            print(
                f"Warning: Configuration '{config_name}' not found in SelectConfigurationWidget.")
