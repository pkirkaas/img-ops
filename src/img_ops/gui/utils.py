"""
Utility functions specific to the Graphical User Interface (GUI).

This module can include helper functions for:
- Creating standard dialogs (e.g., message boxes).
- Loading QSS stylesheets.
- Converting data types for GUI display.
- Other GUI-specific tasks not part of the core logic or specific widgets.
"""
from PySide6.QtWidgets import QMessageBox

def show_info_message(parent=None, title: str = "Information", message: str = ""):
  """
  Displays a standard information message box.

  Args:
    parent (QWidget, optional): The parent widget. Defaults to None.
    title (str): The title of the message box.
    message (str): The message to display.
  """
  QMessageBox.information(parent, title, message)

def show_warning_message(parent=None, title: str = "Warning", message: str = ""):
  """
  Displays a standard warning message box.
  """
  QMessageBox.warning(parent, title, message)

def show_error_message(parent=None, title: str = "Error", message: str = ""):
  """
  Displays a standard error message box.
  """
  QMessageBox.critical(parent, title, message)

# Add other GUI utility functions as needed.
# For example, a function to load and apply a QSS stylesheet:
# def load_stylesheet(filepath: str, app_or_widget):
#   try:
#     with open(filepath, "r") as f:
#       style = f.read()
#       app_or_widget.setStyleSheet(style)
#     return True
#   except FileNotFoundError:
#     print(f"Error: Stylesheet not found at {filepath}")
#     return False