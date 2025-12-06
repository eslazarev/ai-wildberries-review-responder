from __future__ import annotations

from openai import OpenAI

from src.application.llm import LLMClient
from src.domain.entities import LLMResponse
from src.infra.config.settings import YandexLLMSettings


def get_iam_token() -> str:
    """Fetch IAM token from metadata when running inside Yandex Cloud."""
    import requests

    url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    resp = requests.get(url, headers=headers, timeout=3)
    resp.raise_for_status()
    return resp.json()["access_token"]


class YandexGPTClient(LLMClient):
    """Calls Yandex GPT via the OpenAI-compatible Responses API."""

    def __init__(
        self,
        config: YandexLLMSettings,
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
        api_key = self.config.api_key or get_iam_token()
        return OpenAI(
            api_key=api_key, base_url=self.config.base_url, project=self.config.folder_id, timeout=self.timeout
        )

    def generate_reply(self, prompt: str) -> str:
        model_uri = self.config.resolved_model_uri()
        response = self._client().responses.create(
            model=model_uri,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            instructions=self.instructions,
            input=prompt,
        )
        model = LLMResponse.from_response(response)
        return model.text
