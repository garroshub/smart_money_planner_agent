import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return default


def get_config():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    return {
        "agent_enabled": bool(api_key),
        "gemini_api_key": api_key,
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-3-flash-preview"),
        "llm_timeout_seconds": int(os.getenv("LLM_TIMEOUT_SECONDS", "20")),
        "llm_temperature": float(os.getenv("LLM_TEMPERATURE", "0.2")),
        "goals_min_chars": int(os.getenv("GOALS_MIN_CHARS", "20")),
        "goals_max_chars": int(os.getenv("GOALS_MAX_CHARS", "400")),
        "goals_max_lines": int(os.getenv("GOALS_MAX_LINES", "5")),
        "goals_block_urls": _get_bool("GOALS_BLOCK_URLS", True),
        "goals_block_emails": _get_bool("GOALS_BLOCK_EMAILS", True),
        "goals_block_phones": _get_bool("GOALS_BLOCK_PHONES", True),
        "goals_block_markdown": _get_bool("GOALS_BLOCK_MARKDOWN", True),
        "goals_block_guarantees": _get_bool("GOALS_BLOCK_GUARANTEES", True),
    }
