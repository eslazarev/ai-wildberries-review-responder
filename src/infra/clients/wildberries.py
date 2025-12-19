from __future__ import annotations

from typing import Any, Dict, List

import requests

from src.domain.entities import Review
from src.domain.wildberries.entities import WildberriesReview
from src.infra.config.settings import Settings


class WildberriesClient:
    """HTTP adapter for Wildberries feedback API (fetch + publish)."""

    def __init__(self, settings: Settings):
        self._config = settings.wildberries
        self.settings = settings
        self.timeout = self._config.request_timeout
        self.batch_size = self._config.batch_size
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"{self._config.api_token}",
            }
        )

    def fetch_reviews(self) -> List[Review]:
        url = f"{self._config.base_url}/api/v1/feedbacks"
        params = {"isAnswered": False, "take": self.batch_size, "skip": 0}

        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()

        payload: Dict[str, Any] = response.json()
        items = payload.get("data", {}).get("feedbacks", [])

        reviews: List[Review] = []
        for raw in items:
            reviews.append(WildberriesReview(**raw).to_review())
        return reviews

    def publish_reply(self, review_id: str, message: str) -> None:
        url = f"{self._config.base_url}/api/v1/feedbacks/answer"
        payload = {
            "id": review_id,
            "text": message,
        }

        response = self.session.post(url, json=payload, timeout=self.timeout)
        response.raise_for_status()
