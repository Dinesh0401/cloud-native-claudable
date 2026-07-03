"""
Container Manager — Docker lifecycle controller.

This is the core orchestration layer.  It:
  1. Creates workspace directories on the host
  2. Launches Docker containers with volume mounts
  3. Executes CLI agent commands inside containers
  4. Streams stdout chunks back to the caller
  5. Stops/removes containers while preserving workspace files

Design principles:
  - The container is disposable compute.
  - The volume mount is persistent storage.
  - The orchestrator knows NOTHING about how the AI agent thinks.
"""

# Systems dependencies and Docker SDK bindings
import os
import uuid
import docker
import threading
import time
import socket
from docker.errors import NotFound, APIError
from app.logger import get_logger

logger = get_logger("container_manager")

class ContainerManager:
    """Manages Docker containers for agent sessions."""

    def __init__(self, image: str, workspace_root: str, api_key: str):
        self.image = image
        self.workspace_root = os.path.abspath(workspace_root)
        self.api_key = api_key
        self._client = None  # Lazy-initialized

        # In-memory session registry: {session_id: dict}
        # Day 3 — storing container_id and workspace path.
        self._sessions: dict[str, dict] = {}

        # Ensure workspace root exists
        os.makedirs(self.workspace_root, exist_ok=True)
        
        # Start background cleanup task
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
        
        logger.info("ContainerManager initialized (Docker connection is lazy)")

    @property
    def client(self):
        """Lazy Docker client — only connects when first needed."""
        if self._client is not None:
            return self._client
        try:
            self._client = docker.from_env()
            self._client.ping()
            logger.info("Connected to Docker daemon via default socket")
        except Exception:
            try:
                self._client = docker.DockerClient(base_url="npipe:////./pipe/dockerDesktopLinuxEngine")
                self._client.ping()
                logger.info("Connected to Docker daemon via Linux engine pipe")
            except Exception:
                # Store None so we don't retry endlessly — caller will get an error
                self._client = None
                logger.warning("Docker daemon is not available — container operations will fail")
                raise RuntimeError("Docker daemon is not accessible. Please start Docker Desktop.")
        return self._client

    def _cleanup_loop(self):
        """Background thread to periodically reap dead containers."""
        while True:
            time.sleep(300) # Every 5 minutes — sleep first to avoid crashing on startup
            try:
                self.reap_dead_containers()
            except Exception:
                pass  # Docker may not be available yet

    def reap_dead_containers(self):
        """Cleanup any containers created by us that are dead or exited."""
        try:
            for container in self.client.containers.list(all=True, filters={"name": "agent-"}):
                if container.status in ["exited", "dead"]:
                    logger.info(f"Reaping dead container: {container.name}")
                    try:
                        container.remove(force=True)
                    except Exception as e:
                        logger.warning(f"Failed to remove container {container.name}: {e}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def _find_available_port(self) -> int:
        """Find an available dynamic port on the host."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def create_session(self, project_id: str, user_id: str) -> dict:
        """
        Create a new agent session:
          1. Use the provided project_id as the session ID
          2. Mount the existing Next.js workspace directory for the specific user
          3. Launch a Docker container with the workspace mounted
          4. Register the session
        """
        # Sanitize path inputs to prevent directory traversal
        safe_user_id = os.path.basename(user_id.replace("\\", "/"))
        safe_project_id = os.path.basename(project_id.replace("\\", "/"))
        session_id = safe_project_id
        
        workspace_path = os.path.join(self.workspace_root, safe_user_id, session_id)
        
        # Verify it doesn't escape workspace root
        if not os.path.abspath(workspace_path).startswith(self.workspace_root):
            raise ValueError("Invalid path resolution")
            
        os.makedirs(workspace_path, exist_ok=True)

        # Allocate dynamic port for the Next.js preview server
        assigned_port = self._find_available_port()

        # Launch container
        container = self.client.containers.run(
            image=self.image,
            name=f"agent-{session_id}-{uuid.uuid4().hex[:8]}", # Add random suffix to prevent name conflicts if orphaned
            detach=True,                    # Run in background
            remove=False,                   # We manage removal ourselves
            mem_limit="512m",               # Production Hardening: Limit memory
            cpu_quota=50000,                # Production Hardening: 0.5 CPU limit
            cpu_period=100000,              
            privileged=False,               # Production Hardening: No privileged access
            environment={
                "OPENAI_API_KEY": self.api_key,
            },
            ports={
                "3000/tcp": assigned_port
            },
            volumes={
                workspace_path: {
                    "bind": "/workspace",
                    "mode": "rw",
                },
            },
            working_dir="/workspace",
        )

        self._sessions[session_id] = {
            "container_id": container.id,
            "workspace": workspace_path,
            "preview_port": assigned_port
        }
        logger.info(f"Session created: {session_id} -> container {container.short_id} in {workspace_path}, exposed on port {assigned_port}")

        return {
            "session_id": session_id,
            "container_id": container.short_id,
            "workspace": workspace_path,
            "preview_port": assigned_port,
            "status": "running",
        }

    def run_agent_command(self, session_id: str, prompt: str):
        """
        Execute a Codex CLI command inside the session container.
        Yields stdout chunks as they arrive (generator).
        """
        session_info = self._sessions.get(session_id)
        if not session_info:
            raise ValueError(f"Session not found: {session_id}")
        
        container_id = session_info["container_id"]

        container = self.client.containers.get(container_id)

        # Check if we want to run a direct shell command or mock behavior
        # (This bypasses 401 OpenAI API key issues for testing infrastructure)
        if prompt.startswith("mock:") or prompt.startswith("bash:"):
            command_to_run = prompt.split(":", 1)[1].strip()
            if "<current_project_context>" in command_to_run:
                command_to_run = command_to_run.split("<current_project_context>")[0].strip()
            cmd = ["bash", "-c", command_to_run]
        else:
            cmd = [
                "bash",
                "-c",
                'codex exec --json --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check --ephemeral -C /workspace "$0" < /dev/null',
                prompt,
            ]

        logger.info(f"Executing in {session_id}: {prompt[:80]}...")

        # exec_run with stream=True returns (exit_code, output_generator)
        _, output_stream = container.exec_run(
            cmd,
            stream=True,
            demux=False,     # Interleave stdout/stderr
            workdir="/workspace",
        )

        for chunk in output_stream:
            if chunk:
                decoded = chunk.decode("utf-8", errors="replace")
                # Do not spam the root logger with every chunk to prevent log bloat in prod
                yield decoded

    def stop_session(self, session_id: str) -> dict:
        """
        Stop and remove the container for a session.
        The workspace directory remains on the host filesystem.
        """
        session_info = self._sessions.get(session_id)
        if not session_info:
            raise ValueError(f"Session not found: {session_id}")

        container_id = session_info["container_id"]
        workspace_path = session_info["workspace"]

        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=5)
            container.remove(force=True)
            logger.info(f"Container removed for session: {session_id}")
        except NotFound:
            logger.info(f"Container already gone for session: {session_id}")
        except APIError as e:
            logger.error(f"Docker API error: {e}")

        del self._sessions[session_id]

        files = os.listdir(workspace_path) if os.path.exists(workspace_path) else []

        return {
            "session_id": session_id,
            "status": "stopped",
            "workspace_files": files,
            "workspace_persisted": os.path.exists(workspace_path),
        }

    def start_preview(self, session_id: str) -> dict:
        """Start the Next.js preview server inside the container."""
        session_info = self._sessions.get(session_id)
        if not session_info:
            raise ValueError(f"Session not found: {session_id}")
            
        container_id = session_info["container_id"]
        preview_port = session_info.get("preview_port")
        
        try:
            container = self.client.containers.get(container_id)
            
            # We first install dependencies if needed.
            # Then we start the server in the background.
            # For simplicity, we can do it in a single detached bash command.
            cmd = "npm install && npm run dev -- --hostname 0.0.0.0"
            
            # Execute detached in the background
            container.exec_run(
                ["bash", "-c", cmd],
                detach=True,
                workdir="/workspace"
            )
            
            logger.info(f"Started preview server in session {session_id} on port {preview_port}")
            
            return {
                "status": "running",
                "preview_port": preview_port,
                "preview_url": f"http://localhost:{preview_port}"
            }
        except Exception as e:
            logger.error(f"Failed to start preview: {e}")
            raise

    def stop_preview(self, session_id: str) -> dict:
        """Stop the Next.js preview server inside the container."""
        session_info = self._sessions.get(session_id)
        if not session_info:
            raise ValueError(f"Session not found: {session_id}")
            
        container_id = session_info["container_id"]
        
        try:
            container = self.client.containers.get(container_id)
            # Find and kill the Next.js process
            container.exec_run(
                ["bash", "-c", "pkill -f 'next dev'"],
                detach=True
            )
            logger.info(f"Stopped preview server in session {session_id}")
            return {"status": "stopped"}
        except Exception as e:
            logger.error(f"Failed to stop preview: {e}")
            raise

    def get_session_status(self, session_id: str) -> dict | None:
        """Get the current status of a session."""
        session_info = self._sessions.get(session_id)
        if not session_info:
            return None
            
        container_id = session_info["container_id"]
        workspace_path = session_info["workspace"]

        try:
            container = self.client.containers.get(container_id)
            files = os.listdir(workspace_path) if os.path.exists(workspace_path) else []
            return {
                "session_id": session_id,
                "container_id": container.short_id,
                "status": container.status,
                "preview_port": session_info.get("preview_port"),
                "workspace_files": files,
            }
        except NotFound:
            return {
                "session_id": session_id,
                "status": "container_not_found",
            }

