"""
Configuration Linting Module

This module provides linting capabilities to check configuration files
for best practices, common issues, and potential problems.

Features:
---------
- Empty string detection
- Duplicate key checking
- Required field validation
- Type consistency checking
- Naming convention validation
- Custom linting rules support

Linting Rules:
--------------
1. **no_empty_strings**: Warns about empty string values
2. **no_duplicate_keys**: Detects duplicate keys
3. **required_fields**: Validates required fields are present
4. **type_consistency**: Checks for type inconsistencies (e.g., numeric strings)
5. **naming_conventions**: Validates key naming follows conventions

Example:
--------
    >>> from simple_config import Config
    >>> from simple_config.debug_tools.linters import ConfigLinter
    >>>
    >>> config = Config({
    >>>     'database_host': 'localhost',
    >>>     'api-key': 'secret',  # Mixed naming convention
    >>>     'timeout': '30'  # String that looks like number
    >>> })
    >>>
    >>> linter = ConfigLinter(config)
    >>> errors = linter.lint()
    >>> for error in errors:
    >>>     print(f"{error.severity}: {error}")
"""

from typing import Any, Dict, List, Optional, Callable, Set
from ..exceptions import ConfigLintError


class ConfigLinter:
    """
    Handles linting of configuration objects for best practices.

    This class provides methods to check configuration data against
    various linting rules to identify potential issues and violations
    of best practices.

    Attributes:
        config: The configuration object to lint
        file_path: Optional file path for error context
        seen_keys: Set of keys seen during linting (for duplicate detection)
        required_fields: Set of required field names
        custom_rules: Dictionary of custom linting rules
    """

    def __init__(self, config: Any, file_path: Optional[str] = None):
        """
        Initialize the ConfigLinter.

        Args:
            config: Configuration object with _data attribute
            file_path: Optional file path for error reporting
        """
        self.config = config
        self.file_path = file_path
        self.seen_keys: Set[str] = set()
        self.required_fields: Set[str] = set()
        self.custom_rules: Dict[str, Callable] = {}

    def lint(
        self, rules: Optional[Dict[str, Callable]] = None
    ) -> List[ConfigLintError]:
        """
        Run all linting rules against the configuration.

        Args:
            rules: Optional dictionary of custom rules to use instead of defaults

        Returns:
            List of ConfigLintError objects with severity levels

        Example:
            >>> # Use default rules
            >>> errors = linter.lint()
            >>>
            >>> # Use custom rules
            >>> custom_rules = {
            >>>     'no_special_chars': lambda k, v: (
            >>>         f"Special characters in '{k}'"
            >>>         if any(c in k for c in ['!', '@', '#'])
            >>>         else None
            >>>     )
            >>> }
            >>> errors = linter.lint(custom_rules)
        """
        errors = []

        # Reset seen keys for fresh linting
        self.seen_keys = set()

        # Define default linting rules
        default_rules = {
            "no_empty_strings": self._check_no_empty_strings,
            "no_duplicate_keys": self._check_duplicate_keys,
            "required_fields": self._check_required_fields,
            "type_consistency": self._check_type_consistency,
            "naming_conventions": self._check_naming_conventions,
        }

        # Merge with custom rules
        if hasattr(self, "custom_rules") and self.custom_rules:
            default_rules.update(self.custom_rules)

        # Use provided rules or defaults
        active_rules = rules or default_rules

        # Recursively lint the configuration
        def lint_recursive(data: Any, path: str = ""):
            """
            Recursively lint configuration data.

            Args:
                data: Current data being linted
                path: Current path in configuration tree
            """
            if isinstance(data, dict):
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key

                    # Apply each linting rule
                    for rule_name, rule_func in active_rules.items():
                        try:
                            result = rule_func(key, value)
                            if result and isinstance(result, str):
                                # Rule returned an error message
                                errors.append(
                                    ConfigLintError(
                                        result,
                                        severity="warning",
                                        rule=rule_name,
                                        file_path=self.file_path,
                                    )
                                )
                        except Exception as e:
                            # Rule execution failed
                            errors.append(
                                ConfigLintError(
                                    f"Linting rule '{rule_name}' failed: {str(e)}",
                                    severity="error",
                                    rule=rule_name,
                                    file_path=self.file_path,
                                )
                            )

                    # Recursively lint nested structures
                    lint_recursive(value, current_path)
            elif isinstance(data, list):
                # Lint list items
                for i, item in enumerate(data):
                    lint_recursive(item, f"{path}[{i}]")

        # Start linting from root
        lint_recursive(self.config._data)
        return errors

    def set_required_fields(self, fields: Set[str]) -> None:
        """
        Set required fields for linting.

        Args:
            fields: Set of field names that are required

        Example:
            >>> linter.set_required_fields({'host', 'port', 'database'})
        """
        self.required_fields = fields

    def add_custom_rule(
        self, name: str, rule: Callable[[str, Any], Optional[str]]
    ) -> None:
        """
        Add a custom linting rule.

        The rule function should take (key, value) and return:
        - None if the rule passes
        - Error message string if the rule fails

        Args:
            name: Name of the linting rule
            rule: Function that takes (key, value) and returns error message or None

        Example:
            >>> def check_positive_numbers(key, value):
            >>>     if isinstance(value, (int, float)) and value < 0:
            >>>         return f"Negative number in '{key}'"
            >>>     return None
            >>>
            >>> linter.add_custom_rule('positive_numbers', check_positive_numbers)
        """
        self.custom_rules[name] = rule

    # Built-in linting rules

    def _check_no_empty_strings(self, key: str, value: Any) -> Optional[str]:
        """
        Check for empty string values.

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            Error message if value is empty string, None otherwise
        """
        if value == "":
            return f"Empty string value for '{key}'"
        return None

    def _check_duplicate_keys(self, key: str, value: Any) -> Optional[str]:
        """
        Check for duplicate keys in the configuration.

        Note: This is a simplified check that tracks keys at the current
        recursion level. True duplicate detection would require path tracking.

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            Error message if key is duplicate, None otherwise
        """
        if key in self.seen_keys:
            return f"Duplicate key '{key}' found"
        self.seen_keys.add(key)
        return None

    def _check_required_fields(self, key: str, value: Any) -> Optional[str]:
        """
        Check if required fields are present and non-empty.

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            Error message if required field is missing/empty, None otherwise
        """
        if key in self.required_fields:
            if value is None or (
                isinstance(value, str) and value.strip() == ""
            ):
                return f"Required field '{key}' is empty or missing"
        return None

    def _check_type_consistency(self, key: str, value: Any) -> Optional[str]:
        """
        Check for type inconsistencies (e.g., strings that look like numbers).

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            Warning message if type inconsistency detected, None otherwise
        """
        if isinstance(value, str) and value.isdigit():
            return f"String '{value}' for '{key}' might be intended as integer"
        return None

    def _check_naming_conventions(self, key: str, value: Any) -> Optional[str]:
        """
        Check that key names follow naming conventions.

        Validates that keys only contain alphanumeric characters,
        underscores, and hyphens.

        Args:
            key: Configuration key
            value: Configuration value

        Returns:
            Warning message if naming convention violated, None otherwise
        """
        if key and not key.replace("_", "").replace("-", "").isalnum():
            return f"Key '{key}' contains non-alphanumeric characters"
        return None
