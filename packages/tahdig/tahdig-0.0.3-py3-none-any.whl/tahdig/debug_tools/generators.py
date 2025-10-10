"""
Configuration Documentation and IDE Support Generation Module

This module provides tools to generate documentation and IDE support
files for configurations.

Features:
---------
- Markdown documentation generation
- Python type stub (.pyi) files for IDE autocomplete
- VS Code configuration schemas
- Test and mock configuration generation

Example:
--------
    >>> from simple_config import Config
    >>> from simple_config.debug_tools.generators import ConfigGenerator
    >>>
    >>> config = Config({'database': {'host': 'localhost', 'port': 5432}})
    >>> generator = ConfigGenerator(config)
    >>>
    >>> # Generate documentation
    >>> generator.generate_docs('config_docs.md')
    >>>
    >>> # Generate IDE support
    >>> generator.generate_ide_support('config.pyi')
"""

import time
import json
from pathlib import Path
from typing import Any, Dict, Union, Callable
from ..config import Config, ConfigNode


class ConfigGenerator:
    """
    Handles generation of documentation and IDE support files.

    This class provides methods to generate various output files
    from configuration data, including documentation, type stubs,
    and IDE schemas.

    Attributes:
        config: The configuration object to generate from
    """

    def __init__(self, config: Union[Config, ConfigNode]):
        """
        Initialize the ConfigGenerator.

        Args:
            config: Configuration object to generate from
        """
        self.config = config

    def generate_docs(self, output_path: Union[str, Path]) -> None:
        """
        Generate Markdown documentation for the configuration.

        Creates a well-formatted Markdown file documenting the
        configuration structure, types, and values.

        Args:
            output_path: Path to save the documentation file

        Example:
            >>> generator.generate_docs('docs/config.md')
        """

        def generate_section_docs(
            data: Dict, path: str = "", level: int = 1
        ) -> str:
            """
            Recursively generate documentation for a section.

            Args:
                data: Dictionary data to document
                path: Current path in configuration
                level: Heading level for Markdown

            Returns:
                Markdown-formatted documentation string
            """
            docs = ""
            indent = "  " * (level - 1)

            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                docs += f"{indent}### {key}\n\n"

                if isinstance(value, dict):
                    docs += f"{indent}Type: `object`\n\n"
                    docs += f"{indent}Contains:\n"
                    docs += generate_section_docs(
                        value, current_path, level + 1
                    )
                elif isinstance(value, list):
                    docs += f"{indent}Type: `array`\n\n"
                    docs += f"{indent}Length: {len(value)}\n\n"
                else:
                    docs += f"{indent}Type: `{type(value).__name__}`\n\n"
                    docs += f"{indent}Value: `{value}`\n\n"

                docs += "\n"

            return docs

        # Generate documentation content
        content = f"""# Configuration Documentation
Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}

## Overview

This document describes the structure and contents of the configuration file.

## Configuration Structure

{generate_section_docs(self.config._data)}
"""

        # Write to file
        with open(output_path, "w") as f:
            f.write(content)

    def generate_ide_support(self, output_path: Union[str, Path]) -> None:
        """
        Generate Python type stub (.pyi) file for IDE autocomplete.

        Creates a .pyi file that IDEs can use to provide autocomplete
        and type checking for configuration attributes.

        Args:
            output_path: Path to save the .pyi file

        Example:
            >>> generator.generate_ide_support('config.pyi')
        """

        def generate_type_hints(
            data: Dict, path: str = "", level: int = 0
        ) -> str:
            """
            Recursively generate type hints.

            Args:
                data: Dictionary to generate hints for
                path: Current path
                level: Indentation level

            Returns:
                Python type hint string
            """
            hints = ""
            indent = "    " * level

            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key

                if isinstance(value, dict):
                    hints += f"{indent}class {key.title()}:\n"
                    hints += generate_type_hints(value, current_path, level + 1)
                elif isinstance(value, list):
                    hints += f"{indent}{key}: List[Any]\n"
                else:
                    type_name = type(value).__name__
                    hints += f"{indent}{key}: {type_name}\n"

            return hints

        # Generate type stub content
        content = f"""# Configuration type hints
from typing import Any, List

class Config:
{generate_type_hints(self.config._data, level=1)}
"""

        # Write to file
        with open(output_path, "w") as f:
            f.write(content)

    def generate_vscode_config(self, output_path: Union[str, Path]) -> None:
        """
        Generate VS Code configuration for YAML validation.

        Creates a VS Code settings file that enables YAML validation
        and autocomplete for configuration files.

        Args:
            output_path: Path to save the VS Code settings

        Example:
            >>> generator.generate_vscode_config('.vscode/settings.json')
        """
        config = {
            "yaml.schemas": {"file:///path/to/config-schema.json": "*.yaml"},
            "yaml.validate": True,
            "yaml.format.enable": True,
            "yaml.completion": True,
        }

        with open(output_path, "w") as f:
            json.dump(config, f, indent=2)

    def test(self, test_cases: Dict[str, Callable]) -> Dict[str, Any]:
        """
        Test configuration against custom test cases.

        Runs custom test functions against configuration values
        and returns the results.

        Args:
            test_cases: Dictionary mapping paths to test functions

        Returns:
            Dictionary with test results for each path

        Example:
            >>> test_cases = {
            >>>     'database.port': lambda port: 1024 <= port <= 65535,
            >>>     'api.timeout': lambda t: t > 0
            >>> }
            >>> results = generator.test(test_cases)
            >>> for path, result in results.items():
            >>>     if result['status'] == 'passed':
            >>>         print(f"✓ {path}")
        """
        results = {}

        for path, test_func in test_cases.items():
            try:
                # Navigate to the path
                current = self.config
                for part in path.split("."):
                    current = getattr(current, part)

                # Run the test
                result = test_func(current)
                results[path] = {
                    "status": "passed" if result else "failed",
                    "result": result,
                }
            except Exception as e:
                results[path] = {"status": "error", "error": str(e)}

        return results

    def mock(self, overrides: Dict[str, Any]) -> "Config":
        """
        Create a mocked version of the configuration for testing.

        Creates a new Config instance with specified values overridden,
        useful for testing different configurations.

        Args:
            overrides: Dictionary of paths to override with new values

        Returns:
            New Config instance with overridden values

        Example:
            >>> mocked = generator.mock({
            >>>     'database.host': 'test-db',
            >>>     'debug': True
            >>> })
            >>> print(mocked.database.host)  # 'test-db'
        """
        # Create a copy of the configuration
        mocked_data = self.config._data.copy()

        # Apply overrides
        for path, value in overrides.items():
            parts = path.split(".")
            current = mocked_data
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value

        # Create new config
        return Config(mocked_data)
