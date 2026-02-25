from app.tools.interfaces import Constraints, PlanAction, Plan, DemoResult


def test_interfaces_construct():
    constraints = Constraints(
        min_emergency_fund_months=3, focus_debt_reduction=True, risk_tolerance="low"
    )
    action = PlanAction(type="Invest", amount=100, requires_human_approval=True)
    plan = Plan(name="Test", score=50, actions=[action])
    result = DemoResult(
        constraints=constraints, plans=[plan], markdown="# Demo", meta={}
    )
    assert result.constraints.risk_tolerance == "low"


def test_constraints_extended_fields():
    constraints = Constraints(
        min_emergency_fund_months=3,
        focus_debt_reduction=True,
        risk_tolerance="low",
        priority_order=["emergency_fund", "debt", "invest"],
        time_horizon_months=12,
        must_avoid=["new_debt"],
        conflicts=[],
    )
    assert constraints.priority_order[0] == "emergency_fund"
