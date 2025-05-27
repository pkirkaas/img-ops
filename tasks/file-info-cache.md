# Task: A file information cache manager with SQLite

In src/core, implement a sqlite file information cache manager class - `file_info_cache.py`.

Below is my proposed design for the cache manager - evaluate this design, suggest improvements, and implement it if you are satisfied.

The cache manager should be keyed by a full file system path.
The cache manager should retain the file size and modification date for cache invalidations
The cache manager should implement the method `get_phash(filePath)` and return the phash for the file path
If the cache manager does not have an entry corresponding to the file path:
  - It should generate a phash string for the file as implemented by `img_phash`
  - It should create a new cache entry for the file, with modification date and size, and save the generated phash string
  - It should then return the new calculated phash value string

If the cache manager has an entry corresponding to the file path:
 - it should check the modification date and size of the file path with the values cached.
 - If the date or size has changed, or if there is no phash value, the cache manager should generate a phash value, store it in the cache, and return the phash string

The cache manager should also provide cache-wide utility methods:
- clear_cache - clear/empty the cache
- clean_cache - Iterate though all the entries in the cache, checking for file paths that no longer exist, or file path entries that have different modification dates or size from the cached values, and remove them.

Use/create the sqlite db `./db/file_info_cache.db`






