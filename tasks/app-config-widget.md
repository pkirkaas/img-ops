
*   **Project Name/Type:** `img-ops` Python desktop application
*   **Key Technologies:** Python, Pillow
*   **Relevant Modules/Files (if known):** `src/img_ops/core/image_processing.py`, `src/img_ops/core/file_system.py`
Tasks:
## Step 1
Create an app_config_widget that manages the app configs from core/app_config.py

The widget should support choosing an existing configuration, deleting an existing configuration, editing and existing configuration, and creating a new configuration.
It should have buttons for OK & Cancel
It should support sharing the configuration with the rest of the application

## Step 2
In the main_window menu, add a menu item that launches the app_config_widget as a resizable modal dialog box

## Step 3
Add an app_config object to the main app window that is connected to / updated by the configuration values returned by the app_config_widget pop up dialog.
## Step 4
Connect the app_config_widget to update the app config of the main window

Add a "Current Config" widget to the main window just for debugging - it should show the current app config values, and be updated by every change from the app_config_widget