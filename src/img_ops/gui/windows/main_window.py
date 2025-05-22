"""
Defines the MainWindow class for the img-ops application.
"""
from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt # Added for Qt.Orientation
from ..widgets.resize_container import ResizeContainer # Added
from ..widgets.tree_select import TreeSelect # Added
from ..widgets.image_viewer import ImageViewer # Added for image display

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

    # --- Central widget setup with ResizeContainers ---
    v_splitter_main = ResizeContainer(orientation=Qt.Orientation.Vertical, parent=self)
    self.setCentralWidget(v_splitter_main)

    # Top horizontal container
    h_splitter_top = ResizeContainer(orientation=Qt.Orientation.Horizontal, background_color="lightblue", parent=v_splitter_main)
    
    # Create and add the TreeSelect widget to the top-left pane
    # It will default to showing the system root ("This PC" / "/")
    tree_select_widget = TreeSelect(parent=h_splitter_top)
    h_splitter_top.addWidget(tree_select_widget)
    
    label_tr = QLabel("Top-Right Pane", h_splitter_top)
    label_tr.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label_tr.setStyleSheet("background-color: #e0f2f1; border: 1px solid #b2dfdb; padding: 5px;")
    h_splitter_top.addWidget(label_tr)
    
    h_splitter_top.setWidgetSizes([150, 150]) # Initial sizes for top horizontal panes

    # Bottom horizontal container
    h_splitter_bottom = ResizeContainer(orientation=Qt.Orientation.Horizontal, background_color="lightcoral", parent=v_splitter_main)

    # Create and add the ImageViewer to the bottom-left pane
    image_viewer_bl = ImageViewer(parent=h_splitter_bottom)
    # It's good practice to ensure the path separator is correct for the OS,
    # though Python's open and QPixmap are often flexible.
    # For Windows paths given with backslashes in strings, they might need escaping
    # or use raw strings r"Z:\..." or forward slashes "Z:/...".
    # QPixmap should handle "Z:\Photos\FavG\465826_6adaadb6_crop.jpg" correctly on Windows.
    image_path = r"Z:\Photos\FavG\465826_6adaadb6_crop.jpg"
    image_viewer_bl.set_image_from_path(image_path)
    h_splitter_bottom.addWidget(image_viewer_bl)

    label_br = QLabel("Bottom-Right Pane", h_splitter_bottom)
    label_br.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label_br.setStyleSheet("background-color: #fce4ec; border: 1px solid #f8bbd0; padding: 5px;")
    h_splitter_bottom.addWidget(label_br)

    h_splitter_bottom.setWidgetSizes([150, 150]) # Initial sizes for bottom horizontal panes

    # Add horizontal splitters to the main vertical splitter
    v_splitter_main.addWidget(h_splitter_top)
    v_splitter_main.addWidget(h_splitter_bottom)
    v_splitter_main.setWidgetSizes([200, 200]) # Initial sizes for vertical split

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