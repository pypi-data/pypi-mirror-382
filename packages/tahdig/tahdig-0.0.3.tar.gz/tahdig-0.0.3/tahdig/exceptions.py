"""
Exceptions for the simple_config package.

This module defines a comprehensive hierarchy of exceptions for the simple_config
system. The exceptions are organized into logical groups to provide clear error
handling and debugging information.

Exception Hierarchy:
    SimpleConfigError
    ├── RegistryError
    │   ├── ComponentNotFoundError
    │   ├── DuplicateComponentError
    │   └── RegistryNotFoundError
    ├── ConfigError
    │   ├── ConfigValidationError
    │   ├── ConfigKeyError
    │   ├── ConfigFileError
    │   │   ├── ConfigFileNotFoundError
    │   │   └── UnsupportedFileFormatError
    │   ├── ConfigSerializationError
    │   └── EnvironmentVariableError
    └── DecoratorError
        ├── ConfigurableError
        └── ParameterExtractionError

Example:
    >>> try:
    >>>     config = Config.from_file('nonexistent.yaml')
    >>> except ConfigFileNotFoundError as e:
    >>>     print(f"Configuration file not found: {e}")
    >>> except UnsupportedFileFormatError as e:
    >>>     print(f"Unsupported file format: {e}")
"""


class SimpleConfigError(Exception):
    """
    Base exception for simple_config-related errors.

    This is the root exception class for all errors in the simple_config package.
    All other exceptions inherit from this class to provide a common base for
    error handling.
    """

    pass


class RegistryError(SimpleConfigError):
    """
    Base exception for registry-related errors.

    This exception is raised for errors related to component registration,
    retrieval, and management in the registry system.
    """

    pass


class ComponentNotFoundError(RegistryError):
    """
    Raised when a requested component is not found in the registry.

    This exception is raised when trying to retrieve a component that hasn't
    been registered in the registry.

    Example:
        >>> registry = Registry()
        >>> registry.get('nonexistent_component')  # Raises ComponentNotFoundError
    """

    pass


class DuplicateComponentError(RegistryError):
    """
    Raised when trying to register a component with a name that already exists.

    This exception is raised when attempting to register a component with a
    name that's already in use, unless the override option is enabled.

    Example:
        >>> registry = Registry()
        >>> registry.register('my_component', lambda: 'Hello')
        >>> registry.register('my_component', lambda: 'World')  # Raises DuplicateComponentError
    """

    pass


class RegistryNotFoundError(RegistryError):
    """
    Raised when trying to access a registry that doesn't exist.

    This exception is raised when attempting to access a registry by name
    that hasn't been created or doesn't exist.
    """

    pass


class ConfigError(SimpleConfigError):
    """
    Base exception for configuration-related errors.

    This exception is raised for errors related to configuration loading,
    validation, and manipulation.
    """

    pass


class ConfigKeyError(ConfigError, KeyError):
    """
    Raised when trying to access or modify a configuration key that is not allowed.

    This exception is raised when attempting to access or modify configuration
    keys that are not allowed, such as when trying to add new keys to a frozen
    configuration.

    Example:
        >>> config = Config({'key': 'value'})
        >>> config.freeze()
        >>> config.new_key = 'new_value'  # Raises ConfigKeyError
    """

    def __init__(
        self,
        message: str,
        key: str = None,
        allowed_keys: set = None,
        suggestion: str = None,
        file_path: str = None,
        line_number: int = None,
        section: str = None,
    ):
        """
        Initialize ConfigKeyError with helpful debugging information.

        Args:
            message: Error message
            key: The key that caused the error
            allowed_keys: Set of allowed keys (if applicable)
            suggestion: Suggested fix for the error
            file_path: Path to the configuration file
            line_number: Line number where the error occurred
            section: Configuration section where the error occurred
        """
        super().__init__(message)
        self.key = key
        self.allowed_keys = allowed_keys or set()
        self.suggestion = suggestion
        self.file_path = file_path
        self.line_number = line_number
        self.section = section

    def __str__(self) -> str:
        """Return detailed error message with suggestions."""
        msg = super().__str__()

        if self.key:
            msg += f"\n  Key: '{self.key}'"

        if self.section:
            msg += f"\n  Section: '{self.section}'"

        if self.allowed_keys:
            msg += f"\n  Available keys: {sorted(self.allowed_keys)}"

        if self.suggestion:
            msg += f"\n  Suggestion: {self.suggestion}"

        if self.file_path:
            msg += f"\n  File: {self.file_path}"
            if self.line_number:
                msg += f":{self.line_number}"

        return msg


class ConfigFileError(ConfigError):
    """
    Base exception for configuration file-related errors.

    This exception is raised for errors related to reading from or writing
    to configuration files.
    """

    pass


class ConfigFileNotFoundError(ConfigFileError, FileNotFoundError):
    """
    Raised when a configuration file is not found.

    This exception is raised when attempting to load a configuration file
    that doesn't exist at the specified path.

    Example:
        >>> config = Config.from_file('nonexistent.yaml')  # Raises ConfigFileNotFoundError
    """

    pass


class UnsupportedFileFormatError(ConfigFileError, ValueError):
    """
    Raised when trying to load/save a file with an unsupported format.

    This exception is raised when attempting to load or save a configuration
    file in a format that's not supported by the system.

    Example:
        >>> config = Config.from_file('config.txt')  # Raises UnsupportedFileFormatError
    """

    pass


