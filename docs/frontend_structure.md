# Frontend Next.js Structure

## Folder Blueprint
The frontend app router structure for Claudable is organized as follows:

```
app/
├── layout.tsx                # Global Layout
├── page.tsx                  # Dashboard Home Page (project listing/creation)
├── [project_id]/
│   └── chat/
│       └── page.tsx          # Real-time chat workspace & preview UI
├── api/
│   ├── projects/             # Project database CRUD endpoints
│   ├── settings/             # CLI preference configurations
│   └── chat/[project_id]/
│       ├── act/              # Receives and dispatches prompt payloads
│       └── stream/           # Server-Sent Events endpoint
```

## System Keynotes
- Layout sets up global provider interfaces.
- The workspace page sets up the split panel layout (Chat pane on the left, Dev preview browser pane on the right).
