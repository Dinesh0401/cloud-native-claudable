# Cloud-Native Claudable

Cloud-Native Claudable is a high-availability, multi-tenant AI developer workspace orchestration platform. It shifts local AI workstation code execution (which runs un-sandboxed on the host machine) into containerized sandboxes, separating **Compute** (ephemeral execution runtimes) from **Storage** (long-lived workspace state).

---

## 🏗️ Architecture Blueprint

The platform is designed around three decoupled execution runtimes:

```
                  ┌───────────────────────────────┐ 
                  │      React App (Browser UI)   │
                  └──────────────┬────────────────┘
                                 │ REST / WebSockets
                                 ▼
                  ┌───────────────────────────────┐
                  │    FastAPI Orchestrator       │
                  └──────────────┬────────────────┘
                                 │ Docker Engine API
                                 ▼
                  ┌───────────────────────────────┐
                  │   Isolated Docker Container   │
                  │   (Stateless Agent Runtime)   │
                  └──────────────┬────────────────┘
                                 │ Host Volume Mount (rw)
                                 ▼
                  ┌───────────────────────────────┐
                  │    Host Workspace Storage     │
                  │   (Persistent Project Files)  │
                  └───────────────────────────────┘
```

### Decoupled Control & Data Planes
1. **Control Plane (FastAPI)**: Routes prompt requests, coordinates Docker container lifecycles, maps project IDs to container instances, and pipes stdout chunks in real-time.
2. **Compute Plane (Docker Container)**: Runs an isolated Debian-slim image pre-installed with Node, npm, git, and Codex CLI. It processes AI tool actions securely inside namespace boundaries.
3. **Data Plane (Volume Mounts)**: A persistent host disk storage directory mounted into the execution sandbox. This guarantees code durability across container lifetimes.

---

## 🛠️ Technology Stack

- **Gateway / Orchestration**: Python 3.10+, FastAPI, Uvicorn, Docker Python SDK.
- **Agent Sandbox Image**: Node.js 20, Debian Linux, npm, git, Codex CLI.
- **Frontend Panel**: Next.js (React), WebSockets.
- **Database Engine**: Prisma ORM, SQLite (local development) / PostgreSQL (production).

---

## ⚡ Local Development Setup

### Prerequisites
- Docker Desktop installed and running.
- Python 3.10+ and pip.
- Node.js 20+ and npm.

### 1. Initialize and Start the Orchestration Backend
```bash
# Navigate to backend directory
cd backend

# Install python dependencies
pip install -r requirements.txt

# Start the uvicorn API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The FastAPI documentation is available at `http://localhost:8000/docs`.

### 2. Build the Agent Runtime Image
```bash
# Navigate to the container folder
cd agent-container

# Build the runtime image
docker build -t agent-runtime .
```

### 3. Start the Frontend Workspace
```bash
# Navigate to Claudable workspace
cd Claudable

# Run local setup commands
npx prisma generate
npx prisma db push

# Launch the Next.js app with high-memory allocation
NODE_OPTIONS="--max-old-space-size=4096" npm run dev
```
The client UI will bind to `http://localhost:3000`.

---

## 📈 System Roadmap & Production Scaling

1. **Kubernetes Integration**: Replace direct Docker socket execution with a Kubernetes operator to coordinate ephemeral user sandbox pods dynamically.
2. **Shared Filesystem (RWX)**: Transition host volume mounts to cloud network filesystems (AWS EFS or GCP Filestore) to enable pod relocation across host nodes.
3. **Supabase Migration**: Implement PostgreSQL schema migrations for unified session persistence, user auth, and metadata logging.
4. **WebSocket Load Balancing**: Place the FastAPI control plane behind Traefik or Nginx proxies with sticky-session routing.
