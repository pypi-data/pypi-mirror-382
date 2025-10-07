# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa
from typing import Any

from pydantic import BaseModel

from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.llm_models import (
    ChatInput,
    ChatOutput,
    Enum,
    ErrorHandling,
    InferenceMode,
    LLMUsageData,
    ReasoningConfig,
)

__all__ = [
    "ChatInput",
    "ChatOutput",
    "Enum",
    "ErrorHandling",
    "InferenceMode",
    "LLMUsageData",
    "ReasoningConfig",
    "chat",
]


def chat(
    *,
    schema: dict[str, Any] | type[BaseModel] | None = DEFAULT,
    model: str = DEFAULT,
    prompt_str: str | None = DEFAULT,
    file_data: str | None = DEFAULT,
    file_name: str | None = DEFAULT,
    image_url: str | None = DEFAULT,
    temperature: float = DEFAULT,
    stop: list[str] | None = DEFAULT,
    error_handling: ErrorHandling = DEFAULT,
    top_p: float | None = DEFAULT,
    seed: int | None = DEFAULT,
    presence_penalty: float | None = DEFAULT,
    frequency_penalty: float | None = DEFAULT,
    tool_choice: str | None = DEFAULT,
    inference_mode: InferenceMode = DEFAULT,
    output_schema: dict[str, Any] | type[BaseModel] | None = DEFAULT,
    stream: bool = DEFAULT,
    reasoning: ReasoningConfig | None = DEFAULT,
) -> ChatOutput:
    """
    AI powered chat

    Example usage with reasoning:
        from a79.models.tools.llm_models import ReasoningConfig

        reasoning_config = ReasoningConfig(
            effort="medium",  # or "high", "low"
            exclude=False     # Include reasoning in response
        )

        result = chat(ChatInput(
            model="google/gemini-2.5-flash",
            prompt_str="What is the capital of France?",
            reasoning=reasoning_config
        ))

        # Access reasoning tokens
        if result.reasoning:
            print("Reasoning:", result.reasoning)
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ChatInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="llm", name="chat", input=input_model.model_dump()
    )
    return ChatOutput.model_validate(output_model)
