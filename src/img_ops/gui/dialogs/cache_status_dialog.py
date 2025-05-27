"""
Dialog to display the status of the FileInfoCache.
"""
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QDialogButtonBox
)
from PySide6.QtCore import Qt, Slot

from img_ops.core.file_info_cache import FileInfoCache

class CacheStatusDialog(QDialog):
  """
  A dialog window that displays information about the phash cache,
  such as the number of entries and the database file size.
  """
  def __init__(self, cache_instance: FileInfoCache, parent=None):
    """
    Initializes the CacheStatusDialog.

    Args:
      cache_instance: An instance of FileInfoCache to query for status.
      parent: The parent widget, if any.
    """
    super().__init__(parent)
    self.setWindowTitle("Cache Status")
    self.setMinimumWidth(350)

    self._cache = cache_instance

    layout = QVBoxLayout(self)

    self.info_label = QLabel("Fetching cache status...")
    self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.info_label.setWordWrap(True)
    # Make the info label selectable
    self.info_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
    layout.addWidget(self.info_label)

    # Add a refresh button
    self.refresh_button = QPushButton("Refresh Status")
    self.refresh_button.clicked.connect(self.update_status)
    layout.addWidget(self.refresh_button)
    
    # Standard OK button
    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    button_box.accepted.connect(self.accept)
    layout.addWidget(button_box)

    self.setLayout(layout)
    self.update_status() # Initial status update

  @Slot()
  def update_status(self) -> None:
    """
    Queries the FileInfoCache and updates the displayed information.
    """
    self.info_label.setText("Fetching cache status...")
    self.refresh_button.setEnabled(False) # Disable while fetching

    try:
      entry_count = self._cache.get_entry_count()
      db_size_bytes = self._cache.get_database_size_on_disk()

      if db_size_bytes is not None:
        db_size_str = self._format_size(db_size_bytes)
      else:
        db_size_str = "N/A (Could not determine DB file size)"
      
      db_path_str = str(self._cache.db_path)

      status_text = (
        f"<b>Cache Database Location:</b><br>{db_path_str}<br><br>"
        f"<b>Total Cached Entries:</b> {entry_count}<br>"
        f"<b>Database File Size:</b> {db_size_str}"
      )
      self.info_label.setText(status_text)

    except Exception as e:
      self.info_label.setText(f"Error fetching cache status:\n{e}")
    finally:
      self.refresh_button.setEnabled(True)


  def _format_size(self, size_bytes: int) -> str:
    """
    Formats a size in bytes into a human-readable string (KB, MB, GB).

    Args:
      size_bytes: The size in bytes.

    Returns:
      A human-readable string representation of the size.
    """
    if size_bytes < 1024:
      return f"{size_bytes} Bytes"
    elif size_bytes < 1024**2:
      return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024**3:
      return f"{size_bytes / (1024**2):.2f} MB"
    else:
      return f"{size_bytes / (1024**3):.2f} GB"

  def open(self) -> None:
    """
    Overrides QDialog.open() to ensure status is updated when dialog is shown.
    """
    self.update_status()
    super().open()

  def exec(self) -> int:
    """
    Overrides QDialog.exec() to ensure status is updated when dialog is shown modally.
    """
    self.update_status()
    return super().exec()

if __name__ == '__main__':
  import sys
  from PySide6.QtWidgets import QApplication
  from pathlib import Path

  # This is a basic example. In a real app, FileInfoCache would be managed elsewhere.
  # For this example, we create a temporary cache.
  temp_db_path = Path("temp_cache_status_dialog_test.db")
  if temp_db_path.exists():
    temp_db_path.unlink()

  try:
    app = QApplication(sys.argv)
    
    # Create a FileInfoCache instance (it will create the db if not exists)
    # In a real app, this instance would likely be shared or passed from the main app.
    with FileInfoCache(db_path=temp_db_path) as test_cache:
        # Add some dummy data for testing display
        # test_cache.get_phash("some_file.png") # This would require a real file and img_similarity
        # For simplicity, we'll just rely on the count of an empty cache or manually insert
        if test_cache.get_entry_count() == 0:
            print("Populating cache with a dummy entry for dialog test (requires actual file for phash)...")
            # To make this runnable without real images, we'll skip actual phash generation
            # and focus on the dialog's ability to query counts and size.
            # If you have a test image, you can uncomment the get_phash line.

        dialog = CacheStatusDialog(cache_instance=test_cache)
        dialog.exec()

  except Exception as e:
    print(f"An error occurred: {e}")
  finally:
    if temp_db_path.exists():
      # temp_db_path.unlink() # Clean up
      print(f"Test DB at {temp_db_path} was used.")
    sys.exit()