"""
Defines the MainWindow class for the img-ops application.
"""
from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
  """
  The main application window.

  This window will host the primary user interface elements,
  such as image viewers, file browsers, and control panels.
  """
  def __init__(self, parent=None):
    """
    Initializes the MainWindow.

    Args:
      parent (QWidget, optional): The parent widget. Defaults to None.
    """
    super().__init__(parent)

    self.setWindowTitle("Img-Ops - Image Operations")
    self.setGeometry(100, 100, 800, 600) # x, y, width, height

    # Central widget and layout
    central_widget = QWidget(self)
    self.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    # Placeholder content
    placeholder_label = QLabel("Main Application Window - Content Goes Here", self)
    layout.addWidget(placeholder_label)

    # TODO: Add menus, toolbars, status bar, and main content widgets
    self._create_menus()
    self._create_status_bar()

  def _create_menus(self):
    """
    Creates the main menu bar and its actions.
    """
    menu_bar = self.menuBar()
    file_menu = menu_bar.addMenu("&File")

    # Example actions (to be implemented)
    open_action = file_menu.addAction("&Open...")
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

if __name__ == '__main__':
  # This part is for testing the MainWindow independently
  import sys
  from PySide6.QtWidgets import QApplication
  app = QApplication(sys.argv)
  main_win = MainWindow()
  main_win.show()
  sys.exit(app.exec())