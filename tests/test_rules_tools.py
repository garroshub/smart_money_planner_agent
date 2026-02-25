from app.tools.rules.goal_parser import RuleGoalParser
from app.tools.rules.explainer import RulePlanExplainer
from app.tools.interfaces import Plan, PlanAction, Constraints


def test_rule_goal_parser_keywords():
    parser = RuleGoalParser()
    user = {"risk_tolerance": "medium"}
    c = parser.parse("Pay down debt and keep low volatility", user)
    assert c.focus_debt_reduction is True
    assert c.risk_tolerance == "low"


def test_rule_explainer():
    explainer = RulePlanExplainer()
    plans = [Plan(name="Test", score=80, actions=[PlanAction("Invest", 100, True)])]
    constraints = Constraints(3, False, "medium")
    md = explainer.explain(plans, {"id": "u_001"}, constraints)
    assert "Plan 1" in md
