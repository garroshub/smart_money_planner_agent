from app.tools.interfaces import Constraints, Plan


def score_plans(plans: list[Plan], constraints: Constraints):
    scored = []
    for plan in plans:
        score = 60
        debt = next((a for a in plan.actions if a.type == "Debt payment"), None)
        invest = next((a for a in plan.actions if a.type == "Invest"), None)

        if (
            constraints.focus_debt_reduction
            and debt
            and (not invest or debt.amount > invest.amount)
        ):
            score += 15
        if constraints.risk_tolerance == "low" and invest and invest.amount > 0:
            score -= 5
        if constraints.risk_tolerance == "high" and invest and invest.amount > 0:
            score += 5

        scored.append(Plan(name=plan.name, score=score, actions=plan.actions))
    return scored
