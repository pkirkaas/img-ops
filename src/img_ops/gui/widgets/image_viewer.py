"""
Defines a custom ImageViewer widget.
"""
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QSize


class ImageViewer(QWidget):
    """
    A custom widget for displaying images.

    This widget can be enhanced with features like zooming, panning,
    and fitting images to the widget size.
    """

    def __init__(self, parent=None):
        """
        Initializes the ImageViewer.

        Args:
          parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super().__init__(parent)
        self.pixmap = None

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        # Ensure image can use full widget area
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setMinimumSize(QSize(100, 100))  # Set a minimum size

    def set_image_from_path(self, image_path: str):
        """
        Loads and displays an image from the given file path.

        Args:
          image_path (str): The path to the image file.
        """
        self.pixmap = QPixmap(image_path)
        if self.pixmap.isNull():
            self.image_label.setText(f"Cannot load image: {image_path}")
            self.pixmap = None  # Ensure pixmap is None if loading failed
        else:
            self._update_display()

    def clear_image(self):
        """
        Clears the currently displayed image.
        """
        self.pixmap = None
        self.image_label.clear()
        self.image_label.setText("No image loaded.")

    def _update_display(self):
        """
        Updates the displayed image, scaling it to fit the widget.
        """
        if self.pixmap and not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("No image loaded or image is invalid.")

    def resizeEvent(self, event):
        """
        Handles the widget resize event to re-scale the image.
        """
        super().resizeEvent(event)
        self._update_display()

    def paintEvent(self, event):
        """
        Custom paint event to draw a border or background if needed.
        """
        super().paintEvent(event)
        # Example: Draw a border
        # painter = QPainter(self)
        # painter.setPen(QColor(Qt.GlobalColor.gray))
        # painter.drawRect(self.rect().adjusted(0, 0, -1, -1)) # Adjust for pen width


if __name__ == '__main__':
    # This part is for testing the ImageViewer independently
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    # You would need an actual image path here for testing
    # viewer.set_image_from_path("path/to/your/test_image.png")
    viewer.setWindowTitle("Test Image Viewer")
    viewer.resize(400, 300)
    viewer.show()
    sys.exit(app.exec())
