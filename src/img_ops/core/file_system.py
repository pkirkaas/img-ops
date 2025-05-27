"""
Core file system operations.

This module will handle tasks such as scanning directories,
reading and writing files (potentially image-specific metadata files),
and other file system interactions relevant to image operations.
"""

import os
from pathlib import Path
from typing import List, Union, Set

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

def filter_imgs(file_paths: List[Union[str, os.PathLike]],
                case_sensitive: bool = False,
                custom_extensions: List[str] = None) -> List[str]:
  """
  Filters a list of file paths to return only those that represent image files.
  
  Determines if a file is an image based on its file extension. Supports all
  common image formats including JPEG, PNG, GIF, BMP, TIFF, WebP, and many others.
  The function is case-insensitive by default but can be configured to be case-sensitive.
  
  Args:
    file_paths: A list of file paths (strings or PathLike objects) to filter.
                Can include both absolute and relative paths.
    case_sensitive: If True, extension matching will be case-sensitive.
                   If False (default), extensions will be matched case-insensitively.
                   For example, both '.JPG' and '.jpg' will be considered image files.
    custom_extensions: Optional list of additional file extensions to consider as images.
                      Should include the dot (e.g., ['.xyz', '.custom']).
                      These will be added to the default list of image extensions.
  
  Returns:
    A list of file paths that have image file extensions, preserving the original
    path format (absolute/relative) and order from the input list.
    
  Raises:
    TypeError: If file_paths is not a list.
    TypeError: If any element in file_paths is not a string or PathLike object.
    TypeError: If case_sensitive is not a boolean.
    TypeError: If custom_extensions is provided but is not a list.
    ValueError: If any custom extension doesn't start with a dot.
    
  Example:
    >>> # Basic usage with mixed file types
    >>> paths = ['/home/user/photo.jpg', '/home/user/document.txt', '/home/user/image.PNG']
    >>> filter_imgs(paths)
    ['/home/user/photo.jpg', '/home/user/image.PNG']
    
    >>> # Case-sensitive filtering
    >>> paths = ['/home/user/photo.JPG', '/home/user/image.jpg']
    >>> filter_imgs(paths, case_sensitive=True)
    ['/home/user/image.jpg']  # Only lowercase .jpg matches
    
    >>> # With custom extensions
    >>> paths = ['/home/user/photo.jpg', '/home/user/custom.xyz']
    >>> filter_imgs(paths, custom_extensions=['.xyz'])
    ['/home/user/photo.jpg', '/home/user/custom.xyz']
  """
  # Input validation
  if not isinstance(file_paths, list):
    raise TypeError("Input 'file_paths' must be a list.")
    
  if not isinstance(case_sensitive, bool):
    raise TypeError("Parameter 'case_sensitive' must be a boolean.")
    
  if custom_extensions is not None:
    if not isinstance(custom_extensions, list):
      raise TypeError("Parameter 'custom_extensions' must be a list or None.")
    for ext in custom_extensions:
      if not isinstance(ext, str) or not ext.startswith('.'):
        raise ValueError(f"Custom extension '{ext}' must be a string starting with a dot.")
  
  # Define comprehensive list of common image file extensions
  # Includes both lowercase and uppercase variants for case-insensitive matching
  default_image_extensions = {
    # JPEG formats
    '.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi',
    # PNG format
    '.png',
    # GIF format
    '.gif',
    # BMP formats
    '.bmp', '.dib',
    # TIFF formats
    '.tiff', '.tif',
    # WebP format
    '.webp',
    # SVG format
    '.svg', '.svgz',
    # ICO format
    '.ico',
    # Raw camera formats
    '.raw', '.arw', '.cr2', '.cr3', '.crw', '.dng', '.nef', '.nrw', '.orf', '.pef', '.raf', '.rw2', '.srw',
    # Adobe formats
    '.psd', '.psb',
    # HEIF/HEIC formats (modern Apple formats)
    '.heif', '.heic', '.heics', '.avif',
    # Other formats
    '.pcx', '.tga', '.exr', '.hdr', '.pic', '.pnm', '.pbm', '.pgm', '.ppm',
    # Windows formats
    '.wmf', '.emf',
    # JPEG 2000
    '.jp2', '.j2k', '.jpf', '.jpx', '.jpm', '.mj2',
    # JPEG XL
    '.jxl'
  }
  
  # Add custom extensions if provided
  image_extensions = default_image_extensions.copy()
  if custom_extensions:
    # Convert custom extensions to lowercase for consistent comparison
    if case_sensitive:
      image_extensions.update(custom_extensions)
    else:
      image_extensions.update(ext.lower() for ext in custom_extensions)
  
  # If case-insensitive, ensure all extensions are lowercase
  if not case_sensitive:
    image_extensions = {ext.lower() for ext in image_extensions}
  
  # Filter the file paths
  filtered_paths: List[str] = []
  
  for file_path in file_paths:
    # Validate each path item
    if not isinstance(file_path, (str, os.PathLike)):
      raise TypeError(f"All items in 'file_paths' must be strings or PathLike objects, got {type(file_path)} for '{file_path}'")
    
    # Convert PathLike to string
    path_str = str(file_path)
    
    # Extract file extension
    _, extension = os.path.splitext(path_str)
    
    # Compare extension based on case sensitivity setting
    if case_sensitive:
      is_image = extension in image_extensions
    else:
      is_image = extension.lower() in image_extensions
    
    # Add to filtered list if it's an image
    if is_image:
      filtered_paths.append(path_str)
  
  return filtered_paths


