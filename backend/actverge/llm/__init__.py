from actverge.llm.router import (
    INTERPRETER_ALIAS,
    VERIFIER_ALIAS,
    MULTIMODAL_ALIAS,
    FALLBACK_ALIAS,
    is_model_approved,
    get_model_for_alias,
    call_llm,
)

get_model_or_raise = get_model_for_alias

__all__ = [
    "INTERPRETER_ALIAS",
    "VERIFIER_ALIAS",
    "MULTIMODAL_ALIAS",
    "FALLBACK_ALIAS",
    "is_model_approved",
    "get_model_for_alias",
    "get_model_or_raise",
    "call_llm",
]

