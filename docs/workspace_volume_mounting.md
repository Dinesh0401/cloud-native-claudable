# Workspace Volume Mounting

## Overview
The persistent storage model binds directories from the host filesystem directly into the container filesystem.

## Volume Configurations
- **Host Source Path**: `workspaces/{session_id}` (located in the backend directory).
- **Container Destination Path**: `/workspace` (marked as the default Working Directory `WORKDIR` in Dockerfile).
- **Mount Mode**: Read-Write (`rw`).

## Permission & Security Guidelines
- The orchestrator initializes directory creation on the host before container startup to avoid root-owner write privilege locks.
- Container processes write code and install dependencies directly into `/workspace`, making them immediately available to standard host utilities and preview services.
