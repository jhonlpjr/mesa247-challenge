from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./mesa247.db"
    cors_origins: str = "http://localhost:5173"
    daily_report_email: str = ""
    email_provider: str = "disabled"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
