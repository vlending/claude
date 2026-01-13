"""
Application configuration using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="먹은대로 Health Meal Coach")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    api_v1_prefix: str = Field(default="/v1")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    reload: bool = Field(default=True)

    # Security
    secret_key: str = Field(default="change-this-secret-key")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/eatasyoueat"
    )
    database_pool_size: int = Field(default=20)
    database_max_overflow: int = Field(default=0)

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_cache_ttl: int = Field(default=900)  # 15 minutes

    # AWS S3
    s3_bucket_name: str = Field(default="eatasyoueat-uploads")
    s3_region: str = Field(default="ap-northeast-2")
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    s3_endpoint_url: str | None = Field(default=None)  # For MinIO

    # Anthropic API
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022")
    anthropic_max_tokens: int = Field(default=2048)
    anthropic_temperature: float = Field(default=0.3)

    # CORS
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:19006",
            "http://localhost:8081",
        ]
    )

    # File Upload
    max_file_size_mb: int = Field(default=10)
    allowed_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/heic"]
    )
    allowed_document_types: List[str] = Field(default=["application/pdf"])

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=100)
    rate_limit_image_upload_per_minute: int = Field(default=10)

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string to list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for Alembic."""
        return self.database_url.replace("+asyncpg", "")


# Global settings instance
settings = Settings()
