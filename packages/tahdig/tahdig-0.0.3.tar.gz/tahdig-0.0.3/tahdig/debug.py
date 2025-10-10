"""
Main Debugging Interface Module

This module provides the main ConfigDebugger class that coordinates
all debugging tools from the debug_tools package.

The debug functionality has been refactored into specialized modules:
- validators: Schema validation and type checking
- linters: Configuration linting for best practices
- analyzers: Performance profiling and statistical analysis
- visualizers: Tree visualization and interactive exploration
- generators: Documentation and IDE support generation

Example:
--------
    >>> from simple_config import Config, ConfigDebugger
    >>>
    >>> config = Config({'database': {'host': 'localhost', 'port': 5432}})
    >>> debugger = ConfigDebugger(config)
    >>>
    >>> # Validate against schema
    >>> schema = {'database': {'host': str, 'port': int}}
    >>> errors = debugger.validate_schema(schema)
    >>>
    >>> # Lint for issues
    >>> lint_errors = debugger.lint()
    >>>
    >>> # Visualize structure
    >>> print(debugger.visualize())
    >>>
    >>> # Profile performance
    >>> metrics = debugger.profile()
"""

import logging
from typing import Any, Dict, List, Optional, Union, Callable, Set
from pathlib import Path

from .config import Config, ConfigNode
from .exceptions import ConfigValidationError, ConfigLintError

# Import specialized debug tools
from .debug_tools.validators import ConfigValidator
from .debug_tools.linters import ConfigLinter
from .debug_tools.analyzers import ConfigAnalyzer
from .debug_tools.visualizers import ConfigVisualizer
from .debug_tools.generators import ConfigGenerator

# For backward compatibility with tests
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore[assignment]

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None


