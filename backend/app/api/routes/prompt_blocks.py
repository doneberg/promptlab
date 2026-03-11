from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.dependencies import get_db, get_current_user
from app.domain.models.prompt_block import PromptBlock
from app.domain.models.workflow import Workflow
from app.domain.models.user import User
from app.api.schemas.prompt_block import (
    PromptBlockCreate,
    PromptBlockResponse,
)

router = APIRouter(
    prefix="/workflows/{workflow_id}/blocks",
    tags=["prompt_blocks"],
)


@router.post("/", response_model=PromptBlockResponse)
async def create_prompt_block(
    workflow_id: str,
    payload: PromptBlockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify workflow exists and belongs to user
    result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == current_user.id,
        )
    )
    workflow = result.scalar_one_or_none()

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    block = PromptBlock(
        workflow_id=workflow_id,
        order_index=payload.order_index,
        role=payload.role,
        content_template=payload.content_template,
    )

    db.add(block)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate order_index for this workflow",
        )

    await db.refresh(block)

    return PromptBlockResponse(
        id=block.id,
        workflow_id=block.workflow_id,
        order_index=block.order_index,
        role=block.role,
        content_template=block.content_template,
        created_at=block.created_at,
    )