import json
from pathlib import Path


def test_mock_files_exist():
    base_dir = Path(__file__).resolve().parents[1]
    mock_dir = base_dir / "app" / "data" / "mock"

    assert (mock_dir / "README.md").is_file()
    assert (mock_dir / "users.json").is_file()
    assert (mock_dir / "accounts.json").is_file()
    assert (mock_dir / "goals.json").is_file()


def test_users_schema():
    base_dir = Path(__file__).resolve().parents[1]
    users_path = base_dir / "app" / "data" / "mock" / "users.json"

    users = json.loads(users_path.read_text(encoding="utf-8"))

    assert isinstance(users, list)
    assert 6 <= len(users) <= 10

    required_keys = {
        "id",
        "age",
        "risk_tolerance",
        "income_monthly",
        "expenses_monthly",
        "dependents",
        "region",
    }

    ids = set()

    for user in users:
        assert isinstance(user, dict)
        assert required_keys.issubset(user.keys())

        assert isinstance(user["id"], str) and user["id"].strip()
        assert user["id"] not in ids
        ids.add(user["id"])

        assert isinstance(user["age"], int)
        assert 18 <= user["age"] <= 100

        assert isinstance(user["risk_tolerance"], str)
        assert user["risk_tolerance"] in {"low", "medium", "high"}

        assert isinstance(user["income_monthly"], (int, float))
        assert 0 <= user["income_monthly"] <= 50000

        assert isinstance(user["expenses_monthly"], (int, float))
        assert 0 <= user["expenses_monthly"] <= 50000

        assert isinstance(user["dependents"], int)
        assert 0 <= user["dependents"] <= 10

        assert isinstance(user["region"], str)
        assert user["region"] in {
            "central",
            "midwest",
            "northeast",
            "northwest",
            "southeast",
            "southwest",
            "west",
        }


def test_accounts_schema_and_linkage():
    base_dir = Path(__file__).resolve().parents[1]
    users_path = base_dir / "app" / "data" / "mock" / "users.json"
    accounts_path = base_dir / "app" / "data" / "mock" / "accounts.json"

    users = json.loads(users_path.read_text(encoding="utf-8"))
    accounts = json.loads(accounts_path.read_text(encoding="utf-8"))

    user_ids = {user["id"] for user in users}
    account_user_ids = {account.get("user_id") for account in accounts}

    assert isinstance(accounts, list)
    assert accounts

    assert user_ids.issubset(account_user_ids)

    has_debt_free_account = False

    for account in accounts:
        assert isinstance(account, dict)
        assert "user_id" in account
        assert "cash" in account
        assert "debts" in account
        assert "investments" in account

        assert account["user_id"] in user_ids
        assert isinstance(account["cash"], (int, float))
        assert account["cash"] >= 0

        assert isinstance(account["debts"], list)
        if not account["debts"]:
            has_debt_free_account = True
        for debt in account["debts"]:
            assert isinstance(debt, dict)
            assert "type" in debt
            assert "balance" in debt
            assert "apr" in debt
            assert "min_payment" in debt
            assert isinstance(debt["type"], str) and debt["type"].strip()
            assert isinstance(debt["balance"], (int, float))
            assert debt["balance"] >= 0
            assert isinstance(debt["apr"], (int, float))
            assert 0 <= debt["apr"] <= 1
            assert isinstance(debt["min_payment"], (int, float))
            assert debt["min_payment"] >= 0
            if debt["balance"] == 0:
                assert debt["min_payment"] == 0
                assert debt["apr"] == 0
            else:
                assert debt["min_payment"] <= debt["balance"]

        assert isinstance(account["investments"], list)
        for investment in account["investments"]:
            assert isinstance(investment, dict)
            assert "type" in investment
            assert "balance" in investment
            assert isinstance(investment["type"], str) and investment["type"].strip()
            assert isinstance(investment["balance"], (int, float))
            assert investment["balance"] >= 0

    assert has_debt_free_account


def test_goals_schema_and_linkage():
    base_dir = Path(__file__).resolve().parents[1]
    users_path = base_dir / "app" / "data" / "mock" / "users.json"
    goals_path = base_dir / "app" / "data" / "mock" / "goals.json"

    users = json.loads(users_path.read_text(encoding="utf-8"))
    goals = json.loads(goals_path.read_text(encoding="utf-8"))

    user_ids = {user["id"] for user in users}
    goal_user_ids = {goal.get("user_id") for goal in goals}

    assert isinstance(goals, list)
    assert len(goals) >= len(users)

    assert user_ids.issubset(goal_user_ids)

    for goal in goals:
        assert isinstance(goal, dict)
        assert "user_id" in goal
        assert "goals_text" in goal
        assert goal["user_id"] in user_ids
        assert isinstance(goal["goals_text"], str)
        assert goal["goals_text"].strip()
        assert goal["goals_text"].isascii()


def test_edge_cases_present():
    base_dir = Path(__file__).resolve().parents[1]
    goals_path = base_dir / "app" / "data" / "mock" / "goals.json"

    goals = json.loads(goals_path.read_text(encoding="utf-8"))
    text = " ".join(goal["goals_text"].lower() for goal in goals)

    assert "debt" in text
    assert "emergency fund" in text
    assert "low volatility" in text
