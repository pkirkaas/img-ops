"""
Core file system operations.

This module will handle tasks such as scanning directories,
reading and writing files (potentially image-specific metadata files),
and other file system interactions relevant to image operations.
"""

import os
from typing import List, Union

def extract_paths(paths: List[Union[str, os.PathLike]]) -> List[str]:
  """
  Extracts all file paths from a list of mixed file and directory paths.

  Iterates through the input list. For each element, it verifies if the path
  exists in the file system. If the item is a file, it's added to the result.
  If the item is a directory, the function recursively traverses the directory
  structure to find all files within and adds them to the result.

  Args:
    paths: A list of strings, where each string can be a path to a file
           or a directory. `os.PathLike` objects are also accepted.

  Returns:
    A list of absolute file paths. If a path in the input list does not exist,
    it will be ignored.

  Raises:
    TypeError: If the input `paths` is not a list.
    TypeError: If any element in `paths` is not a string or os.PathLike.

  Example:
    >>> # Assuming '/path/to/dir' contains 'file1.txt' and 'subdir/file2.txt'
    >>> # and '/path/to/file.txt' exists.
    >>> extract_paths(['/path/to/dir', '/path/to/file.txt', '/non/existent/path'])
    ['/path/to/dir/file1.txt', '/path/to/dir/subdir/file2.txt', '/path/to/file.txt']
  """
  if not isinstance(paths, list):
    raise TypeError("Input 'paths' must be a list.")

  all_file_paths: List[str] = []
  for path_item in paths:
    if not isinstance(path_item, (str, os.PathLike)):
      raise TypeError(f"All items in 'paths' must be strings or PathLike objects, got {type(path_item)} for '{path_item}'")

    # Convert os.PathLike to string and get absolute path
    abs_path_item = os.path.abspath(str(path_item))

    if not os.path.exists(abs_path_item):
      # According to the instructions, ignore non-existent paths.
      # Optionally, we could raise an error or log a warning here.
      # print(f"Warning: Path '{abs_path_item}' does not exist and will be skipped.")
      continue

    if os.path.isfile(abs_path_item):
      all_file_paths.append(abs_path_item)
    elif os.path.isdir(abs_path_item):
      for root, _, files in os.walk(abs_path_item):
        for filename in files:
          # Construct absolute path for each file
          file_path = os.path.join(root, filename)
          all_file_paths.append(os.path.abspath(file_path))
  
  # Remove duplicates that might occur if a file is listed explicitly
  # and also part of a directory that is listed.
  return sorted(list(set(all_file_paths)))

# Placeholder for future file system functions
pass