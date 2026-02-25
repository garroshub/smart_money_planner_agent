import json
from pathlib import Path


def test_pages_mock_data_loads():
    base = Path(__file__).resolve().parents[1] / "docs" / "data" / "mock"
    for name in ["users.json", "accounts.json", "goals.json"]:
        path = base / name
        assert path.is_file()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
