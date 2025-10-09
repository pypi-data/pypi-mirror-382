"""
Registry Builders for AI Provider Integration

This module provides builder functions for creating tool registries compatible
with various AI providers including Anthropic Claude, OpenAI, Mistral AI,
AWS Bedrock, and Google Gemini.
"""

import logging
from collections import OrderedDict
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from ._json_schema import InlineDefsJsonSchemaTransformer

if TYPE_CHECKING:
    from anthropic.types import ToolParam


logger = logging.getLogger(__name__)


class ToolRegistryError(Exception):
    """Exception for tool registry validation errors."""

    pass


def _build_registry_base[T](
    functions: list[Callable[..., T]],
    provider_name: str,
    build_representation_func: Callable[
        [Callable[..., Any], str], dict[str, Any] | Any
    ],
) -> dict[str, dict[str, Any]]:
    """
    Base function for building tool registries for any provider.

    Args:
        functions: List of functions decorated with @tool
        provider_name: Name of the provider (for logging)
        build_representation_func: Function to build provider-specific representation

    Returns:
        Dictionary mapping tool names to their registry entries
    """
    logger.info(
        f"Building {provider_name} tool registry for {len(functions)} functions"
    )

    registry: OrderedDict[str, dict[str, Any]] = OrderedDict()
    processed_count = 0
    skipped_count = 0

    for func in functions:
        if not hasattr(func, "_input_schema"):
            logger.warning(
                f"Skipping function {func.__name__}: not decorated with @tool"
            )
            skipped_count += 1
            continue

        func_name = func.__name__
        logger.debug(f"Processing tool: {func_name}")

        if func_name in registry:
            raise ToolRegistryError(
                f"Duplicate tool name '{func_name}' found. Each tool must have a unique name."
            )

        representation = build_representation_func(func, func_name)

        registry[func_name] = {
            "tool": func,
            "representation": representation,
        }

        processed_count += 1
        logger.debug(
            f"Successfully added {provider_name} tool to registry: {func_name}"
        )

    logger.info(
        f"{provider_name} registry building completed: {processed_count} tools processed, {skipped_count} functions skipped"
    )

    return registry


