#!/bin/bash

# start.sh - Launch script for the FastAPI backend

# Fail on any error
set -e

# Default to port 8000 if not set by host provider (like Render/Railway)
PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

echo "Starting Claudable Orchestrator Backend on $HOST:$PORT..."
echo "Verifying Docker socket access..."

if ! docker info > /dev/null 2>&1; then
    echo "WARNING: Docker socket is not accessible."
    echo "If running locally, ensure /var/run/docker.sock is volume mounted."
    echo "If on Render/Railway, ensure Docker in Docker (DinD) is properly configured."
fi

# Run uvicorn server via the main module
# Using standard uvicorn since the app is robustly structured
exec python -m uvicorn app.main:app --host "$HOST" --port "$PORT" --proxy-headers --forwarded-allow-ips="*"
