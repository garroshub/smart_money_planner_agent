# GitHub Pages Demo

This folder hosts the static demo for GitHub Pages.

## What Works Here
- **Rules mode** runs fully in the browser (no backend).
- **Agent mode** shows curated preset outputs (no API keys).

## Local Preview
Serve the `docs/` folder with any static server:

```bash
python -m http.server --directory docs 8000
```

Open: http://localhost:8000

## Data Sources
- Mock data: `docs/data/mock/*.json`
- Preset outputs: `docs/data/presets/preset_outputs.json`

## Notes
- GitHub Pages is static-only.
- For live Agent calls, use the local Streamlit app instead.
