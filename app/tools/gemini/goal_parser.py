from app.tools.interfaces import Constraints
from app.tools.gemini.client import GeminiClient


class GeminiGoalParser:
    def __init__(self, client: GeminiClient):
        self.client = client

    def parse(self, text: str, user: dict) -> Constraints:
        data = self.client.parse_constraints(text, user)
        return Constraints(
            min_emergency_fund_months=int(data.get("min_emergency_fund_months", 3)),
            focus_debt_reduction=bool(data.get("focus_debt_reduction", False)),
            risk_tolerance=str(
                data.get("risk_tolerance", user.get("risk_tolerance", "medium"))
            ),
            priority_order=list(data.get("priority_order", [])),
            time_horizon_months=int(data.get("time_horizon_months", 12)),
            must_avoid=list(data.get("must_avoid", [])),
            conflicts=list(data.get("conflicts", [])),
        )
