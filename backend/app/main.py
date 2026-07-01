"""
Day 2 — FastAPI Orchestration Backend

Minimal backend that manages Docker container lifecycles for AI agent runtimes.
Endpoints:
  GET  /                          → health check
  POST /sessions                  → create a new agent session (launches container)
  GET  /sessions/{session_id}     → get session status
  POST /sessions/{session_id}/exec → run agent command, stream stdout
  DELETE /sessions/{session_id}   → stop and remove container
  GET  /projects/{project_id}/download → zip and download a project
"""

import jwt
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
import tempfile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.container_manager import ContainerManager
from app import config

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not config.SUPABASE_JWT_SECRET:
        # If no secret configured, skip auth (for dev)
        return {"sub": "dev_user"}
        
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            config.SUPABASE_JWT_SECRET, 
            algorithms=["HS256"], 
            audience="authenticated"
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication credentials: {str(e)}")

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


class CreateSessionRequest(BaseModel):
    project_id: str

@app.post("/sessions")
def create_session(body: CreateSessionRequest, token: dict = Depends(verify_token)):
    """Create a new agent session — launches a Docker container with a mounted workspace."""
    try:
        user_id = token.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        session = manager.create_session(project_id=body.project_id, user_id=user_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}")
def get_session(session_id: str, token: dict = Depends(verify_token)):
    """Get the status of a session."""
    status = manager.get_session_status(session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return status


@app.post("/sessions/{session_id}/exec")
def exec_command(session_id: str, body: ExecRequest, token: dict = Depends(verify_token)):
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
def delete_session(session_id: str, token: dict = Depends(verify_token)):
    """Stop and remove the session container. Workspace files persist on the host."""
    try:
        result = manager.stop_session(session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/download")
def download_project(project_id: str, token: dict = Depends(verify_token)):
    """Zip the project workspace and return it for download."""
    user_id = token.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")
        
    workspace_path = os.path.join(manager.workspace_root, user_id, project_id)
    if not os.path.exists(workspace_path):
        raise HTTPException(status_code=404, detail="Project not found")

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"{project_id}.zip")
    
    # Create a zip archive of the directory
    shutil.make_archive(zip_path[:-4], 'zip', workspace_path)

    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{project_id}.zip"
    )
