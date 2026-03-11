from pydantic import BaseModel, Field
from datetime import datetime


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str | None
    created_at: datetime