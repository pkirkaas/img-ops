# Specification: Tree Structured file system browser GUI widget

Create/update the tree structured file system browsing widget called `tree_select` that can be included as a widget in a resize_container, according to the following specification:

## Specification
The browser widget should be a single tree structured pane. Each folder should be expandable by clicking on a `+` expand.
The default root of the tree_select should be the file system root - on Windows, "This PC", on Linux, "/"
The widget should include the equivalent of "up" or ".." to move the root of the widget up a level
Each item (node & leaf) should be selectable by a checkbox.
For testing, the widget should provide a `Show Selected` button that pops up a dialog box that shows all selections
For demo/testing, put a `tree_select` widget in the top left component of the nested resize_container components of the main window.
The poetry command `poetry run start_gui` should open the main application window with the tree_select component in the top left