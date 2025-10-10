"""
Configuration Analysis Module

This module provides analysis tools for configurations including:
- Performance profiling and memory usage tracking
- Statistical analysis of configuration structure
- Comparison and diff generation between configurations
- Loading trace analysis

Features:
---------
- Memory usage tracking (with optional psutil)
- Configuration depth and key counting
- Value type distribution analysis
- Configuration comparison with detailed diffs
- Performance metrics collection

Example:
--------
    >>> from simple_config import Config
    >>> from simple_config.debug_tools.analyzers import ConfigAnalyzer
    >>>
    >>> config = Config({'database': {'host': 'localhost', 'port': 5432}})
    >>> analyzer = ConfigAnalyzer(config)
    >>>
    >>> # Get statistics
    >>> stats = analyzer.get_stats()
    >>> print(f"Total keys: {stats['total_keys']}")
    >>> print(f"Max depth: {stats['max_depth']}")
    >>>
    >>> # Profile performance
    >>> metrics = analyzer.profile()
    >>> print(f"Config size: {metrics['config_size']} bytes")
"""

from typing import Any, Dict, List, Optional, Union
from ..config import Config, ConfigNode, load_config

# Optional psutil for memory tracking
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore[assignment]


class ConfigAnalyzer:
    """
    Handles performance analysis, profiling, and comparison of configurations.

    This class provides tools to analyze configuration structure, measure
    performance, track memory usage, and compare configurations.

    Attributes:
        config: The configuration object to analyze
        loading_trace: List of loading steps for inheritance tracking
        performance_metrics: Dictionary of performance measurements
    """

    def __init__(
        self,
        config: Union[Config, ConfigNode],
        loading_trace: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize the ConfigAnalyzer.

        Args:
            config: Configuration object to analyze
            loading_trace: Optional loading trace from config inheritance
        """
        self.config = config
        self.loading_trace = loading_trace or []
        self.performance_metrics: Dict[str, Any] = {}

    def profile(self) -> Dict[str, Any]:
        """
        Profile configuration loading and memory usage.

        Collects metrics about:
        - Loading time (if available from trace)
        - Number of files loaded (for inherited configs)
        - Configuration size in bytes
        - Maximum nesting depth
        - Total number of keys
        - Memory usage (if psutil available)
        - CPU usage (if psutil available)

        Returns:
            Dictionary with performance metrics

        Example:
            >>> metrics = analyzer.profile()
            >>> print(f"Config has {metrics['total_keys']} keys")
            >>> print(f"Max depth: {metrics['config_depth']}")
            >>> if 'memory_usage_mb' in metrics:
            >>>     print(f"Memory: {metrics['memory_usage_mb']} MB")
        """
        metrics = {
            "loading_time": self.performance_metrics.get("loading_time", 0),
            "file_count": len(self.loading_trace),
            "config_size": len(str(self.config._data)),
            "config_depth": self._calculate_max_depth(self.config._data),
            "total_keys": self._count_keys(self.config._data),
        }

        # Add memory and CPU metrics if psutil is available
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                metrics.update(
                    {
                        "memory_usage_mb": round(
                            memory_info.rss / 1024 / 1024, 2
                        ),
                        "memory_percent": round(process.memory_percent(), 2),
                        "cpu_percent": round(process.cpu_percent(), 2),
                        "available_memory_mb": round(
                            psutil.virtual_memory().available / 1024 / 1024, 2
                        ),
                    }
                )
            except Exception:
                # Silently ignore psutil errors
                pass

        return metrics

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the configuration.

        Analyzes the configuration structure and returns detailed statistics
        about value types, nesting, and structure complexity.

        Returns:
            Dictionary with configuration statistics including:
            - total_keys: Total number of keys
            - max_depth: Maximum nesting depth
            - string_values: Count of string values
            - numeric_values: Count of numeric values
            - boolean_values: Count of boolean values
            - list_values: Count of list values
            - dict_values: Count of dict values
            - null_values: Count of None values
            - empty_strings: Count of empty string values
            - longest_string: Length of longest string
            - largest_list: Size of largest list

        Example:
            >>> stats = analyzer.get_stats()
            >>> print(f"Strings: {stats['string_values']}")
            >>> print(f"Numbers: {stats['numeric_values']}")
            >>> print(f"Longest string: {stats['longest_string']} chars")
        """
        data = self.config._data

        def analyze_data(data: Any, path: str = "") -> Dict[str, Any]:
            """Recursively analyze data structure."""
            stats = {
                "total_keys": 0,
                "max_depth": 0,
                "string_values": 0,
                "numeric_values": 0,
                "boolean_values": 0,
                "list_values": 0,
                "dict_values": 0,
                "null_values": 0,
                "empty_strings": 0,
                "longest_string": 0,
                "largest_list": 0,
            }

            if isinstance(data, dict):
                stats["dict_values"] += 1
                for key, value in data.items():
                    current_path = f"{path}.{key}" if path else key
                    child_stats = analyze_data(value, current_path)

                    # Merge child stats
                    for k, v in child_stats.items():
                        if k in ["max_depth", "longest_string", "largest_list"]:
                            stats[k] = max(stats[k], v)
                        else:
                            stats[k] += v

                    stats["max_depth"] = max(stats["max_depth"], 1)

            elif isinstance(data, list):
                stats["list_values"] += 1
                stats["largest_list"] = max(stats["largest_list"], len(data))
                for item in data:
                    child_stats = analyze_data(item, path)
                    for k, v in child_stats.items():
                        if k in ["max_depth", "longest_string", "largest_list"]:
                            stats[k] = max(stats[k], v)
                        else:
                            stats[k] += v

            else:
                # Leaf node - analyze the value
                stats["total_keys"] = 1
                if isinstance(data, str):
                    stats["string_values"] += 1
                    stats["longest_string"] = max(
                        stats["longest_string"], len(data)
                    )
                    if data == "":
                        stats["empty_strings"] += 1
                elif isinstance(data, (int, float)):
                    stats["numeric_values"] += 1
                elif isinstance(data, bool):
                    stats["boolean_values"] += 1
                elif data is None:
                    stats["null_values"] += 1

            return stats

        return analyze_data(data)

    def diff_with_file(
        self, other_file: Union[str, "Config"]
    ) -> Dict[str, Any]:
        """
        Compare configuration with another file or Config object.

        Generates a detailed diff showing:
        - Keys added (prefix: +)
        - Keys removed (prefix: -)
        - Keys modified (prefix: ~)

        Args:
            other_file: Path to config file or Config object to compare with

        Returns:
            Dictionary with diff results, or error dict if comparison fails

        Example:
            >>> diff = analyzer.diff_with_file('other_config.yaml')
            >>> for key, value in diff.items():
            >>>     if key.startswith('+'):
            >>>         print(f"Added: {key}")
            >>>     elif key.startswith('-'):
            >>>         print(f"Removed: {key}")
            >>>     elif key.startswith('~'):
            >>>         print(f"Changed: {key}")
        """
        try:
            # Load the other configuration
            if isinstance(other_file, (Config, ConfigNode)):
                other_config = other_file
            else:
                other_config_data = load_config(str(other_file))
                other_config = Config(other_config_data)

            return self._diff_configs(self.config, other_config)
        except Exception as e:
            return {"error": f"Failed to load comparison file: {str(e)}"}

    def _diff_configs(
        self,
        config1: Union[Config, ConfigNode],
        config2: Union[Config, ConfigNode],
    ) -> Dict[str, Any]:
        """
        Internal method to compare two configurations.

        Args:
            config1: First configuration
            config2: Second configuration

        Returns:
            Dictionary with diff results
        """

        def dict_diff(d1: Dict, d2: Dict, path: str = "") -> Dict[str, Any]:
            """Recursively diff two dictionaries."""
            diff = {}

            # Check keys in d1 but not in d2 (removed)
            for key in d1:
                if key not in d2:
                    diff[f"+ {path}.{key}" if path else f"+ {key}"] = d1[key]
                elif isinstance(d1[key], dict) and isinstance(d2[key], dict):
                    # Both are dicts, recursively diff them
                    nested_diff = dict_diff(
                        d1[key], d2[key], f"{path}.{key}" if path else key
                    )
                    diff.update(nested_diff)
                elif d1[key] != d2[key]:
                    # Values differ
                    diff[f"~ {path}.{key}" if path else f"~ {key}"] = {
                        "old": d1[key],
                        "new": d2[key],
                    }

            # Check keys in d2 but not in d1 (added)
            for key in d2:
                if key not in d1:
                    diff[f"- {path}.{key}" if path else f"- {key}"] = d2[key]

            return diff

        return dict_diff(config1._data, config2._data)

    def get_loading_trace(self) -> List[Dict[str, Any]]:
        """
        Get the loading trace for configuration inheritance.

        Returns:
            List of loading steps with file paths, step numbers, and timestamps

        Example:
            >>> trace = analyzer.get_loading_trace()
            >>> for step in trace:
            >>>     print(f"Step {step['step']}: {step['file']}")
        """
        return self.loading_trace

    # Private helper methods

    def _calculate_max_depth(self, data: Any, current_depth: int = 0) -> int:
        """
        Calculate the maximum nesting depth of the configuration.

        Args:
            data: Data structure to analyze
            current_depth: Current depth level

        Returns:
            Maximum depth found
        """
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(
                self._calculate_max_depth(value, current_depth + 1)
                for value in data.values()
            )
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(
                self._calculate_max_depth(item, current_depth + 1)
                for item in data
            )
        else:
            return current_depth

    def _count_keys(self, data: Any) -> int:
        """
        Count the total number of keys in the configuration.

        Args:
            data: Data structure to count keys in

        Returns:
            Total number of keys
        """
        if isinstance(data, dict):
            return len(data) + sum(
                self._count_keys(value) for value in data.values()
            )
        elif isinstance(data, list):
            return sum(self._count_keys(item) for item in data)
        else:
            return 0
