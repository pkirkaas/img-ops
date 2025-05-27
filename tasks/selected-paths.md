# Task: Create a `selected_paths.py` GUI widget

This will be a more complete, powerful implementation somewhat similar to the `show_selected.py` widget already implemented.

The new `selected_paths` widget should only display/allow file folders or individual image file paths.

The individual paths should not be just text in a text box, but individual, selectable path widgets - multi-selectable.

Each path widget should support mouse right-click context menu functionality, including "Remove" to remove the selected path from the set of selected paths.

The `selected_paths` widget should support the right-click "Add Path" option to add a new path selected from the file system using the new `select_path.py` pop-up/dialog widget

In the main application window, there is currently a placeholder "Bottom-Right Pane". Replace this placeholder pane with this new "selected_paths" widget