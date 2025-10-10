"""
Enhanced configuration system inspired by Detectron2.

This module provides a flexible and powerful configuration system that supports:
- Nested configuration access with dot notation
- Environment variable substitution
- Key protection and configuration freezing
- Multiple file format support (YAML, JSON)
- Type-safe configuration handling

The main classes are:
- ConfigNode: A nested configuration container with attribute access
- Config: A configuration manager with file I/O capabilities

Example:
    >>> cfg = Config({'model': {'name': 'resnet50', 'layers': 50}})
    >>> print(cfg.model.name)  # 'resnet50'
    >>> print(cfg.model.layers)  # 50
"""

import os
import yaml
import json
import time
from typing import Any, Dict, Union, Optional, Set, List, Callable
from pathlib import Path
from .constants import (
    YAML_EXTENSIONS,
    JSON_EXTENSION,
    CONFIG_FILE_NOT_FOUND_MSG,
    UNSUPPORTED_FILE_FORMAT_MSG,
    UNSUPPORTED_FORMAT_MSG,
    KEY_NOT_ALLOWED_MSG,
    CANNOT_ADD_KEY_MSG,
)
from .exceptions import (
    ConfigKeyError,
    ConfigFileNotFoundError,
    UnsupportedFileFormatError,
    EnvironmentVariableError,
    CircularDependencyError,
    ConfigValidationError,
    ConfigLintError,
    ConfigError,
)


