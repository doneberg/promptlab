from app.domain.models.execution_step import ExecutionStep
from app.api.schemas.execution import (
    WorkflowExecutionResponse,
    ExecutionStepResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db, get_current_user
from app.domain.models.workflow import Workflow
from app.domain.models.workflow_execution import WorkflowExecution
from app.domain.models.user import User
from app.services.execution_service import ExecutionService
from pydantic import BaseModel
from typing import Dict, Any
from pydantic import Field

class ExecutionInput(BaseModel):
    variables: Dict[str, Any] = Field(default_factory=dict)

router = APIRouter(
    prefix="/executions",
    tags=["executions"],
)


@router.post("/workflows/{workflow_id}")
async def execute_workflow(
    workflow_id: str,
    payload: ExecutionInput,
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


    background_tasks.add_task(
        ExecutionService.execute_workflow,
        execution.id,
        payload.variables,
    )

    return {
        "execution_id": execution.id,
        "status": execution.status,
    }

@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
async def get_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Load execution with ownership check via workflow
    result = await db.execute(
        select(WorkflowExecution)
        .join(Workflow, Workflow.id == WorkflowExecution.workflow_id)
        .where(
            WorkflowExecution.id == execution_id,
            Workflow.user_id == current_user.id,
        )
    )
    execution = result.scalar_one_or_none()

    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    # Load steps
    steps_result = await db.execute(
        select(ExecutionStep)
        .where(ExecutionStep.execution_id == execution.id)
        .order_by(ExecutionStep.order_index)
    )
    steps = steps_result.scalars().all()

    return WorkflowExecutionResponse(
        id=execution.id,
        workflow_id=execution.workflow_id,
        status=execution.status,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        steps=[
            ExecutionStepResponse(
                id=s.id,
                order_index=s.order_index,
                rendered_prompt=s.rendered_prompt,
                response_text=s.response_text,
                latency_ms=s.latency_ms,
                created_at=s.created_at,
            )
            for s in steps
        ],
    )

@router.get("/workflows/{workflow_id}/executions", response_model=list[WorkflowExecutionResponse])
async def list_executions(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership
    workflow_result = await db.execute(
        select(Workflow).where(
            Workflow.id == workflow_id,
            Workflow.user_id == current_user.id,
        )
    )
    workflow = workflow_result.scalar_one_or_none()

    if workflow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    result = await db.execute(
        select(WorkflowExecution)
        .where(WorkflowExecution.workflow_id == workflow_id)
        .order_by(WorkflowExecution.started_at.desc())
    )
    executions = result.scalars().all()

    return [
        WorkflowExecutionResponse(
            id=e.id,
            workflow_id=e.workflow_id,
            status=e.status,
            started_at=e.started_at,
            completed_at=e.completed_at,
            steps=[],
        )
        for e in executions
    ]