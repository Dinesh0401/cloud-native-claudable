#!/bin/bash
# Agent runtime entrypoint.
# Keeps the container alive so the orchestrator can exec commands into it.
echo "🤖 Agent runtime ready — waiting for commands..."
echo "Node: $(node -v)"
echo "npm: $(npm -v)"
echo "Git: $(git --version)"
echo "Codex: $(codex --version 2>/dev/null || echo 'not found')"
# Stay alive
tail -f /dev/null
