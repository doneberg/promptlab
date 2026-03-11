import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class PromptBlock(Base):
    __tablename__ = "prompt_blocks"

    __table_args__ = (
        UniqueConstraint(
            "workflow_id",
            "order_index",
            name="uq_workflow_order",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    workflow_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,  # system | user | assistant
    )

    content_template: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    workflow = relationship("Workflow", backref="prompt_blocks")