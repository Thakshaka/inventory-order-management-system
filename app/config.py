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

    # Supabase/Vercel typically provides DATABASE_URL.
    # We use that for sync operations and derive/use async for the app.
    database_url: str = (
        "postgresql://inventory_user:inventory_pass@localhost:5432/inventory_db"
    )
    async_database_url: str = (
        "postgresql+asyncpg://inventory_user:inventory_pass@localhost:5432/inventory_db"
    )
    test_async_database_url: str = (
        "postgresql+asyncpg://inventory_user:inventory_pass@localhost:5432/test_inventory_db"
    )

    default_page_limit: int = 20
    max_page_limit: int = 100


@lru_cache
def get_settings() -> Settings:
    return Settings()
