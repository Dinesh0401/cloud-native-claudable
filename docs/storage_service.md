# Storage Service Abstraction

## Overview
To prepare the system for cloud-native deployment, a Storage Service abstraction is structured to handle file sync operations between the host disk and cloud object storage (e.g. AWS S3 / GCP Cloud Storage).

## Interface Design

```python
class CloudStorageService:
    """Interface for cloud object storage sync."""

    def download_workspace(self, session_id: str, local_path: str):
        """Fetch remote zipped project files from object store and unpack locally."""
        pass

    def upload_workspace(self, session_id: str, local_path: str):
        """Pack local project workspace directory and push zipped archive back to bucket."""
        pass
```

## Storage Sync Hook Points
1. **Container Bootstrap**: Before launching the Docker container, the orchestrator pulls the remote workspace to the host volume path.
2. **Container Terminate**: When a session is closed, the orchestrator updates the remote zip file with the latest workspace edits.
