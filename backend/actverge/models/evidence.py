from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlmodel import SQLModel, Field, Column, JSON
import uuid

class EvidencePackage(SQLModel, table=True):
    __tablename__ = "evidence_packages"
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    task_id: str = Field(foreign_key="tasks.id", index=True)
    dom_snapshot: Optional[str] = Field(default=None)
    screenshot_url: Optional[str] = Field(default=None)
    action_trace: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    network_logs: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    console_logs: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    accessibility_tree: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    raw_state: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    collected_at: datetime = Field(default_factory=datetime.utcnow)
