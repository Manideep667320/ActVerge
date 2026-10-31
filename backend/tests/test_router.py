import pytest
from actverge.llm.router import (
    VERIFIER_ALIAS,
    INTERPRETER_ALIAS,
    MULTIMODAL_ALIAS,
    FALLBACK_ALIAS,
    get_model_for_alias,
    DEFAULT_OPENROUTER_MAP
)

def test_router_aliases():
    assert VERIFIER_ALIAS == "actverge/verifier"
    assert INTERPRETER_ALIAS == "actverge/interpreter"
    assert MULTIMODAL_ALIAS == "actverge/multimodal"
    assert FALLBACK_ALIAS == "actverge/fallback"

def test_model_resolution():
    verifier_model = get_model_for_alias(VERIFIER_ALIAS)
    assert verifier_model is not None
    assert "gpt-4o-mini" in verifier_model

    interpreter_model = get_model_for_alias(INTERPRETER_ALIAS)
    assert interpreter_model is not None
    assert "gpt-4o-mini" in interpreter_model

def test_default_openrouter_map():
    assert VERIFIER_ALIAS in DEFAULT_OPENROUTER_MAP
    assert INTERPRETER_ALIAS in DEFAULT_OPENROUTER_MAP
    assert MULTIMODAL_ALIAS in DEFAULT_OPENROUTER_MAP
    assert FALLBACK_ALIAS in DEFAULT_OPENROUTER_MAP
