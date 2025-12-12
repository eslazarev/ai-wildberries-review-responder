from __future__ import annotations

from src.application.llm import LLMClient
from src.infra.config.settings import Settings


def make_llm_client(settings: Settings) -> LLMClient:
    runtime = settings.llm
    from src.infra.llm.openai_client import OpenAIClient

    return OpenAIClient(
        runtime,
        temperature=runtime.temperature,
        max_tokens=runtime.max_tokens,
        instructions=runtime.instructions,
        timeout=runtime.timeout,
    )
