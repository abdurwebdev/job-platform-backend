from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Rozgar API"

    debug: bool = False

    api_v1_prefix: str = "/api"

    log_level: str = "INFO"

    database_url: PostgresDsn

    allowed_origins: list[str] = [
        "http://localhost:3000",
        "https://job-platform-frontend-62ud.vercel.app",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()