"""
Optional main application dispatcher for img-ops.

This script can be used as a single entry point to launch
either the CLI or the GUI version of the application based on arguments
or configuration.

Alternatively, `pyproject.toml` can define separate script entry points
for the CLI and GUI directly.
"""
import argparse

def main():
  """
  Parses arguments and launches the appropriate application mode (CLI or GUI).
  """
  parser = argparse.ArgumentParser(
    description="Img-Ops: Image Operations Tool. Run with --gui for the graphical interface."
  )
  parser.add_argument(
    "--mode",
    choices=["cli", "gui"],
    default="cli", # Default to CLI if no mode is specified
    help="Specify the application mode to run: 'cli' or 'gui'."
  )
  # Add other global arguments if needed

  args = parser.parse_args()

  if args.mode == "gui":
    print("Launching Img-Ops GUI...")
    # Import and run the GUI main function
    # Ensure PySide6 is installed or handle ImportError
    try:
      from .gui.main import run_gui
      run_gui()
    except ImportError as e:
      print(f"Error: Could not import GUI components. Is PySide6 installed? {e}")
      print("Please install PySide6: pip install pyside6")
  else: # Default to CLI
    print("Img-Ops CLI starting (with Python & Poetry)...")
    # Import and run the CLI main function
    # Ensure Typer is installed or handle ImportError
    try:
      from .cli.main import app as cli_app
      cli_app()
    except ImportError as e:
      print(f"Error: Could not import CLI components. Is Typer installed? {e}")
      print("Please install Typer: pip install typer[all]")

if __name__ == "__main__":
  main()