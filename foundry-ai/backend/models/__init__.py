"""
Foundry AI — SQLAlchemy Models
Database models for projects, council decisions, and agent tasks.
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
import enum


class ProjectStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    COUNCIL_ANALYZING = "council_analyzing"
    COUNCIL_PLANNING = "council_planning"
    AGENTS_EXECUTING = "agents_executing"
    REVIEW_IN_PROGRESS = "review_in_progress"
    INTEGRATING = "integrating"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentTaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class Project(Base):
    """A user-submitted project idea and its lifecycle."""
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    idea: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), default=ProjectStatus.SUBMITTED.value
    )
    prd: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    architecture: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    schema_contract: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    agent_plan: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    final_output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    project_structure: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    workflow_run_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    council_decisions: Mapped[list["CouncilDecision"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    agent_tasks: Mapped[list["AgentTask"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    logs: Mapped[list["ProjectLog"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class CouncilDecision(Base):
    """A decision made by the AI Council during deliberation."""
    __tablename__ = "council_decisions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False
    )
    phase: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(30), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    project: Mapped["Project"] = relationship(back_populates="council_decisions")


class AgentTask(Base):
    """A task assigned to an execution agent."""
    __tablename__ = "agent_tasks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False
    )
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=AgentTaskStatus.PENDING.value
    )
    input_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(default=0)
    depends_on: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    project: Mapped["Project"] = relationship(back_populates="agent_tasks")


class ProjectLog(Base):
    """Log entry for council reasoning or agent execution."""
    __tablename__ = "project_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id"), nullable=False
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    level: Mapped[str] = mapped_column(String(10), default="info")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    project: Mapped["Project"] = relationship(back_populates="logs")
