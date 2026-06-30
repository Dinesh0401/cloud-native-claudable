# Day 1 Research: Architecture Deep Dive

## Phase 1: Environment Validation
Confirmed core utilities required for cloud-native orchestration:
- **Git**: Local version control and workspace snapshot tracking.
- **Node.js**: The local execution runtime that currently hosts the Next.js process.
- **npm**: Dependency resolution for packages.
- **Docker**: Used as the remote sandbox runtime for isolated agent execution.

## Phase 2: Claudable Clone & Key Discovery
Claudable functions as a Next.js-based application that can run in standard Web mode, Desktop dev mode (Electron wrapping Next.js), and Desktop Production mode. 

**Key System Discovery**: Claudable does *not* use a raw `child_process.spawn("claude", ...)` execution loop for its primary Claude agent. Instead, it utilizes the `@anthropic-ai/claude-agent-sdk` library. It invokes `query({prompt, options})` which returns an `AsyncIterable<SDKMessage>` stream.

This is a critical distinction:
- **Claude SDK Approach**: Coordinates Node.js processes, offering strong abstractions but higher API coupling and configuration limits inside the sandbox.
- **Codex CLI Approach**: Spawns Codex CLI as a standard black-box child process (`codex exec`). This fits container isolation models natively since standard POSIX streams are used.
