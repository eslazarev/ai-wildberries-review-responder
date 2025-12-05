"""
Cron-friendly entrypoint for Yandex Cloud Function triggers.

Use `infra.cron_entrypoint:cron_handler` as the function entrypoint.
"""

from typing import Any, Dict

from src.application.respond_on_reviews import respond_on_reviews
from src.infra.clients import WildberriesClient
from src.infra.config.settings import Settings
from src.infra.llm.base import make_llm_client
from src.infra.logger import init_logger
from src.infra.prompt import PromptBuilder
from src.infra.reply_generator import LLMReplyGenerator


def cron_handler(event: Dict[str, Any] | None = None, context: Any = None) -> Dict[str, Any]:

    settings = Settings()
    logger = init_logger()
    wildberries_client = WildberriesClient(settings)
    llm_client = make_llm_client(settings)
    prompt_builder = PromptBuilder(template=settings.llm.prompt_template)
    reply_generator = LLMReplyGenerator(prompt_builder=prompt_builder, llm_client=llm_client)

    respond_on_reviews(
        review_fetcher=wildberries_client,
        reply_generator=reply_generator,
        review_publisher=wildberries_client,
        logger=logger,
    )

    return {
        "status": "ok",
    }

if __name__ == "__main__":
    cron_handler()
