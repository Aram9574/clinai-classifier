# Agent Instructions

## Package Manager
Use **pip** with `requirements.txt` (Python 3.11). No lock file — pin new deps with `>=` at minimum.

## Commit Attribution
AI commits MUST include:
```
Co-Authored-By: (the agent model's name and attribution byline)
```

## File-Scoped Commands
| Task | Command |
|------|---------|
| Run single test file | `python -m pytest backend/tests/test_rules_engine.py -v` |
| Run one test | `python -m pytest backend/tests/test_classify.py::test_cdss_classified_as_high_risk` |
| Full suite | `python -m pytest backend/tests/` |
| Start backend | `python -m backend.main` |
| Start Streamlit | `streamlit run app/main.py` |

## Key Conventions
- **Never downgrade a risk classification** — `rules_engine.py` escalates only; if in doubt, go higher.
- **All regulatory text lives in `backend/data/*.json`** — never hardcode article text in Python.
- **Pydantic everywhere** — no raw dicts in API responses. Models in `backend/models/`.
- **Stub the Claude agent in tests** — patch `backend.routers.classify._get_agent`; never hit the real API in CI.
- **SaMD flag is mandatory** for anything that could qualify as a medical device under MDR/IVDR.
- **PDF template at `templates/audit_report.html`** uses Jinja2 + WeasyPrint; needs Pango/Cairo system libs.

## Architecture
- `backend/services/classification_agent.py` — Claude wrapper (structured JSON out)
- `backend/services/rules_engine.py` — static validator that escalates
- `backend/routers/` — FastAPI endpoints (`/classify`, `/report`, `/health`, `/examples`)
- `app/main.py` — Streamlit entry; launches FastAPI as subprocess on :8000
- HF Spaces deploy: see `docs/DEPLOYMENT.md`

## Coding Standards
- Type hints on every function; docstrings with Args/Returns on public ones
- Functions ≤ 50 lines
- `logging`, never `print()`
- No emojis in code (UI or otherwise) except the HF frontmatter `🏥`
