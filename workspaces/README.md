# Project Workspaces Directory

This directory contains persistent user project directories.
* Each directory is named after its `session_id` (e.g., `session-xxxx`).
* This directory is mounted as a volume into the agent container at `/workspace`.
* This folder is excluded from version control to prevent checking in generated code output.
