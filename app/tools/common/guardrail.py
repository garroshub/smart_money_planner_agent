from app.tools.interfaces import Constraints, Plan, PlanAction


def apply_guardrails(
    plans: list[Plan], user: dict, accounts: dict, constraints: Constraints
):
    disposable = max(0, user["income_monthly"] - user["expenses_monthly"])
    emergency_target = user["expenses_monthly"] * constraints.min_emergency_fund_months
    emergency_gap = max(0, emergency_target - accounts.get("cash", 0))

    guarded = []
    for plan in plans:
        total = sum(action.amount for action in plan.actions)
        scale = (disposable / total) if total > disposable and total > 0 else 1

        actions = [
            PlanAction(a.type, int(round(a.amount * scale)), a.requires_human_approval)
            for a in plan.actions
        ]

        if emergency_gap > 0 and not any(a.type == "Emergency fund" for a in actions):
            actions.insert(
                0, PlanAction("Emergency fund", min(emergency_gap, disposable), False)
            )

        guarded.append(Plan(name=plan.name, score=plan.score, actions=actions))
    return guarded
