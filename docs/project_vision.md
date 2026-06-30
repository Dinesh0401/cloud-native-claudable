# Project Vision: Cloud-Native Claudable

## The Problem
Local AI workstations run code execution directly on the developer's laptop. This has several key limitations:
1. **No Sandbox Isolation**: Malicious code or execution loops can destroy files outside the workspace.
2. **Local Resource Limits**: CPU/RAM usage competes with daily workflows.
3. **No Multi-Tenancy**: Multiple users cannot safely share a single execution host.

## The Solution: Cloud-Native Architecture
Transition the agent workspace into an isolated, remote execution container hosted in the cloud.

```
┌─────────────────────────────────┐
│       Frontend (Browser UI)     │
└────────────────┬────────────────┘
                 │ WebSockets
                 ▼
┌─────────────────────────────────┐
│     FastAPI Backend Router      │
└────────────────┬────────────────┘
                 │ Docker API
                 ▼
┌─────────────────────────────────┐
│    Isolated Docker Container    │
│    (Compute: npm, git, Codex)   │
└────────────────┬────────────────┘
                 │ Volume Mount
                 ▼
┌─────────────────────────────────┐
│      Host Persistent Folder     │
│      (Storage: Workspace Files) │
└─────────────────────────────────┘
```

## Primitives
* **Compute (Container)**: Disposable, stateless, and short-lived container environments.
* **Storage (Volume)**: Long-lived, user-owned, and persistent filesystems on the host.
* **Orchestrator (Backend)**: FastAPI backend managing container lifecycle and WebSocket stream routing.
