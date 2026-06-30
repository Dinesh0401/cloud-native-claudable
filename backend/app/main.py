"""
Day 2 — FastAPI Orchestration Backend

Minimal backend that manages Docker container lifecycles for AI agent runtimes.
Endpoints:
  GET  /                          → health check
  POST /sessions                  → create a new agent session (launches container)
  GET  /sessions/{session_id}     → get session status
  POST /sessions/{session_id}/exec → run agent command, stream stdout
  DELETE /sessions/{session_id}   → stop and remove container
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.container_manager import ContainerManager
from app import config

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Claudable Cloud Orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton container manager — lives for the lifetime of the server process
manager = ContainerManager(
    image=config.AGENT_IMAGE,
    workspace_root=config.WORKSPACE_ROOT,
    api_key=config.OPENAI_API_KEY,
)

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ExecRequest(BaseModel):
    prompt: str

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
def health():
    """Health check."""
    return {"status": "ok", "service": "claudable-orchestrator"}


@app.post("/sessions")
def create_session():
    """Create a new agent session — launches a Docker container with a mounted workspace."""
    try:
        session = manager.create_session()
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    """Get the status of a session."""
    status = manager.get_session_status(session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return status


@app.post("/sessions/{session_id}/exec")
def exec_command(session_id: str, body: ExecRequest):
    """
    Execute an agent command inside the session container.
    Streams stdout back as text/plain in real-time.
    """
    status = manager.get_session_status(session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Session not found")

    def generate():
        for chunk in manager.run_agent_command(session_id, body.prompt):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """Stop and remove the session container. Workspace files persist on the host."""
    try:
        result = manager.stop_session(session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
