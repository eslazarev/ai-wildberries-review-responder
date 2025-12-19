from __future__ import annotations

from src.application.llm import LLMClient
from src.domain.wildberries.entities import WildberriesReview
from src.infra.prompt import PromptBuilder


class LLMReplyGenerator:
    """Adapter that uses PromptBuilder + LLM client to craft replies."""

    def __init__(self, prompt_builder: PromptBuilder, llm_client: LLMClient):
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client

    def generate(self, review: WildberriesReview) -> str:
        prompt = self.prompt_builder.build(review)
        return self.llm_client.generate_reply(prompt)
