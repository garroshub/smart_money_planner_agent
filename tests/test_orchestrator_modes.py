import pytest
from app.agent.orchestrator import OrchestratorAgent


def test_orchestrator_rules_mode():
    agent = OrchestratorAgent(config={"agent_enabled": False})
    user = {
        "id": "u_001",
        "income_monthly": 1000,
        "expenses_monthly": 750,
        "risk_tolerance": "high",
    }
    accounts = {"cash": 200}
    goals = "Pay down debt and build emergency fund."

    result = agent.run("rules", user, accounts, goals)
    assert result.constraints
    assert result.plans
    assert result.markdown


def test_orchestrator_agent_requires_key():
    agent = OrchestratorAgent(config={"agent_enabled": False})
    user = {
        "id": "u_001",
        "income_monthly": 1000,
        "expenses_monthly": 750,
        "risk_tolerance": "high",
    }
    accounts = {"cash": 200}
    goals = "Pay down debt and build emergency fund."

    with pytest.raises(RuntimeError):
        agent.run("agent", user, accounts, goals)
