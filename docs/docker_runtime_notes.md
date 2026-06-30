# Docker Runtime Learning Notes

## Container Isolation Primitives
Containers are standard OS processes isolated using Linux Kernel namespaces and cgroups:

- **PID Namespace**: Isolates the process ID tree. An agent running inside Container A has no visibility into Container B's process tree.
- **Network Namespace**: Provides independent network interfaces and loopbacks. Each agent workspace can boot preview web servers (like Next.js on port 3000) without port conflicts on the host.
- **Mount Namespace**: Restricts filesystem access. The agent process only sees `/workspace` (which maps to its project volume mount).
- **User Namespace**: Maps root inside the container to a non-privileged UID on the host, preventing host takeover.
- **Cgroups**: Restricts hardware resource consumption (limits CPU cores, RAM, and disk I/O) to prevent resource starvation.
