from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "mock"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_timeout_seconds: int = 30
    max_retries: int = 1

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
