from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from actverge.core.database import get_session
from actverge.models import Verdict, EvidencePackage

router = APIRouter(prefix="/verdicts", tags=["verdicts"])

@router.get("/{task_id}", response_model=Verdict)
async def get_verdict(task_id: str, session: AsyncSession = Depends(get_session)):
    statement = select(Verdict).where(Verdict.task_id == task_id)
    result = await session.exec(statement)
    verdict = result.first()
    if not verdict:
        raise HTTPException(status_code=404, detail="Verdict not found for task")
    return verdict

@router.get("/{task_id}/evidence", response_model=EvidencePackage)
async def get_evidence(task_id: str, session: AsyncSession = Depends(get_session)):
    statement = select(EvidencePackage).where(EvidencePackage.task_id == task_id)
    result = await session.exec(statement)
    evidence = result.first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found for task")
    return evidence
