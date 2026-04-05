from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    debug_mode: bool = False

    db_user: str
    db_password: str
    db_name: str
    db_host: str
    db_port: int
    db_url: PostgresDsn


db_settings = DBSettings()
