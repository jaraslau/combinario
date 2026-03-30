from pydantic import RedisDsn, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    debug_mode: bool = False

    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: int
    db_url: PostgresDsn

    redis_host: str
    redis_port: int
    redis_db: int
    redis_url: RedisDsn

    llm_base_url: str
    llm_model: str

    max_tokens: int
    model_temperature: float

    open_ai_api_key: str


settings = Settings()
