import os
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "dScribe"
    ALLOWED_HOSTS: list = ["*"]
    STATIC_DIR: str = os.path.join(BASE_DIR, "static/dscribe/dist")

    class Config:
        env_file = ".env"


settings = Settings()