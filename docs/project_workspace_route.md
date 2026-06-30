# Project Workspace Route

## Overview
The route `app/[project_id]/chat/page.tsx` renders the primary AI development environment:

1. **Left Split Panel (Chat & Controls)**:
   - Chat console with token usage trackers.
   - Assistant toggle (Codex vs. Claude Code).
   - Prompt input editor.
2. **Right Split Panel (Live App Sandbox)**:
   - Tab 1: **App Preview** (renders iframe mapped to localhost:3100+ running the hot-reloaded project web app).
   - Tab 2: **Console Logs** (real-time build logs from Next.js).
   - Tab 3: **File Explorer** (Prisma file tree from `/api/repo/[project_id]/tree`).
