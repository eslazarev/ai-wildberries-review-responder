from __future__ import annotations

from openai import OpenAI

from src.application.llm import LLMClient
from src.domain.entities import LLMResponse
from src.infra.config.settings import LLMRuntimeSettings


class OpenAIClient(LLMClient):
    """Calls OpenAI-compatible chat completion API."""

    def __init__(
        self,
        config: LLMRuntimeSettings,
        *,
        temperature: float,
        max_tokens: int,
        instructions: str,
        timeout: int,
    ):
        super().__init__(
            temperature=temperature,
            max_tokens=max_tokens,
            instructions=instructions,
            timeout=timeout,
        )
        self.config = config

    def _client(self) -> OpenAI:
        base_url = self.config.base_url.rstrip("/")
        return OpenAI(api_key=self.config.api_key, base_url=base_url, timeout=self.timeout)

    def generate_reply(self, prompt: str) -> str:
        response = self._client().responses.create(
            model=self.config.model,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            input=prompt,
            instructions=self.instructions,
        )
        model = LLMResponse.from_response(response)
        return model.text
