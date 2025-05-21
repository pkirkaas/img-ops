# Specification: Widget Container

Create or update a reusable, configurable multi-widget container component called `resize_container`, in `src/gui/widgets/resize_container.py`, according to these specifications:

## Purpose
- The resize_container component should allow including multiple GUI widgets/components, with draggable handles/separators to resize the components contained.
- The resize_container should be nestable/composable - each resize-container should be able to contain other resize-containers.
- Each resize_container should have an orientation - horizontal or vertical
- By nesting vertical/horizontal resize_containers, arbitrary composition of resizable components should be possible
- resize_container should be configurable, with background-color, initial size, orientation, etc. Each configurable parameter should have a reasonable default

## Integration into project

To demonstrate the functionality, modify the main_window component to include:
- A vertical resize component with 2 widgets
- Each of the vertical resize component widgets should contain two horizontal resize_container widgets
- Each resize_container should have a different background color to distinguish them
- The initial content of each resize_container can be arbitrary text.




















