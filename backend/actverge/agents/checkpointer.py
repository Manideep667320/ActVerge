from langgraph.checkpoint.memory import MemorySaver

def get_checkpointer():
    """Returns the LangGraph checkpointer instance for state management."""
    return MemorySaver()
