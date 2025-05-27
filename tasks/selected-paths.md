# Task: Create a `selected_paths.py` GUI widget

This will be a more complete, powerful implementation somewhat similar to the `show_selected.py` widget already implemented.

The new `selected_paths` widget should only display/allow file folders or individual image file paths.

The individual paths should not be just text in a text box, but individual, selectable path widgets - multi-selectable.

Each path widget should support mouse right-click context menu functionality, including "Remove" to remove the selected path from the set of selected paths.

The `selected_paths` widget should support the right-click "Add Path" option to add a new path selected from the file system using the new `select_path.py` pop-up/dialog widget

In the main application window, there is currently a placeholder "Bottom-Right Pane". Replace this placeholder pane with this new "selected_paths" widget

## Changes to `selected_paths_widget.py` widget
- Add a label to the top of the widget: "Which Paths to Scan for Similarity?"
- The body containing the selected paths should be a table, with the column header "Paths"
- Each path should be preceded by a small icon, indicating if it is a Folder, File, Drive, etc
- When a path is added through the `select_path` dialog widget, the selected_paths_widget should validate that there are no nested paths in the list before adding the path
- Below the table of selected paths, add a button row with the following buttons:
- "Validate" - Checks the paths are not nested, and any file paths are image file paths
- "List" - Should process the path list to return a list of all the files within - for all folders, recurse and return all image files therein. The result of the "List" button should pop up a dialog listing all the image files, a count of how many image files, and an "OK" button to dismiss
- "PHash" - The phash button should take the list of image files, and use the `file_info_cache` to add phash strings for each file path if the cache entry is missing or outdated. 

