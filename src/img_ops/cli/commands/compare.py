"""
CLI commands related to image comparison.
"""
import typer
from typing_extensions import Annotated
from typing import List

# Create a Typer app for the 'compare' command group
app = typer.Typer(name="compare", help="Compare images based on various criteria.")

@app.command("checksum")
def compare_checksums(
    files: Annotated[List[str], typer.Argument(help="Two or more image files to compare by checksum.")]
):
  """
  Compares images based on their checksums (e.g., MD5, SHA256).
  """
  if len(files) < 2:
    print("Error: At least two files are required for comparison.")
    raise typer.Exit(code=1)
  print(f"Placeholder: Comparing checksums for files: {', '.join(files)}")
  # Future implementation:
  # - Use core.file_system to read files
  # - Use core.comparison (or a utility) to calculate checksums and compare

@app.command("phash")
def compare_phashes(
    file1: Annotated[str, typer.Argument(help="Path to the first image file.")],
    file2: Annotated[str, typer.Argument(help="Path to the second image file.")]
):
  """
  Compares two images using perceptual hashing.
  """
  print(f"Placeholder: Comparing perceptual hashes for '{file1}' and '{file2}'")
  # Future implementation:
  # - Use core.image_processing or core.comparison for pHash generation and diff

if __name__ == "__main__":
  app()