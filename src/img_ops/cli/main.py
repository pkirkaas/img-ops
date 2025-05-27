"""
Main entry point for the img-ops Command Line Interface (CLI).

This script will initialize the CLI application (e.g., using Typer or Click)
and register all available commands.
"""
print("\n\n\n\n\n") # Add 5 newlines before starting

import typer

# Create a Typer application instance
# This will be the main entry point for all CLI commands.
app = typer.Typer(
  name="img-ops",
  help="A CLI tool for comparing, analyzing, sorting, and moving images.",
  add_completion=False, # Can be enabled later if desired
  no_args_is_help=True
)

# Placeholder for a simple command
@app.command()
def hello(name: str = "World"):
  """
  A simple hello command to test the CLI setup.
  """
  print(f"Hello {name} from img-ops CLI!")

# Import and register command groups/modules here
# For example:
# from .commands import analyze, compare
# app.add_typer(analyze.app, name="analyze")
# app.add_typer(compare.app, name="compare")

if __name__ == "__main__":
  app()