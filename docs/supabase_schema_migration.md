# Supabase Schema Migration

## Overview
Moving from a local SQLite schema to a remote Supabase (PostgreSQL) database ensures high-availability multi-tenancy.

## Table Structure Blueprint

### 1. `projects`
- `id` (UUID, primary key)
- `name` (text)
- `description` (text)
- `template_type` (text, e.g., Next.js / Vite)
- `created_at` (timestamptz)

### 2. `sessions`
- `id` (UUID, primary key)
- `project_id` (UUID, foreign key -> projects.id)
- `container_id` (text, maps to remote Docker instance)
- `status` (text, e.g., running / stopped)

### 3. `messages`
- `id` (UUID, primary key)
- `project_id` (UUID, foreign key)
- `role` (text, e.g., user / assistant / system)
- `content` (text)
