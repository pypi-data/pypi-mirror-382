"""
Configuration Visualization Module

This module provides visualization and interactive exploration tools
for configurations.

Features:
---------
- Tree visualization with customizable depth and width limits
- Interactive configuration explorer with REPL interface
- Path inspection with detailed metadata
- Safe navigation with error handling

Example:
--------
    >>> from simple_config import Config
    >>> from simple_config.debug_tools.visualizers import ConfigVisualizer
    >>>
    >>> config = Config({
    >>>     'database': {
    >>>         'host': 'localhost',
    >>>         'port': 5432
    >>>     },
    >>>     'api': {
    >>>         'version': 'v1',
    >>>         'timeout': 30
    >>>     }
    >>> })
    >>>
    >>> visualizer = ConfigVisualizer(config)
    >>> tree = visualizer.visualize(max_depth=2)
    >>> print(tree)
"""

import json
from typing import Any, Dict, Optional, Union
from ..config import Config, ConfigNode


class ConfigVisualizer:
    """
    Handles visualization and interactive exploration of configurations.

    This class provides methods to visualize configuration structure
    as a tree, inspect specific paths, and explore configurations
    interactively.

    Attributes:
        config: The configuration object to visualize
        file_path: Optional file path for context
    """

    def __init__(
        self, config: Union[Config, ConfigNode], file_path: Optional[str] = None
    ):
        """
        Initialize the ConfigVisualizer.

        Args:
            config: Configuration object to visualize
            file_path: Optional file path for context
        """
        self.config = config
        self.file_path = file_path

    def visualize(self, max_depth: int = 3, max_width: int = 100) -> str:
        """
        Create a visual tree representation of the configuration.

        Generates an ASCII tree showing the configuration structure
        with customizable depth and width limits for readability.

        Args:
            max_depth: Maximum nesting depth to display
            max_width: Maximum number of items to show per level

        Returns:
            String representation of the configuration tree

        Example:
            >>> tree = visualizer.visualize(max_depth=2, max_width=50)
            >>> print(tree)
            ├── database/
            │   ├── host: localhost
            │   └── port: 5432
            └── api/
                ├── version: v1
                └── timeout: 30
        """

        def visualize_dict(data: Dict, prefix: str = "", depth: int = 0) -> str:
            """
            Recursively visualize a dictionary as a tree.

            Args:
                data: Dictionary to visualize
                prefix: Current line prefix for tree structure
                depth: Current depth level

            Returns:
                Tree string representation
            """
            if depth >= max_depth:
                return f"{prefix}...\n"

            result = ""
            items = list(data.items())[:max_width]  # Limit items

            for i, (key, value) in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                next_prefix = "    " if is_last else "│   "

                if isinstance(value, dict):
                    # Dictionary node - show as folder
                    result += f"{prefix}{current_prefix}{key}/\n"
                    result += visualize_dict(
                        value, prefix + next_prefix, depth + 1
                    )
                elif isinstance(value, list):
                    # List node - show count
                    result += f"{prefix}{current_prefix}{key}[] ({len(value)} items)\n"
                else:
                    # Leaf node - show value (truncated if too long)
                    value_str = str(value)
                    if len(value_str) > 50:
                        value_str = value_str[:50] + "..."
                    result += f"{prefix}{current_prefix}{key}: {value_str}\n"

            # Show truncation indicator if needed
            if len(data) > max_width:
                result += (
                    f"{prefix}└── ... ({len(data) - max_width} more items)\n"
                )

            return result

        return visualize_dict(self.config._data)

    def inspect(self, path: str) -> Dict[str, Any]:
        """
        Get detailed information about a configuration section.

        Navigates to the specified path and returns metadata about
        the configuration value at that location.

        Args:
            path: Dot-separated path to the section (e.g., 'database.host')

        Returns:
            Dictionary with section information including:
            - path: The path inspected
            - type: Type of the value
            - value: The actual value (or data dict)
            - is_frozen: Whether the config is frozen
            - allowed_keys: Set of allowed keys (if frozen)
            - source_file: Source file path (if available)
            - memory_size: Approximate memory size in bytes

        Example:
            >>> info = visualizer.inspect('database.host')
            >>> print(f"Type: {info['type']}")
            >>> print(f"Value: {info['value']}")
        """
        try:
            # Navigate to the section using dot notation
            current = self.config
            for part in path.split("."):
                current = getattr(current, part)

            return {
                "path": path,
                "type": type(current).__name__,
                "value": current._data
                if hasattr(current, "_data")
                else current,
                "is_frozen": getattr(current, "_frozen", False),
                "allowed_keys": getattr(current, "_allowed_keys", None),
                "source_file": self.file_path
                or getattr(self.config, "_file_path", None),
                "memory_size": len(
                    str(current._data if hasattr(current, "_data") else current)
                ),
            }
        except AttributeError as e:
            return {"error": f"Path '{path}' not found: {str(e)}"}

    def explore(self) -> None:
        """
        Start an interactive configuration explorer.

        Provides a REPL-like interface for exploring the configuration
        with various commands.

        Commands:
        ---------
        - .help: Show help message
        - .inspect <path>: Inspect a configuration section
        - .visualize: Show configuration tree
        - .quit: Exit explorer
        - <path>: Navigate to and show value at path

        Example:
            >>> visualizer.explore()
            Configuration Explorer
            ==================================================
            config> .inspect database.host
            {
              "path": "database.host",
              "type": "str",
              "value": "localhost"
            }
            config> .quit
        """
        print("Configuration Explorer")
        print("=" * 50)
        print("Available commands:")
        print("  .help - Show this help")
        print("  .inspect <path> - Inspect a section")
        print("  .visualize - Show configuration tree")
        print("  .quit - Exit explorer")
        print()

        while True:
            try:
                command = input("config> ").strip()

                if command == ".quit":
                    break
                elif command == ".help":
                    print(
                        "Available commands: .help, .inspect <path>, .visualize, .quit"
                    )
                elif command == ".visualize":
                    print(self.visualize())
                elif command.startswith(".inspect "):
                    path = command[9:].strip()
                    info = self.inspect(path)
                    print(json.dumps(info, indent=2))
                else:
                    # Try to navigate to the path
                    try:
                        result = self._safe_navigate(command)
                        print(result)
                    except Exception as e:
                        print(f"Error: {e}")

            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    def _safe_navigate(self, path: str) -> Any:
        """
        Safely navigate to a configuration section.

        Args:
            path: Dot-separated path to navigate to

        Returns:
            Configuration value at the path

        Raises:
            AttributeError: If path is not found
        """
        current = self.config
        for part in path.split("."):
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                raise AttributeError(f"Path '{path}' not found")
        return current
