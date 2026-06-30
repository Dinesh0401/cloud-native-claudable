# Runtime Lifecycle Document

## Overview
This document traces the timeline of an agent session container from creation to destruction:

```
  [ Client Request ]
         │
         ▼
┌──────────────────┐
│  State: CREATED  │ ──> Host directory spaces initialized
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  State: RUNNING  │ ──> Docker run triggers, entrypoint waiting
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  State: EXEC     │ ──> Command injected via docker exec, outputs logs
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  State: STOPPED  │ ──> Stop command signals, container terminates
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  State: REMOVED  │ ──> Container destroyed, files remain on host disk
└──────────────────┘
```

## Lifecycle States
- **CREATED**: Unique project session and workspace generated on host disk.
- **RUNNING**: Base `agent-runtime` container launched in background with mounted volume.
- **EXEC**: Code instructions executed dynamically. Standard output streamed chunk-by-chunk.
- **STOPPED**: Session termination request received. Container processes terminated gracefully.
- **REMOVED**: Container deleted. Resources freed. Workspace folder persists.
