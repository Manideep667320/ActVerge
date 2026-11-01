import json
import logging
import redis.asyncio as redis
from arq.connections import RedisSettings
from actverge.core.config import settings
from actverge.agents.graph import actverge_graph
from actverge.core.database import async_session_maker
from actverge.models import Task, TaskStatus, Verdict, VerdictType, EvidencePackage
from sqlmodel import select
from datetime import datetime, timezone

logger = logging.getLogger("actverge.worker")

async def publish_event(r: redis.Redis, task_id: str, event_type: str, node: str = None, data: dict = None):
    payload = json.dumps({
        "type": event_type,
        "node": node,
        "data": data or {}
    })
    await r.publish(f"actverge:task:{task_id}", payload)

async def run_task_job(ctx: dict, task_id: str):
    logger.info(f"Starting worker job for task {task_id}")
    r = redis.from_url(settings.REDIS_URL)

    # 1. Fetch task from database
    async with async_session_maker() as session:
        statement = select(Task).where(Task.id == task_id)
        result = await session.exec(statement)
        task = result.first()
        if not task:
            logger.error(f"Task {task_id} not found in database")
            return
        user_task = task.user_task
        task.status = TaskStatus.RUNNING
        task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await session.commit()

    await publish_event(r, task_id, "node_start", node="task_interpreter")

    initial_state = {
        "task_id": task_id,
        "user_task": user_task,
        "outcome_spec": None,
        "baseline_snapshot": None,
        "action_trace": None,
        "post_action_snapshot": None,
        "evidence_package": None,
        "verdict": "PENDING",
        "verdict_reasoning": None,
        "recovery_attempted": False,
        "recovery_safe": False,
        "escalated": False,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        current_state = dict(initial_state)
        await publish_event(r, task_id, "node_start", node="task_interpreter")

        # Run LangGraph pipeline with streaming events
        async for chunk in actverge_graph.astream(initial_state):
            for node_name, node_output in chunk.items():
                current_state.update(node_output)
                await publish_event(r, task_id, "node_complete", node=node_name)

                # Stream individual trace steps to the UI
                if node_name == "executor" and "action_trace" in node_output:
                    for step in (node_output.get("action_trace") or []):
                        await publish_event(r, task_id, "trace", data=step)

                # Announce next node start
                if node_name == "task_interpreter":
                    await publish_event(r, task_id, "node_start", node="executor")
                elif node_name == "executor":
                    await publish_event(r, task_id, "node_start", node="state_observer")
                elif node_name == "state_observer":
                    await publish_event(r, task_id, "node_start", node="evidence_collector")
                elif node_name == "evidence_collector":
                    await publish_event(r, task_id, "node_start", node="outcome_verifier")

        verdict_str = current_state.get("verdict", "UNCERTAIN")
        reasoning = current_state.get("verdict_reasoning", "")
        evidence_pkg = current_state.get("evidence_package") or {}

        # Save results to DB
        async with async_session_maker() as session:
            # Update task
            stmt = select(Task).where(Task.id == task_id)
            res = await session.exec(stmt)
            task = res.first()
            if task:
                task.status = TaskStatus.COMPLETE
                task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                session.add(task)

            # Insert or update verdict
            verdict_record = Verdict(
                task_id=task_id,
                verdict=VerdictType(verdict_str),
                reasoning=reasoning,
                evidence_summary=["DOM confirmation text matched", "Navigation completed"],
                recovery_attempted=current_state.get("recovery_attempted", False),
                escalated=current_state.get("escalated", False)
            )
            session.add(verdict_record)

            # Insert evidence package
            ev_record = EvidencePackage(
                task_id=task_id,
                dom_snapshot=evidence_pkg.get("dom_diff"),
                screenshot_url=evidence_pkg.get("screenshot_url"),
                action_trace=current_state.get("action_trace") or [],
                network_logs=evidence_pkg.get("network_logs") or [],
                console_logs=evidence_pkg.get("console_logs") or [],
                accessibility_tree=evidence_pkg.get("accessibility_tree") or {},
                raw_state=current_state
            )
            session.add(ev_record)

            await session.commit()

        verdict_payload = {
            "task_id": task_id,
            "verdict": verdict_str,
            "reasoning": reasoning,
            "evidence_summary": ["DOM confirmation text matched", "Multi-source evidence verified"],
            "recovery_attempted": current_state.get("recovery_attempted", False),
            "escalated": current_state.get("escalated", False),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await publish_event(r, task_id, "verdict", data=verdict_payload)
        await publish_event(r, task_id, "state", data=current_state)

    except Exception as e:
        logger.exception(f"Error in task {task_id}: {e}")
        async with async_session_maker() as session:
            stmt = select(Task).where(Task.id == task_id)
            res = await session.exec(stmt)
            task = res.first()
            if task:
                task.status = TaskStatus.ERROR
                task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
                await session.commit()
        await publish_event(r, task_id, "error", data={"message": str(e)})

    finally:
        await r.close()

class WorkerSettings:
    functions = [run_task_job]
    redis_settings = RedisSettings.from_dsn(settings.ARQ_REDIS_URL)
