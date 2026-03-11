import time
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.workflow_execution import WorkflowExecution
from app.domain.models.execution_step import ExecutionStep
from app.domain.models.prompt_block import PromptBlock
from app.infrastructure.ai.factory import get_ai_provider


class ExecutionService:

    @staticmethod
    async def execute_workflow(
        execution: WorkflowExecution,
        db: AsyncSession,
    ):
        provider = get_ai_provider()

        try:
            # Mark running
            execution.status = "running"
            execution.started_at = datetime.utcnow()
            await db.commit()

            # Load blocks in order
            result = await db.execute(
                select(PromptBlock)
                .where(PromptBlock.workflow_id == execution.workflow_id)
                .order_by(PromptBlock.order_index)
            )
            blocks = result.scalars().all()

            messages = []

            for block in blocks:
                # Render template (basic: no variables yet)
                rendered_prompt = block.content_template

                messages.append({
                    "role": block.role,
                    "content": rendered_prompt,
                })

                start_time = time.time()

                response_text = await provider.generate(messages)

                latency_ms = int((time.time() - start_time) * 1000)

                step = ExecutionStep(
                    execution_id=execution.id,
                    prompt_block_id=block.id,
                    order_index=block.order_index,
                    rendered_prompt=rendered_prompt,
                    response_text=response_text,
                    latency_ms=latency_ms,
                )

                db.add(step)
                await db.commit()

            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            await db.commit()

        except Exception:
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            await db.commit()
            raise