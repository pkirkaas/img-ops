"""
Core library for image hashing and similarity functions.
"""

import os
from PIL import Image
import imagehash
from typing import Union, Literal, Any
# from .file_system import is_valid_image_file # Removed as it's not implemented/used

ReturnFormat = Literal['object', 'hex', 'int']


def img_phash(img: Union[str, Image.Image], return_format: ReturnFormat = 'int', hash_size: int = 8) -> Union[imagehash.ImageHash, str, int]:
    """
    Generates a perceptual hash (phash) for an image.

    The input can be either a file path to an image or a PIL Image object.
    The function computes its perceptual hash using the imagehash library.

    Args:
      img: The file path to the image (str) or a PIL Image object.
      return_format: The desired format for the returned hash.
                     'object' returns the imagehash.ImageHash object.
                     'hex' returns the hexadecimal string representation of the hash.
                     'int' (default) returns the integer representation of the hash.
      hash_size: The size of the hash to compute. Default is 8 (64-bit hash).
                 The resulting hash will have hash_size * hash_size bits.

    Returns:
      An imagehash.ImageHash object, its hexadecimal string representation, or its integer representation,
      based on the return_format argument.

    Raises:
      FileNotFoundError: If img is a path and does not point to a valid file.
      TypeError: If img is not a string path or a PIL.Image.Image object.
      PIL.UnidentifiedImageError: If the file at img (if path) is not a recognizable image format,
                                   or if the provided Image object is invalid.
      ValueError: If an invalid return_format is specified.

    Example:
      ```python
      from PIL import Image
      # Assuming 'path/to/image.jpg' is a valid image file
      try:
          # Using file path
          hash_int = img_phash("path/to/image.jpg") # Default return_format is 'int'
          print(f"The phash integer: {hash_int}")

          hash_obj = img_phash("path/to/image.jpg", return_format='object')
          print(f"The phash object: {hash_obj}")

          hash_hex = img_phash("path/to/image.jpg", return_format='hex')
          print(f"The phash hex string: {hash_hex}")

          # Using PIL Image object
          pil_img = Image.open("path/to/image.jpg")
          hash_int_from_obj = img_phash(pil_img, return_format='int')
          print(f"The phash integer from PIL object: {hash_int_from_obj}")

      except FileNotFoundError:
          print("Error: Image file not found.")
      except TypeError as te:
          print(f"Type Error: {te}")
      except ValueError as ve:
          print(f"Value Error: {ve}")
      except Exception as e:
          print(f"An error occurred: {e}")
      ```
    """
    image_input = None
    input_source_for_error_msg = ""

    if isinstance(img, str):
        input_source_for_error_msg = img
        if not os.path.exists(img):
            raise FileNotFoundError(f"Error: Image file not found at '{img}'")
        # Optional: Add more robust validation using a utility like is_valid_image_file
        # if not is_valid_image_file(img): # This function would check extensions etc.
        #     raise ValueError(f"Error: File at '{img}' is not a valid image file or unsupported format.")
        try:
            image_input = Image.open(img)
        except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
            raise FileNotFoundError(f"Error: Image file not found at '{img}'")
        except Exception as e: # Catch other PIL errors, e.g., UnidentifiedImageError
            raise type(e)(f"Error processing image at '{img}': {e}")

    elif isinstance(img, Image.Image):
        image_input = img
        input_source_for_error_msg = "PIL.Image.Image object"
    else:
        raise TypeError(
            "Input 'img' must be a file path (str) or a PIL.Image.Image object."
        )

    if image_input is None: # Should not happen if logic above is correct
        raise ValueError("Could not load image from provided input.")

    try:
        hash_object = imagehash.phash(image_input, hash_size=hash_size)
    except Exception as e:
        raise RuntimeError(f"Error generating phash for '{input_source_for_error_msg}': {e}")


    if return_format == 'object':
        return hash_object
    elif return_format == 'hex':
        return phash_to_hex(hash_object)
    elif return_format == 'int':
        return phash_to_int(hash_object)
    else:
        raise ValueError(
            f"Invalid return_format: '{return_format}'. Must be 'object', 'hex', or 'int'.")


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
        raise TypeError(
            "hash1 must be an imagehash.ImageHash object or a hex string.")

    if isinstance(hash2, str):
        h2_obj = hex_to_phash(hash2)
    elif isinstance(hash2, imagehash.ImageHash):
        h2_obj = hash2
    else:
        raise TypeError(
            "hash2 must be an imagehash.ImageHash object or a hex string.")

    # The Hamming distance is the number of bits that are different.
    # imagehash objects overload the subtraction operator to calculate Hamming distance.
    hamming_distance = h1_obj - h2_obj

    # phash typically generates a 64-bit hash.
    # The length of the hash array (bool array) gives the number of bits.
    hash_length = len(hash1.hash) if hasattr(
        hash1, 'hash') and isinstance(hash1.hash, list) else 64
    if hash_length == 0:  # Should not happen with valid imagehash objects
        return 0.0

    # Normalize the similarity: 1.0 for identical, 0.0 for maximum difference.
    similarity = 1.0 - (hamming_distance / hash_length)
    # Ensure value is strictly between 0 and 1
    return max(0.0, min(similarity, 1.0))


