from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class WorkflowRequest(BaseModel):
    goal: str

class WorkflowStep(BaseModel):
    id: str
    type: str # 'shell', 'ai', 'write_file'
    content: str # the command, prompt, or file content
    target: Optional[str] = None # file path for write_file
    depends_on: Optional[List[str]] = []

class WorkflowResponse(BaseModel):
    id: int
    goal: str
    steps: List[WorkflowStep]

class RunResponse(BaseModel):
    run_id: int
    status: str
