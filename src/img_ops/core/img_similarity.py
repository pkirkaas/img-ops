"""
Core library for image hashing and similarity functions.
"""

from PIL import Image
import imagehash
from typing import Union, Literal

ReturnFormat = Literal['object', 'hex']

def img_phash(image_path: str, return_format: ReturnFormat = 'hex') -> Union[imagehash.ImageHash, str]:
  """
  Generates a perceptual hash (phash) for an image.

  This function uses the imagehash library to open an image,
  normalize it (implicitly done by the phash function), and
  compute its perceptual hash.

  Args:
    image_path: The file path to the image.
    return_format: The desired format for the returned hash.
                   'object' returns the imagehash.ImageHash object.
                   'hex' (default) returns the hexadecimal string representation of the hash.

  Returns:
    Either an imagehash.ImageHash object or its hexadecimal string representation,
    based on the return_format argument.

  Raises:
    FileNotFoundError: If the image_path does not point to a valid file.
    PIL.UnidentifiedImageError: If the file at image_path is not a recognizable image format.
    ValueError: If an invalid return_format is specified.

  Example:
    ```python
    try:
      hash_obj = img_phash("path/to/image.jpg", return_format='object')
      print(f"The phash object: {hash_obj}")
      hash_hex = img_phash("path/to/image.jpg", return_format='hex')
      print(f"The phash hex string: {hash_hex}")
      # Default is hex
      default_hash_hex = img_phash("path/to/image.jpg")
      print(f"Default phash hex string: {default_hash_hex}")
    except FileNotFoundError:
      print("Error: Image file not found.")
    except Exception as e:
      print(f"An error occurred: {e}")
    ```
  """
  try:
    img = Image.open(image_path)
    hash_object = imagehash.phash(img)
  except FileNotFoundError:
    raise FileNotFoundError(f"Error: Image file not found at '{image_path}'")
  except Exception as e: # Catch other PIL errors, e.g., UnidentifiedImageError
    raise type(e)(f"Error processing image at '{image_path}': {e}")

  if return_format == 'object':
    return hash_object
  elif return_format == 'hex':
    return phash_to_hex(hash_object)
  else:
    raise ValueError(f"Invalid return_format: '{return_format}'. Must be 'object' or 'hex'.")


