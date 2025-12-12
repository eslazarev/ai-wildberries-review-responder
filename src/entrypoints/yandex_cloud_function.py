from __future__ import annotations

from typing import Any, Dict, cast

from src.application.respond_on_reviews import respond_on_reviews
from src.application.ports import AppLogger
from src.infra.clients import WildberriesClient
from src.infra.config.settings import Settings
from src.infra.llm.base import make_llm_client
from src.infra.logger import init_logger
from src.infra.prompt import PromptBuilder
from src.infra.reply_generator import LLMReplyGenerator


def _apply_yc_context_settings(settings: Settings, context: Any) -> None:
    if context is None:
        return

    folder_id = getattr(context, "function_folder_id", None)
    if isinstance(folder_id, str) and folder_id:
        if settings.llm.model and "{FOLDER_ID}" in settings.llm.model:
            settings.llm.model = settings.llm.model.replace("{FOLDER_ID}", folder_id)

    token = getattr(context, "token", None)
    if isinstance(token, dict):
        access_token = token.get("access_token")
        if isinstance(access_token, str) and access_token.strip():
            api_key = (settings.llm.api_key or "").strip()
            if not api_key or api_key.lower() == "null":
                settings.llm.api_key = access_token


def handler(event: Dict[str, Any] | None = None, context: Any = None) -> Dict[str, Any]:
    settings = Settings()
    _apply_yc_context_settings(settings, context)

    logger = cast(AppLogger, init_logger())
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