class ConfigDebugger:
    """
    Main debugging interface for configuration analysis.

    This class coordinates all debugging tools and provides a unified
    interface for validation, linting, profiling, visualization, and
    generation of configuration-related files.

    The ConfigDebugger delegates to specialized modules:
    - ConfigValidator: Schema validation and type checking
    - ConfigLinter: Linting for best practices
    - ConfigAnalyzer: Performance profiling and analysis
    - ConfigVisualizer: Tree visualization and exploration
    - ConfigGenerator: Documentation and IDE support generation

    Attributes:
        config: Configuration object being debugged
        debug: Whether debug logging is enabled
        logger: Logger instance for debug messages
        validator: Schema validation handler
        linter: Configuration linting handler
        analyzer: Performance analysis handler
        visualizer: Visualization and exploration handler
        generator: Documentation generation handler

    Example:
        >>> from simple_config import Config, ConfigDebugger
        >>>
        >>> config = Config({
        >>>     'database': {
        >>>         'host': 'localhost',
        >>>         'port': 5432,
        >>>         'timeout': 30
        >>>     },
        >>>     'api': {
        >>>         'version': 'v1',
        >>>         'rate_limit': 1000
        >>>     }
        >>> })
        >>>
        >>> # Create debugger
        >>> debugger = ConfigDebugger(config, debug=True)
        >>>
        >>> # Validate configuration
        >>> schema = {
        >>>     'database': {
        >>>         'host': str,
        >>>         'port': int,
        >>>         'timeout': int
        >>>     },
        >>>     'api': {
        >>>         'version': str,
        >>>         'rate_limit': int
        >>>     }
        >>> }
        >>> errors = debugger.validate_schema(schema)
        >>> if not errors:
        >>>     print("Configuration is valid!")
        >>>
        >>> # Lint for issues
        >>> lint_errors = debugger.lint()
        >>> for error in lint_errors:
        >>>     print(f"{error.severity}: {error}")
        >>>
        >>> # Get statistics
        >>> stats = debugger.get_stats()
        >>> print(f"Total keys: {stats['total_keys']}")
        >>> print(f"Max depth: {stats['max_depth']}")
        >>>
        >>> # Visualize structure
        >>> tree = debugger.visualize(max_depth=3)
        >>> print(tree)
    """

    def __init__(self, config: Union[Config, ConfigNode], debug: bool = False):
        """
        Initialize the ConfigDebugger.

        Creates specialized handler instances for each debugging function.

        Args:
            config: Configuration object to debug
            debug: Enable debug logging (default: False)
        """
        self.config = config
        self.debug = debug
        self.logger = self._setup_logger()

        # Get file path if available
        file_path = getattr(config, "_file_path", None)
        loading_trace = getattr(config, "_loading_trace", [])

        # Initialize specialized handlers
        self.validator = ConfigValidator(config, file_path)
        self.linter = ConfigLinter(config, file_path)
        self.analyzer = ConfigAnalyzer(config, loading_trace)
        self.visualizer = ConfigVisualizer(config, file_path)
        self.generator = ConfigGenerator(config)

        if self.debug:
            self.logger.debug(
                f"ConfigDebugger initialized for config with {len(config._data)} top-level keys"
            )

    def _setup_logger(self) -> logging.Logger:
        """
        Set up debug logger.

        Returns:
            Configured logger instance
        """
        logger = logging.Logger(f"simple_config.debug.{id(self.config)}")
        if self.debug:
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    # ========== Validation Methods ==========

    def validate_schema(
        self, schema: Dict[str, Any], file_path: Optional[str] = None
    ) -> List[ConfigValidationError]:
        """
        Validate configuration against a schema.

        Delegates to ConfigValidator for schema validation.

        Args:
            schema: Schema definition with expected types and constraints
            file_path: Optional file path for error context

        Returns:
            List of validation errors (empty if valid)
        """
        if self.debug:
            self.logger.debug(
                f"Validating schema with {len(schema)} top-level keys"
            )
        return self.validator.validate_schema(schema, file_path)

    # ========== Linting Methods ==========

    def lint(
        self, rules: Optional[Dict[str, Callable]] = None
    ) -> List[ConfigLintError]:
        """
        Lint configuration for common issues and best practices.

        Delegates to ConfigLinter for linting operations.

        Args:
            rules: Optional dictionary of custom linting rules

        Returns:
            List of linting errors and warnings
        """
        if self.debug:
            self.logger.debug("Running configuration linter")
        return self.linter.lint(rules)

    def set_required_fields(self, fields: Set[str]) -> None:
        """
        Set required fields for linting validation.

        Args:
            fields: Set of field names that are required
        """
        self.linter.set_required_fields(fields)

    def add_validation_rule(
        self, name: str, rule: Callable[[str, Any], Optional[str]]
    ) -> None:
        """
        Add a custom linting rule.

        Args:
            name: Name of the validation rule
            rule: Function that takes (key, value) and returns error message or None
        """
        self.linter.add_custom_rule(name, rule)

    # ========== Analysis Methods ==========

    def profile(self) -> Dict[str, Any]:
        """
        Profile configuration loading and memory usage.

        Delegates to ConfigAnalyzer for profiling.

        Returns:
            Dictionary with performance metrics
        """
        if self.debug:
            self.logger.debug("Profiling configuration")
        return self.analyzer.profile()

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the configuration.

        Delegates to ConfigAnalyzer for statistical analysis.

        Returns:
            Dictionary with configuration statistics
        """
        if self.debug:
            self.logger.debug("Gathering configuration statistics")
        return self.analyzer.get_stats()

    def diff_with_file(self, other_file: Union[str, Path]) -> Dict[str, Any]:
        """
        Compare configuration with another file.

        Delegates to ConfigAnalyzer for diff generation.

        Args:
            other_file: Path to the other configuration file

        Returns:
            Dictionary showing differences
        """
        if self.debug:
            self.logger.debug(f"Comparing with file: {other_file}")
        return self.analyzer.diff_with_file(str(other_file))

    def get_loading_trace(self) -> List[Dict[str, Any]]:
        """
        Get the loading trace for configuration inheritance.

        Returns:
            List of loading steps with file paths and timestamps
        """
        return self.analyzer.get_loading_trace()

    # ========== Visualization Methods ==========

    def visualize(self, max_depth: int = 3, max_width: int = 100) -> str:
        """
        Create a visual representation of the configuration structure.

        Delegates to ConfigVisualizer for tree generation.

        Args:
            max_depth: Maximum depth to visualize
            max_width: Maximum number of items to show per level

        Returns:
            String representation of the configuration tree
        """
        if self.debug:
            self.logger.debug(
                f"Visualizing configuration (max_depth={max_depth})"
            )
        return self.visualizer.visualize(max_depth, max_width)

    def inspect(self, path: str) -> Dict[str, Any]:
        """
        Get detailed information about a configuration section.

        Delegates to ConfigVisualizer for inspection.

        Args:
            path: Dot-separated path to the section

        Returns:
            Dictionary with section information
        """
        if self.debug:
            self.logger.debug(f"Inspecting path: {path}")
        return self.visualizer.inspect(path)

    def explore(self) -> None:
        """
        Start an interactive configuration explorer.

        Delegates to ConfigVisualizer for interactive exploration.
        """
        if self.debug:
            self.logger.debug("Starting interactive explorer")
        self.visualizer.explore()

    # ========== Generation Methods ==========

    def generate_docs(self, output_path: Union[str, Path]) -> None:
        """
        Generate documentation for the configuration.

        Delegates to ConfigGenerator for documentation generation.

        Args:
            output_path: Path to save the documentation
        """
        if self.debug:
            self.logger.debug(f"Generating documentation to: {output_path}")
        self.generator.generate_docs(output_path)

    def generate_ide_support(self, output_path: Union[str, Path]) -> None:
        """
        Generate IDE support files for autocomplete.

        Delegates to ConfigGenerator for IDE support generation.

        Args:
            output_path: Path to save the .pyi file
        """
        if self.debug:
            self.logger.debug(f"Generating IDE support to: {output_path}")
        self.generator.generate_ide_support(output_path)

    def generate_vscode_config(self, output_path: Union[str, Path]) -> None:
        """
        Generate VS Code configuration for validation.

        Delegates to ConfigGenerator for VS Code config generation.

        Args:
            output_path: Path to save the VS Code settings
        """
        if self.debug:
            self.logger.debug(f"Generating VS Code config to: {output_path}")
        self.generator.generate_vscode_config(output_path)

    def test(self, test_cases: Dict[str, Callable]) -> Dict[str, Any]:
        """
        Test configuration against custom test cases.

        Delegates to ConfigGenerator for testing.

        Args:
            test_cases: Dictionary mapping paths to test functions

        Returns:
            Dictionary with test results
        """
        if self.debug:
            self.logger.debug(f"Running {len(test_cases)} test cases")
        return self.generator.test(test_cases)

    def mock(self, overrides: Dict[str, Any]) -> "ConfigDebugger":
        """
        Create a mocked version of the configuration for testing.

        Delegates to ConfigGenerator for mock creation.

        Args:
            overrides: Dictionary of values to override

        Returns:
            New ConfigDebugger instance with mocked configuration
        """
        if self.debug:
            self.logger.debug(f"Creating mock with {len(overrides)} overrides")
        mocked_config = self.generator.mock(overrides)
        return ConfigDebugger(mocked_config, self.debug)

    # ========== Properties (for backward compatibility) ==========

    @property
    def _loading_trace(self) -> List[Dict[str, Any]]:
        """For backward compatibility."""
        return self.analyzer.loading_trace

    @_loading_trace.setter
    def _loading_trace(self, value: List[Dict[str, Any]]):
        """For backward compatibility."""
        self.analyzer.loading_trace = value

    @property
    def _seen_keys(self) -> Set[str]:
        """For backward compatibility."""
        return self.linter.seen_keys

    @_seen_keys.setter
    def _seen_keys(self, value: Set[str]):
        """For backward compatibility."""
        self.linter.seen_keys = value

    @property
    def _required_fields(self) -> Set[str]:
        """For backward compatibility."""
        return self.linter.required_fields

    @_required_fields.setter
    def _required_fields(self, value: Set[str]):
        """For backward compatibility."""
        self.linter.required_fields = value

    @property
    def _custom_rules(self) -> Dict[str, Callable]:
        """For backward compatibility."""
        return self.linter.custom_rules

    @_custom_rules.setter
    def _custom_rules(self, value: Dict[str, Callable]):
        """For backward compatibility."""
        self.linter.custom_rules = value

    # ========== Private Methods (for backward compatibility) ==========

    def _check_duplicate_keys(self, key: str, value: Any) -> Optional[str]:
        """For backward compatibility - delegates to linter."""
        return self.linter._check_duplicate_keys(key, value)

    def _check_required_fields(self, key: str, value: Any) -> Optional[str]:
        """For backward compatibility - delegates to linter."""
        return self.linter._check_required_fields(key, value)

    def _check_type_consistency(self, key: str, value: Any) -> Optional[str]:
        """For backward compatibility - delegates to linter."""
        return self.linter._check_type_consistency(key, value)

    def _check_naming_conventions(self, key: str, value: Any) -> Optional[str]:
        """For backward compatibility - delegates to linter."""
        return self.linter._check_naming_conventions(key, value)

    def _calculate_max_depth(self, data: Any, current_depth: int = 0) -> int:
        """For backward compatibility - delegates to analyzer."""
        return self.analyzer._calculate_max_depth(data, current_depth)

    def _count_keys(self, data: Any) -> int:
        """For backward compatibility - delegates to analyzer."""
        return self.analyzer._count_keys(data)


# ========== Convenience Functions ==========


def create_debugger(
    config: Union[Config, ConfigNode], debug: bool = False
) -> ConfigDebugger:
    """
    Create a ConfigDebugger instance.

    Factory function for creating debugger instances.

    Args:
        config: Configuration object to debug
        debug: Enable debug logging

    Returns:
        ConfigDebugger instance

    Example:
        >>> from simple_config import Config, create_debugger
        >>> config = Config({'key': 'value'})
        >>> debugger = create_debugger(config, debug=True)
    """
    return ConfigDebugger(config, debug)


def validate_config(
    config: Union[Config, ConfigNode], schema: Dict[str, Any]
) -> bool:
    """
    Validate configuration against schema (convenience function).

    Args:
        config: Configuration to validate
        schema: Schema definition

    Returns:
        True if valid, False otherwise

    Example:
        >>> from simple_config import Config, validate_config
        >>> config = Config({'database': {'host': 'localhost'}})
        >>> schema = {'database': {'host': str}}
        >>> is_valid = validate_config(config, schema)
    """
    debugger = ConfigDebugger(config)
    errors = debugger.validate_schema(schema)
    return len(errors) == 0


def lint_config(config: Union[Config, ConfigNode]) -> List[ConfigLintError]:
    """
    Lint configuration for issues (convenience function).

    Args:
        config: Configuration to lint

    Returns:
        List of linting errors

    Example:
        >>> from simple_config import Config, lint_config
        >>> config = Config({'timeout': '30'})  # String that looks like number
        >>> errors = lint_config(config)
    """
    debugger = ConfigDebugger(config)
    return debugger.lint()


def visualize_config(config: Union[Config, ConfigNode]) -> str:
    """
    Visualize configuration structure (convenience function).

    Args:
        config: Configuration to visualize

    Returns:
        String representation of the configuration tree

    Example:
        >>> from simple_config import Config, visualize_config
        >>> config = Config({'database': {'host': 'localhost', 'port': 5432}})
        >>> tree = visualize_config(config)
        >>> print(tree)
    """
    debugger = ConfigDebugger(config)
    return debugger.visualize()
