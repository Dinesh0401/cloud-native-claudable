# Dashboard Route Structure

## Overview
The dashboard home route (`app/page.tsx`) provides:
1. **Workspace Listing**: Queries the sqlite database via `GET /api/projects` to render the cards.
2. **Project Generation**: Captures project name and initial prompt to hit `POST /api/projects`.

## API Integration Details
- **Projects Fetching**: Returns a JSON summary of user workspaces, showing their preferred CLI (Codex/Claude), active sessions, and timestamps.
- **Dependency Bootstrap**: When a project is created, the system triggers `POST /api/projects/[project_id]/install-dependencies` in the background to initialize Tailwind and build files on disk.
