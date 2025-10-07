"""
Universal Tool Registry Module for AI Provider Integration

A sophisticated tool registration system that automatically converts Python functions
into AI provider tools with proper schema generation, validation, and error handling.
Supports multiple AI providers including Anthropic Claude, OpenAI, Mistral AI, AWS Bedrock, and Google Gemini.
"""

from .registry_builders import (
    ToolRegistryError,
    build_registry_anthropic,
    build_registry_bedrock,
    build_registry_gemini,
    build_registry_mistral,
    build_registry_openai,
    get_tool_info,
    validate_registry,
)
from .tool_context_type import Ctx, RunContext, ToolContext
from .tool_registry import create_schema_from_signature, tool

__version__ = "0.1.0"
__all__ = [
    "tool",
    "ToolContext",
    "RunContext",
    "Ctx",
    "build_registry_anthropic",
    "build_registry_openai",
    "build_registry_mistral",
    "build_registry_bedrock",
    "build_registry_gemini",
    "create_schema_from_signature",
    "get_tool_info",
    "validate_registry",
    "ToolRegistryError",
]