def img_sim(hash1: Union[imagehash.ImageHash, str], hash2: Union[imagehash.ImageHash, str]) -> float:
  """
  Calculates the similarity between two perceptual hashes.

  The inputs can be either imagehash.ImageHash objects or their hexadecimal string representations.
  The similarity is determined using the Hamming distance between the two hashes.
  The result is normalized to a floating-point number between 0.0 (no similarity)
  and 1.0 (complete similarity/identical hashes).

  Args:
    hash1: The first perceptual hash, as an imagehash.ImageHash object or hex string.
    hash2: The second perceptual hash, as an imagehash.ImageHash object or hex string.

  Returns:
    A float between 0.0 and 1.0, where 1.0 means the images are
    perceptually identical, and 0.0 means they are completely different.

  Raises:
    TypeError: If inputs are not imagehash.ImageHash objects or strings.
    ValueError: If string inputs cannot be converted to valid ImageHash objects.

  Example:
    ```python
    # Using ImageHash objects
    h_obj1 = img_phash("image1.jpg", return_format='object')
    h_obj2 = img_phash("image2.jpg", return_format='object')
    similarity1 = img_sim(h_obj1, h_obj2)
    print(f"Similarity (objects): {similarity1:.2f}")

    # Using hex strings
    h_hex1 = img_phash("image1.jpg", return_format='hex')
    h_hex2 = img_phash("image3.jpg", return_format='hex')
    similarity2 = img_sim(h_hex1, h_hex2)
    print(f"Similarity (hex strings): {similarity2:.2f}")

    # Using mixed types
    similarity3 = img_sim(h_obj1, h_hex2)
    print(f"Similarity (mixed): {similarity3:.2f}")

    # Example with known hashes
    hex_str1 = 'b79a37f037f037f0'
    hex_str2 = 'b79a37f037f037f1' # 1 bit difference
    obj_hash1 = hex_to_phash(hex_str1)
    similarity_known = img_sim(obj_hash1, hex_str2)
    # Expected similarity: 1 - (1/64) = 0.984375
    print(f"Known Similarity: {similarity_known}")
    ```
  """
  # Convert inputs to ImageHash objects if they are strings
  if isinstance(hash1, str):
    h1_obj = hex_to_phash(hash1)
  elif isinstance(hash1, imagehash.ImageHash):
    h1_obj = hash1
  else:
    raise TypeError("hash1 must be an imagehash.ImageHash object or a hex string.")

  if isinstance(hash2, str):
    h2_obj = hex_to_phash(hash2)
  elif isinstance(hash2, imagehash.ImageHash):
    h2_obj = hash2
  else:
    raise TypeError("hash2 must be an imagehash.ImageHash object or a hex string.")

  # The Hamming distance is the number of bits that are different.
  # imagehash objects overload the subtraction operator to calculate Hamming distance.
  hamming_distance = h1_obj - h2_obj

  # phash typically generates a 64-bit hash.
  # The length of the hash array (bool array) gives the number of bits.
  hash_length = len(hash1.hash) if hasattr(hash1, 'hash') and isinstance(hash1.hash, list) else 64
  if hash_length == 0: # Should not happen with valid imagehash objects
      return 0.0

  # Normalize the similarity: 1.0 for identical, 0.0 for maximum difference.
  similarity = 1.0 - (hamming_distance / hash_length)
  return max(0.0, min(similarity, 1.0)) # Ensure value is strictly between 0 and 1


def phash_to_hex(phash: imagehash.ImageHash) -> str:
  """
  Converts an imagehash.ImageHash object to its hexadecimal string representation.

  This is useful for storing the hash in a database or a text file.

  Args:
    phash: The imagehash.ImageHash object to convert.

  Returns:
    A string representing the hexadecimal value of the hash.

  Example:
    ```python
    # Assuming hash_val is an ImageHash object
    # hash_val = img_phash("image.jpg")
    # hex_representation = phash_to_hex(hash_val)
    # print(f"Hex string: {hex_representation}")
    #
    # # Example with a known hash
    # h = imagehash.hex_to_hash('b79a37f037f037f0')
    # print(phash_to_hex(h)) # Output: b79a37f037f037f0
    ```
  """
  if not isinstance(phash, imagehash.ImageHash):
    raise TypeError("Input must be an imagehash.ImageHash object.")
  return str(phash)


def hex_to_phash(hex_string: str) -> imagehash.ImageHash:
  """
  Converts a hexadecimal string representation back into an imagehash.ImageHash object.

  This is useful for retrieving a hash stored as a string (e.g., from a database)
  and converting it back to an ImageHash object for comparison.

  Args:
    hex_string: The hexadecimal string to convert.

  Returns:
    An imagehash.ImageHash object.

  Raises:
    TypeError: If the hex_string is not a string.
    ValueError: If the hex_string is not a valid hexadecimal hash string
                (e.g., invalid characters, incorrect length for typical hashes).

  Example:
    ```python
    # hex_str = "b79a37f037f037f0" # A valid hex string for a phash
    # image_hash_object = hex_to_phash(hex_str)
    # print(image_hash_object)
    #
    # try:
    #   invalid_hash = hex_to_phash("not_a_hex_string")
    # except ValueError as e:
    #   print(f"Error: {e}")
    ```
  """
  if not isinstance(hex_string, str):
    raise TypeError("Input must be a string.")
  try:
    return imagehash.hex_to_hash(hex_string)
  except Exception as e: # Catch potential errors from imagehash.hex_to_hash
    raise ValueError(f"Invalid hexadecimal string for hash: '{hex_string}'. Error: {e}")