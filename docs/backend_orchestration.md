# Backend Orchestration Architecture

## Overview
This document traces the responsibilities of the FastAPI Control Plane:

1. **Docker Client Connection**: Connects to the host daemon socket using standard environment namespaces (`docker.from_env()`).
2. **Session Mappings**: Stores mappings between unique project session IDs and running containers.
3. **Execution Streams**: Uses `container.exec_run` with stream flags enabled. As stdout/stderr chunks are populated inside the container, they are decoded and streamed chunk-by-chunk back to the client using non-buffered generators.
4. **Lifecycle Hooks**: Triggers stop and force removals on container objects during deletion request sequences.
