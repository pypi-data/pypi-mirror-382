"""
Tahdig - Configuration with a Crispy Layer

A delightful configuration and registry system inspired by Detectron2.
Like the golden crust of Persian rice, Tahdig provides a solid foundation
with hierarchical configuration management, automatic parameter injection,
and elegant component registry.

Core Features
-------------

**Configuration System:**
- Nested configuration access with dot notation (e.g., `config.model.layers`)
- Environment variable substitution with defaults (`${VAR:default}`)
- Key protection and configuration freezing for safety
- Multiple file format support (YAML, JSON)
- Configuration inheritance using the `extends` keyword
- Deep merging of inherited configurations

**Registry System:**
- Component registration with decorator syntax (`@registry.register()`)
- Automatic parameter injection from configuration via `cfg` argument
- Support for functions, classes, and instances
- Metadata storage for registered components
- Hierarchical component initialization
- Custom config transformation functions

**Debugging & Validation:**
- Schema validation with custom validators
- Configuration linting for best practices
- Visual tree representation of config structure
- Performance profiling and memory tracking
- Interactive configuration explorer
- Diff comparison between configurations

Architecture
------------
- **ConfigNode**: Nested configuration container with attribute access
- **Config**: Main configuration class with file I/O capabilities
- **Registry**: Component registration and retrieval system
- **ConfigDebugger**: Comprehensive debugging and validation tools

Quick Start
-----------

Basic Configuration:
    >>> from tahdig import Config
    >>>
    >>> # Create configuration with nested structure
    >>> config = Config({
    >>>     'model': {
    >>>         'name': 'resnet50',
    >>>         'layers': 50,
    >>>         'pretrained': True
    >>>     },
    >>>     'training': {
    >>>         'batch_size': 32,
    >>>         'learning_rate': 0.001
    >>>     }
    >>> })
    >>>
    >>> # Access with dot notation
    >>> print(config.model.name)  # 'resnet50'
    >>> print(config.training.batch_size)  # 32
    >>>
    >>> # Freeze to prevent modifications
    >>> config.freeze()

Registry with Config-Aware Components:
    >>> from tahdig import Registry, Config
    >>>
    >>> # Create a registry instance
    >>> registry = Registry("services")
    >>>
    >>> # Register a class with automatic parameter injection
    >>> @registry.register()
    >>> class DatabaseService:
    >>>     def __init__(self, host, port, database, cfg=None):
    >>>         self.host = host
    >>>         self.port = port
    >>>         self.database = database
    >>>
    >>> # Create configuration
    >>> config = Config({
    >>>     'host': 'localhost',
    >>>     'port': 5432,
    >>>     'database': 'myapp'
    >>> })
    >>>
    >>> # Get factory and instantiate with config
    >>> ServiceFactory = registry.get("DatabaseService")
    >>> service = ServiceFactory(cfg=config)
    >>> print(service.host)  # "localhost"

Configuration Files with Inheritance:
    >>> # base_config.yaml
    >>> # model:
    >>> #   name: resnet50
    >>> #   layers: 50
    >>>
    >>> # production_config.yaml
    >>> # extends: base_config.yaml
    >>> # model:
    >>> #   pretrained: true  # Inherits name and layers from base
    >>>
    >>> config = Config.from_file('production_config.yaml')
    >>> print(config.model.name)  # 'resnet50' (inherited)
    >>> print(config.model.pretrained)  # True (new)

Environment Variables:
    >>> # config.yaml
    >>> # database:
    >>> #   host: ${DB_HOST:localhost}
    >>> #   port: ${DB_PORT:5432}
    >>>
    >>> config = Config.from_file('config.yaml')
    >>> # If DB_HOST is set, uses that value, otherwise uses 'localhost'

Version: 1.0.0
Package: Tahdig (تهدیگ)
Author: Fardin
License: MIT
Repository: https://github.com/fardin/tahdig
"""

# Core configuration classes and functions
from .config import Config, load_config, save_config, ConfigNode, deep_merge

# Registry system for component management
from .registry import Registry

# Exception hierarchy for proper error handling
from .exceptions import (
    # Base exceptions
    SimpleConfigError,  # Root exception for all simple_config errors
    # Registry exceptions
    RegistryError,  # Base for registry-related errors
    ComponentNotFoundError,  # Component not found in registry
    DuplicateComponentError,  # Duplicate component registration
    RegistryNotFoundError,  # Registry not found
    # Config exceptions
    ConfigError,  # Base for config-related errors
    ConfigKeyError,  # Invalid or disallowed config key
    ConfigFileNotFoundError,  # Config file not found
    UnsupportedFileFormatError,  # Unsupported file format
    ConfigSerializationError,  # Serialization/deserialization error
    EnvironmentVariableError,  # Environment variable substitution error
    CircularDependencyError,  # Circular dependency in config inheritance
    ConfigValidationError,  # Configuration validation error
    ConfigLintError,  # Configuration linting error
    # Decorator exceptions
    DecoratorError,  # Base for decorator-related errors
    ConfigurableError,  # Error in config-aware component
    ParameterExtractionError,  # Parameter extraction error
)

# Debugging and validation utilities
from .debug import (
    ConfigDebugger,  # Main debugging class with all tools
    create_debugger,  # Factory function for debugger
    validate_config,  # Quick validation function
    lint_config,  # Quick linting function
    visualize_config,  # Quick visualization function
)

# Package metadata
__version__ = "1.0.0"
__author__ = "Config System Team"
__license__ = "MIT"

# Public API - Organized by category
__all__ = [
    # === Configuration System ===
    "Config",  # Main configuration class with file I/O
    "ConfigNode",  # Nested configuration container with dot notation
    "load_config",  # Load configuration from file with inheritance
    "save_config",  # Save configuration to file (YAML/JSON)
    "deep_merge",  # Deep merge two configuration dictionaries
    # === Registry System ===
    "Registry",  # Component registry with automatic parameter injection
    # === Base Exceptions ===
    "SimpleConfigError",  # Root exception for all package errors
    # === Registry Exceptions ===
    "RegistryError",  # Base registry exception
    "ComponentNotFoundError",  # Component not found in registry
    "DuplicateComponentError",  # Duplicate component name
    "RegistryNotFoundError",  # Registry doesn't exist
    # === Configuration Exceptions ===
    "ConfigError",  # Base config exception
    "ConfigKeyError",  # Invalid/disallowed key access
    "ConfigFileNotFoundError",  # Config file not found
    "UnsupportedFileFormatError",  # Unsupported file format
    "ConfigSerializationError",  # Serialization failed
    "EnvironmentVariableError",  # Env var substitution failed
    "CircularDependencyError",  # Circular config inheritance
    "ConfigValidationError",  # Validation failure
    "ConfigLintError",  # Linting issue found
    # === Decorator Exceptions ===
    "DecoratorError",  # Base decorator exception
    "ConfigurableError",  # Config-aware component error
    "ParameterExtractionError",  # Parameter extraction failed
    # === Debugging & Validation ===
    "ConfigDebugger",  # Comprehensive debugging tools
    "create_debugger",  # Factory for creating debuggers
    "validate_config",  # Validate against schema
    "lint_config",  # Lint for best practices
    "visualize_config",  # Visualize config structure
]
