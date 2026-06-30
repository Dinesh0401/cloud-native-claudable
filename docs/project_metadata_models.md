# Project Metadata Models

## Overview
FastAPI uses Pydantic schemas to validate and serialize data transmitted over REST endpoints.

## Pydantic Model Blueprint

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ExecRequest(BaseModel):
    prompt: str = Field(..., description="Prompt instruction for the agent")

class SessionResponse(BaseModel):
    session_id: str
    container_id: str
    workspace: str
    status: str

class ProjectSettings(BaseModel):
    preferred_cli: str = "codex"
    selected_model: str = "gpt-4o"
    fallback_enabled: bool = True
```
