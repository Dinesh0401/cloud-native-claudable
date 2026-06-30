"""
Backend configuration.
Reads from environment variables with sensible defaults.
"""

import os

# Where project workspaces live on the host filesystem
WORKSPACE_ROOT = os.environ.get(
    "WORKSPACE_ROOT",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "workspaces"),
)

# Docker image name for the agent runtime container
AGENT_IMAGE = os.environ.get("AGENT_IMAGE", "agent-runtime")

# OpenAI API key — required for Codex CLI inside containers
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# FastAPI server
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8000"))
