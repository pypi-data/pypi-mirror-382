"""
Core registry implementation.

This module provides a flexible registry system for storing and retrieving
components (functions, classes, instances) by name. The registry supports
metadata, decorator-based registration, and fluent API patterns.

Key Features:
- Component registration and retrieval by name
- Metadata support for components
- Decorator-based registration with fluent API
- Duplicate component handling with override option
- Type-safe component handling
- Optional config-aware initialization when calling registered components

Examples:
    >>> registry = Registry("my_components")
    >>>
    >>> # Register a simple function
    >>> @registry.register("my_function")
    >>> def my_function():
    >>>     return "Hello"
    >>>
    >>> component = registry.get("my_function")
    >>> print(component())  # "Hello"

    >>> # Register a class with config-aware initialization
    >>> @registry.register()
    >>> class Service:
    >>>     def __init__(self, host, port, cfg=None):
    >>>         self.host = host
    >>>         self.port = port
    >>>
    >>> # Call with cfg to initialize from configuration automatically
    >>> cfg = ConfigNode({"host": "localhost", "port": 8080})
    >>> ServiceFactory = registry.get("Service")
    >>> service = ServiceFactory(cfg=cfg)
    >>> print(service.host)  # "localhost"

    >>> # Custom name and custom config function
    >>> def init_params_from_cfg(cfg):
    >>>     return {"host": cfg.host, "port": cfg.port}
    >>>
    >>> @registry.register("custom_service", config_fn=init_params_from_cfg)
    >>> class CustomService:
    >>>     def __init__(self, host, port):
    >>>         self.host = host
    >>>         self.port = port
"""

from typing import (
    Any,
    Dict,
    List,
    Callable,
    Optional,
    Sequence,
    Type,
    get_type_hints,
)
import inspect
from functools import wraps
from .exceptions import (
    ComponentNotFoundError,
    DuplicateComponentError,
    ParameterExtractionError,
)
from .constants import COMPONENT_NOT_FOUND_MSG, DUPLICATE_COMPONENT_MSG
from .config import ConfigNode


def _extract_hierarchical_params(
    init_func,
    cfg: ConfigNode,
    type_hints: Dict[str, Type],
    registry: Optional["Registry"] = None,
) -> Dict[str, Any]:
    """
    Extract parameters from config for hierarchical configurable classes.

    Args:
        init_func: The __init__ function
        cfg: The configuration node
        type_hints: Type hints for the function
        registry: Optional registry to look up classes by parameter name

    Returns:
        Dictionary of parameters
    """
    sig = inspect.signature(init_func)
    params = {}

    for param_name in sig.parameters:
        if param_name == "cfg" or param_name == "self":
            continue

        # Get the parameter type
        param_type = type_hints.get(param_name)

        # Try to find the value in config sections
        value = None

        # First, try to find a section that matches the parameter name
        for section_name in dir(cfg):
            if (
                not section_name.startswith("_")
                and section_name.upper() == param_name.upper()
            ):
                section_obj = getattr(cfg, section_name)
                if isinstance(section_obj, ConfigNode) and section_obj._data:
                    value = section_obj
                    break

        # If not found, try to find the parameter in any section that contains it
        if value is None:
            for section_name in dir(cfg):
                if not section_name.startswith("_"):
                    section_obj = getattr(cfg, section_name)
                    if hasattr(section_obj, param_name):
                        param_value = getattr(section_obj, param_name)
                        # Only use if it's not an empty ConfigNode (which means it was found via __getattr__)
                        if not (
                            isinstance(param_value, ConfigNode)
                            and not param_value._data
                        ):
                            value = param_value
                            break

        # If still not found, try direct access
        if value is None and hasattr(cfg, param_name):
            direct_value = getattr(cfg, param_name)
            if not (
                isinstance(direct_value, ConfigNode) and not direct_value._data
            ):
                value = direct_value

        if value is not None:
            # Check if this should be a configurable class instance
            # Handle both regular classes and configurable-wrapped classes
            actual_class = param_type
            if param_type and hasattr(param_type, "__wrapped__"):
                actual_class = param_type.__wrapped__  # type: ignore[union-attr]

            # If no type hint, try to look up in registry
            if (
                not actual_class
                and registry
                and isinstance(value, (ConfigNode, dict))
            ):

                def try_lookup(lookup_name: str):
                    """Try to get original class from registry by name."""
                    registered_component = registry.get(lookup_name)
                    if registered_component:
                        # Check if it's a class
                        if inspect.isclass(registered_component):
                            return registered_component
                        # Check if it's a wrapped class (factory function)
                        # Look for original_component in metadata
                        meta = registry._metadata.get(lookup_name, {})
                        original = meta.get("original_component")
                        if original and inspect.isclass(original):
                            return original
                    return None

                # Check for explicit 'type' field in config
                type_name = None
                if isinstance(value, ConfigNode):
                    if hasattr(value, "type") and not (
                        isinstance(getattr(value, "type"), ConfigNode)
                        and not getattr(value, "type")._data
                    ):
                        type_name = value.type
                elif isinstance(value, dict) and "type" in value:
                    type_name = value["type"]

                if type_name:
                    actual_class = try_lookup(type_name)

            # Check if it's a configurable class (wrapped by @configurable decorator)
            is_configurable_class = False
            if actual_class and hasattr(actual_class, "__wrapped__"):
                # It's a configurable class wrapped by the decorator
                is_configurable_class = inspect.isclass(
                    actual_class.__wrapped__
                )
                actual_class = actual_class.__wrapped__
            elif actual_class:
                # It's a regular class
                is_configurable_class = inspect.isclass(actual_class)

            condition = actual_class and is_configurable_class

            if condition:
                # Check if the class is configurable
                if hasattr(actual_class, "__init__"):
                    init_sig = inspect.signature(actual_class.__init__)  # type: ignore[misc]
                    if "cfg" in init_sig.parameters:
                        try:
                            # Create instance with the config section
                            # Filter out 'type' field as it's metadata, not a parameter
                            if isinstance(value, ConfigNode):
                                config_data = value.to_dict()
                            else:
                                config_data = dict(value)

                            # Remove 'type' field if present
                            config_data.pop("type", None)
                            config_section = ConfigNode(config_data)

                            # Use recursive hierarchical extraction for nested class
                            nested_type_hints = get_type_hints(
                                actual_class.__init__
                            )  # type: ignore[misc]
                            nested_params = _extract_hierarchical_params(
                                actual_class.__init__,  # type: ignore[misc]
                                config_section,
                                nested_type_hints,
                                registry,  # Pass registry for recursive lookup
                            )
                            instance = actual_class(**nested_params)  # type: ignore[misc]
                            params[param_name] = instance
                            continue
                        except Exception:
                            # If creation fails, fall back to regular value
                            pass

            # Regular value handling
            if isinstance(value, ConfigNode):
                params[param_name] = value.to_dict()
            else:
                params[param_name] = value

    return params


