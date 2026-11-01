"""
LiteLLM Gateway & Router Configuration.
Configured for Option 2: OpenRouter Universal API.
Supports the OpenRouter Free Models Router ('openrouter/free') which automatically
load-balances across available free models without rate limiting (429) or model missing (404) errors.
"""
import os
import logging
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("actverge.llm.router")

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "litellm_config.yaml"

INTERPRETER_ALIAS = "actverge/interpreter"
VERIFIER_ALIAS = "actverge/verifier"
MULTIMODAL_ALIAS = "actverge/multimodal"
FALLBACK_ALIAS = "actverge/fallback"

# Fallback direct OpenRouter models if config file cannot be read
DEFAULT_OPENROUTER_MAP = {
    INTERPRETER_ALIAS: "openrouter/free",
    VERIFIER_ALIAS: "openrouter/free",
    MULTIMODAL_ALIAS: "openrouter/free",
    FALLBACK_ALIAS: "openrouter/free",
}


def get_litellm_config() -> Dict[str, Any]:
    """Load the LiteLLM config yaml file."""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Could not parse {CONFIG_PATH}: {e}")
    return {}


def get_model_for_alias(alias: str) -> str:
    """Returns the underlying provider model name for a given alias."""
    config = get_litellm_config()
    for entry in config.get("model_list", []):
        if entry.get("model_name") == alias:
            model = entry.get("litellm_params", {}).get("model", "")
            if model and model != "PENDING_USER_APPROVAL":
                return model
    return DEFAULT_OPENROUTER_MAP.get(alias, "openrouter/free")


get_model_or_raise = get_model_for_alias

from actverge.core.config import settings

def get_api_key() -> str:
    return os.environ.get("OPENROUTER_API_KEY", "").strip() or settings.OPENROUTER_API_KEY.strip()

def is_model_approved(alias: str) -> bool:
    """Checks if a valid OpenRouter API key is configured and model is mapped."""
    if settings.ENVIRONMENT == "test" or os.environ.get("ENVIRONMENT") == "test":
        logger.info(f"Test environment active; skipping live LLM call for {alias}.")
        return None

    api_key = get_api_key()
    if not api_key or api_key == "PENDING_APPROVAL":
        return False
    model = get_model_for_alias(alias)
    return bool(model) and model != "PENDING_USER_APPROVAL"


async def call_llm(
    alias: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    response_format: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Invokes the mapped LLM asynchronously using OpenRouter.

    Returns the assistant message content string, or None if the API key is not configured.
    """
    if settings.ENVIRONMENT == "test" or os.environ.get("ENVIRONMENT") == "test":
        logger.info(f"Test environment active; skipping live LLM call for {alias}.")
        return None

    api_key = get_api_key()
    if not api_key or api_key == "PENDING_APPROVAL":
        logger.info(f"OPENROUTER_API_KEY not set; skipping LLM call for {alias}.")
        return None

    model = get_model_for_alias(alias)
    
    # OpenRouter model resolution:
    # 'openrouter/free' is a special meta-router model slug and must NOT have 'openrouter/' stripped.
    if model == "openrouter/free":
        clean_model = "openrouter/free"
    elif model.startswith("openrouter/"):
        clean_model = model[len("openrouter/"):]
    else:
        clean_model = model

    logger.info(f"Calling LLM for alias '{alias}' -> model: {clean_model}")

    try:
        import httpx
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "ActVerge",
            "Content-Type": "application/json"
        }
        payload: Dict[str, Any] = {
            "model": clean_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 800
        }
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                logger.warning(f"OpenRouter returned status {resp.status_code}: {resp.text[:120]}")
    except Exception as e:
        logger.warning(f"OpenRouter direct call error for {alias} ({clean_model}): {e}")

    try:
        import litellm
        litellm_model = clean_model if clean_model.startswith("openrouter/") else f"openrouter/{clean_model}"
        kwargs: Dict[str, Any] = {
            "model": litellm_model,
            "messages": messages,
            "api_key": api_key,
            "temperature": temperature,
            "max_tokens": 1500
        }
        if response_format:
            kwargs["response_format"] = response_format

        response = await litellm.acompletion(**kwargs)
        return response.choices[0].message.content
    except Exception as lite_err:
        logger.warning(f"LiteLLM fallback failed ({lite_err})")
        return None
