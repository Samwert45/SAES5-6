"""Configuration globale de l'application."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration de l'application."""
    
    # API
    app_name: str = "Gateway Provisioning"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # Database
    db_host: str = "::1"
    db_port: int = 5435
    db_name: str = "gateway_db"
    db_user: str = "gateway"
    db_password: str = "gateway123"
    
    # Rules
    rules_path: str = "rules/rules.yaml"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
