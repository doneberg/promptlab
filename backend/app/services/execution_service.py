import time
from datetime import datetime
from sqlalchemy import select

from app.domain.models.workflow_execution import WorkflowExecution
from app.domain.models.execution_step import ExecutionStep
from app.domain.models.prompt_block import PromptBlock
from app.infrastructure.ai.factory import get_ai_provider
from app.infrastructure.database import AsyncSessionLocal
from jinja2 import Template


class ExecutionService:

    @staticmethod
    async def execute_workflow(
        execution_id: str,
        variables: dict,
    ):
        provider = get_ai_provider()

        async with AsyncSessionLocal() as db:

            # Load execution fresh
            result = await db.execute(
                select(WorkflowExecution).where(
                    WorkflowExecution.id == execution_id
                )
            )
            execution = result.scalar_one()

            try:
                execution.status = "running"
                execution.started_at = datetime.utcnow()
                await db.commit()

                # Load blocks
                result = await db.execute(
                    select(PromptBlock)
                    .where(PromptBlock.workflow_id == execution.workflow_id)
                    .order_by(PromptBlock.order_index)
                )
                blocks = result.scalars().all()

                messages = []

                for block in blocks:
                    template = Template(block.content_template)
                    rendered_prompt = template.render(**variables)

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

            except Exception as e:
                execution.status = "failed"
                execution.completed_at = datetime.utcnow()
                execution.error_message = str(e)
                await db.commit()