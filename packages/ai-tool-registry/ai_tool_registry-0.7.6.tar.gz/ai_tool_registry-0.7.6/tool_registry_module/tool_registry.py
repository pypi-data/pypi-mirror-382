"""
Tool Registry Decorator for AI Provider Integration

This module provides the core tool decorator that automatically converts Python functions
into AI provider tools with proper schema generation, validation, and error handling.

Key Features:
- Automatic JSON schema generation from function signatures
- Pydantic model integration and validation
- Parameter filtering for internal/context parameters
- Comprehensive error handling and logging
- Type safety with full type hints

Usage Example:
    ```python
    from tool_registry_module import tool
    from pydantic import BaseModel


    class UserData(BaseModel):
        name: str
        age: int


    @tool(description="Process user information")
    def process_user(input: UserData, context: str = "default") -> UserData:
        return input
    ```

Author: Claude Code Assistant
Version: 3.0
"""

import inspect
import logging
import types
from collections.abc import Callable
from functools import wraps
from typing import (
    Annotated,
    Any,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from pydantic import ValidationError, create_model

from .tool_context_type import _is_tool_context_param

logger = logging.getLogger(__name__)


def create_schema_from_signature(
    func: Callable[..., Any], ignore_in_schema: list[str] | None = None
) -> dict[str, Any]:
    """
    Create a JSON schema from a function signature using Pydantic models.

    This function introspects a function's signature and creates a corresponding
    JSON schema that can be used by AI providers for tool calling. It handles
    both simple types and complex Pydantic models.

    Args:
        func: The function to generate schema for
        ignore_in_schema: List of parameter names to exclude from the schema

    Returns:
        A JSON schema dictionary compatible with AI provider tool formats

    Example:
        ```python
        def my_func(name: str, age: int = 25, context: str = "internal"):
            pass


        schema = create_schema_from_signature(my_func, ["context"])
        # Returns schema for 'name' and 'age' parameters only
        ```
    """
    if ignore_in_schema is None:
        ignore_in_schema = []

    sig = inspect.signature(func)
    hints = get_type_hints(func, include_extras=True)

    logger.debug(f"Generating schema for function: {func.__name__}")

    fields: dict[str, Any] = {}
    for param_name, param in sig.parameters.items():
        if param_name in ["args", "kwargs"] + ignore_in_schema:
            logger.debug(f"Skipping parameter: {param_name}")
            continue

        param_type = hints.get(param_name, Any)

        # Skip ToolContext parameters
        if _is_tool_context_param(param_type):
            logger.debug(f"Skipping ToolContext parameter: {param_name}")
            continue

        if param.default != inspect.Parameter.empty:
            fields[param_name] = (param_type, param.default)
            logger.debug(f"Added optional parameter: {param_name} = {param.default}")
        else:
            fields[param_name] = (param_type, ...)
            logger.debug(f"Added required parameter: {param_name}")

    if not fields:
        logger.warning(f"No fields found for function {func.__name__}")

    model_name = f"{func.__name__}InputModel"
    temp_model = create_model(model_name, **fields)

    schema = temp_model.model_json_schema()
    logger.debug(f"Generated schema for {func.__name__}: {len(fields)} fields")

    return schema


def _is_pydantic_model(param_type: type) -> bool:
    """
    Check if a type is a Pydantic model.

    Args:
        param_type: The type to check

    Returns:
        True if the type is a Pydantic model, False otherwise
    """
    return hasattr(param_type, "__bases__") and any(
        hasattr(base, "model_validate") for base in param_type.__mro__
    )


def _convert_parameter(param_type: type, param_value: Any) -> Any:
    """
    Convert a parameter value to the expected type.

    Args:
        param_name: Name of the parameter (for error messages)
        param_type: Expected type of the parameter
        param_value: The value to convert

    Returns:
        The converted parameter value
    """
    from enum import Enum

    # Handle None values
    if param_value is None:
        return param_value
    origin = get_origin(param_type)
    if origin is Annotated:
        param_type = get_args(param_type)[0]
        origin = get_origin(param_type)

    if origin is None:
        origin = getattr(param_type, "__origin__", None)

    args = getattr(param_type, "__args__", ())
    last_exception = None
    if origin is Union or isinstance(param_type, types.UnionType):
        for union_type in args:
            if union_type is type(None) and param_value is None:
                return None
            # Skip isinstance check for Any and parameterized generics
            if union_type is Any:
                return param_value  # Any accepts all values
            try:
                if isinstance(param_value, union_type):
                    return param_value
            except TypeError:
                # union_type is a parameterized generic, skip isinstance check
                pass

        last_exception = None
        for union_type in args:
            if union_type is type(None):
                continue
            try:
                return _convert_parameter(union_type, param_value)
            except (ValueError, ValidationError, TypeError) as e:
                last_exception = e
                continue

        if last_exception:
            raise last_exception

    elif origin is list:
        if args and isinstance(param_value, list):
            element_type = args[0]
            return [
                _convert_parameter(param_type=element_type, param_value=item)
                for item in param_value
            ]
        return param_value
    elif origin is dict:
        if len(args) == 2 and isinstance(param_value, dict):
            key_type, val_type = args
            return {
                _convert_parameter(
                    param_type=key_type, param_value=k
                ): _convert_parameter(param_type=val_type, param_value=v)
                for k, v in param_value.items()
            }

        # Only use isinstance for concrete types, not parameterized generics
    if get_origin(param_type) is None and not hasattr(param_type, "__args__"):
        if param_type is Any:
            return param_value  # Any accepts all values
        try:
            if isinstance(param_value, param_type):
                return param_value
        except TypeError:
            # Handle special forms that aren't valid isinstance targets
            pass

    if inspect.isclass(param_type) and issubclass(param_type, Enum):
        if isinstance(param_value, str):
            try:
                return param_type(param_value)
            except ValueError:
                # If direct value doesn't work, try by name
                for enum_member in param_type:
                    if enum_member.name.lower() == param_value.lower():
                        return enum_member
                raise ValueError(
                    f"Invalid enum value '{param_value}' for {param_type.__name__}"
                )
        return param_value

    basic_types = {int: int, float: float, str: str, bool: bool}

    if param_type in basic_types:
        try:
            return basic_types[param_type](param_value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert {param_value} to {param_type.__name__}: {e}"
            )

    if _is_pydantic_model(param_type):
        # Only use isinstance for concrete types, not parameterized generics
        if get_origin(param_type) is None and not hasattr(param_type, "__args__"):
            if isinstance(param_value, param_type):
                return param_value
        return param_type(**param_value)

    return param_value


@overload
def tool[T, **P](func: Callable[P, T]) -> Callable[P, T]: ...


@overload
def tool[T, **P](
    *,
    description: str | None = None,
    cache_control: Any | None = None,
    ignore_in_schema: list[str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]: ...


def tool[T, **P](
    func: Callable[P, T] | None = None,
    *,
    description: str | None = None,
    cache_control: Any | None = None,
    ignore_in_schema: list[str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]] | Callable[P, T]:
    """
    Decorator that converts a Python function into an AI provider tool.

    This decorator automatically generates JSON schemas from function signatures,
    handles Pydantic model validation, and provides parameter filtering capabilities.
    The resulting tool can be used with multiple AI providers including Anthropic Claude,
    OpenAI, Mistral AI, AWS Bedrock, and Google Gemini.

    Args:
        description: Human-readable description of what the tool does
        cache_control: Optional cache control settings (supported by some providers)
        ignore_in_schema: List of parameter names to exclude from the generated schema.
                         Useful for internal parameters like context or configuration.

    Returns:
        A decorator function that wraps the original function with tool capabilities

    Raises:
        SchemaGenerationError: If schema generation fails
        ToolValidationError: If parameter validation fails during execution

    Example:
        ```python
        @tool(
            description="Calculate the area of a rectangle",
            ignore_in_schema=["debug_mode"],
        )
        def calculate_area(
            length: float, width: float, debug_mode: bool = False
        ) -> float:
            if debug_mode:
                print(f"Calculating area for {length} x {width}")
            return length * width
        ```

    Note:
        The decorator preserves the original function's signature and behaviour while
        adding tool-specific metadata and automatic parameter conversion.
    """
    if ignore_in_schema is None:
        ignore_in_schema = []

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        logger.info(f"Registering tool: {func.__name__}")

        sig = inspect.signature(func)
        hints = get_type_hints(func, include_extras=True)

        # Generate schema for the function
        input_schema = create_schema_from_signature(func, ignore_in_schema or [])

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            """
            Tool wrapper that handles parameter conversion and validation.

            Args:
                *args: Positional arguments from tool invocation
                **kwargs: Keyword arguments from tool invocation

            Returns:
                Result from the original function
            """

            # Filter kwargs to only include parameters that the function accepts
            valid_params = set(sig.parameters.keys())
            filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}

            # Bind arguments and apply defaults
            bound_args = sig.bind(*args, **filtered_kwargs)
            bound_args.apply_defaults()

            # Convert parameters to expected types
            converted_kwargs = {}
            for param_name, param_value in bound_args.arguments.items():
                if param_name in ["args", "kwargs"]:
                    continue
                param_type = hints.get(param_name, Any)

                # Skip conversion for parameters that should be ignored or are ToolContext
                if (
                    param_type is Any
                    or _is_tool_context_param(param=param_type)
                    or param_name in (ignore_in_schema or [])
                ):
                    converted_kwargs[param_name] = param_value
                else:
                    converted_kwargs[param_name] = _convert_parameter(
                        param_type=param_type, param_value=param_value
                    )

            return func(**converted_kwargs)

        func_description = description if description else inspect.getdoc(func)
        if not func_description:
            func_description = func.__name__
        setattr(wrapper, "_description", func_description)
        setattr(wrapper, "_cache_control", cache_control)
        setattr(wrapper, "_input_schema", input_schema)
        setattr(wrapper, "_original_func", func)
        setattr(wrapper, "_ignore_in_schema", ignore_in_schema)

        logger.info(f"Successfully registered tool: {func.__name__}")
        return wrapper

    if func is not None:
        return decorator(func)

    return decorator


__all__ = [
    "tool",
    "create_schema_from_signature",
]
