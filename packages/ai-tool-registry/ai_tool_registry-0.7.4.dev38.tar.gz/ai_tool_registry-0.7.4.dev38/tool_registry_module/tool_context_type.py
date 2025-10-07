import types
from typing import (
    Annotated,
    Union,  # pyright: ignore[reportDeprecated]
    get_args,
    get_origin,
)


class ToolContext[T]:
    """
    This is a generic type to mark a tool context variable in function inputs that will be ignored by the tool decorator
    """

    def __getattr__(self, name: str) -> T:
        """Type checking helper for accessing context attributes."""
        ...


class RunContext[T](ToolContext[T]):
    """
    Alias for ToolContext, compatible with PydanticAI naming conventions.

    This allows you to use RunContext[T] instead of ToolContext[T] for better
    compatibility with PydanticAI code patterns. Both are functionally identical.

    Example:
        @tool(description="Process user data")
        def process_user(
            user_id: str,
            ctx: RunContext[dict]  # Context parameter, excluded from schema
        ) -> str:
            ctx['last_user'] = user_id
            return f"Processed: {user_id}"
    """

    @property
    def deps(self) -> T:
        """
        PydanticAI compatibility property.

        In PydanticAI, context is accessed via ctx.deps.attribute_name.
        This property makes that pattern work by returning the context itself.

        At runtime, since the actual context object (type T) is passed to the tool,
        this property returns 'self', which IS the context object.

        Example:
            @tool
            def my_tool(ctx: RunContext[UserContext]) -> str:
                # Both of these work identically:
                name1 = ctx.deps.username  # PydanticAI style
                name2 = ctx.username        # Direct style
                return name1
        """
        return self  # pyright: ignore[reportReturnType]


Ctx = RunContext


def _is_tool_context_param(param: type) -> bool:
    if param is type(None):
        return False

    origin = get_origin(param)

    # Check if this is a direct ToolContext generic or its subclasses (e.g., ToolContext[str], RunContext[str])
    if (
        origin is not None
        and isinstance(origin, type)
        and issubclass(origin, ToolContext)
    ):
        return True

    # Also check for ToolContext itself without type parameters
    if origin is ToolContext:
        return True

    # Check if this is an Annotated type with ToolContext
    if origin is Annotated:
        args = get_args(param)
        for arg in args[1:]:  # pyright: ignore[reportAny]
            # Check for ToolContext class itself or its subclasses
            if arg is ToolContext:
                return True
            if isinstance(arg, type) and issubclass(arg, ToolContext):
                return True
            # Check for ToolContext generic instances (e.g., ToolContext[str], RunContext[dict])
            if hasattr(arg, "__origin__"):  # pyright: ignore[reportUnknownArgumentType]
                arg_origin = get_origin(arg)
                if (
                    arg_origin is not None
                    and isinstance(arg_origin, type)
                    and issubclass(arg_origin, ToolContext)
                ):
                    return True

    # Check for Union types (both typing.Union and types.UnionType)
    if origin is Union or origin is types.UnionType:  # pyright: ignore[reportDeprecated]
        args = get_args(param)
        for arg in args:  # pyright: ignore[reportAny]
            if arg is not type(None) and _is_tool_context_param(arg):  # pyright: ignore[reportAny]
                raise TypeError(
                    "The ToolContext should not be used as a union type as the variable needs to fill a single function to pass context between the agent loop and the given tool."
                )

    return False
