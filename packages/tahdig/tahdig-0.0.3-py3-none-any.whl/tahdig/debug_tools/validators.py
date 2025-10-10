"""
Configuration Schema Validation Module

This module provides comprehensive schema validation for configurations.
It supports type checking, required field validation, custom validators,
and detailed error reporting.

Features:
---------
- Type validation (dict, list, primitives)
- Required field checking
- Custom callable validators
- Nested structure validation
- Detailed error messages with file path and field context

Example:
--------
    >>> from simple_config import Config
    >>> from simple_config.debug_tools.validators import ConfigValidator
    >>>
    >>> config = Config({'database': {'host': 'localhost', 'port': 5432}})
    >>> validator = ConfigValidator(config)
    >>>
    >>> # Define schema
    >>> schema = {
    >>>     'database': {
    >>>         'host': str,
    >>>         'port': int
    >>>     }
    >>> }
    >>>
    >>> # Validate
    >>> errors = validator.validate_schema(schema)
    >>> if not errors:
    >>>     print("Configuration is valid!")
"""

from typing import Any, Dict, List, Optional
from ..exceptions import ConfigValidationError


class ConfigValidator:
    """
    Handles schema validation for configuration objects.

    This class provides methods to validate configuration data against
    defined schemas, checking types, required fields, and custom constraints.

    Attributes:
        config: The configuration object to validate
        file_path: Optional file path for error context
    """

    def __init__(self, config: Any, file_path: Optional[str] = None):
        """
        Initialize the ConfigValidator.

        Args:
            config: Configuration object with _data attribute
            file_path: Optional file path for error reporting
        """
        self.config = config
        self.file_path = file_path

    def validate_schema(
        self, schema: Dict[str, Any], file_path: Optional[str] = None
    ) -> List[ConfigValidationError]:
        """
        Validate configuration against a schema definition.

        The schema can contain:
        - Type objects (str, int, bool, etc.) for type checking
        - Nested dictionaries for nested validation
        - Callable validators that return True/False

        Args:
            schema: Schema definition mapping paths to expected types/validators
            file_path: Optional file path to include in error messages

        Returns:
            List of ConfigValidationError objects (empty if valid)

        Example:
            >>> schema = {
            >>>     'database': {
            >>>         'host': str,
            >>>         'port': lambda x: 1024 <= x <= 65535,  # Custom validator
            >>>         'timeout': int
            >>>     },
            >>>     'debug': bool
            >>> }
            >>> errors = validator.validate_schema(schema)
        """
        errors = []
        file_path = file_path or self.file_path

        def validate_section(data: Any, schema_section: Any, path: str = ""):
            """
            Recursively validate a section of configuration data.

            Args:
                data: The data to validate
                schema_section: The schema definition for this section
                path: Current path in the configuration (for error reporting)
            """
            # Handle dictionary schemas (nested structures)
            if isinstance(schema_section, dict):
                # Data must be a dict to match dict schema
                if not isinstance(data, dict):
                    errors.append(
                        ConfigValidationError(
                            f"Expected dict at '{path}', got {type(data).__name__}",
                            field=path,
                            expected_type="dict",
                            actual_type=type(data).__name__,
                            value=data,
                            file_path=file_path,
                        )
                    )
                    return

                # Validate each key in the schema
                for key, expected_type in schema_section.items():
                    current_path = f"{path}.{key}" if path else key

                    if key in data:
                        # Key exists, recursively validate it
                        validate_section(data[key], expected_type, current_path)
                    else:
                        # Required key is missing
                        errors.append(
                            ConfigValidationError(
                                f"Required field '{current_path}' is missing",
                                field=current_path,
                                file_path=file_path,
                            )
                        )

            # Handle type validators (str, int, bool, etc.)
            elif isinstance(schema_section, type):
                if not isinstance(data, schema_section):
                    errors.append(
                        ConfigValidationError(
                            f"Type mismatch at '{path}': expected {schema_section.__name__}, "
                            f"got {type(data).__name__}",
                            field=path,
                            expected_type=schema_section.__name__,
                            actual_type=type(data).__name__,
                            value=data,
                            file_path=file_path,
                        )
                    )

            # Handle callable validators (custom validation functions)
            elif callable(schema_section):
                try:
                    if not schema_section(data):
                        errors.append(
                            ConfigValidationError(
                                f"Validation failed at '{path}': {schema_section.__name__}",
                                field=path,
                                value=data,
                                file_path=file_path,
                            )
                        )
                except Exception as e:
                    errors.append(
                        ConfigValidationError(
                            f"Validation error at '{path}': {str(e)}",
                            field=path,
                            value=data,
                            file_path=file_path,
                        )
                    )

        # Start validation from root
        validate_section(self.config._data, schema)
        return errors

    def validate_required_fields(
        self, required_fields: List[str]
    ) -> List[ConfigValidationError]:
        """
        Validate that required fields exist and are not empty.

        Args:
            required_fields: List of dot-notation paths to required fields

        Returns:
            List of validation errors for missing/empty required fields

        Example:
            >>> errors = validator.validate_required_fields([
            >>>     'database.host',
            >>>     'database.port',
            >>>     'api.key'
            >>> ])
        """
        errors = []

        for field_path in required_fields:
            # Navigate to the field using dot notation
            parts = field_path.split(".")
            current = self.config._data
            found = True

            try:
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        found = False
                        break

                if not found:
                    errors.append(
                        ConfigValidationError(
                            f"Required field '{field_path}' is missing",
                            field=field_path,
                            file_path=self.file_path,
                        )
                    )
                elif current is None or (
                    isinstance(current, str) and not current.strip()
                ):
                    errors.append(
                        ConfigValidationError(
                            f"Required field '{field_path}' is empty",
                            field=field_path,
                            value=current,
                            file_path=self.file_path,
                        )
                    )
            except Exception as e:
                errors.append(
                    ConfigValidationError(
                        f"Error validating required field '{field_path}': {str(e)}",
                        field=field_path,
                        file_path=self.file_path,
                    )
                )

        return errors

    def validate_types(
        self, type_mappings: Dict[str, type]
    ) -> List[ConfigValidationError]:
        """
        Validate that fields match expected types.

        Args:
            type_mappings: Dictionary mapping field paths to expected types

        Returns:
            List of type mismatch errors

        Example:
            >>> errors = validator.validate_types({
            >>>     'database.port': int,
            >>>     'database.host': str,
            >>>     'features.caching': bool
            >>> })
        """
        errors = []

        for field_path, expected_type in type_mappings.items():
            parts = field_path.split(".")
            current = self.config._data
            found = True

            try:
                # Navigate to the field
                for part in parts:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        found = False
                        break

                if found and not isinstance(current, expected_type):
                    errors.append(
                        ConfigValidationError(
                            f"Type mismatch at '{field_path}': expected {expected_type.__name__}, "
                            f"got {type(current).__name__}",
                            field=field_path,
                            expected_type=expected_type.__name__,
                            actual_type=type(current).__name__,
                            value=current,
                            file_path=self.file_path,
                        )
                    )
            except Exception as e:
                errors.append(
                    ConfigValidationError(
                        f"Error validating type for '{field_path}': {str(e)}",
                        field=field_path,
                        file_path=self.file_path,
                    )
                )

        return errors
