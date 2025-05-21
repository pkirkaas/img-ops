"""
Main entry point for the img-ops Graphical User Interface (GUI).

This script initializes the QApplication and shows the main window.
"""
import sys
from PySide6.QtWidgets import QApplication
# from .windows.main_window import MainWindow # To be created

def run_gui():
  """
  Initializes and runs the GUI application.
  """
  app = QApplication(sys.argv)

  # Create and show the main window
  # main_win = MainWindow() # Placeholder
  # main_win.show() # Placeholder
  print("Placeholder: GUI app started. Main window would show here.") # Temporary

  sys.exit(app.exec())

if __name__ == "__main__":
  run_gui()