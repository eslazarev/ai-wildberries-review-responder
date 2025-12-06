from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Application-level abstraction for LLM providers."""

    def __init__(
        self,
        *,
        temperature: float,
        max_tokens: int,
        instructions: str,
        timeout: int,
    ) -> None:
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.instructions = instructions
        self.timeout = timeout

    @abstractmethod
    def generate_reply(self, prompt: str) -> str:
        """Return the text reply produced by the model."""
        raise NotImplementedError