def _config_to_params(
    func: Callable, cfg: ConfigNode, registry: Optional["Registry"] = None
) -> Dict[str, Any]:
    """
    Convert a ConfigNode to function parameters by matching config keys to parameter names.
    Uses hierarchical parameter extraction by default.

    Args:
        func: The function to get parameter names from
        cfg: The configuration node
        registry: Optional registry to look up classes by parameter name

    Returns:
        Dictionary of parameters

    Raises:
        ParameterExtractionError: If parameter extraction fails
    """
    try:
        # Get type hints for the function
        # Try to get type hints from the decorated function first, then fall back to original
        type_hints = get_type_hints(func)
        original_func = func

        if not type_hints and hasattr(func, "__wrapped__"):
            original_func = func.__wrapped__
            type_hints = get_type_hints(original_func)

        # Filter type hints to only include parameters that are actually in the signature
        sig = inspect.signature(original_func)
        filtered_type_hints = {
            name: type_hints.get(name)
            for name in sig.parameters
            if name in type_hints
        }

        # Use hierarchical parameter extraction
        return _extract_hierarchical_params(
            original_func, cfg, filtered_type_hints, registry
        )  # type: ignore[arg-type]
    except Exception as e:
        if isinstance(e, ParameterExtractionError):
            raise
        raise ParameterExtractionError(
            f"Failed to extract parameters for {func.__name__}: {e}"
        )