class ConfigSerializationError(ConfigError):
    """
    Raised when configuration serialization/deserialization fails.

    This exception is raised when there's an error during the process of
    converting configuration data to or from a serialized format.
    """

    pass


class CircularDependencyError(ConfigError):
    """
    Raised when circular dependency is detected in configuration inheritance.

    This exception is raised when a configuration file tries to inherit
    from another file that eventually leads back to itself, creating
    an infinite loop.

    Example:
        # config_a.yaml
        extends: config_b.yaml
        value: 1

        # config_b.yaml
        extends: config_a.yaml  # Circular dependency!
        value: 2
    """

    def __init__(
        self,
        message: str,
        dependency_chain: list = None,
        circular_file: str = None,
        line_numbers: list = None,
    ):
        """
        Initialize CircularDependencyError with dependency chain information.

        Args:
            message: Error message
            dependency_chain: List of files in the dependency chain
            circular_file: The file that creates the circular dependency
            line_numbers: Line numbers where 'extends' statements are located
        """
        super().__init__(message)
        self.dependency_chain = dependency_chain or []
        self.circular_file = circular_file
        self.line_numbers = line_numbers or []

    def __str__(self) -> str:
        """Return detailed error message with dependency chain."""
        msg = super().__str__()

        if self.dependency_chain:
            msg += "\n  Dependency chain:"
            for i, file_path in enumerate(self.dependency_chain):
                line_info = ""
                if i < len(self.line_numbers) and self.line_numbers[i]:
                    line_info = f" (line {self.line_numbers[i]})"
                msg += f"\n    {i + 1}. {file_path}{line_info}"

        if self.circular_file:
            msg += f"\n  Circular dependency at: {self.circular_file}"

        msg += "\n  Suggestion: Remove one of the 'extends' statements to break the cycle"

        return msg


class EnvironmentVariableError(ConfigError):
    """
    Raised when environment variable substitution fails.

    This exception is raised when there's an error during the process of
    substituting environment variables in configuration data.

    Example:
        >>> config = Config({'host': '${NONEXISTENT_VAR}'})  # Raises EnvironmentVariableError
    """

    pass


class DecoratorError(SimpleConfigError):
    """
    Base exception for decorator-related errors.

    This exception is raised for errors related to the configurable decorator
    and parameter extraction functionality.
    """

    pass


class ConfigurableError(DecoratorError):
    """
    Raised when configurable decorator encounters an error.

    This exception is raised when there's an error during the execution of
    a function or class decorated with @configurable.
    """

    pass


class ParameterExtractionError(DecoratorError):
    """
    Raised when parameter extraction from configuration fails.

    This exception is raised when there's an error during the process of
    extracting parameters from configuration data for a configurable function
    or class.
    """

    pass


class ConfigValidationError(ConfigError):
    """
    Raised when configuration validation fails.

    This exception is raised when configuration data does not meet
    the required validation criteria or schema.
    """

    def __init__(
        self,
        message: str,
        field: str = None,
        expected_type: str = None,
        actual_type: str = None,
        value=None,
        file_path: str = None,
        line_number: int = None,
    ):
        """
        Initialize ConfigValidationError with validation details.

        Args:
            message: Error message
            field: The field that failed validation
            expected_type: Expected type for the field
            actual_type: Actual type of the field
            value: The value that failed validation
            file_path: Path to the configuration file
            line_number: Line number where validation failed
        """
        super().__init__(message)
        self.field = field
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.value = value
        self.file_path = file_path
        self.line_number = line_number

    def __str__(self) -> str:
        """Return detailed validation error message."""
        msg = super().__str__()

        if self.field:
            msg += f"\n  Field: '{self.field}'"

        if self.expected_type and self.actual_type:
            msg += f"\n  Type mismatch: expected {self.expected_type}, got {self.actual_type}"

        if self.value is not None:
            msg += f"\n  Value: {repr(self.value)}"

        if self.file_path:
            msg += f"\n  File: {self.file_path}"
            if self.line_number:
                msg += f":{self.line_number}"

        return msg


class ConfigLintError(ConfigError):
    """
    Raised when configuration linting finds issues.

    This exception is raised when configuration linting detects
    potential issues or violations of best practices.
    """

    def __init__(
        self,
        message: str,
        severity: str = "error",
        rule: str = None,
        file_path: str = None,
        line_number: int = None,
        suggestion: str = None,
    ):
        """
        Initialize ConfigLintError with linting details.

        Args:
            message: Error message
            severity: Severity level (error, warning, info)
            rule: The linting rule that was violated
            file_path: Path to the configuration file
            line_number: Line number where the issue was found
            suggestion: Suggested fix for the issue
        """
        super().__init__(message)
        self.severity = severity
        self.rule = rule
        self.file_path = file_path
        self.line_number = line_number
        self.suggestion = suggestion

    def __str__(self) -> str:
        """Return detailed linting error message."""
        msg = f"[{self.severity.upper()}] {super().__str__()}"

        if self.rule:
            msg += f"\n  Rule: {self.rule}"

        if self.file_path:
            msg += f"\n  File: {self.file_path}"
            if self.line_number:
                msg += f":{self.line_number}"

        if self.suggestion:
            msg += f"\n  Suggestion: {self.suggestion}"

        return msg
