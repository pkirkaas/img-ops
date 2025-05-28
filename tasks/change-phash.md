We will make several simultaneous modifications in several files, so they can continue to work together.

We are changing from storing phash values as hex strings to storing them as integers; also in the `file_info_cache.py`  which will also require the DB schema to be changed, requires flushing the current DB cache, updated all other files that use phash value

We will change the implementation in `img_similarity.py`, and change the format of the phash data stored in the cache db in `file_info_cache.py` as follows:

We will store and compare phash values as integers rather than hex strings, but continue to support hex strings. 

We will also make the `img_phash` function more robust & flexible
The first param to `img_phash` will be called 'img' - this can be either a PIL Image instance, or a valid image file path that is converted to an Image instance with Image.open(fpath)

If the img arg is a string, verify it represents an existing file in the file system, with a valid image extension.

The second, optional param return_format will accept a new, additional default format - "int" to return the integer value of the phash.

It is the new integer value for phash that will be stored in the cache db now, not the hex string.

Also, create a new function `hamming_distance` that returns the hamming distance of two phashes.

It will accept 2 parameters for phashes to compare - but each parameter can be of type any of int,str, or ImageHash

Each parameter will be converted to an integer, and the simple hamming distance function will be:

```py
    return bin(hash1 ^ hash2).count('1')
```

The return value must be an integer between 0 and hash_size (64)

Ignore the function `img_sim` for now, I will manually edit it.

Please be very careful with the refactoring, as there are other files and configurations built around storing the phash value as string rather than int. This isn't a difficult change to implement, but it has to be done carefully and thoroughly









