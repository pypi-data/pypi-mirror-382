"""
Tests for PydanticAI compatibility features.

This module tests that RunContext and Ctx aliases work identically to ToolContext,
allowing drop-in compatibility with PydanticAI naming conventions.
"""

from dataclasses import dataclass
from typing import Annotated

from tool_registry_module import Ctx, RunContext, ToolContext, tool
from tool_registry_module.tool_context_type import _is_tool_context_param


class TestPydanticAICompatibility:
    """Test PydanticAI compatibility aliases and naming conventions."""

    def test_run_context_is_subclass_of_tool_context(self):
        """Test that RunContext is a proper subclass of ToolContext."""
        assert issubclass(RunContext, ToolContext)

    def test_ctx_is_run_context_alias(self):
        """Test that Ctx is an alias for RunContext."""
        assert Ctx is RunContext

    def test_run_context_detection(self):
        """Test that RunContext parameters are detected as tool context."""
        assert _is_tool_context_param(RunContext[str]) is True
        assert _is_tool_context_param(RunContext[int]) is True
        assert _is_tool_context_param(RunContext[dict]) is True

    def test_ctx_detection(self):
        """Test that Ctx parameters are detected as tool context."""
        assert _is_tool_context_param(Ctx[str]) is True
        assert _is_tool_context_param(Ctx[dict]) is True

    def test_annotated_run_context_detection(self):
        """Test that Annotated RunContext types are detected."""
        assert _is_tool_context_param(Annotated[str, RunContext]) is True
        assert _is_tool_context_param(Annotated[dict, RunContext[dict]]) is True

    def test_annotated_ctx_detection(self):
        """Test that Annotated Ctx types are detected."""
        assert _is_tool_context_param(Annotated[str, Ctx]) is True
        assert _is_tool_context_param(Annotated[dict, Ctx[dict]]) is True

    def test_tool_decorator_with_run_context(self):
        """Test that @tool decorator properly handles RunContext parameters."""

        @tool(description="Test function with RunContext")
        def test_function(user_id: str, ctx: RunContext[dict], message: str) -> str:
            return f"User {user_id}: {message}"

        schema = getattr(test_function, "_input_schema")
        properties = schema["properties"]

        assert "user_id" in properties
        assert "message" in properties
        assert "ctx" not in properties
        assert len(properties) == 2

    def test_tool_decorator_with_ctx_alias(self):
        """Test that @tool decorator properly handles Ctx parameters."""

        @tool(description="Test function with Ctx")
        def test_function(name: str, ctx: Ctx[dict]) -> str:
            return f"Hello {name}"

        schema = getattr(test_function, "_input_schema")
        properties = schema["properties"]

        assert "name" in properties
        assert "ctx" not in properties
        assert len(properties) == 1

    def test_pydantic_ai_style_function_signature(self):
        """Test function signature that mimics PydanticAI patterns."""

        @tool(description="Generate persona demographics")
        async def create_persona(ctx: RunContext[dict], demographics: dict) -> str:
            ctx["call_count"] = ctx.get("call_count", 0) + 1
            return f"Created persona with demographics: {demographics}"

        schema = getattr(create_persona, "_input_schema")
        properties = schema["properties"]

        assert "demographics" in properties
        assert "ctx" not in properties
        assert len(properties) == 1

    def test_mixed_context_types(self):
        """Test function using both ToolContext and RunContext."""

        @tool(description="Mixed context types")
        def mixed_contexts(
            param: str,
            tool_ctx: ToolContext[dict],
            run_ctx: RunContext[dict],
            ctx_alias: Ctx[dict],
        ) -> str:
            return param

        schema = getattr(mixed_contexts, "_input_schema")
        properties = schema["properties"]

        assert "param" in properties
        assert "tool_ctx" not in properties
        assert "run_ctx" not in properties
        assert "ctx_alias" not in properties
        assert len(properties) == 1

    def test_run_context_reference_preservation(self):
        """Test that RunContext parameters maintain references like ToolContext."""

        @tool(description="Modify RunContext")
        def modify_run_context(action: str, ctx: RunContext[dict]) -> str:
            ctx["actions"] = ctx.get("actions", [])
            ctx["actions"].append(action)
            return f"Action: {action}"

        context = {"initial": True}
        original_id = id(context)

        result = modify_run_context(action="test", ctx=context)

        assert id(context) == original_id
        assert context["initial"] is True
        assert context["actions"] == ["test"]
        assert result == "Action: test"

    def test_ctx_alias_reference_preservation(self):
        """Test that Ctx alias maintains references."""

        @tool(description="Modify Ctx")
        def modify_ctx(message: str, ctx: Ctx[list]) -> str:
            ctx.append(message)
            return f"Added: {message}"

        context = ["start"]
        original_id = id(context)

        result = modify_ctx(message="test", ctx=context)

        assert id(context) == original_id
        assert context == ["start", "test"]
        assert result == "Added: test"

    def test_annotated_run_context_in_function(self):
        """Test Annotated RunContext in function signature."""

        @tool(description="Annotated RunContext test")
        def annotated_run_context_func(
            param: str,
            session: Annotated[dict, RunContext, "session context"],
        ) -> str:
            return param

        schema = getattr(annotated_run_context_func, "_input_schema")
        properties = schema["properties"]

        assert "param" in properties
        assert "session" not in properties
        assert len(properties) == 1

    def test_pydantic_ai_migration_example(self):
        """Test a realistic PydanticAI-style function after migration."""

        class AgentDeps:
            def __init__(self):
                self.call_count = 0
                self.personas = []

        @tool(description="List generated personas")
        async def list_generated_personas(ctx: RunContext[AgentDeps]) -> str:
            ctx.call_count += 1
            return f"Listed {len(ctx.personas)} personas (call #{ctx.call_count})"

        schema = getattr(list_generated_personas, "_input_schema")
        properties = schema["properties"]

        assert len(properties) == 0

        deps = AgentDeps()
        deps.personas = ["persona1", "persona2"]

        import asyncio

        result = asyncio.run(list_generated_personas(ctx=deps))

        assert deps.call_count == 1
        assert "2 personas" in result
        assert "call #1" in result

    def test_all_three_aliases_interchangeable(self):
        """Test that ToolContext, RunContext, and Ctx are all detected the same."""

        @tool(description="Three aliases")
        def three_aliases(
            data: str,
            tc: ToolContext[dict],
            rc: RunContext[dict],
            ctx: Ctx[dict],
        ) -> str:
            return data

        schema = getattr(three_aliases, "_input_schema")
        properties = schema["properties"]

        assert "data" in properties
        assert "tc" not in properties
        assert "rc" not in properties
        assert "ctx" not in properties
        assert len(properties) == 1

    def test_type_hints_preserved(self):
        """Test that type hints work correctly with all aliases."""
        from typing import get_type_hints

        @tool(description="Type hints test")
        def type_hints_func(
            param: str, tc: ToolContext[dict], rc: RunContext[list], ctx: Ctx[set]
        ) -> str:
            return param

        hints = get_type_hints(type_hints_func, include_extras=True)

        assert "param" in hints
        assert "tc" in hints
        assert "rc" in hints
        assert "ctx" in hints


