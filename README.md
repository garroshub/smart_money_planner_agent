# Smart Money Planner

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Demo-GitHub%20Pages-blue)](https://garroshub.github.io/smart_money_planner/)
[![GitHub Repo stars](https://img.shields.io/github/stars/garroshub/smart_money_planner?style=social)](https://github.com/garroshub/smart_money_planner)

Enterprise-grade financial planning demo for multi-account analysis and strategy generation.

## Business Scenario

Financial teams and advisors often need to assess clients across multiple account types (cash, debt, investments) and produce consistent plans. Manual workflows make it difficult to build a clear, unified client profile when data is spread across many accounts.

This project addresses that gap by producing a structured planning workflow with auditable calculations, strategy comparison, and executive-style recommendations.

## Core Value

- Unified client snapshot across account categories
- Deterministic planning engine for reproducible outputs
- Side-by-side strategy comparison with assumptions and risk notes
- Executive-ready output: KPIs, charts, recommendation, narrative

## Modes

- `rules`: deterministic parsing and deterministic planning
- `agent`: Gemini-powered intent parsing and report generation, with deterministic planning logic

## Demo and Local Run

### GitHub Pages (static)

Rules mode runs in-browser. Agent mode uses curated presets.

```bash
python -m http.server --directory docs 8000
```

Open: `http://localhost:8000`

### Streamlit (local)

```bash
python -m pip install -r requirements.txt
python -m streamlit run app/streamlit_app.py
```

Use `.env` to configure Gemini:

```bash
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
GEMINI_MODEL=gemini-3-flash-preview
```

## Quality

```bash
python -m pytest -q
```

## License

MIT License.
