"""
Utility functions specific to the Graphical User Interface (GUI).

This module can include helper functions for:
- Creating standard dialogs (e.g., message boxes).
- Loading QSS stylesheets.
- Converting data types for GUI display.
- Other GUI-specific tasks not part of the core logic or specific widgets.
"""
from PySide6.QtWidgets import QMessageBox, QWidget # Added QWidget for type hint
from PySide6.QtCore import Qt # Added Qt for TextInteractionFlags
from typing import Optional # Added for Optional type hint

def show_selectable_message_box(
   parent: Optional[QWidget],
   icon_type: QMessageBox.Icon,
   title: str,
   text: str,
   informative_text: str = "",
   detailed_text: str = ""
) -> QMessageBox.StandardButton: # Return the button clicked
   """
   Displays a QMessageBox with selectable text and returns the button clicked.

   Args:
       parent (Optional[QWidget]): The parent widget.
       icon_type (QMessageBox.Icon): The icon to display (e.g., QMessageBox.Critical).
       title (str): The window title of the message box.
       text (str): The main text of the message box.
       informative_text (str, optional): Additional informative text.
       detailed_text (str, optional): Detailed text for a details area.
   
   Returns:
       QMessageBox.StandardButton: The standard button that was clicked by the user.
   """
   msg_box = QMessageBox(parent)
   msg_box.setIcon(icon_type)
   msg_box.setWindowTitle(title)
   msg_box.setText(text)
   if informative_text:
       msg_box.setInformativeText(informative_text)
   if detailed_text:
       msg_box.setDetailedText(detailed_text)
   
   # Allow text selection
   msg_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
   
   # Set standard buttons if not already set by icon (some icons imply buttons)
   if not msg_box.buttons():
       msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
       
   return msg_box.exec()


def show_info_message(parent: Optional[QWidget] = None, title: str = "Information", message: str = "", informative_text: str = ""):
 """
 Displays a standard information message box with selectable text.
 """
 show_selectable_message_box(parent, QMessageBox.Icon.Information, title, message, informative_text)

def show_warning_message(parent: Optional[QWidget] = None, title: str = "Warning", message: str = "", informative_text: str = ""):
 """
 Displays a standard warning message box with selectable text.
 """
 show_selectable_message_box(parent, QMessageBox.Icon.Warning, title, message, informative_text)

def show_error_message(parent: Optional[QWidget] = None, title: str = "Error", message: str = "", informative_text: str = "", detailed_text: str = ""):
 """
 Displays a standard error message box with selectable text.
 """
 show_selectable_message_box(parent, QMessageBox.Icon.Critical, title, message, informative_text, detailed_text)

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