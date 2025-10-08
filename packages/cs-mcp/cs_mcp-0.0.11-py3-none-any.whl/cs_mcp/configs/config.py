from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    IS_DEBUG: bool = False
    DATABASE_URL: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


config = Settings()
