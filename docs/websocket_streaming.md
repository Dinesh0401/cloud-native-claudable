# WebSocket Streaming Architecture

## Overview
Real-time status tracking and code compilation updates are delivered via a unified pub/sub streaming architecture.

## Streaming Infrastructure
1. **The StreamManager (Pub/Sub)**:
   - Contained in `lib/services/stream.ts`.
   - Maintained as a global singleton.
   - Publishes events using `streamManager.publish(projectId, event)`.
2. **Dual-Transport Bridge**:
   - **WebSockets (Primary)**: Managed by `lib/server/websocket-manager.ts`. Dispatches JSON envelopes over active WebSocket connections.
   - **SSE (Fallback)**: Pipes event payloads using HTTP `text/event-stream` ReadableStream controllers.
3. **Websocket Lifecycle**:
   - Upgraded at `pages/api/ws/[projectId].ts`.
   - Cleaned up using heartbeat pings every 25 seconds.
   - The browser hook `useWebSocket.ts` handles exponential backoff connections (up to 30-60s) to keep UI streams active.
