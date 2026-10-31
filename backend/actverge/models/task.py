from datetime import datetime, timezone
from enum import Enum
from sqlmodel import SQLModel, Field
import uuid

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    INTERPRETING = "interpreting"
    EXECUTING = "executing"
    OBSERVING = "observing"
    COLLECTING_EVIDENCE = "collecting_evidence"
    VERIFYING = "verifying"
    RECOVERING = "recovering"
    ESCALATED = "escalated"
    COMPLETE = "complete"
    ERROR = "error"

class TaskBase(SQLModel):
    user_task: str

class Task(TaskBase, table=True):
    __tablename__ = "tasks"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    status: TaskStatus = Field(default=TaskStatus.QUEUED)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
