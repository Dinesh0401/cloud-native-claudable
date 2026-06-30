# Compute vs. Storage Analysis

## Compute (Container)
- **State**: Stateless and ephemeral.
- **Role**: Serves as a disposable runtime containing global CLI tools (npm, git, Node.js, Codex).
- **Lifecycle**: Created when a project session starts, and completely destroyed (`docker rm`) when the session ends.

## Storage (Volume)
- **State**: Stateful and persistent.
- **Role**: Stores user project files (Next.js scaffold, package.json, source code).
- **Lifecycle**: Exists permanently on the host storage disk (mounted into the container at `/workspace`). 

## Systems Advantage
By separating execution (Compute) from files (Storage), the system achieves:
1. **Safety**: Malicious commands cannot escape the ephemeral container to access host files.
2. **Reliability**: Stopping a workspace container never risks corrupting or deleting project code.
3. **Density**: Hundreds of idle user workspaces can reside on disk without consuming CPU/RAM since no containers need to run for them.
