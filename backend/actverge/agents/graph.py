from langgraph.graph import StateGraph, START, END
from actverge.agents.state import ActVergeState
from actverge.agents.nodes.task_interpreter import task_interpreter_node
from actverge.agents.nodes.executor import executor_node
from actverge.agents.nodes.state_observer import state_observer_node
from actverge.agents.nodes.evidence_collector import evidence_collector_node
from actverge.agents.nodes.outcome_verifier import outcome_verifier_node
from actverge.agents.nodes.recovery_agent import recovery_agent_node
from actverge.agents.nodes.human_escalation import human_escalation_node

def route_after_verification(state: ActVergeState) -> str:
    verdict = state.get("verdict")
    if verdict == "SUCCESS":
        return END
    elif verdict in ["PARTIAL", "UNCERTAIN", "FAILED"]:
        retries = state.get("retry_count") or 0
        if retries < 2:
            return "recovery_agent"
        else:
            return "human_escalation"
    return END

def route_after_recovery(state: ActVergeState) -> str:
    if state.get("escalated") or not state.get("recovery_safe"):
        return "human_escalation"
    retries = state.get("retry_count") or 0
    if retries <= 2:
        return "state_observer"
    return "human_escalation"

def create_actverge_graph():
    builder = StateGraph(ActVergeState)

    builder.add_node("task_interpreter", task_interpreter_node)
    builder.add_node("executor", executor_node)
    builder.add_node("state_observer", state_observer_node)
    builder.add_node("evidence_collector", evidence_collector_node)
    builder.add_node("outcome_verifier", outcome_verifier_node)
    builder.add_node("recovery_agent", recovery_agent_node)
    builder.add_node("human_escalation", human_escalation_node)

    builder.add_edge(START, "task_interpreter")
    builder.add_edge("task_interpreter", "executor")
    builder.add_edge("executor", "state_observer")
    builder.add_edge("state_observer", "evidence_collector")
    builder.add_edge("evidence_collector", "outcome_verifier")

    builder.add_conditional_edges(
        "outcome_verifier",
        route_after_verification,
        {
            "recovery_agent": "recovery_agent",
            "human_escalation": "human_escalation",
            END: END
        }
    )

    builder.add_conditional_edges(
        "recovery_agent",
        route_after_recovery,
        {
            "state_observer": "state_observer",
            "human_escalation": "human_escalation",
            END: END
        }
    )

    builder.add_edge("human_escalation", END)

    return builder.compile()

actverge_graph = create_actverge_graph()
