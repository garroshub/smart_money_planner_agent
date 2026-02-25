from app.tools.common.plan_generator import generate_plans
from app.tools.common.scorer import score_plans
from app.tools.common.guardrail import apply_guardrails
from app.tools.interfaces import Constraints


def test_common_pipeline():
    user = {"income_monthly": 3000, "expenses_monthly": 2000}
    accounts = {"cash": 500}
    constraints = Constraints(
        min_emergency_fund_months=3, focus_debt_reduction=True, risk_tolerance="medium"
    )

    plans = generate_plans(user, accounts, constraints)
    scored = score_plans(plans, constraints)
    guarded = apply_guardrails(scored, user, accounts, constraints)

    assert guarded
    assert all(plan.actions for plan in guarded)
