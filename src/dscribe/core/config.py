import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "dScribe"
    ALLOWED_HOSTS: list = ["*"]
    STATIC_DIR: str = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), os.path.join("static", "dscribe", "dist")
)

    class Config:
        env_file = ".env"


settings = Settings()