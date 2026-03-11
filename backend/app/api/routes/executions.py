from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db, get_current_user
from app.domain.models.workflow import Workflow
from app.domain.models.workflow_execution import WorkflowExecution
from app.domain.models.user import User
from app.services.execution_service import ExecutionService


router = APIRouter(
    prefix="/workflows/{workflow_id}/execute",
    tags=["executions"],
)


@router.post("/")
async def execute_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify workflow ownership
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

    # Create execution record
    execution = WorkflowExecution(
        workflow_id=workflow_id,
        user_id=current_user.id,
        status="pending",
    )

    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    # Run background execution
    background_tasks.add_task(
        ExecutionService.execute_workflow,
        execution,
        db,
    )

    return {
        "execution_id": execution.id,
        "status": execution.status,
    }