class ConfigNode:
    """
    A configuration node that supports nested access and key protection.

    This class provides a dictionary-like interface with attribute access for
    configuration data. It supports nested configurations, environment variable
    substitution, and key protection mechanisms.

    Inspired by Detectron2's CfgNode but simplified for general use.

    Attributes:
        _data (Dict[str, Any]): The underlying configuration data
        _frozen (bool): Whether the configuration is frozen (read-only)
        _allowed_keys (Set[str]): Set of allowed keys when frozen

    Example:
        >>> node = ConfigNode({'model': {'name': 'resnet50'}})
        >>> print(node.model.name)  # 'resnet50'
        >>> node.freeze()
        >>> node.new_key = 'value'  # Raises ConfigKeyError
    """

    def __init__(self, data: Dict[str, Any] = None, frozen: bool = False):
        """
        Initialize a ConfigNode with optional data and freeze state.

        Args:
            data: Dictionary containing configuration data. Environment variables
                  in the format ${VAR_NAME} or ${VAR_NAME:default_value} will be
                  automatically substituted.
            frozen: Whether this configuration should be frozen (read-only).
                   Frozen configs prevent addition of new keys.

        Example:
            >>> node = ConfigNode({'host': '${DB_HOST:localhost}'})
            >>> # Environment variable DB_HOST will be substituted
        """
        # Substitute environment variables in the data
        processed_data = _substitute_env_vars(data or {})
        self._data = processed_data
        self._frozen = frozen
        self._allowed_keys: Set[str] = set()

    def __getattr__(self, key: str) -> Any:
        """
        Allow attribute access for configuration keys.

        This method enables dot notation access to configuration values.
        If a key contains a dictionary, it returns a new ConfigNode for
        nested access. Missing keys return empty ConfigNodes to allow chaining.

        Args:
            key: The configuration key to access

        Returns:
            The configuration value, or a ConfigNode for nested access,
            or an empty ConfigNode for missing keys

        Example:
            >>> node = ConfigNode({'model': {'name': 'resnet50'}})
            >>> print(node.model.name)  # 'resnet50'
            >>> print(node.missing.nested.key)  # Empty ConfigNode (no error)
        """
        if key.startswith("_"):
            return super().__getattribute__(key)

        if key in self._data:
            value = self._data[key]
            if isinstance(value, dict):
                return ConfigNode(value, self._frozen)
            return value

        # Return empty ConfigNode for missing keys to allow chaining
        return ConfigNode(frozen=self._frozen)

    def __dir__(self):
        """
        Return directory listing including data keys.

        This method enables tab completion in interactive environments
        by including configuration keys in the directory listing.

        Returns:
            Sorted list of available attributes and configuration keys
        """
        attrs = set(super().__dir__())
        attrs.update(self._data.keys())
        return sorted(attrs)

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Control attribute setting based on frozen state and allowed keys.

        This method handles setting configuration values with protection
        against adding new keys to frozen configurations. It automatically
        converts dictionaries to ConfigNode instances for nested access.

        Args:
            key: The configuration key to set
            value: The value to set for the key

        Raises:
            ConfigKeyError: If trying to add a new key to a frozen config
                          or if the key is not in the allowed keys set
        """
        if key.startswith("_"):
            super().__setattr__(key, value)
            return

        if self._frozen:
            if self._allowed_keys and key not in self._allowed_keys:
                raise ConfigKeyError(
                    KEY_NOT_ALLOWED_MSG.format(key, sorted(self._allowed_keys))
                )
            if key not in self._data:
                raise ConfigKeyError(CANNOT_ADD_KEY_MSG.format(key))

        if isinstance(value, dict) and not isinstance(value, ConfigNode):
            value = ConfigNode(value, self._frozen)

        self._data[key] = value

    def __getitem__(self, key: str) -> Any:
        """
        Allow dictionary-style access to configuration values.

        This method enables bracket notation for accessing configuration
        values, making the ConfigNode behave like a dictionary.

        Args:
            key: The configuration key to access

        Returns:
            The configuration value or a ConfigNode for nested access
        """
        return self.__getattr__(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Allow dictionary-style assignment of configuration values.

        This method enables bracket notation for setting configuration
        values, making the ConfigNode behave like a dictionary.

        Args:
            key: The configuration key to set
            value: The value to set for the key
        """
        self.__setattr__(key, value)

    def __contains__(self, key: str) -> bool:
        """
        Check if key exists in configuration.

        This method enables the 'in' operator to check for key existence.

        Args:
            key: The key to check for existence

        Returns:
            True if the key exists, False otherwise
        """
        return key in self._data

    def __repr__(self) -> str:
        """
        Return string representation of the ConfigNode.

        Returns:
            String representation showing the configuration data
        """
        return f"ConfigNode({self._data})"

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value with default. Supports dot notation.

        This method provides safe access to configuration values with
        support for dot notation to access nested values. It returns
        a default value if the key doesn't exist.

        Args:
            key: The configuration key to retrieve (supports dot notation)
            default: Default value to return if key doesn't exist

        Returns:
            The configuration value, or default if key doesn't exist
        """
        if "." in key:
            # Handle dot notation
            parts = key.split(".")
            current = self
            for part in parts:
                if isinstance(current, ConfigNode):
                    if part in current._data:
                        value = current._data[part]
                        if isinstance(value, dict):
                            current = ConfigNode(value, self._frozen)
                        else:
                            current = value
                    else:
                        return default
                else:
                    return default
            return current
        else:
            # Handle simple key
            if key in self._data:
                value = self._data[key]
                if isinstance(value, dict):
                    return ConfigNode(value, self._frozen)
                return value
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        This method provides an alternative way to set configuration values
        using the set method instead of attribute assignment.

        Args:
            key: The configuration key to set
            value: The value to set for the key
        """
        self.__setattr__(key, value)

    def update(self, other: Union[Dict, "ConfigNode"]) -> None:
        """
        Update with another dictionary or ConfigNode.

        This method merges configuration data from another source into
        this ConfigNode. Nested dictionaries are handled intelligently
        by creating ConfigNode instances for nested access.

        Args:
            other: Dictionary or ConfigNode to merge data from
        """
        if isinstance(other, ConfigNode):
            other = other._data

        for key, value in other.items():
            if isinstance(value, dict):
                if key in self._data and isinstance(
                    self._data[key], ConfigNode
                ):
                    self._data[key].update(value)
                else:
                    self._data[key] = ConfigNode(value, self._frozen)
            else:
                self._data[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        This method converts the ConfigNode and all nested ConfigNodes
        back to regular Python dictionaries.

        Returns:
            Dictionary representation of the configuration data
        """
        result = {}
        for key, value in self._data.items():
            if isinstance(value, ConfigNode):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    def freeze(self) -> None:
        """
        Freeze the configuration to prevent new keys.

        This method makes the configuration read-only by preventing
        the addition of new keys. Existing keys can still be modified
        unless they are also frozen.
        """
        self._frozen = True
        for value in self._data.values():
            if isinstance(value, ConfigNode):
                value.freeze()

    def defrost(self) -> None:
        """
        Allow modifications to the configuration.

        This method reverses the freeze operation, allowing new keys
        to be added to the configuration again.
        """
        self._frozen = False
        for value in self._data.values():
            if isinstance(value, ConfigNode):
                value.defrost()

    def set_allowed_keys(self, keys: Set[str]) -> None:
        """
        Set allowed keys for frozen configuration.

        This method specifies which keys are allowed to be modified
        when the configuration is frozen. Only these keys can be
        changed after freezing.

        Args:
            keys: Set of keys that are allowed to be modified
        """
        self._allowed_keys = keys

    def set_nested(self, key_path: str, value: Any) -> None:
        """
        Set a nested configuration value using dot notation.

        This method allows setting nested values using dot notation,
        which is useful when you need to update deeply nested configuration
        values that can't be accessed directly through attribute assignment.

        Args:
            key_path: Dot-separated path to the nested key (e.g., 'database.host')
            value: The value to set

        Example:
            >>> node = ConfigNode({'database': {'host': 'localhost'}})
            >>> node.set_nested('database.host', 'production.db.com')
            >>> print(node.database.host)  # 'production.db.com'
        """
        if "." in key_path:
            parts = key_path.split(".")
            current = self
            for part in parts[:-1]:
                if part not in current._data:
                    current._data[part] = {}
                if isinstance(current._data[part], dict):
                    current._data[part] = ConfigNode(
                        current._data[part], self._frozen
                    )
                current = current._data[part]
            current._data[parts[-1]] = value
        else:
            self._data[key_path] = value

    def clone(self) -> "ConfigNode":
        """
        Create a deep copy of the configuration.

        This method creates a completely independent copy of the
        configuration that can be modified without affecting the original.

        Returns:
            A new ConfigNode with the same data and freeze state
        """
        return ConfigNode(self.to_dict(), self._frozen)


class Config(ConfigNode):
    """
    Main configuration class with additional utilities.

    This class extends ConfigNode with file I/O capabilities and additional
    configuration management features. It provides methods for loading
    configurations from files and saving them back to disk.

    Example:
        >>> config = Config.from_file('config.yaml')
        >>> config.model.name = 'resnet50'
        >>> config.save('updated_config.yaml')
    """

    def __init__(self, data: Dict[str, Any] = None, frozen: bool = False):
        """
        Initialize a Config instance.

        Args:
            data: Dictionary containing configuration data
            frozen: Whether this configuration should be frozen (read-only)
        """
        super().__init__(data, frozen)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "Config":
        """
        Load configuration from a file with inheritance support.

        This class method creates a Config instance by loading data from
        a YAML or JSON file. The file format is automatically detected
        based on the file extension. Inheritance is always enabled and
        automatically resolves 'extends' keys in configuration files.

        Args:
            file_path: Path to the configuration file

        Returns:
            Config instance loaded from the file with inheritance resolved

        Raises:
            ConfigFileNotFoundError: If the file or inherited file doesn't exist
            CircularDependencyError: If circular inheritance is detected
            UnsupportedFileFormatError: If the file format is not supported

        Example:
            >>> # base_config.yaml
            >>> # model:
            >>> #   name: resnet50
            >>> #   layers: 50
            >>>
            >>> # derived_config.yaml
            >>> # extends: base_config.yaml
            >>> # model:
            >>> #   name: vgg16  # Override base model
            >>>
            >>> config = Config.from_file('derived_config.yaml')
            >>> print(config.model.name)  # 'vgg16'
            >>> print(config.model.layers)  # 50 (inherited)
        """
        loading_trace: List[Dict[str, Any]] = []
        data = load_config(file_path, loading_trace=loading_trace)
        config = cls(data)
        config._loading_trace = loading_trace
        config._file_path = str(file_path)
        return config

    def save(self, file_path: Union[str, Path], format: str = "yaml") -> None:
        """
        Save configuration to a file.

        This method saves the current configuration to a file in the
        specified format (YAML or JSON).

        Args:
            file_path: Path where to save the configuration
            format: File format ('yaml' or 'json')

        Raises:
            UnsupportedFileFormatError: If the format is not supported
            ConfigSerializationError: If serialization fails
        """
        save_config(self, file_path, format)

    def validate_schema(
        self, schema: Dict[str, Any]
    ) -> List[ConfigValidationError]:
        """
        Validate configuration against a schema.

        Args:
            schema: Schema definition with expected types and constraints

        Returns:
            List of validation errors (empty if valid)
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        return debugger.validate_schema(
            schema, getattr(self, "_file_path", None)
        )

    def lint(
        self, rules: Optional[Dict[str, Callable]] = None
    ) -> List[ConfigLintError]:
        """
        Lint configuration for common issues and best practices.

        Args:
            rules: Custom linting rules (optional)

        Returns:
            List of linting errors and warnings
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        return debugger.lint(rules)

    def diff_with_file(self, other_file: Union[str, Path]) -> Dict[str, Any]:
        """
        Compare configuration with another file.

        Args:
            other_file: Path to the other configuration file

        Returns:
            Dictionary showing differences
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        return debugger.diff_with_file(other_file)

    def visualize(self, max_depth: int = 3) -> str:
        """
        Create a visual representation of the configuration structure.

        Args:
            max_depth: Maximum depth to visualize

        Returns:
            String representation of the configuration tree
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        return debugger.visualize(max_depth)

    def inspect(self, path: str) -> Dict[str, Any]:
        """
        Get detailed information about a configuration section.

        Args:
            path: Dot-separated path to the section

        Returns:
            Dictionary with section information
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        return debugger.inspect(path)

    def explore(self) -> None:
        """
        Start an interactive configuration explorer.
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        debugger.explore()

    def test(self, test_cases: Dict[str, Callable]) -> Dict[str, Any]:
        """
        Test configuration against custom test cases.

        Args:
            test_cases: Dictionary mapping paths to test functions

        Returns:
            Dictionary with test results
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        return debugger.test(test_cases)

    def mock(self, overrides: Dict[str, Any]) -> "Config":
        """
        Create a mocked version of the configuration for testing.

        Args:
            overrides: Dictionary of values to override

        Returns:
            New Config instance with mocked configuration
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        mocked_debugger = debugger.mock(overrides)
        return mocked_debugger.config  # type: ignore[return-value]

    def generate_docs(self, output_path: Union[str, Path]) -> None:
        """
        Generate documentation for the configuration.

        Args:
            output_path: Path to save the documentation
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        debugger.generate_docs(output_path)

    def generate_ide_support(self, output_path: Union[str, Path]) -> None:
        """
        Generate IDE support files for autocomplete.

        Args:
            output_path: Path to save the .pyi file
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        debugger.generate_ide_support(output_path)

    def generate_vscode_config(self, output_path: Union[str, Path]) -> None:
        """
        Generate VS Code configuration for validation.

        Args:
            output_path: Path to save the VS Code settings
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        debugger.generate_vscode_config(output_path)

    def profile(self) -> Dict[str, Any]:
        """
        Profile configuration loading and memory usage.

        Returns:
            Dictionary with performance metrics
        """
        from .debug import ConfigDebugger

        debugger = ConfigDebugger(self)
        return debugger.profile()

    def get_loading_trace(self) -> List[Dict[str, Any]]:
        """
        Get the loading trace for configuration inheritance.

        Returns:
            List of loading steps with file paths and timestamps
        """
        return getattr(self, "_loading_trace", [])


def load_config(
    file_path: Union[str, Path],
    visited: Optional[Set[str]] = None,
    loading_trace: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Load configuration from a file with inheritance support.

    This function loads a configuration file and automatically resolves
    inheritance using the 'extends' key. It supports both relative and
    absolute paths for inherited configurations.

    Args:
        file_path: Path to configuration file (YAML or JSON)
        visited: Set of already visited files to detect circular dependencies
        loading_trace: List to track loading steps for debugging

    Returns:
        Configuration data as dictionary with inheritance resolved

    Raises:
        ConfigFileNotFoundError: If the configuration file or inherited file is not found
        CircularDependencyError: If circular inheritance is detected
        UnsupportedFileFormatError: If the file format is not supported

    Example:
        # base_config.yaml
        model:
          name: resnet50
          layers: 50
        training:
          epochs: 100
          lr: 0.001

        # derived_config.yaml
        extends: base_config.yaml
        model:
          name: vgg16  # Override base model
        training:
          lr: 0.01    # Override learning rate
        # epochs will inherit from base (100)
    """
    if visited is None:
        visited = set()
    if loading_trace is None:
        loading_trace = []

    file_path = Path(file_path)
    file_path_str = str(file_path.resolve())

    # Check for circular dependency
    if file_path_str in visited:
        # Find the circular dependency chain
        chain = list(visited) + [file_path_str]
        circular_index = chain.index(file_path_str)
        circular_chain = chain[circular_index:] + [file_path_str]

        raise CircularDependencyError(
            f"Circular dependency detected: {file_path_str}",
            dependency_chain=circular_chain,
            circular_file=file_path_str,
        )

    # Add current file to visited set
    visited.add(file_path_str)

    # Track loading step
    loading_trace.append(
        {
            "file": file_path_str,
            "step": len(loading_trace) + 1,
            "timestamp": time.time(),
        }
    )

    try:
        if not file_path.exists():
            raise ConfigFileNotFoundError(
                CONFIG_FILE_NOT_FOUND_MSG.format(file_path)
            )

        with open(file_path, "r") as f:
            if file_path.suffix.lower() in YAML_EXTENSIONS:
                data = yaml.safe_load(f)
            elif file_path.suffix.lower() == JSON_EXTENSION:
                data = json.load(f)
            else:
                raise UnsupportedFileFormatError(
                    UNSUPPORTED_FILE_FORMAT_MSG.format(file_path.suffix)
                )

        # Substitute environment variables
        data = _substitute_env_vars(data)

        # Check for inheritance
        if "extends" in data:
            extends_path = data["extends"]

            # Resolve the path (support both relative and absolute paths)
            if Path(extends_path).is_absolute():
                base_path = Path(extends_path)
            else:
                base_path = file_path.parent / extends_path

            # Load the base configuration recursively
            base_config = load_config(base_path, visited.copy())

            # Merge configurations (override takes precedence)
            data = deep_merge(base_config, data)

            # Remove the extends key from the final config
            del data["extends"]

        return data

    except Exception as e:
        if isinstance(
            e,
            (
                ConfigFileNotFoundError,
                UnsupportedFileFormatError,
                CircularDependencyError,
                EnvironmentVariableError,
            ),
        ):
            raise
        raise ConfigError(f"Failed to load configuration with inheritance: {e}")
    finally:
        # Remove current file from visited set
        visited.discard(file_path_str)


def save_config(
    config: Union[Config, ConfigNode],
    file_path: Union[str, Path],
    format: str = "yaml",
) -> None:
    """
    Save configuration to a file.

    Args:
        config: Config or ConfigNode object to save
        file_path: Path to save configuration file
        format: File format ('yaml' or 'json')
    """
    file_path = Path(file_path)
    data = config.to_dict()

    with open(file_path, "w") as f:
        if format.lower() == "yaml":
            yaml.dump(data, f, default_flow_style=False, indent=2)
        elif format.lower() == "json":
            json.dump(data, f, indent=2)
        else:
            raise UnsupportedFileFormatError(
                UNSUPPORTED_FORMAT_MSG.format(format)
            )


def _substitute_env_vars(data: Any) -> Any:
    """
    Recursively substitute environment variables in configuration data.

    Environment variables should be referenced as ${VAR_NAME} or ${VAR_NAME:default_value}

    Args:
        data: Configuration data (dict, list, or primitive)

    Returns:
        Data with environment variables substituted

    Raises:
        EnvironmentVariableError: If environment variable substitution fails
    """
    try:
        if isinstance(data, dict):
            return {
                key: _substitute_env_vars(value) for key, value in data.items()
            }
        elif isinstance(data, list):
            return [_substitute_env_vars(item) for item in data]
        elif (
            isinstance(data, str)
            and data.startswith("${")
            and data.endswith("}")
        ):
            # Extract variable name and default value
            var_content = data[2:-1]
            if ":" in var_content:
                var_name, default_value = var_content.split(":", 1)
                return os.getenv(var_name.strip(), default_value.strip())
            else:
                var_name = var_content.strip()
                if var_name not in os.environ:
                    raise EnvironmentVariableError(
                        f"Environment variable '{var_name}' not found"
                    )
                return os.environ[var_name]
        else:
            return data
    except Exception as e:
        if isinstance(e, EnvironmentVariableError):
            raise
        raise EnvironmentVariableError(
            f"Failed to substitute environment variables: {e}"
        )


def deep_merge(
    base: Dict[str, Any], override: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deep merge two configurations, with override taking precedence.

    This function recursively merges two dictionaries, with the override
    dictionary taking precedence over the base dictionary for conflicting keys.
    Nested dictionaries are merged recursively.

    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary

    Returns:
        Merged configuration dictionary

    Example:
        >>> base = {'model': {'name': 'resnet50', 'layers': 50}, 'training': {'epochs': 100}}
        >>> override = {'model': {'name': 'vgg16'}, 'training': {'lr': 0.01}}
        >>> result = deep_merge(base, override)
        >>> print(result)
        {'model': {'name': 'vgg16', 'layers': 50}, 'training': {'epochs': 100, 'lr': 0.01}}
    """
    result = base.copy()

    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result
