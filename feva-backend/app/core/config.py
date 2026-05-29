from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours (Requirement 3.4)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REDIS_URL: str = "redis://localhost:6379/0"
    OBJECT_STORAGE_URL: str = ""
    ENVIRONMENT: str = "development"

    # RS256 key pair — if empty, an ephemeral RSA-2048 pair is generated at startup (dev only)
    JWT_PRIVATE_KEY: str = ""
    JWT_PUBLIC_KEY: str = ""

    # Rate limiting (Requirement 20.5)
    LOGIN_RATE_LIMIT_ATTEMPTS: int = 5
    LOGIN_RATE_LIMIT_WINDOW_MINUTES: int = 15

    # File upload limits (Requirement 20.8)
    MAX_UPLOAD_SIZE_MB: int = 50

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
