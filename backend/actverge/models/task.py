from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field
import uuid

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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    pass

class TaskRead(TaskBase):
    id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
