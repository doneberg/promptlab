import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class ExecutionStep(Base):
    __tablename__ = "execution_steps"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    execution_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    prompt_block_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("prompt_blocks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    rendered_prompt: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    response_text: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )

    latency_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    execution = relationship("WorkflowExecution", backref="steps")