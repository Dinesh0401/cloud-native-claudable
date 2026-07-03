"""
Backend configuration.
Uses pydantic-settings to validate environment variables.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Security / Auth
    supabase_jwt_secret: str = ""

    # Workspace
    workspace_root: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Claudable", "data", "projects")

    # Docker
    agent_image: str = "agent-runtime"

    # API Keys
    openai_api_key: str = ""

    # FastAPI server config
    host: str = "0.0.0.0"
    port: int = 8000

    # Pydantic settings config to load from .env files
    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Claudable", ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Claudable", ".env.local"),
            ".env"
        ),
        env_file_encoding='utf-8',
        extra='ignore',
        env_prefix=""
    )

settings = Settings()

# Alias legacy config variables to avoid breaking existing imports immediately
SUPABASE_JWT_SECRET = settings.supabase_jwt_secret
WORKSPACE_ROOT = settings.workspace_root
AGENT_IMAGE = settings.agent_image
OPENAI_API_KEY = settings.openai_api_key
HOST = settings.host
PORT = settings.port

