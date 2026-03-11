from pydantic import BaseModel, Field
from datetime import datetime


class PromptBlockCreate(BaseModel):
    order_index: int = Field(ge=0)
    role: str = Field(min_length=1, max_length=50)
    content_template: str = Field(min_length=1)


class PromptBlockResponse(BaseModel):
    id: str
    workflow_id: str
    order_index: int
    role: str
    content_template: str
    created_at: datetime