# Task: A file information cache manager with SQLite




In src/core, implement a sqlite file information cache manager - `file_info_cache.py`.

Use/create the sqlite db `./db/file_info_cache.db`

The cache should be keyed by the full file path/name

The cache should store metadata about the file/path - initially `phash` value, but allow for additional metadata properties in future.

The cache manager should also store the file creation date/time & file size, for cache invalidation.

The cache manager should accept a request for file metadata with the file path and metadata field value requested (ex, `phash`).

The cache manager should use the submitted file path to retrieve the file creation date and size from the file system.

The cache manager should then check the `file_info_cache.db` for the file path, creation date, and size.





