from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Migration Platform"
    metadata_database_url: str = (
        "postgresql+psycopg://migration:change_me@localhost:5432/migration_metadata"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
