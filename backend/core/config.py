from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL")

    # Keycloak
    keycloak_url: str = os.getenv("KEYCLOAK_URL", "http://keycloak:8080")
    keycloak_realm: str = os.getenv("KEYCLOAK_REALM", "psycho-realm")
    keycloak_client_id: str = "psycho-client"
    keycloak_client_secret: Optional[str] = None
    keycloak_external_url: str = os.getenv("KEYCLOAK_EXTERNAL_URL", "http://localhost:3000/auth")

    # JWT
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    class Config:
        env_file = ".env"

settings = Settings()