class TestDataclassCompatibility:
    """Test that RunContext/Ctx work with dataclass context objects."""

    def test_run_context_with_dataclass(self):
        """Test RunContext with a dataclass context object."""

        @dataclass
        class AgentDeps:
            call_count: int = 0
            personas: list[str] | None = None

            def __post_init__(self):
                if self.personas is None:
                    self.personas = []

        @tool(description="Test with dataclass RunContext")
        def create_persona(name: str, ctx: RunContext[AgentDeps]) -> str:
            ctx.call_count += 1
            ctx.personas.append(name)  # type: ignore
            return f"Created {name}"

        schema = getattr(create_persona, "_input_schema")
        properties = schema["properties"]

        assert "name" in properties
        assert "ctx" not in properties
        assert len(properties) == 1

        deps = AgentDeps()
        result = create_persona(name="Alice", ctx=deps)

        assert result == "Created Alice"
        assert deps.call_count == 1
        assert deps.personas == ["Alice"]

    def test_ctx_alias_with_dataclass(self):
        """Test Ctx alias with a dataclass context object."""

        @dataclass
        class SessionContext:
            messages: list[str] | None = None
            user_id: str = "unknown"

            def __post_init__(self):
                if self.messages is None:
                    self.messages = []

        @tool(description="Add message with Ctx")
        def add_message(text: str, ctx: Ctx[SessionContext]) -> str:
            ctx.messages.append(text)  # type: ignore
            return f"Added: {text}"

        session = SessionContext(user_id="user123")
        result = add_message(text="Hello", ctx=session)

        assert result == "Added: Hello"
        assert session.messages == ["Hello"]
        assert session.user_id == "user123"

    def test_pydantic_ai_migration_realistic_example(self):
        """Test a realistic PydanticAI migration scenario with dataclass deps."""

        @dataclass
        class PopulationDeps:
            shared_data: dict[str, list[str]] | None = None
            user_id: str = ""
            generation_count: int = 0

            def __post_init__(self):
                if self.shared_data is None:
                    self.shared_data = {}

        @tool(description="Generate population demographics")
        async def generate_demographics(
            ctx: RunContext[PopulationDeps], demographics: dict
        ) -> str:
            ctx.generation_count += 1
            if "personas" not in ctx.shared_data:  # type: ignore
                ctx.shared_data["personas"] = []  # type: ignore
            ctx.shared_data["personas"].append(str(demographics))  # type: ignore
            return f"Generated demographics for user {ctx.user_id}"

        schema = getattr(generate_demographics, "_input_schema")
        properties = schema["properties"]

        assert "demographics" in properties
        assert "ctx" not in properties
        assert len(properties) == 1

        import asyncio

        deps = PopulationDeps(user_id="test_user")
        result = asyncio.run(
            generate_demographics(ctx=deps, demographics={"age": 30, "location": "NYC"})
        )

        assert "test_user" in result
        assert deps.generation_count == 1
        assert len(deps.shared_data["personas"]) == 1  # type: ignore
