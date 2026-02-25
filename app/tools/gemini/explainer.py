from app.tools.gemini.client import GeminiClient
from app.tools.interfaces import Plan, Constraints


class GeminiPlanExplainer:
    def __init__(self, client: GeminiClient):
        self.client = client

    def explain(self, plans: list[Plan], user: dict, constraints: Constraints) -> str:
        report_input = {
            "user": user,
            "constraints": constraints.__dict__,
            "plans": [
                {
                    "name": plan.name,
                    "score": plan.score,
                    "actions": [a.__dict__ for a in plan.actions],
                }
                for plan in plans
            ],
        }
        return self.client.explain_report(report_input)
