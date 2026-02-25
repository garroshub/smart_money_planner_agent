from app.config import get_config
from app.tools.rules.goal_parser import RuleGoalParser
from app.tools.rules.explainer import RulePlanExplainer
from app.tools.gemini.client import GeminiClient
from app.tools.gemini.goal_parser import GeminiGoalParser
from app.tools.gemini.explainer import GeminiPlanExplainer


def build_tools(mode: str, config: dict | None = None):
    cfg = config or get_config()
    if mode == "rules":
        return RuleGoalParser(), RulePlanExplainer()
    if mode == "agent":
        if not cfg.get("agent_enabled"):
            raise RuntimeError("Agent mode requires GEMINI_API_KEY.")
        client = GeminiClient(
            api_key=cfg.get("gemini_api_key", ""),
            model=cfg.get("gemini_model", "gemini-3-flash-preview"),
            timeout_seconds=cfg.get("llm_timeout_seconds", 20),
            temperature=cfg.get("llm_temperature", 0.2),
        )
        return GeminiGoalParser(client), GeminiPlanExplainer(client)
    raise ValueError(f"Unsupported mode: {mode}")
