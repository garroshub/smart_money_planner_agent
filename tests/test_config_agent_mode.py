from app.config import get_config


def test_agent_disabled_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    cfg = get_config()
    assert cfg["agent_enabled"] is False


def test_agent_enabled_with_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    cfg = get_config()
    assert cfg["agent_enabled"] is True


def test_goal_validation_defaults_present(monkeypatch):
    monkeypatch.delenv("GOALS_MIN_CHARS", raising=False)
    monkeypatch.delenv("GOALS_MAX_CHARS", raising=False)
    monkeypatch.delenv("GOALS_MAX_LINES", raising=False)
    monkeypatch.delenv("GOALS_BLOCK_URLS", raising=False)
    monkeypatch.delenv("GOALS_BLOCK_EMAILS", raising=False)
    monkeypatch.delenv("GOALS_BLOCK_PHONES", raising=False)
    monkeypatch.delenv("GOALS_BLOCK_MARKDOWN", raising=False)
    monkeypatch.delenv("GOALS_BLOCK_GUARANTEES", raising=False)
    cfg = get_config()
    assert cfg["goals_min_chars"] == 20
    assert cfg["goals_max_chars"] == 400
    assert cfg["goals_max_lines"] == 5
    assert cfg["goals_block_urls"] is True
    assert cfg["goals_block_emails"] is True
    assert cfg["goals_block_phones"] is True
    assert cfg["goals_block_markdown"] is True
    assert cfg["goals_block_guarantees"] is True


def test_goal_validation_env_overrides(monkeypatch):
    monkeypatch.setenv("GOALS_MIN_CHARS", "30")
    monkeypatch.setenv("GOALS_MAX_CHARS", "500")
    monkeypatch.setenv("GOALS_MAX_LINES", "7")
    monkeypatch.setenv("GOALS_BLOCK_URLS", "false")
    monkeypatch.setenv("GOALS_BLOCK_EMAILS", "0")
    monkeypatch.setenv("GOALS_BLOCK_PHONES", "no")
    monkeypatch.setenv("GOALS_BLOCK_MARKDOWN", "off")
    monkeypatch.setenv("GOALS_BLOCK_GUARANTEES", "false")
    cfg = get_config()
    assert cfg["goals_min_chars"] == 30
    assert cfg["goals_max_chars"] == 500
    assert cfg["goals_max_lines"] == 7
    assert cfg["goals_block_urls"] is False
    assert cfg["goals_block_emails"] is False
    assert cfg["goals_block_phones"] is False
    assert cfg["goals_block_markdown"] is False
    assert cfg["goals_block_guarantees"] is False
