# Deployment Planning Notes

## Cloud-Native Production Architecture
Transitioning the orchestration plane to production scaling:

1. **Orchestrator Host**:
   - FastAPI deployed on AWS ECS (Fargate) or Kubernetes (EKS).
   - Load-balanced with sticky sessions for WebSockets.
2. **Compute Plane (User Sandboxes)**:
   - Dynamic pod provisioning using the Kubernetes API instead of local Docker socket connections.
   - Pods are restricted to sandboxed nodes with specific namespace constraints and IAM task roles.
3. **Storage Plane (Workspace Volume Mounts)**:
   - Host directory volumes replaced by AWS EFS (Elastic File System) or GCP Filestore.
   - Read-Write-Many (RWX) volume mounts allow workspaces to float across container hosting nodes dynamically.
4. **API Gateway / Proxy**:
   - Nginx or Traefik routing HTTP and WebSocket traffic with CORS protection.
