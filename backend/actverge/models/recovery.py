from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON
import uuid

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class RecoveryAction(SQLModel, table=True):
    __tablename__ = "recovery_actions"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", index=True)
    action_type: str = Field(...)
    details: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    idempotency_key: str = Field(index=True)
    success: bool = Field(default=False)
    executed_at: datetime = Field(default_factory=utc_now)

class EscalationRequest(SQLModel, table=True):
    __tablename__ = "escalation_requests"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", index=True)
    reason: str = Field(...)
    risk_level: str = Field(default="HIGH")
    resolved: bool = Field(default=False)
    resolution_notes: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
