from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str
    app_url: str = ""
    craigslist_area: str = "sfbay"
    num_posts: int = 500


@lru_cache
def get_settings() -> Settings:
    return Settings()
