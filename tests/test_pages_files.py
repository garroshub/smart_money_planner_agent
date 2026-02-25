from pathlib import Path


def test_pages_files_exist():
    base = Path(__file__).resolve().parents[1]
    expected = [
        base / "docs" / ".nojekyll",
        base / "docs" / "index.html",
        base / "docs" / "assets" / "app.js",
        base / "docs" / "assets" / "styles.css",
    ]

    missing = [str(path) for path in expected if not path.exists()]

    assert not missing, f"Missing required files: {', '.join(missing)}"
