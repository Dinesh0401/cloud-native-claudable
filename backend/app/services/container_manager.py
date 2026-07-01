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
from docker.errors import NotFound, APIError


class ContainerManager:
    """Manages Docker containers for agent sessions."""

    def __init__(self, image: str, workspace_root: str, api_key: str):
        self.image = image
        self.workspace_root = os.path.abspath(workspace_root)
        self.api_key = api_key
        self.client = docker.from_env()

        # In-memory session registry: {session_id: container_id}
        # Day 2 only — no database needed.
        self._sessions: dict[str, str] = {}

        # Ensure workspace root exists
        os.makedirs(self.workspace_root, exist_ok=True)

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def create_session(self, project_id: str) -> dict:
        """
        Create a new agent session:
          1. Use the provided project_id as the session ID
          2. Mount the existing Next.js workspace directory
          3. Launch a Docker container with the workspace mounted
          4. Register the session
        """
        session_id = project_id
        workspace_path = os.path.join(self.workspace_root, session_id)
        os.makedirs(workspace_path, exist_ok=True)

        # Launch container
        container = self.client.containers.run(
            image=self.image,
            name=f"agent-{session_id}",
            detach=True,                    # Run in background
            remove=False,                   # We manage removal ourselves
            environment={
                "OPENAI_API_KEY": self.api_key,
            },
            volumes={
                workspace_path: {
                    "bind": "/workspace",
                    "mode": "rw",
                },
            },
            working_dir="/workspace",
        )

        self._sessions[session_id] = container.id
        print(f"[ContainerManager] Session created: {session_id} -> container {container.short_id}")

        return {
            "session_id": session_id,
            "container_id": container.short_id,
            "workspace": workspace_path,
            "status": "running",
        }

    def run_agent_command(self, session_id: str, prompt: str):
        """
        Execute a Codex CLI command inside the session container.
        Yields stdout chunks as they arrive (generator).

        Uses `codex exec` with:
          --json                                    → JSONL event stream
          --dangerously-bypass-approvals-and-sandbox → autonomous execution
          --skip-git-repo-check                     → no git requirement
          --ephemeral                               → no session persistence
          -C /workspace                             → working directory
        """
        container_id = self._sessions.get(session_id)
        if not container_id:
            raise ValueError(f"Session not found: {session_id}")

        container = self.client.containers.get(container_id)

        # Check if we want to run a direct shell command or mock behavior
        # (This bypasses 401 OpenAI API key issues for testing infrastructure)
        if prompt.startswith("mock:") or prompt.startswith("bash:"):
            command_to_run = prompt.split(":", 1)[1].strip()
            cmd = ["bash", "-c", command_to_run]
        else:
            cmd = [
                "codex", "exec",
                "--json",
                "--dangerously-bypass-approvals-and-sandbox",
                "--skip-git-repo-check",
                "--ephemeral",
                "-C", "/workspace",
                prompt,
            ]

        print(f"[ContainerManager] Executing in {session_id}: {prompt[:80]}...")

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
                print(decoded, end="", flush=True)  # Echo to server logs
                yield decoded

    def stop_session(self, session_id: str) -> dict:
        """
        Stop and remove the container for a session.
        The workspace directory remains on the host filesystem.
        """
        container_id = self._sessions.get(session_id)
        if not container_id:
            raise ValueError(f"Session not found: {session_id}")

        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=5)
            container.remove(force=True)
            print(f"[ContainerManager] Container removed for session: {session_id}")
        except NotFound:
            print(f"[ContainerManager] Container already gone for session: {session_id}")
        except APIError as e:
            print(f"[ContainerManager] Docker API error: {e}")

        del self._sessions[session_id]

        workspace_path = os.path.join(self.workspace_root, session_id)
        files = os.listdir(workspace_path) if os.path.exists(workspace_path) else []

        return {
            "session_id": session_id,
            "status": "stopped",
            "workspace_files": files,
            "workspace_persisted": os.path.exists(workspace_path),
        }

    def get_session_status(self, session_id: str) -> dict | None:
        """Get the current status of a session."""
        container_id = self._sessions.get(session_id)
        if not container_id:
            return None

        try:
            container = self.client.containers.get(container_id)
            workspace_path = os.path.join(self.workspace_root, session_id)
            files = os.listdir(workspace_path) if os.path.exists(workspace_path) else []
            return {
                "session_id": session_id,
                "container_id": container.short_id,
                "status": container.status,
                "workspace_files": files,
            }
        except NotFound:
            return {
                "session_id": session_id,
                "status": "container_not_found",
            }
