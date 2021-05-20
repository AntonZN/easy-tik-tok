import os
import secrets
from enum import IntEnum
from functools import lru_cache
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, PostgresDsn, validator

load_dotenv()


class Storages(IntEnum):
    AWS_S3 = 1
    LOCAL = 2


class Settings(BaseSettings):
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    PROJECT_NAME: str = "Parody of TikTok"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Media conf
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_DIR: str = "../media"
    MEDIA_ROOT: str = os.path.join(BASE_DIR, MEDIA_DIR)
    MEDIA_URL: str = "/media/"

    # Storage conf
    STORAGE: IntEnum = Storages.LOCAL
    STORAGE_ENDPOINT_URL: str = "https://storage.yandexcloud.net"
    BUCKET_NAME: str = ""

    # Encoding conf
    FFPROBE_COMMAND: str = "ffprobe"
    FFMPEG_COMMAND: str = "ffmpeg"
    UPLOAD_TYPES: list = ["video/mp4"]

    # DB conf
    MODELS: List[str] = ["app.models.video", "app.models.user", "app.models.comment"]

    POSTGRES_SCHEME: str = "postgres"
    POSTGRES_HOST: str = "db"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URI: str = None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme=values.get("POSTGRES_SCHEME"),
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():

    return Settings()
