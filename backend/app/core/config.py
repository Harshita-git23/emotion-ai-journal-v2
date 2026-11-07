
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Emotion AI Journal"
    DATABASE_URL: str = "sqlite:///./emotion_journal.db"

    FRONTEND_URL: str = "http://localhost:5173"

    # Development-only fallback. Set a strong random value in .env.
    SECRET_KEY: str = "development-only-change-this-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
