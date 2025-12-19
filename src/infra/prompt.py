from __future__ import annotations

import json

from src.domain.entities import Review


class PromptBuilder:
    """Serializes reviews into prompts using a preconfigured template."""

    def __init__(self, *, template: str):
        self.template = template.strip()

    @staticmethod
    def _serialize_review(review: Review) -> str:
        payload = review.model_dump(by_alias=True)
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)

    def build(self, review: Review) -> str:
        review_payload = self._serialize_review(review)
        parts = [
            self.template,
            "Full review payload:",
            review_payload,
        ]
        return "\n".join(parts).strip()
