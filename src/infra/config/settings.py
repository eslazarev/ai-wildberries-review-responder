from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource


class WildberriesSettings(BaseModel):
    api_token: str = ""
    base_url: str = "https://feedbacks-api.wildberries.ru"
    request_timeout: int = 10
    batch_size: int = 10


class LLMRuntimeSettings(BaseModel):
    api_key: str | None = None
    model: str = ""
    base_url: str = "https://rest-assistant.api.cloud.yandex.net/v1"
    temperature: float = 0.3
    max_tokens: int = 600
    instructions: str = "You are a polite support agent replying to Wildberries reviews."
    timeout: int = 10
    prompt_template: str = "Reply to the Wildberries review in a polite and concise tone."


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    wildberries: WildberriesSettings = Field(default_factory=WildberriesSettings)
    llm: LLMRuntimeSettings = Field(default_factory=LLMRuntimeSettings)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        project_root = Path(__file__).resolve().parents[3]
        yaml_path = project_root / "settings.yaml"
        yaml_settings = YamlConfigSettingsSource(settings_cls, yaml_file=yaml_path)

        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            yaml_settings,
        )
