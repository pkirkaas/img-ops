The task is to implement an Application Configuration that can save and restore the application settings to a local YAML text file.

We will use `pydantic` to specify & validate the configuration data, and `pyyaml` to read/write the configuration to a local file.

Use pydantic to specify the structure of a configuration object, and validate a python object according to the pydantic schema.

The text description of the configuration schema follows. If there is any question, ambiguity, clarification, or if you have suggestions to improve, ask and suggest.

When you are satisfied the requirements for the config schema are clear and correct, create the `app_config` class in `src/core` with complete implementation, including validation, error checking, reading/writing to file system, etc

The app_config class should support operations on the configuration, for example adding or removing file paths
Also should provide validation of the paths to ensure no duplicate entries, etc

Each config instance should have a default if no value specified

## App Config Description
The actual app config implementation should support multiple named application configurations. Each app config should support:

name: The name of the configuration - default: "MyConf"
description: Description of the configuration - default: "MyConf desc"
paths: A list of file paths - default: empty list
method: similarity comparison method (phash, ssim, orb, etc) - default: phash
percent: Percent similarity to filter by - between 0-100 - default: 90%