def build_registry_anthropic[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with Anthropic Claude API.

    This function takes a list of tool-decorated functions and creates a registry
    that can be used directly with Anthropic's tool calling API. Each tool in the
    registry includes both the callable function and its API representation.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": ToolParam object for Anthropic API

    Raises:
        ToolRegistryError: If registry building fails

    Example:
        ```python
        @tool(description="Add two numbers")
        def add(a: int, b: int) -> int:
            return a + b

        @tool(description="Multiply two numbers")
        def multiply(a: int, b: int) -> int:
            return a * b

        registry = build_registry_anthropic([add, multiply])

        # Use with Anthropic API
        tools = [entry["representation"] for entry in registry.values()]
        ```

    Note:
        Only functions with the @tool decorator will be included in the registry.
        Functions without tool metadata will be silently skipped.
    """

    def build_anthropic_representation(
        func: Callable[..., Any], func_name: str
    ) -> "ToolParam":
        from anthropic.types import ToolParam

        tool_param = ToolParam(
            name=func_name,
            description=getattr(func, "_description"),
            input_schema=getattr(func, "_input_schema"),
        )

        if getattr(func, "_cache_control"):
            tool_param["cache_control"] = getattr(func, "_cache_control")
            logger.debug(f"Added cache control for tool: {func_name}")

        return tool_param

    return _build_registry_base(
        functions,
        "Anthropic",
        build_anthropic_representation,
    )


def build_registry_openai[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with OpenAI Function Calling API.

    This function takes a list of tool-decorated functions and creates a registry
    that can be used directly with OpenAI's function calling API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in OpenAI function format

    Example:
        ```python
        registry = build_registry_openai([add, multiply])

        # Use with OpenAI API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """

    def build_openai_representation(
        func: Callable[..., Any], func_name: str
    ) -> dict[str, Any]:
        try:
            import openai  # type: ignore # noqa: F401
        except ImportError:
            pass

        return {
            "type": "function",
            "name": func_name,
            "description": getattr(func, "_description"),
            "parameters": getattr(func, "_input_schema"),
            "strict": True,
        }

    return _build_registry_base(functions, "OpenAI", build_openai_representation)


def build_registry_mistral[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with Mistral AI Function Calling API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in Mistral function format

    Example:
        ```python
        registry = build_registry_mistral([add, multiply])

        # Use with Mistral AI API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """

    def build_mistral_representation(
        func: Callable[..., Any], func_name: str
    ) -> dict[str, Any]:
        try:
            import mistralai  # type: ignore # noqa: F401
        except ImportError:
            pass

        return {
            "type": "function",
            "function": {
                "name": func_name,
                "description": getattr(func, "_description"),
                "parameters": getattr(func, "_input_schema"),
            },
        }

    return _build_registry_base(functions, "Mistral", build_mistral_representation)


def build_registry_bedrock[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with AWS Bedrock Converse API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in Bedrock tool format

    Example:
        ```python
        registry = build_registry_bedrock([add, multiply])

        # Use with AWS Bedrock API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """

    def build_bedrock_representation(
        func: Callable[..., Any], func_name: str
    ) -> dict[str, Any]:
        try:
            import boto3  # type: ignore  # noqa: F401, I001
        except ImportError:
            pass

        return {
            "toolSpec": {
                "name": func_name,
                "description": getattr(func, "_description"),
                "inputSchema": {
                    "json": InlineDefsJsonSchemaTransformer(
                        getattr(func, "_input_schema")
                    ).walk()
                },
            }
        }

    return _build_registry_base(functions, "Bedrock", build_bedrock_representation)


def build_registry_gemini[T](
    functions: list[Callable[..., T]],
) -> dict[str, dict[str, Any]]:
    """
    Build a tool registry compatible with Google Gemini Function Calling API.

    Args:
        functions: List of functions decorated with @tool

    Returns:
        Dictionary mapping tool names to their registry entries, where each entry contains:
        - "tool": The callable wrapper function
        - "representation": Dictionary in Gemini function format

    Example:
        ```python
        registry = build_registry_gemini([add, multiply])

        # Use with Google Gemini API
        tools = [entry["representation"] for entry in registry.values()]
        ```
    """

    def build_gemini_representation(
        func: Callable[..., Any], func_name: str
    ) -> dict[str, Any]:
        try:
            import google.generativeai as genai  # type: ignore  # noqa: F401, I001
        except ImportError:
            pass

        return {
            "name": func_name,
            "description": getattr(func, "_description"),
            "parameters": getattr(func, "_input_schema"),
        }

    return _build_registry_base(functions, "Gemini", build_gemini_representation)


def get_tool_info(
    registry: dict[str, dict[str, Any]], tool_name: str
) -> dict[str, Any]:
    """
    Get detailed information about a specific tool in the registry.

    Args:
        registry: Tool registry from build_registry_anthropic_tool_registry
        tool_name: Name of the tool to get information for

    Returns:
        Dictionary containing tool information

    Raises:
        KeyError: If tool is not found in registry
    """
    if tool_name not in registry:
        available_tools = list(registry.keys())
        raise KeyError(
            f"Tool '{tool_name}' not found. Available tools: {available_tools}"
        )

    tool_entry = registry[tool_name]
    wrapper_func = tool_entry["tool"]

    return {
        "name": tool_name,
        "description": wrapper_func._description,
        "schema": wrapper_func._input_schema,
        "cache_control": wrapper_func._cache_control,
        "ignored_parameters": wrapper_func._ignore_in_schema,
        "original_function": getattr(wrapper_func, "_original_func").__name__,
    }


def validate_registry(registry: dict[str, dict[str, Any]]) -> bool:
    """
    Validate that a tool registry has the correct structure.

    Args:
        registry: Tool registry to validate

    Returns:
        True if registry is valid

    Raises:
        ToolRegistryError: If registry is invalid
    """
    logger.info(f"Validating tool registry with {len(registry)} tools")

    for tool_name, tool_data in registry.items():
        if "tool" not in tool_data:
            raise ToolRegistryError(f"Tool '{tool_name}' missing 'tool' key")
        if "representation" not in tool_data:
            raise ToolRegistryError(f"Tool '{tool_name}' missing 'representation' key")

        tool_func = tool_data["tool"]
        required_attrs = ["_description", "_input_schema", "_original_func"]
        for attr in required_attrs:
            if not hasattr(tool_func, attr):
                raise ToolRegistryError(f"Tool '{tool_name}' missing attribute: {attr}")

        representation = tool_data["representation"]

        has_name = (
            "name" in representation
            or (representation.get("function", {}).get("name"))
            or (representation.get("toolSpec", {}).get("name"))
        )

        has_description = (
            "description" in representation
            or (representation.get("function", {}).get("description"))
            or (representation.get("toolSpec", {}).get("description"))
        )

        has_schema = (
            "input_schema" in representation
            or "parameters" in representation
            or (representation.get("function", {}).get("parameters"))
            or (representation.get("toolSpec", {}).get("inputSchema"))
        )

        if not has_name:
            raise ToolRegistryError(
                f"Tool '{tool_name}' representation missing name field"
            )
        if not has_description:
            raise ToolRegistryError(
                f"Tool '{tool_name}' representation missing description field"
            )
        if not has_schema:
            raise ToolRegistryError(
                f"Tool '{tool_name}' representation missing schema field"
            )

    logger.info("Tool registry validation completed successfully")
    return True


__all__ = [
    "build_registry_anthropic",
    "build_registry_openai",
    "build_registry_mistral",
    "build_registry_bedrock",
    "build_registry_gemini",
    "get_tool_info",
    "validate_registry",
    "ToolRegistryError",
]
