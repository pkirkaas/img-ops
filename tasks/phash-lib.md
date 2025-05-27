Specification: A core library `src/core/img_similarity.py` that provides image hashing and similarity functions.

Using the python library `imagehash` and other supporting libraries (Pillow, etc), implement a function `img_phash` that accepts a file path of an image, and generates a phash value for the image.

The img_phash function should use utilities provided by the `imagehash` library to normalize the image and execute the phash function on the normalized image.

The `img_similarity.py` file should also implement a similarity comparison `img_sim` function that accepts 2 phash values and calculates the similarity between the two using hamming distance and other tools. The result should be normalized to a floating point number between 0 (no similarity) and 1 (complete similarity)