from pydantic import BaseModel
from datetime import datetime
from typing import List


class ExecutionStepResponse(BaseModel):
    id: str
    order_index: int
    rendered_prompt: str
    response_text: str | None
    latency_ms: int | None
    created_at: datetime


class WorkflowExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    steps: List[ExecutionStepResponse] = []