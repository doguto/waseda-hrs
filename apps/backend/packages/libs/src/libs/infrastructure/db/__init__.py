"""DBエンジンの構築。接続情報はdocker-compose等が渡すPG*環境変数から読む。"""

from functools import lru_cache

import sqlalchemy
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PG")

    host: str = "localhost"
    port: int = 5432
    database: str = "hrs"
    user: str = "postgres"
    password: str = "password"

    @property
    def url(self) -> str:
        return (
            f"postgresql+psycopg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


@lru_cache
def get_engine() -> sqlalchemy.Engine:
    """プロセス内で使い回すEngine。connection poolはEngineが保持する。"""
    return sqlalchemy.create_engine(DbSettings().url, pool_pre_ping=True)