def check_nested(paths: List[Union[str, Path]]) -> bool:
  """
  Verifies a list of file system paths to ensure they all exist and that
  no path in the list is contained within another path in the list.

  For example, if '/folderA' is in the list, then '/folderA/file.txt' or
  '/folderA/subfolderB' cannot be in the list.

  Args:
    paths: A list of file system paths (strings or pathlib.Path objects).

  Returns:
    True if all paths exist and no path is nested within another.

  Raises:
    TypeError: If `paths` is not a list or contains non-path-like objects.
    FileNotFoundError: If any path in the list does not exist.
    ValueError: If any path in the list is found to be nested within another
                path in the same list.

  Example:
    ```python
    # Valid scenarios
    check_nested(["/tmp/file1.txt", "/tmp/folderA"]) # Assuming they exist
    check_nested([Path("/var/log"), Path("/etc/hosts")]) # Assuming they exist

    # Invalid scenarios
    # check_nested(["/tmp/file1.txt", "/tmp/non_existent_folder"]) # Raises FileNotFoundError
    # check_nested(["/tmp", "/tmp/file1.txt"]) # Raises ValueError (nesting)
    # check_nested(["/usr/local", "/usr/local/bin/my_script"]) # Raises ValueError
    ```
  """
  if not isinstance(paths, list):
    raise TypeError("Input 'paths' must be a list.")

  if not paths:
    return True # An empty list has no nesting issues and all (zero) paths exist.

  # Convert all paths to absolute pathlib.Path objects and check existence
  absolute_paths: List[Path] = []
  for p_item in paths:
    if not isinstance(p_item, (str, Path)):
      raise TypeError(
          f"All items in 'paths' must be strings or Path objects, got {type(p_item)} for '{p_item}'"
      )
    
    abs_path = Path(p_item).resolve() # resolve() makes it absolute and resolves symlinks

    if not abs_path.exists():
      raise FileNotFoundError(f"Path does not exist: '{abs_path}' (original: '{p_item}')")
    absolute_paths.append(abs_path)

  # Sort paths to make parent checking easier (shorter paths, typically parents, come first)
  # This isn't strictly necessary for correctness with Path.is_relative_to but can be intuitive.
  # More importantly, sorting helps in identifying the *first* pair that violates the rule.
  # We sort by string length of the path, then alphabetically for tie-breaking.
  # This ensures that potential parents are generally processed before potential children.
  sorted_paths = sorted(absolute_paths, key=lambda p: (len(str(p)), str(p)))

  # Check for nesting
  # Iterate through each path and compare it against all subsequent paths
  for i in range(len(sorted_paths)):
    p1 = sorted_paths[i]
    for j in range(i + 1, len(sorted_paths)):
      p2 = sorted_paths[j]
      
      # Check if p2 is a child of p1
      # Path.is_relative_to() checks if p2 can be made relative to p1
      # This means p1 is an ancestor of p2.
      if p2.is_relative_to(p1):
        raise ValueError(
            f"Nesting violation: Path '{p2}' (original: '{paths[absolute_paths.index(p2)]}') "
            f"is inside path '{p1}' (original: '{paths[absolute_paths.index(p1)]}')."
        )
      # We also need to check if p1 is a child of p2, which shouldn't happen if sorted by length
      # but good for robustness if sorting logic changes or for unsorted comparison.
      # However, given the sorting by length, p1 cannot be a child of p2 if p1 comes before p2.
      # If we didn't sort, we'd need:
      # if p1.is_relative_to(p2):
      #   raise ValueError(f"Nesting violation: Path '{p1}' is inside path '{p2}'.")

  return True

def get_all_image_files_in_paths(
    paths_to_scan: List[Union[str, Path]],
    image_extensions_patterns: List[str]
) -> List[Path]:
    """
    Scans a list of input paths (which can be files or directories) and returns
    a list of all unique image files found.

    For directories, it recursively searches for image files.
    Image files are identified by the provided extension patterns.

    Args:
      paths_to_scan: A list of file system paths (strings or pathlib.Path objects)
                     to scan.
      image_extensions_patterns: A list of image file extension patterns (e.g., "*.jpg", "*.png").

    Returns:
      A list of pathlib.Path objects, each pointing to a unique image file found.
      Returns an empty list if no image files are found or if inputs are empty.

    Raises:
      TypeError: If inputs are not of the expected types.
      ValueError: If image_extensions_patterns contains invalid patterns.
    """
    if not isinstance(paths_to_scan, list):
        raise TypeError("Input 'paths_to_scan' must be a list.")
    if not isinstance(image_extensions_patterns, list):
        raise TypeError("Input 'image_extensions_patterns' must be a list.")

    if not paths_to_scan:
        return []

    # Convert patterns like "*.jpg" to ".jpg" for filter_imgs
    custom_extensions_for_filter = []
    for pattern in image_extensions_patterns:
        if not isinstance(pattern, str) or not pattern.startswith("*.") or len(pattern) <= 2:
            raise ValueError(f"Invalid image extension pattern: '{pattern}'. Must be like '*.ext'.")
        custom_extensions_for_filter.append(pattern[1:]) # Get ".ext"

    try:
        # 1. Extract all file paths from the input list (handles directories recursively)
        all_files_str = extract_paths(paths_to_scan)

        # 2. Filter these files to get only images based on the provided extensions
        #    filter_imgs expects extensions like ['.jpg'], not ['jpg'] or ['*.jpg']
        #    It's case-insensitive by default.
        image_files_str = filter_imgs(all_files_str, custom_extensions=custom_extensions_for_filter)
        
        # Convert to Path objects and ensure uniqueness (though extract_paths already does some sorting/uniquing)
        unique_image_paths = sorted(list(set(Path(p) for p in image_files_str)))
        return unique_image_paths

    except Exception as e:
        # Re-raise or handle more gracefully depending on desired behavior
        # For now, print and re-raise to make debugging easier.
        print(f"Error in get_all_image_files_in_paths: {e}")
        raise