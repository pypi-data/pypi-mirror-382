"""
Constants used throughout the simple_config package.

This module defines all the constants used throughout the simple_config package.
These constants help maintain consistency and avoid magic values in the codebase.

Constants are organized into logical groups:
- File extensions: Supported file formats for configuration files
- Environment variable patterns: Regex patterns for environment variable substitution
- Registry names: Default registry names and identifiers
- Error messages: Standardized error messages for consistent error handling

Example:
    >>> from simple_config.constants import YAML_EXTENSIONS, DEFAULT_REGISTRY_NAME
    >>> print(YAML_EXTENSIONS)  # ['.yaml', '.yml']
    >>> print(DEFAULT_REGISTRY_NAME)  # 'default'
"""

# File extensions
YAML_EXTENSIONS = [".yaml", ".yml"]
JSON_EXTENSION = ".json"

# Environment variable patterns
ENV_VAR_PATTERN = r"\$\{([^}]+)\}"

# Registry names
DEFAULT_REGISTRY_NAME = "default"

# Error messages
COMPONENT_NOT_FOUND_MSG = "Component '{}' not found in registry '{}'"
DUPLICATE_COMPONENT_MSG = "Component '{}' already registered in registry '{}'"
KEY_NOT_ALLOWED_MSG = "Key '{}' is not allowed. Allowed keys: {}"
CANNOT_ADD_KEY_MSG = "Cannot add new key '{}' to frozen config"
CONFIG_FILE_NOT_FOUND_MSG = "Configuration file not found: {}"
UNSUPPORTED_FILE_FORMAT_MSG = "Unsupported file format: {}"
UNSUPPORTED_FORMAT_MSG = "Unsupported format: {}"
