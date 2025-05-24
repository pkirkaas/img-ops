# Task: Implement State & Communication between Main App & Widgets
Now we need to implement bi-directional communication between widgets and the main app.

Proposal: Implement this using signals & slots in the widgets, and maintain cental state in the main app through a model.

Steps:

Create a state model shared by the main application & widgets
Add appropriate signals & slots to the widgets & main application for bi-directional updates
To test/demo, create a new widget - "show_selected". This can be a simple multi-line text widget, that shows every selection from the "tree_select" widget on a separate line
Every change of selection in the "tree_select" widget should be immediately shown in the new "show_selected" widget
Put the new "show_selected" widget in the top right pane of the main app, which currently just contains the text "Top-Right Pane" 