class Registry:
    """
    A flexible registry for storing and retrieving components by name.

    This class provides a registry system that can store functions, classes,
    and instances with optional metadata. It supports decorator-based
    registration and provides methods for component management. Registered
    callables are wrapped to support config-aware invocation: when called with
    a 'cfg' keyword argument, parameters are extracted from the configuration
    automatically, or via user-provided hooks.

    Attributes:
        name (str): Name of the registry
        _components (Dict[str, Any]): Dictionary storing components by name
        _metadata (Dict[str, Dict[str, Any]]): Dictionary storing component metadata

    Example:
        >>> registry = Registry("my_components")
        >>>
        >>> @registry.register("my_function")
        >>> def my_function():
        >>>     return "Hello"
        >>>
        >>> component = registry.get("my_function")
        >>> print(component())  # "Hello"
    """

    def __init__(self, name: str = "default"):
        """
        Initialize a Registry instance.

        Args:
            name: Name of the registry (default: "default")
        """
        self.name = name
        self._components: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str = None,
        component: Any = None,
        metadata: Dict[str, Any] = None,
        override: bool = False,
        *,
        config_fn: Optional[Callable[[Any], Dict[str, Any]]] = None,
        config_method_names: Optional[Sequence[str]] = None,
    ):
        """
        Register a component in this registry.

        Supports both decorator usage and direct callable usage. Registered
        callables are wrapped to accept an optional 'cfg' keyword argument at
        call time for config-aware invocation.

        Decorator usage:
            @registry.register("my_function")
            def my_function():
                return "Hello"

            @registry.register("MyClass", {"version": "1.0"})
            class MyClass:
                pass

            # Using as a decorator without parentheses
            @registry.register
            def another_function():
                pass

            # Config-aware: default name, infer params from cfg
            @registry.register()
            class Service:
                def __init__(self, host, port, cfg=None):
                    self.host = host
                    self.port = port

            # Config-aware with custom parameter extractor
            def make_params(cfg):
                return {"host": cfg.host, "port": cfg.port}

            @registry.register("service", config_fn=make_params)
            class Service2:
                def __init__(self, host, port):
                    self.host = host
                    self.port = port

        Direct callable usage:
            registry.register("my_function", my_function)
            registry.register("MyClass", MyClass, {"version": "1.0"})

        Args:
            name: Name to register the component under. When omitted in decorator
                form, defaults to the function or class name.
            component: Component to register (class, function, or instance). Used
                only in direct callable usage.
            metadata: Optional metadata about the component.
            override: If True, allow overriding an existing component with the
                same name.
            config_fn: Optional callable taking a single 'cfg' argument and
                returning a dict of keyword arguments for the callable (or class
                constructor). If provided, it is used to translate cfg into
                parameters.
            config_method_names: Optional sequence of class method names to look
                for on classes, in order, when 'cfg' is provided. Defaults to
                ("from_config", "from_cfg"). If the method returns a dict it will
                be passed as kwargs to the constructor; if it returns an instance,
                that instance will be used directly.

        Returns:
            The wrapped component (for decorator usage) or None (for direct
            callable usage).

        Raises:
            DuplicateComponentError: If a component with the same name already
                exists and override is False.

        Notes:
            - For functions, when calling the registered callable with a 'cfg'
              keyword argument, parameters are derived from 'cfg' via
              'config_fn' if provided, otherwise via hierarchical extraction.
            - For classes, when calling the registered factory with a 'cfg'
              keyword argument, resolution order is: 'config_fn' -> class method
              in 'config_method_names' -> hierarchical extraction using __init__.
        """

        def decorator(comp: Any) -> Any:
            component_name = name or comp.__name__

            # Wrap by default for decorator usage to enable config-aware functionality
            # Only skip wrapping if explicitly disabled (not implemented yet)
            should_wrap = True
            if should_wrap:
                wrapped = self._wrap_component_for_config(
                    comp,
                    config_fn=config_fn,
                    config_method_names=config_method_names,
                )
                meta = dict(metadata or {})
                if "original_component" not in meta:
                    meta["original_component"] = comp
                self._register_component(
                    component_name, wrapped, meta, override
                )
            else:
                # Store component directly without wrapping
                self._register_component(
                    component_name, comp, metadata, override
                )

            # Return original component to preserve type identity at definition site
            return comp

        # Handle direct callable usage: registry.register("name", component)
        if component is not None and not isinstance(component, dict):
            # This is a direct call with a component (not metadata)
            if name is None:
                name = getattr(component, "__name__", str(component))

            # Only wrap if config-related parameters are provided
            should_wrap = (
                config_fn is not None or config_method_names is not None
            )
            if should_wrap:
                wrapped = self._wrap_component_for_config(
                    component,
                    config_fn=config_fn,
                    config_method_names=config_method_names,
                )
                meta = dict(metadata or {})
                if "original_component" not in meta:
                    meta["original_component"] = component
                self._register_component(name, wrapped, meta, override)
            else:
                # Store component directly without wrapping
                self._register_component(name, component, metadata, override)
            return None
        elif (
            component is not None
            and isinstance(component, dict)
            and metadata is None
        ):
            # This is likely a decorator call with metadata: @registry.register("name", metadata)
            # The component is actually metadata, and we need to return a decorator
            actual_metadata = component

            def decorator_with_metadata(comp: Any) -> Any:
                component_name = name or comp.__name__

                # Wrap by default for decorator usage to enable config-aware functionality
                should_wrap = True
                if should_wrap:
                    wrapped = self._wrap_component_for_config(
                        comp,
                        config_fn=config_fn,
                        config_method_names=config_method_names,
                    )
                    meta = dict(actual_metadata or {})
                    if "original_component" not in meta:
                        meta["original_component"] = comp
                    self._register_component(
                        component_name, wrapped, meta, override
                    )
                else:
                    # Store component directly without wrapping
                    self._register_component(
                        component_name, comp, actual_metadata, override
                    )

                # Return original component to preserve type identity
                return comp

            return decorator_with_metadata

        # Handle decorator usage
        if callable(name):
            # Called without parentheses: @registry.register
            comp = name
            component_name = comp.__name__

            # Wrap by default for decorator usage to enable config-aware functionality
            should_wrap = True
            if should_wrap:
                wrapped = self._wrap_component_for_config(
                    comp,
                    config_fn=config_fn,
                    config_method_names=config_method_names,
                )
                meta = dict(metadata or {})
                if "original_component" not in meta:
                    meta["original_component"] = comp
                self._register_component(
                    component_name, wrapped, meta, override
                )
            else:
                # Store component directly without wrapping
                self._register_component(
                    component_name, comp, metadata, override
                )

            # Return original component to preserve type identity
            return comp
        else:
            # Called with parentheses: @registry.register("name") or @registry.register()
            return decorator

    def _register_component(
        self,
        name: str,
        component: Any,
        metadata: Dict[str, Any] = None,
        override: bool = False,
    ) -> None:
        """
        Internal method to register a component with the given name.

        Args:
            name: Unique name for the component
            component: Component to register (class, function, or instance)
            metadata: Optional metadata about the component
            override: If True, allow overriding existing components

        Raises:
            DuplicateComponentError: If component with name already exists and override=False
        """
        if name in self._components and not override:
            raise DuplicateComponentError(
                DUPLICATE_COMPONENT_MSG.format(name, self.name)
            )

        self._components[name] = component
        self._metadata[name] = metadata or {}

    def _wrap_component_for_config(
        self,
        component: Any,
        *,
        config_fn: Optional[Callable[[Any], Dict[str, Any]]] = None,
        config_method_names: Optional[Sequence[str]] = None,
    ) -> Any:
        """
        Wrap a component to support config-aware initialization/invocation.

        If called with a 'cfg' keyword argument, the wrapper will:
        - Use the provided config_fn(cfg) if given
        - Else, for classes, look for a class method named in config_method_names
          (defaults to ["from_config", "from_cfg"]) and use it to get parameters
          or an instance
        - Else, fall back to automatic parameter extraction using hierarchical
          rules (_config_to_params) for functions or class __init__

        If 'cfg' is not provided, behavior is identical to the original component.
        """
        default_method_names = (
            ("from_config", "from_cfg")
            if config_method_names is None
            else tuple(config_method_names)
        )

        is_class = inspect.isclass(component)

        def resolve_params_via_hierarchy(
            target_callable: Callable, cfg: Any
        ) -> Dict[str, Any]:
            node = cfg if isinstance(cfg, ConfigNode) else ConfigNode(cfg or {})
            return _config_to_params(target_callable, node, self)

        if not callable(component):
            return component

        if not is_class:

            @wraps(component)
            def func_wrapper(*args, **kwargs):
                if "cfg" in kwargs:
                    cfg = kwargs.pop("cfg")
                    if config_fn is not None:
                        params = config_fn(cfg) or {}
                    else:
                        params = resolve_params_via_hierarchy(component, cfg)
                    # kwargs take precedence
                    kwargs = {**params, **kwargs}
                return component(*args, **kwargs)

            return func_wrapper

        # Component is a class
        def class_factory(*args, **kwargs):
            if "cfg" in kwargs:
                cfg = kwargs.pop("cfg")
                # 1) Custom config_fn
                if config_fn is not None:
                    params = config_fn(cfg) or {}
                    return component(**{**params, **kwargs})
                # 2) Named class methods
                for method_name in default_method_names:
                    if hasattr(component, method_name):
                        method = getattr(component, method_name)
                        try:
                            result = method(cfg)
                            # If method returns a dict, treat as kwargs
                            if isinstance(result, dict):
                                return component(**{**result, **kwargs})
                            # If it returns an instance, use it directly
                            return result
                        except Exception:
                            # Fall back to hierarchical extraction
                            break
                # 3) Fallback to hierarchical extraction using __init__
                params = resolve_params_via_hierarchy(component.__init__, cfg)
                return component(**{**params, **kwargs})
            # No cfg provided
            return component(*args, **kwargs)

        # Preserve some metadata
        try:
            class_factory.__name__ = component.__name__
            class_factory.__doc__ = component.__doc__
        except Exception:
            pass
        return class_factory

    def get(self, name: str, default: Any = None) -> Any:
        """
        Get a component by name.

        Args:
            name: Name of the component
            default: Default value if component not found

        Returns:
            Registered component or default value
        """
        return self._components.get(name, default)

    def get_required(self, name: str) -> Any:
        """
        Get a component by name, raising an error if not found.

        Args:
            name: Name of the component

        Returns:
            Registered component

        Raises:
            ComponentNotFoundError: If component not found
        """
        if name not in self._components:
            raise ComponentNotFoundError(
                COMPONENT_NOT_FOUND_MSG.format(name, self.name)
            )
        return self._components[name]

    def build(self, cfg: Any) -> Any:
        """
        Build an instance directly from a config with a 'type' field.

        This method reads the 'type' field from the config to determine which
        class to instantiate, then uses the remaining config as parameters.

        Args:
            cfg: Configuration object or dict with a 'type' field specifying
                 the class name to instantiate

        Returns:
            Instance of the class specified by the 'type' field

        Raises:
            ValueError: If 'type' field is missing or invalid
            ComponentNotFoundError: If the specified type is not registered

        Example:
            >>> registry = Registry("app")
            >>>
            >>> @registry.register()
            ... class Database:
            ...     def __init__(self, host, port, cfg=None):
            ...         self.host = host
            ...         self.port = port
            >>>
            >>> config = Config({
            ...     'type': 'Database',
            ...     'host': 'localhost',
            ...     'port': 5432
            ... })
            >>>
            >>> db = registry.build(cfg=config)
            >>> assert isinstance(db, Database)
        """
        # Convert to ConfigNode if needed
        config_node = (
            cfg if isinstance(cfg, ConfigNode) else ConfigNode(cfg or {})
        )

        # Extract type field
        type_name = None
        if hasattr(config_node, "type") and not (
            isinstance(getattr(config_node, "type"), ConfigNode)
            and not getattr(config_node, "type")._data
        ):
            type_name = config_node.type
        elif isinstance(cfg, dict) and "type" in cfg:
            type_name = cfg["type"]

        if not type_name:
            raise ValueError(
                "Config must have a 'type' field specifying the class to build"
            )

        # Get the component factory
        component_factory = self.get(type_name)
        if component_factory is None:
            raise ComponentNotFoundError(
                COMPONENT_NOT_FOUND_MSG.format(type_name, self.name)
            )

        # Build the instance using cfg parameter
        return component_factory(cfg=config_node)

    def list_components(self) -> List[str]:
        """
        List all registered component names.

        Returns:
            List of component names
        """
        return list(self._components.keys())

    def get_metadata(self, name: str) -> Dict[str, Any]:
        """
        Get metadata for a component.

        Args:
            name: Name of the component

        Returns:
            Component metadata dictionary
        """
        return self._metadata.get(name, {})

    def unregister(self, name: str) -> Any:
        """
        Unregister a component.

        Args:
            name: Name of the component to unregister

        Returns:
            The unregistered component

        Raises:
            ComponentNotFoundError: If component not found
        """
        if name not in self._components:
            raise ComponentNotFoundError(
                COMPONENT_NOT_FOUND_MSG.format(name, self.name)
            )

        component = self._components.pop(name)
        self._metadata.pop(name, None)
        return component

    def clear(self) -> None:
        """Clear all registered components."""
        self._components.clear()
        self._metadata.clear()

    def __contains__(self, name: str) -> bool:
        """Check if a component is registered."""
        return name in self._components

    def __len__(self) -> int:
        """Get number of registered components."""
        return len(self._components)

    def has_component(self, name: str) -> bool:
        """
        Check if a component is registered.

        Args:
            name: Name of the component

        Returns:
            True if component is registered, False otherwise
        """
        return name in self._components

    def remove_component(self, name: str) -> Any:
        """
        Remove a component from the registry.

        Args:
            name: Name of the component to remove

        Returns:
            The removed component

        Raises:
            ComponentNotFoundError: If component not found
        """
        return self.unregister(name)

    def __repr__(self) -> str:
        return (
            f"Registry(name='{self.name}', components={len(self._components)})"
        )


def create_registry(name: str) -> Registry:
    """
    Create a new registry.

    Args:
        name: Name for the new registry

    Returns:
        New Registry instance
    """
    return Registry(name)
