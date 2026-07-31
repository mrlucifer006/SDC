from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Siege of the Five Gates"
    DATABASE_URL: str = "sqlite:///./ctf.db" # Default local DB, overridden by K8s secret
    JWT_SECRET: str = "super-secret-key-for-siege-of-the-five-gates-ctf"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    JUDGE0_URL: str = "http://judge0-server:2358" # In K8s

    class Config:
        env_file = ".env"

settings = Settings()
