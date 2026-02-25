from app.tools.common.plan_generator import generate_plans
from app.tools.common.scorer import score_plans
from app.tools.common.guardrail import apply_guardrails
from app.tools.interfaces import DemoResult
from app.agent.factory import build_tools
from app.config import get_config


class OrchestratorAgent:
    def __init__(self, config: dict | None = None):
        self.config = config or get_config()

    def run(self, mode: str, user: dict, accounts: dict, goals_text: str) -> DemoResult:
        parser, explainer = build_tools(mode, self.config)
        user_with_mode = {**user, "mode": mode}
        constraints = parser.parse(goals_text, user_with_mode)
        plans = generate_plans(user, accounts, constraints)
        scored = score_plans(plans, constraints)
        guarded = apply_guardrails(scored, user, accounts, constraints)
        markdown = explainer.explain(
            guarded, {**user_with_mode, "goals_text": goals_text}, constraints
        )
        return DemoResult(
            constraints=constraints,
            plans=guarded,
            markdown=markdown,
            meta={"mode": mode},
        )
