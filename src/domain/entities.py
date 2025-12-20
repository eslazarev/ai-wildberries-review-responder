from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Review(BaseModel):
    """Base review data shared across sources."""

    model_config = ConfigDict(frozen=True)

    id: str
    text: str | None = None
    summary: str | None = None


class LLMResponse(BaseModel):
    """Normalized answer from any LLM provider."""

    model_config = ConfigDict(frozen=True)

    text: str

    @classmethod
    def from_response(cls, response: object) -> "LLMResponse":
        raw_text = getattr(response, "output_text", None)
        return cls(text=str(raw_text).strip())
