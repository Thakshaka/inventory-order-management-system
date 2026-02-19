from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"
    app_title: str = "Inventory & Order Management API"
    app_version: str = "1.0.0"

    database_url: str = (
        "postgresql://inventory_user:inventory_pass@localhost:5432/inventory_db"
    )
    async_database_url: str | None = None

    @property
    def async_url(self) -> str:
        """Derive async database URL from sync URL if not provided."""
        url = self.async_database_url
        if not url and self.database_url:
            if self.database_url.startswith("postgresql://"):
                url = self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Ensure we always return a valid-looking SQLAlchemy connection string to avoid early crashes
        return url or "postgresql+asyncpg://user:pass@localhost/db"
    test_async_database_url: str = (
        "postgresql+asyncpg://inventory_user:inventory_pass@localhost:5432/test_inventory_db"
    )

    default_page_limit: int = 20
    max_page_limit: int = 100


@lru_cache
def get_settings() -> Settings:
    return Settings()
