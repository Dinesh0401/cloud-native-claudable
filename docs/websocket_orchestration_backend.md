# WebSocket Orchestration Layer

## Overview
The WebSocket orchestration layer binds container standard output streams to dynamic frontend connections.

## Pipeline Flow
1. **WS Client Upgrade**: FastAPI routes connections to `/ws/sessions/{session_id}`.
2. **Dynamic Channel Registry**: Active sockets are mapped to container session contexts.
3. **Execution Stream Broker**:
   - Spawns background task `docker exec`.
   - Loops through container output generator chunks.
   - Forwards stringified JSONL events directly into the client socket.
4. **Safety & Disconnection**:
   - Handles client interrupts by terminating processes safely inside the container.
   - Clears memory references upon connection close.
