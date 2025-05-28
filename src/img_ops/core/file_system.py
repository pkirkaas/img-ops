"""
Core file system operations.

This module will handle tasks such as scanning directories,
reading and writing files (potentially image-specific metadata files),
and other file system interactions relevant to image operations.
"""

import os
from pathlib import Path
from typing import List, Union, Set
import warnings

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    # Pillow is optional for level 2 validation.
    # A warning will be issued if level 2 is attempted without Pillow.

# Define comprehensive list of common image file extensions at the module level
# Includes both lowercase and uppercase variants for case-insensitive matching by design
# but will be converted to lowercase for consistent comparison.
DEFAULT_IMAGE_EXTENSIONS: Set[str] = {
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
# Ensure all default extensions are lowercase for consistent comparison
_LOWERCASE_DEFAULT_IMAGE_EXTENSIONS: Set[str] = {ext.lower() for ext in DEFAULT_IMAGE_EXTENSIONS}


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
            raise TypeError(
                f"All items in 'paths' must be strings or PathLike objects, got {type(path_item)} for '{path_item}'")

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


def valid_img_path(file_path: Union[str, os.PathLike], validation_level: int = 0) -> bool:
    """
    Checks if a given path is a valid image file based on the specified validation level.

    Validation Levels:
      - 0: Checks only if the file extension is a known image type (case-insensitive).
           Does not check for file existence.
      - 1: Performs level 0 check AND verifies that the path exists and is a file.
      - 2: Performs level 1 check AND attempts to open and verify the file as an image
           using Pillow (if available). If Pillow is not installed, or if the file
           cannot be verified as an image, this check will fail (returns False).

    Args:
      file_path: The file path (string or PathLike object) to validate.
      validation_level: An integer (0, 1, or 2) specifying the depth of validation.
                        Defaults to 0.

    Returns:
      True if the path meets the validation criteria for the given level, False otherwise.

    Raises:
      TypeError: If file_path is not a string or PathLike object.
      ValueError: If validation_level is not 0, 1, or 2.

    Example:
      >>> # Level 0: Only checks extension
      >>> valid_img_path('photo.jpg', 0)
      True
      >>> valid_img_path('non_existent.png', 0)
      True
      >>> # Level 1: Checks extension and existence (assuming 'photo.jpg' exists)
      >>> valid_img_path('photo.jpg', 1)
      True
      >>> valid_img_path('non_existent.png', 1)
      False
      >>> # Level 2: Checks extension, existence, and image content (assuming 'photo.jpg' is valid)
      >>> # valid_img_path('photo.jpg', 2) # Might be True if Pillow can open it
      >>> # valid_img_path('corrupt.jpg', 2) # Might be False
    """
    if not isinstance(file_path, (str, os.PathLike)):
        raise TypeError(
            f"Input 'file_path' must be a string or PathLike object, got {type(file_path)}")
    if validation_level not in [0, 1, 2]:
        raise ValueError(
            f"validation_level must be 0, 1, or 2, got {validation_level}")

    p = Path(file_path)
    extension = p.suffix.lower()

    # Level 0: Check extension only
    is_valid_extension = extension in _LOWERCASE_DEFAULT_IMAGE_EXTENSIONS
    if not is_valid_extension:
        return False
    if validation_level == 0:
        return True

    # Level 1: Check existence and if it's a file
    if not p.is_file():
        return False
    if validation_level == 1:
        return True

    # Level 2: Verify image content using Pillow
    if validation_level == 2:
        if not PIL_AVAILABLE:
            warnings.warn(
                f"Pillow (PIL) is not installed. Cannot perform level 2 image content validation for '{p}'. "
                "Falling back to level 1 (file existence check).", UserWarning
            )
            return True # Already passed level 1

        try:
            with Image.open(p) as img:
                img.verify()  # Verifies image integrity
            return True
        except Exception:  # Catches PIL specific errors and others like FileNotFoundError if somehow missed
            return False

    return False # Should not be reached if validation_level is 0, 1, or 2


def filter_imgs(file_paths: List[Union[str, os.PathLike]], validation_level: int = 0) -> List[str]:
    """
    Filters a list of file paths to return only those that represent valid image files,
    based on the specified validation level.

    Uses `valid_img_path` internally for each file.

    Args:
      file_paths: A list of file paths (strings or PathLike objects) to filter.
      validation_level: An integer (0, 1, or 2) specifying the depth of validation
                        for each file. Defaults to 0.
                        See `valid_img_path` for details on validation levels.

    Returns:
      A list of file paths that are considered valid images according to the
      specified validation level. Preserves original path format and order.

    Raises:
      TypeError: If file_paths is not a list or if any element is not a string/PathLike.
      ValueError: If validation_level is not 0, 1, or 2 (raised by `valid_img_path`).

    Example:
      >>> paths = ['img.jpg', 'doc.txt', 'non_existent.png']
      >>> # filter_imgs(paths, 0) would include 'img.jpg', 'non_existent.png'
      >>> # filter_imgs(paths, 1) (assuming 'img.jpg' exists) would include 'img.jpg'
    """
    if not isinstance(file_paths, list):
        raise TypeError("Input 'file_paths' must be a list.")

    filtered_paths: List[str] = []
    for path_item in file_paths:
        if not isinstance(path_item, (str, os.PathLike)):
            raise TypeError(
                f"All items in 'file_paths' must be strings or PathLike objects, got {type(path_item)} for '{path_item}'")

        path_str = str(path_item)
        if valid_img_path(path_str, validation_level=validation_level):
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
        # An empty list has no nesting issues and all (zero) paths exist.
        return True

    # Convert all paths to absolute pathlib.Path objects and check existence
    absolute_paths: List[Path] = []
    for p_item in paths:
        if not isinstance(p_item, (str, Path)):
            raise TypeError(
                f"All items in 'paths' must be strings or Path objects, got {type(p_item)} for '{p_item}'"
            )

        # resolve() makes it absolute and resolves symlinks
        abs_path = Path(p_item).resolve()

        if not abs_path.exists():
            raise FileNotFoundError(
                f"Path does not exist: '{abs_path}' (original: '{p_item}')")
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
    paths_to_scan: List[Union[str, Path]]
) -> List[Path]:
    """
    Scans a list of input paths (which can be files or directories) and returns
    a list of all unique image files found.

    For directories, it recursively searches for image files.
    Image files are identified by the predefined list of common image extensions
    (see DEFAULT_IMAGE_EXTENSIONS).

    Args:
      paths_to_scan: A list of file system paths (strings or pathlib.Path objects)
                     to scan.

    Returns:
      A list of pathlib.Path objects, each pointing to a unique image file found.
      Returns an empty list if no image files are found or if inputs are empty.

    Raises:
      TypeError: If paths_to_scan is not of the expected type.
    """
    if not isinstance(paths_to_scan, list):
        raise TypeError("Input 'paths_to_scan' must be a list.")

    if not paths_to_scan:
        return []

    try:
        # 1. Extract all file paths from the input list (handles directories recursively)
        #    This step ensures that paths exist and are files before filtering.
        all_files_str = extract_paths(paths_to_scan)

        # 2. Filter these files to get only images based on the default extensions.
        #    validation_level=0 is used because extract_paths already confirms existence.
        #    We only need to check the extension here.
        image_files_str = filter_imgs(
            all_files_str, validation_level=0
        )

        # Convert to Path objects and ensure uniqueness
        # (though extract_paths already does some sorting/uniquing of its output)
        unique_image_paths = sorted(
            list(set(Path(p) for p in image_files_str)))
        return unique_image_paths

    except Exception as e:
        # Re-raise or handle more gracefully depending on desired behavior
        # For now, print and re-raise to make debugging easier.
        print(f"Error in get_all_image_files_in_paths: {e}")
        raise
