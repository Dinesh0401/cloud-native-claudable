# Local Execution Flow

## Overview
This document traces the complete pipeline of how Claudable processes prompts and executes code locally.

## The Pipeline
1. **Frontend Dispatch**: The React app in `app/page.tsx` fires a `POST` request to `/api/chat/[project_id]/act`.
2. **Database Registration**: The act API handler logs the instruction in SQLite (`cc.db`), notifies WebSocket subscribers of the new message state, and starts execution.
3. **Fire-and-Forget Dispatch**: The act API handler calls the `executeClaude()` executor inside `lib/services/cli/claude.ts` without awaiting its promise. It returns an HTTP `200 OK` response to the client immediately.
4. **Agent Execution**:
   - The CLI service spawns the agent process.
   - For Claude: Calls `@anthropic-ai/claude-agent-sdk`'s `query()` iterator loop.
   - For Codex: Spawns the CLI child process (`codex.cmd` or `codex`).
5. **Real-time Event Streaming**: Stream deltas are captured and published via `StreamManager` to client WebSocket connections.
