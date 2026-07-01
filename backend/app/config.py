"""
Backend configuration.
Reads from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load environment variables from backend/ .env if exists
load_dotenv()

# Load environment variables from Next.js .env as fallback/shared config
nextjs_env = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Claudable", ".env")
nextjs_env_local = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Claudable", ".env.local")
if os.path.exists(nextjs_env):
    load_dotenv(nextjs_env)
if os.path.exists(nextjs_env_local):
    load_dotenv(nextjs_env_local)

SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")


# Where project workspaces live on the host filesystem (mapping to Next.js data/projects)
WORKSPACE_ROOT = os.environ.get(
    "WORKSPACE_ROOT",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Claudable", "data", "projects"),
)

# Docker image name for the agent runtime container
AGENT_IMAGE = os.environ.get("AGENT_IMAGE", "agent-runtime")

# OpenAI API key — required for Codex CLI inside containers
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# FastAPI server
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
