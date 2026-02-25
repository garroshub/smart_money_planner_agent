from app.tools.interfaces import Plan, PlanAction, Constraints


def generate_plans(user: dict, accounts: dict, constraints: Constraints):
    disposable = max(0, user["income_monthly"] - user["expenses_monthly"])
    base_cash = accounts.get("cash", 0)
    emergency_target = user["expenses_monthly"] * constraints.min_emergency_fund_months
    emergency_gap = max(0, emergency_target - base_cash)

    def plan(name: str, actions):
        return Plan(name=name, score=0, actions=[a for a in actions if a.amount > 0])

    debt_amount = int(disposable * 0.5)
    invest_amount = int(disposable * 0.3)
    cash_amount = int(disposable * 0.2)

    return [
        plan(
            "Debt focus",
            [
                PlanAction("Emergency fund", min(emergency_gap, cash_amount)),
                PlanAction("Debt payment", debt_amount, True),
                PlanAction("Invest", invest_amount, True),
            ],
        ),
        plan(
            "Balanced",
            [
                PlanAction("Emergency fund", min(emergency_gap, int(disposable * 0.3))),
                PlanAction("Debt payment", int(disposable * 0.35), True),
                PlanAction("Invest", int(disposable * 0.35), True),
            ],
        ),
        plan(
            "Growth focus",
            [
                PlanAction(
                    "Emergency fund", min(emergency_gap, int(disposable * 0.15))
                ),
                PlanAction("Invest", int(disposable * 0.6), True),
                PlanAction("Debt payment", int(disposable * 0.25), True),
            ],
        ),
    ]
