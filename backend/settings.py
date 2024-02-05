import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """
    TODO: Documentation (https://google.github.io/styleguide/pyguide.html)Custom settings for this app.
    """

    PROJECT_NAME: str
    ENVIRONMENT: str

    # Database
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    POSTGRES_CONNECTION_POOL_MIN_SIZE: int = 1
    POSTGRES_CONNECTION_POOL_MAX_SIZE: int = 20

    LOG_LEVEL: str = "INFO"
    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
        env_file=os.environ.get("dotenv_path", ".env"),
    )

    def is_local_environment(self):
        return self.ENVIRONMENT == "local"


settings = Settings()
