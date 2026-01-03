from __future__ import annotations

from typing import Any, List, cast
from wildberries_sdk import communications
from wildberries_sdk.communications import ApiV1FeedbacksGet200Response
from wildberries_sdk.communications.models import ApiV1FeedbacksAnswerPostRequest

from src.domain.entities import Review
from src.infra.clients.wildberries_dto import WildberriesReview
from src.infra.config.settings import Settings


class WildberriesClient:
    """SDK adapter for Wildberries feedback API (fetch + publish)."""

    def __init__(self, settings: Settings):
        self._config = settings.wildberries
        self.settings = settings
        self.timeout = self._config.request_timeout
        self.batch_size = self._config.batch_size
        self._api_client = self._build_client()
        self._api = communications.DefaultApi(api_client=self._api_client)

    def _build_client(self) -> communications.ApiClient:
        config = communications.Configuration(host=self._config.base_url.rstrip("/"))
        config.api_key["HeaderApiKey"] = self._config.api_token
        config.ignore_operation_servers = True
        return communications.ApiClient(configuration=config)

    def fetch_reviews(self) -> List[Review]:
        response: ApiV1FeedbacksGet200Response = self._api.api_v1_feedbacks_get(
            is_answered=False,
            take=self.batch_size,
            skip=0,
            _request_timeout=self.timeout,
        )
        data = cast(Any, response.data)
        items = list(cast(List[Any], data.feedbacks))
        reviews: List[Review] = []
        for item in items:
            payload = item.model_dump(by_alias=True, exclude_none=True)
            reviews.append(WildberriesReview(**payload).to_review())
        return reviews

    def publish_reply(self, review_id: str, message: str) -> None:
        payload = ApiV1FeedbacksAnswerPostRequest(id=review_id, text=message)
        self._api.api_v1_feedbacks_answer_post(
            api_v1_feedbacks_answer_post_request=payload,
            _request_timeout=self.timeout,
        )
