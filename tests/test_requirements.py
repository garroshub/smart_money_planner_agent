from pathlib import Path


def test_requirements_exists():
    assert (Path(__file__).resolve().parents[1] / "requirements.txt").is_file()
