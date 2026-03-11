from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_env: str
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30
    ai_provider: str
    openai_api_key: str

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()