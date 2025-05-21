"""
Defines the ResizeContainer widget.

A reusable, configurable multi-widget container component that allows
including multiple GUI widgets/components, with draggable handles/separators
to resize the components contained.
"""
from PySide6.QtWidgets import QWidget, QSplitter, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QPalette
from typing import List, Optional, Union

class ResizeContainer(QWidget):
  """
  A QWidget that internally uses a QSplitter to manage resizable child widgets.
  It supports horizontal or vertical orientation and configurable background color.
  """

  def __init__(
    self,
    orientation: Qt.Orientation = Qt.Orientation.Horizontal,
    background_color: Optional[Union[QColor, str]] = None,
    initial_size: Optional[QSize] = None,
    parent: Optional[QWidget] = None
  ):
    """
    Initializes the ResizeContainer.

    Args:
      orientation (Qt.Orientation, optional): The orientation of the splitter.
                                               Defaults to Qt.Orientation.Horizontal.
      background_color (Optional[Union[QColor, str]], optional):
                                               The background color for the container.
                                               Can be a QColor instance or a color name string.
                                               Defaults to None (system default background).
      initial_size (Optional[QSize], optional): The initial preferred size for this container widget.
                                                Defaults to None (auto-sized by layout).
      parent (Optional[QWidget], optional): The parent widget. Defaults to None.
    """
    super().__init__(parent)

    self._splitter = QSplitter(orientation, self)

    # Main layout for this QWidget container
    if orientation == Qt.Orientation.Horizontal:
      layout = QHBoxLayout(self)
    else:
      layout = QVBoxLayout(self)
    
    layout.setContentsMargins(0, 0, 0, 0) # No margins for the container itself
    layout.addWidget(self._splitter)
    self.setLayout(layout)

    if initial_size:
      self.resize(initial_size) # Sets the initial size of the ResizeContainer widget

    if background_color:
      self.setAutoFillBackground(True)
      palette = self.palette()
      if isinstance(background_color, str):
        palette.setColor(QPalette.ColorRole.Window, QColor(background_color))
      elif isinstance(background_color, QColor):
        palette.setColor(QPalette.ColorRole.Window, background_color)
      self.setPalette(palette)

  def addWidget(self, widget: QWidget):
    """
    Adds a widget to the container's internal QSplitter.

    Args:
      widget (QWidget): The widget to add.
    """
    self._splitter.addWidget(widget)

  def setWidgetSizes(self, sizes: List[int]):
    """
    Sets the initial (or current) sizes of the widgets within the splitter.
    These are relative sizes and will be adjusted by the splitter.

    Args:
      sizes (List[int]): A list of integers representing the desired sizes
                         for each widget in the splitter.
    """
    if self._splitter.count() == len(sizes):
      self._splitter.setSizes(sizes)
    else:
      print(
        f"Warning: ResizeContainer.setWidgetSizes - Mismatch between widget count "
        f"({self._splitter.count()}) and provided sizes count ({len(sizes)})."
      )

  def getSplitter(self) -> QSplitter:
    """
    Returns the internal QSplitter instance.
    Useful for accessing more advanced QSplitter properties if needed.

    Returns:
      QSplitter: The internal QSplitter.
    """
    return self._splitter

if __name__ == '__main__':
  # Example usage for testing ResizeContainer independently
  import sys
  from PySide6.QtWidgets import QApplication

  app = QApplication(sys.argv)

  # --- Test 1: Simple Horizontal Splitter ---
  main_test_window1 = QWidget()
  main_test_window1.setWindowTitle("Test 1: Horizontal ResizeContainer")
  main_layout1 = QVBoxLayout(main_test_window1)

  h_container = ResizeContainer(orientation=Qt.Orientation.Horizontal, background_color="lightgray")
  label1 = QLabel("Left Pane")
  label1.setStyleSheet("background-color: lightblue; padding: 10px;")
  label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
  h_container.addWidget(label1)

  label2 = QLabel("Right Pane")
  label2.setStyleSheet("background-color: lightgreen; padding: 10px;")
  label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
  h_container.addWidget(label2)
  
  h_container.setWidgetSizes([100, 200]) # Initial relative sizes

  main_layout1.addWidget(h_container)
  main_test_window1.resize(400, 200)
  main_test_window1.show()

  # --- Test 2: Nested Splitters ---
  main_test_window2 = QWidget()
  main_test_window2.setWindowTitle("Test 2: Nested ResizeContainers")
  main_layout2 = QVBoxLayout(main_test_window2)

  # Top-level vertical container
  v_container_main = ResizeContainer(orientation=Qt.Orientation.Vertical, background_color="#f0f0f0")

  # Top horizontal container
  h_container_top = ResizeContainer(orientation=Qt.Orientation.Horizontal, background_color="lightblue")
  h_container_top.addWidget(QLabel("Top-Left (Text in Label)"))
  h_container_top.addWidget(QLabel("Top-Right (Text in Label)"))
  v_container_main.addWidget(h_container_top)

  # Bottom horizontal container
  h_container_bottom = ResizeContainer(orientation=Qt.Orientation.Horizontal, background_color="lightcoral")
  h_container_bottom.addWidget(QLabel("Bottom-Left (Text in Label)"))
  h_container_bottom.addWidget(QLabel("Bottom-Right (Text in Label)"))
  v_container_main.addWidget(h_container_bottom)
  
  v_container_main.setWidgetSizes([150, 150]) # Initial relative sizes for vertical split

  main_layout2.addWidget(v_container_main)
  main_test_window2.resize(500, 400)
  main_test_window2.show()

  sys.exit(app.exec())