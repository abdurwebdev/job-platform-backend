from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Rozgar API"

    debug: bool = False

    api_v1_prefix: str = "/api"

    log_level: str = "INFO"

    database_url: PostgresDsn

    # Shared secret the GitHub Actions cron job sends via the
    # X-Scrape-Secret header. If left empty, the /scrape endpoint stays
    # open (fine for local dev, not recommended once this is public).
    scrape_secret: str = ""

    # In-container scheduler: when True, a background thread runs
    # run_and_save_jobs() on a loop instead of relying on an external
    # trigger (GitHub Actions). Turn this off for local dev if you'd
    # rather trigger scrapes manually via POST /api/job/scrape.
    scheduler_enabled: bool = True
    scrape_interval_hours: float = 6

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