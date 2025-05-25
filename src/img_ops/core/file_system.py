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