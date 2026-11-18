from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    database_url: str = 'postgresql+psycopg://portfolio:portfolio_dev_only@localhost:5432/portfolio'
    jwt_secret_key: str = Field(min_length=32)
    jwt_issuer: str = 'portfolio-api'
    jwt_audience: str = 'portfolio-client'
    access_token_minutes: int = Field(default=30, ge=1, le=1440)
    cors_origins: str = 'http://localhost:5173'

    @field_validator('jwt_secret_key')
    @classmethod
    def reject_example_key(cls, value: str) -> str:
        if value.startswith('replace-with-'):
            raise ValueError('Generate a random JWT_SECRET_KEY before starting the API')
        return value

    @property
    def allowed_origins(self) -> list[str]:
        return [url.strip() for url in self.cors_origins.split(',') if url.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
