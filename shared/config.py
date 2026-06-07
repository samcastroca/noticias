from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://noticias:noticias@postgres:5432/noticias"
    redis_url: str = "redis://redis:6379/0"

    embed_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"

    trend_window_hours: int = 2

    hdbscan_min_cluster_size: int = 3
    hdbscan_min_samples: int = 2

    ingest_interval_seconds: int = 300

    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
