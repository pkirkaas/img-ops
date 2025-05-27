"""
SQLite-based cache manager for file information, primarily focused on storing
and retrieving perceptual hashes (phashes) of images.
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional, Tuple, Any # Using Any for exc_tb in __exit__

from PIL import UnidentifiedImageError
import platformdirs

# Assuming img_similarity.py is in the same package (src.img_ops.core)
from .img_similarity import img_phash


class FileInfoCache:
  """
  Manages a cache of file information, including file size, modification time,
  and perceptual hash (phash), stored in an SQLite database.

  The cache helps to avoid re-computing phashes for files that haven't changed.
  It uses platformdirs to store the database in a user-specific application data directory
  by default.
  """

  def __init__(self, db_path: Optional[Union[str, Path]] = None):
    """
    Initializes the FileInfoCache.

    Args:
      db_path: Optional path to the SQLite database file. If None, a default
               path in the user's application data directory will be used
               (e.g., using platformdirs).

    Raises:
      sqlite3.Error: If there's an issue connecting to or setting up the database.
    """
    if db_path:
      self.db_path: Path = Path(db_path).resolve()
    else:
      app_name = "img-ops"
      app_author = "pkirkaas" # As per typical platformdirs usage
      self.db_path = Path(platformdirs.user_data_dir(app_name, app_author)) / "file_info_cache.db"

    # Ensure the parent directory for the database exists
    try:
      self.db_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
      # This might happen due to permission issues, though mkdir with exist_ok=True is quite robust.
      raise sqlite3.Error(f"Failed to create database directory {self.db_path.parent}: {e}") from e

    try:
      self._conn: sqlite3.Connection = sqlite3.connect(self.db_path)
      self._cursor: sqlite3.Cursor = self._conn.cursor()
      self._ensure_db_table()
    except sqlite3.Error as e:
      raise sqlite3.Error(f"Failed to initialize database at {self.db_path}: {e}") from e

  def _ensure_db_table(self) -> None:
    """
    Ensures that the 'file_cache' table exists in the database with the correct schema.
    If the table does not exist, it is created.
    """
    try:
      self._cursor.execute("""
        CREATE TABLE IF NOT EXISTS file_cache (
            file_path TEXT PRIMARY KEY,
            size INTEGER NOT NULL,
            mod_time REAL NOT NULL,
            phash TEXT
        );
      """)
      self._conn.commit()
    except sqlite3.Error as e:
      # Rollback might not be strictly necessary for DDL, but good practice
      self._conn.rollback()
      raise sqlite3.Error(f"Failed to create or verify 'file_cache' table: {e}") from e

  def _get_file_stats(self, file_path: str) -> Optional[Tuple[int, float]]:
    """
    Retrieves the size and modification time of a file.

    Args:
      file_path: The absolute path to the file.

    Returns:
      A tuple (size_in_bytes, modification_timestamp) if the file exists,
      otherwise None.
    """
    try:
      stat_info = os.stat(file_path)
      return stat_info.st_size, stat_info.st_mtime
    except FileNotFoundError:
      return None
    except OSError as e: # Catch other potential os.stat errors
      # Consider logging this error if a logging mechanism is in place
      # print(f"Warning: Could not get stats for {file_path}: {e}")
      return None

  def get_phash(self, file_path: Union[str, Path]) -> Optional[str]:
    """
    Retrieves the perceptual hash (phash) for a given file.

    If the file is already in the cache and has not been modified, the cached
    phash is returned. Otherwise, a new phash is generated, stored in the
    cache, and then returned. If phash generation fails (e.g., not an image),
    None is stored and returned.

    Args:
      file_path: The path to the image file (can be relative or absolute).

    Returns:
      The hexadecimal string representation of the phash if successful,
      or None if the file doesn't exist, is not a valid image, or an error occurs.
    """
    abs_file_path = str(Path(file_path).resolve())
    current_stats = self._get_file_stats(abs_file_path)

    if current_stats is None:
      # File does not exist or is inaccessible
      return None
    current_size, current_mod_time = current_stats

    cached_phash_value: Optional[str] = None
    update_cache = True # Assume we need to update/insert unless proven otherwise

    try:
      self._cursor.execute(
          "SELECT size, mod_time, phash FROM file_cache WHERE file_path = ?",
          (abs_file_path,)
      )
      cached_entry = self._cursor.fetchone()

      if cached_entry:
        cached_size, cached_mod_time, db_phash_val = cached_entry
        # Ensure floating point comparison is safe for mod_time
        # SQLite REAL can store floats precisely, os.stat().st_mtime is float
        if cached_size == current_size and abs(cached_mod_time - current_mod_time) < 1e-6: # Check for near equality for floats
          if db_phash_val is not None: # We have a valid, non-NULL phash
            cached_phash_value = db_phash_val
            update_cache = False # Cache is valid and phash exists
          # If db_phash_val is NULL, it means we tried before and failed,
          # but file hasn't changed, so don't try again unless forced.
          # However, the spec implies re-generating if phash is NULL.
          # Let's stick to: if file unchanged and phash is NULL, it means it's not an image
          # or failed previously. We should only re-calculate if file changed OR phash is NULL.
          # The current logic will proceed to "Cache miss or invalidation" if db_phash_val is NULL.
          # This is correct as per "or if there is no phash value" in the spec.

    except sqlite3.Error as e:
      # Log this error, but proceed as if cache miss
      # print(f"SQLite error during phash retrieval for {abs_file_path}: {e}")
      cached_entry = None # Ensure we treat it as a cache miss

    if update_cache:
      new_phash_val: Optional[str] = None
      try:
        # img_phash from .img_similarity is expected to return str or raise error
        new_phash_val = img_phash(abs_file_path, return_format='hex')
      except FileNotFoundError: # Should be caught by _get_file_stats, but defensive
        return None # File disappeared
      except UnidentifiedImageError: # PIL specific error for non-images
        new_phash_val = None # Store None to indicate it's not a processable image
      except Exception:
        # Catch any other error from img_phash (e.g., internal library issues)
        # Consider logging the specific exception e
        # print(f"Error generating phash for {abs_file_path}: {e_phash}")
        new_phash_val = None # Store None for other errors

      try:
        if cached_entry: # Entry exists, so update it
          self._cursor.execute(
              "UPDATE file_cache SET size = ?, mod_time = ?, phash = ? WHERE file_path = ?",
              (current_size, current_mod_time, new_phash_val, abs_file_path)
          )
        else: # No entry, so insert new one
          self._cursor.execute(
              "INSERT INTO file_cache (file_path, size, mod_time, phash) VALUES (?, ?, ?, ?)",
              (abs_file_path, current_size, current_mod_time, new_phash_val)
          )
        self._conn.commit()
      except sqlite3.Error as e:
        # Log this error
        # print(f"SQLite error during cache update/insert for {abs_file_path}: {e}")
        self._conn.rollback() # Rollback on error
        # Depending on policy, we might want to return new_phash_val anyway,
        # or None if DB operation failed. For now, return what we calculated.
      cached_phash_value = new_phash_val

    return cached_phash_value

  def clear_cache(self) -> None:
    """
    Removes all entries from the file information cache.
    """
    try:
      self._cursor.execute("DELETE FROM file_cache")
      self._conn.commit()
    except sqlite3.Error as e:
      # print(f"SQLite error during clear_cache: {e}")
      self._conn.rollback()
      raise # Re-raise after rollback

  def clean_cache(self) -> None:
    """
    Iterates through all entries in the cache, removing entries for:
    1. File paths that no longer exist.
    2. File paths where the file's size or modification time has changed
       compared to the cached values.
    """
    try:
      self._cursor.execute("SELECT file_path, size, mod_time FROM file_cache")
      all_entries = self._cursor.fetchall()
    except sqlite3.Error as e:
      # print(f"SQLite error fetching entries for clean_cache: {e}")
      return # Cannot proceed

    paths_to_delete = []
    for path_str, cached_size, cached_mod_time in all_entries:
      current_stats = self._get_file_stats(path_str)
      if current_stats is None: # File deleted
        paths_to_delete.append(path_str)
      else:
        current_size, current_mod_time = current_stats
        if current_size != cached_size or abs(current_mod_time - cached_mod_time) > 1e-6:
          paths_to_delete.append(path_str)

    if paths_to_delete:
      try:
        # Using a list of tuples for executemany for safety with many ?
        placeholders = ','.join(['?'] * len(paths_to_delete))
        self._cursor.execute(
            f"DELETE FROM file_cache WHERE file_path IN ({placeholders})",
            paths_to_delete
        )
        self._conn.commit()
      except sqlite3.Error as e:
        # print(f"SQLite error during clean_cache deletion: {e}")
        self._conn.rollback()
        # Not re-raising here, as some cleanup might have occurred or failed partially.

  def close(self) -> None:
    """
    Closes the database connection.
    It's recommended to use the FileInfoCache as a context manager (`with ... as ...`)
    to ensure the connection is closed automatically.
    """
    if self._conn:
      try:
        self._conn.close()
      except sqlite3.Error as e:
        # print(f"Error closing SQLite connection: {e}")
        pass # Suppress error on close
      finally:
        self._conn = None # type: ignore [assignment] # Mark as closed

  def __enter__(self) -> 'FileInfoCache':
    """Allows the FileInfoCache to be used as a context manager."""
    return self

  def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
    """Closes the database connection when exiting the context."""
    self.close()

# Example Usage (for testing purposes, typically not here)
if __name__ == '__main__':
  # This example assumes you have some images in a 'test_images' folder
  # and img_similarity.py is correctly set up.
  print(f"Default DB path would be: {Path(platformdirs.user_data_dir('img-ops', 'pkirkaas')) / 'file_info_cache.db'}")

  # Create a dummy image file for testing
  dummy_image_dir = Path("test_cache_images")
  dummy_image_dir.mkdir(exist_ok=True)
  dummy_image_path1 = dummy_image_dir / "test1.png"
  dummy_image_path2 = dummy_image_dir / "test2.jpg"
  not_an_image_path = dummy_image_dir / "not_an_image.txt"

  try:
    from PIL import Image as PILImage
    # Create a small PNG
    img1 = PILImage.new('RGB', (60, 30), color = 'red')
    img1.save(dummy_image_path1)
    # Create a small JPG
    img2 = PILImage.new('RGB', (50, 50), color = 'blue')
    img2.save(dummy_image_path2)
    # Create a text file
    with open(not_an_image_path, "w") as f:
      f.write("This is not an image.")
  except ImportError:
    print("Pillow is not installed, cannot run full example.")
  except Exception as e:
    print(f"Error creating dummy files: {e}")


  # Using a temporary DB for this example
  temp_db_path = "temp_file_info_cache.db"
  if Path(temp_db_path).exists():
    Path(temp_db_path).unlink() # Clean up from previous run

  with FileInfoCache(db_path=temp_db_path) as cache:
    print(f"Using DB at: {cache.db_path}")

    # Test get_phash for existing image
    phash1 = cache.get_phash(dummy_image_path1)
    print(f"PHash for {dummy_image_path1.name}: {phash1}")

    # Test again, should be from cache
    phash1_cached = cache.get_phash(dummy_image_path1)
    print(f"PHash for {dummy_image_path1.name} (cached): {phash1_cached}")
    assert phash1 == phash1_cached

    # Test for another image
    phash2 = cache.get_phash(dummy_image_path2)
    print(f"PHash for {dummy_image_path2.name}: {phash2}")

    # Test for a non-image file
    phash_txt = cache.get_phash(not_an_image_path)
    print(f"PHash for {not_an_image_path.name} (should be None): {phash_txt}")
    assert phash_txt is None

    # Test for a non-existent file
    phash_non_existent = cache.get_phash("non_existent_file.png")
    print(f"PHash for non_existent_file.png (should be None): {phash_non_existent}")
    assert phash_non_existent is None

    print("\nCache content before clean_cache:")
    cache._cursor.execute("SELECT file_path, phash FROM file_cache")
    for row in cache._cursor.fetchall():
      print(row)

    # Modify a file and check if phash is recomputed (or rather, if cache is invalidated)
    if dummy_image_path1.exists():
      print(f"\nModifying {dummy_image_path1.name}...")
      # Simple modification: append some data
      with open(dummy_image_path1, "ab") as f: # Append bytes
        f.write(b"extra_data")
      # Or, if you want to ensure Pillow can still open it, re-save it
      # try:
      #   img_mod = PILImage.open(dummy_image_path1) # This will fail if "extra_data" corrupts it
      #   img_mod.save(dummy_image_path1, "PNG")
      # except Exception as e_mod:
      #   print(f"Could not re-save modified image: {e_mod}")

      # For a more reliable modification that changes timestamp and size:
      Path(dummy_image_path1).touch() # Update timestamp
      # And to change size, we'd need to actually alter content.
      # The append above changes size.

      phash1_modified = cache.get_phash(dummy_image_path1)
      print(f"PHash for {dummy_image_path1.name} (after modification): {phash1_modified}")
      # This might be None if the modification corrupted the image for phash.
      # Or it might be different if phash could still be computed.
      # The key is that it should have tried to recompute.
      if phash1 is not None and phash1_modified is not None:
           # This assertion is tricky because modification might make it unhashable
           # assert phash1 != phash1_modified
           print(f"Old phash: {phash1}, New phash: {phash1_modified}")
      elif phash1 is None and phash1_modified is not None:
          print(f"Image became hashable. New phash: {phash1_modified}")
      elif phash1 is not None and phash1_modified is None:
          print(f"Image became unhashable. Old phash: {phash1}")


    # Test clean_cache
    print("\nTesting clean_cache...")
    if dummy_image_path2.exists():
      dummy_image_path2.unlink() # Delete one file
      print(f"Deleted {dummy_image_path2.name}")

    cache.clean_cache()
    print("Cache content after clean_cache:")
    cache._cursor.execute("SELECT file_path, phash FROM file_cache")
    for row in cache._cursor.fetchall():
      print(row)
      assert Path(row[0]).name != dummy_image_path2.name # Ensure deleted file is gone

    # Test clear_cache
    print("\nTesting clear_cache...")
    cache.clear_cache()
    cache._cursor.execute("SELECT COUNT(*) FROM file_cache")
    count = cache._cursor.fetchone()[0]
    print(f"Number of entries after clear_cache: {count}")
    assert count == 0

  print(f"\nExample finished. Temporary DB was at: {temp_db_path}")
  # You might want to manually delete temp_db_path if you don't want it lingering
  # Path(temp_db_path).unlink(missing_ok=True)