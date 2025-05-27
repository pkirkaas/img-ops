"""
Main entry point for the img-ops Graphical User Interface (GUI).

This script initializes the QApplication and shows the main window.
"""
import sys
from PySide6.QtWidgets import QApplication
from .windows.main_window import MainWindow

def run_gui():
  """
  Initializes and runs the GUI application.
  """
  print("\n\n\n\n\n") # Add 5 newlines before starting
  app = QApplication(sys.argv)

  # Create and show the main window
  main_win = MainWindow()
  main_win.show()
  # print("Placeholder: GUI app started. Main window would show here.") # Temporary

  sys.exit(app.exec())

if __name__ == "__main__":
  run_gui()