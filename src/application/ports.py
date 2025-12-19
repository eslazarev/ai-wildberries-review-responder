from __future__ import annotations

from typing import Protocol, Sequence

from src.domain.wildberries.entities import WildberriesReview


class AppLogger(Protocol):
    """Minimal logging contract required by application services."""

    def info(self, message: str, *args: object, **kwargs: object) -> None: ...

    def warning(self, message: str, *args: object, **kwargs: object) -> None: ...  # pragma: no cover


class ReviewFetcher(Protocol):
    """Port for loading pending reviews."""

    def fetch_reviews(self) -> Sequence[WildberriesReview]: ...


class ReplyGenerator(Protocol):
    """Port for transforming a review into an LLM-ready reply."""

    def generate(self, review: WildberriesReview) -> str: ...


class ReviewPublisher(Protocol):
    """Port for publishing a reply back to the review source."""

    def publish_reply(self, review_id: str, reply: str) -> None: ...
