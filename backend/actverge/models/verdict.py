from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlmodel import SQLModel, Field, Column, JSON
import uuid

class VerdictType(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    UNCERTAIN = "UNCERTAIN"
    PENDING = "PENDING"

class Verdict(SQLModel, table=True):
    __tablename__ = "verdicts"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", index=True)
    verdict: VerdictType = Field(default=VerdictType.PENDING)
    reasoning: Optional[str] = Field(default=None)
    evidence_summary: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    recovery_attempted: bool = Field(default=False)
    escalated: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
