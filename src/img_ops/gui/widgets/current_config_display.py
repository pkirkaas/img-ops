from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGroupBox,
                             QFormLayout, QLineEdit, QTextEdit)
from PySide6.QtCore import Qt
from src.img_ops.core.app_config import AppConfiguration

class CurrentConfigDisplay(QWidget):
    """
    A widget to display the current configuration values in a read-only format.

    This widget shows the active configuration details including:
    - Configuration name
    - Description
    - List of paths
    - Similarity method
    - Similarity percentage

    The display is organized in a clean layout suitable for embedding in the main window.
    """

    def __init__(self, parent=None):
        """
        Initialize the CurrentConfigDisplay widget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create a group box for the configuration display
        config_group = QGroupBox("Current Configuration")
        config_group.setFlat(True)
        config_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        # Create a form layout for the configuration details
        form_layout = QFormLayout(config_group)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(8)

        # Configuration name
        self.name_label = QLineEdit()
        self.name_label.setReadOnly(True)
        self.name_label.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 3px; padding: 2px;")

        # Description
        self.desc_label = QTextEdit()
        self.desc_label.setReadOnly(True)
        self.desc_label.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 3px; padding: 2px;")
        self.desc_label.setFixedHeight(60)

        # List of paths
        self.paths_label = QTextEdit()
        self.paths_label.setReadOnly(True)
        self.paths_label.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 3px; padding: 2px;")
        self.paths_label.setFixedHeight(80)

        # Similarity method
        self.method_label = QLineEdit()
        self.method_label.setReadOnly(True)
        self.method_label.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 3px; padding: 2px;")

        # Similarity percentage
        self.percentage_label = QLineEdit()
        self.percentage_label.setReadOnly(True)
        self.percentage_label.setStyleSheet("background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 3px; padding: 2px;")

        # Add widgets to the form layout
        form_layout.addRow(QLabel("Name:"), self.name_label)
        form_layout.addRow(QLabel("Description:"), self.desc_label)
        form_layout.addRow(QLabel("Paths:"), self.paths_label)
        form_layout.addRow(QLabel("Similarity Method:"), self.method_label)
        form_layout.addRow(QLabel("Similarity Percentage:"), self.percentage_label)

        # Add the group box to the main layout
        layout.addWidget(config_group)
        self.setLayout(layout)

    def update_display(self, config: AppConfiguration):
        """
        Update the display with the current configuration values.

        Args:
            config (AppConfiguration): The configuration object containing the current settings.
        """
        if not config:
            self._clear_display()
            return

        self.name_label.setText(config.name)
        self.desc_label.setPlainText(config.description)

        # Format paths as a newline-separated list
        paths_text = "\n".join(config.paths) if config.paths else "No paths configured"
        self.paths_label.setPlainText(paths_text)

        self.method_label.setText(config.method if config.method else "Not set")
        self.percentage_label.setText(f"{config.percent}%" if config.percent is not None else "Not set")

    def _clear_display(self):
        """Clear all fields in the display."""
        self.name_label.clear()
        self.desc_label.clear()
        self.paths_label.clear()
        self.method_label.clear()
        self.percentage_label.clear()