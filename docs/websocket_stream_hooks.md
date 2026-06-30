# WebSocket Stream Hooks

## Overview
The frontend connects to real-time streams using hooks to handle state synchronizations:

1. **useWebSocket (`hooks/useWebSocket.ts`)**:
   - Manages connection lifecycle (`CONNECTING`, `OPEN`, `CLOSED`).
   - Parses the envelope structure `{type, data}`.
   - Triggers `onMessage()` callback for text deltas.
   - Handles connection errors and reconnect strategies.
2. **useUserRequests (`hooks/useUserRequests.ts`)**:
   - Manages prompt active count state.
   - Sets polling frequency adaptive to agent activity (500ms active vs 5000ms idle).
   - Signals completion transitions.
