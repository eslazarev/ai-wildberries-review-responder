from __future__ import annotations

from typing import Callable, Dict

from src.application.llm import LLMClient
from src.infra.config.settings import LLMProvider, Settings


def make_llm_client(settings: Settings) -> LLMClient:
    runtime = settings.llm
    from src.infra.llm.openai_client import OpenAIClient
    from src.infra.llm.yandex import YandexGPTClient

    factory_map: Dict[LLMProvider, Callable[[], LLMClient]] = {
        LLMProvider.YANDEX: lambda: YandexGPTClient(
            runtime.yandexgpt,
            temperature=runtime.temperature,
            max_tokens=runtime.max_tokens,
            instructions=runtime.instructions,
            timeout=runtime.timeout,
        ),
        LLMProvider.OPENAI: lambda: OpenAIClient(
            runtime.openai,
            temperature=runtime.temperature,
            max_tokens=runtime.max_tokens,
            instructions=runtime.instructions,
            timeout=runtime.timeout,
        ),
    }

    return factory_map[runtime.provider]()
