from app.tools.interfaces import Constraints


class RuleGoalParser:
    def parse(self, text: str, user: dict) -> Constraints:
        t = (text or "").lower()
        focus_debt = any(k in t for k in ["debt", "loan", "mortgage", "credit card"])
        risk = user.get("risk_tolerance", "medium")
        if any(k in t for k in ["low volatility", "conservative", "low risk"]):
            risk = "low"
        if any(k in t for k in ["high return", "aggressive", "high risk"]):
            risk = "high"

        return Constraints(
            min_emergency_fund_months=3,
            focus_debt_reduction=focus_debt,
            risk_tolerance=risk,
            priority_order=["emergency_fund", "debt", "invest"],
            time_horizon_months=12,
            must_avoid=[],
            conflicts=[],
        )