def phash_to_int(phash: imagehash.ImageHash) -> int:
    """
    Converts an imagehash.ImageHash object to its integer representation.

    Args:
      phash: The imagehash.ImageHash object to convert.

    Returns:
      An integer representing the hash value.

    Raises:
      TypeError: If input is not an imagehash.ImageHash object.

    Example:
      ```python
      # Assuming hash_val is an ImageHash object
      # hash_val = img_phash("image.jpg", return_format='object')
      # int_representation = phash_to_int(hash_val)
      # print(f"Integer value: {int_representation}")
      ```
    """
    if not isinstance(phash, imagehash.ImageHash):
        raise TypeError("Input must be an imagehash.ImageHash object.")
    # The string representation of an ImageHash is its hex value.
    # Convert this hex string to an integer.
    return int(str(phash), 16)


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
    except Exception as e:  # Catch potential errors from imagehash.hex_to_hash
        raise ValueError(
            f"Invalid hexadecimal string for hash: '{hex_string}'. Error: {e}")


def hamming_distance(hash1: Any, hash2: Any, hash_size: int = 64) -> int:
    """
    Calculates the Hamming distance between two perceptual hashes.

    The inputs can be imagehash.ImageHash objects, hexadecimal strings, or integers.
    The function converts both inputs to integers before calculating the Hamming distance.
    The Hamming distance is the number of bit positions at which the corresponding bits are different.

    Args:
      hash1: The first perceptual hash (ImageHash, hex string, or int).
      hash2: The second perceptual hash (ImageHash, hex string, or int).
      hash_size: The bit length of the hashes. Default is 64 (for an 8x8 phash).
                 This is used to validate the range of the result.

    Returns:
      An integer representing the Hamming distance (number of differing bits).
      The value will be between 0 and hash_size.

    Raises:
      TypeError: If inputs are of unsupported types.
      ValueError: If string inputs cannot be converted to valid hashes or if integer
                  hashes seem to be out of typical range (though this is not strictly checked).

    Example:
      ```python
      h_obj = img_phash("image1.jpg", return_format='object')
      h_hex = img_phash("image2.jpg", return_format='hex')
      h_int = img_phash("image3.jpg", return_format='int')

      dist1 = hamming_distance(h_obj, h_hex)
      print(f"Distance (obj vs hex): {dist1}")

      dist2 = hamming_distance(h_int, "a1b2c3d4e5f60718") # Assuming a 64-bit hex
      print(f"Distance (int vs hex string): {dist2}")

      dist3 = hamming_distance(0xabcdef0123456789, 0xabcdef0123456788) # 1 bit diff
      print(f"Distance (int vs int): {dist3}") # Expected: 1

      # Example with known ImageHash objects
      # hash_a = imagehash.hex_to_hash('b79a37f037f037f0')
      # hash_b = imagehash.hex_to_hash('b79a37f037f037f1') # 1 bit difference
      # print(f"Known Hamming Distance: {hamming_distance(hash_a, hash_b)}") # Expected: 1
      ```
    """
    int_hash1: int
    int_hash2: int

    # Convert hash1 to integer
    if isinstance(hash1, imagehash.ImageHash):
        int_hash1 = phash_to_int(hash1)
    elif isinstance(hash1, str):
        try:
            # Ensure it's a valid hex string for a hash before converting
            # imagehash.hex_to_hash(hash1) # This validates format/length implicitly
            int_hash1 = int(hash1, 16)
        except ValueError:
            raise ValueError(f"Invalid hex string for hash1: '{hash1}'")
    elif isinstance(hash1, int):
        int_hash1 = hash1
    else:
        raise TypeError(f"Unsupported type for hash1: {type(hash1)}. Must be ImageHash, hex string, or int.")

    # Convert hash2 to integer
    if isinstance(hash2, imagehash.ImageHash):
        int_hash2 = phash_to_int(hash2)
    elif isinstance(hash2, str):
        try:
            # imagehash.hex_to_hash(hash2) # Validation
            int_hash2 = int(hash2, 16)
        except ValueError:
            raise ValueError(f"Invalid hex string for hash2: '{hash2}'")
    elif isinstance(hash2, int):
        int_hash2 = hash2
    else:
        raise TypeError(f"Unsupported type for hash2: {type(hash2)}. Must be ImageHash, hex string, or int.")

    # Calculate Hamming distance using bitwise XOR and counting set bits
    distance = bin(int_hash1 ^ int_hash2).count('1')

    # Ensure the distance is within the expected range [0, hash_size]
    if not (0 <= distance <= hash_size):
        # This case should ideally not be reached if inputs are valid phashes of 'hash_size' bits.
        # It might indicate an issue with hash_size parameter or unexpected hash values.
        # For robustness, clamp or raise error. Here, we'll just note it.
        # Consider if strict clamping `max(0, min(distance, hash_size))` is needed
        # or if an error should be raised for out-of-range results.
        # Given the calculation, it should naturally fall within this range if inputs are correct.
        pass # Or: raise ValueError(f"Calculated distance {distance} is out of expected range [0, {hash_size}]")

    return distance
