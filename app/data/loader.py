import json
from pathlib import Path

BASE = Path(__file__).resolve().parent / "mock"


def _load(name: str):
    path = BASE / name
    return json.loads(path.read_text(encoding="utf-8"))


def load_users():
    return _load("users.json")


def load_accounts():
    return _load("accounts.json")


def load_goals():
    return _load("goals.json")
