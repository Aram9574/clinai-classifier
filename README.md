---
title: ClinAI Classifier - EU AI Act for Healthcare
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: true
license: mit
---

# ClinAI Classifier

**An EU AI Act compliance classifier built for healthcare AI, by a clinician.**

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B.svg)](https://streamlit.io/)
[![Claude API](https://img.shields.io/badge/Claude-sonnet--4--5-8A2BE2.svg)](https://www.anthropic.com/)
[![HF Spaces](https://img.shields.io/badge/Hugging%20Face-Spaces-FFD21E.svg)](https://huggingface.co/spaces)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## Why this exists — a clinician's note

Every week I meet hospital teams, startup founders, and clinicians building AI tools that will eventually sit between a patient and a decision. Most of them have never read [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj). They do not know whether their sepsis predictor is a high-risk AI system under Annex III, whether their patient-facing chatbot needs an Article 50 transparency notice, or whether their eligibility-scoring tool crosses the prohibition line of Article 5. That is not a failure of will — it is a failure of accessible tooling. The regulation is 144 articles long and was written for lawyers, not for the people who actually build and deploy these systems in clinical environments.

ClinAI Classifier is my attempt to close that gap. It is a two-stage pipeline that takes a plain-language description of a healthcare AI system and returns a structured EU AI Act risk classification, the legal basis for it, a practical compliance checklist, and physician-oriented notes about clinical workflow implications. It is not legal advice and it does not replace a Notified Body, but it gives clinical and technical teams a fast, defensible starting point for their compliance conversations — and it does so with the clinical context that generic legal tools miss.

---

## Try it

**Live demo:** https://huggingface.co/spaces/aram1585/clinai-classifier

The app has two modes, switchable from the sidebar:

| Mode | What it does | API key required |
|------|--------------|------------------|
| **Demo** (default) | Click any of 6 curated example AI systems and see its full classification (risk level, legal basis, compliance checklist, PDF report) — all pre-computed against Claude + the rules engine. | No |
| **Classify my own system** | Paste an Anthropic API key and classify any AI system you describe. The key is used for a single outbound call to Claude and is never logged, stored, or retained on the server. | Yes (your own) |

This design keeps the tool free to explore for every visitor without exposing a shared API budget.

---

## How it works

ClinAI Classifier uses a **two-stage classification pipeline**:

1. **Claude classification agent** — `claude-sonnet-4-5` is prompted with a regulatory-expert system prompt and the system description. It returns a structured JSON classification with risk level, Annex III categories, Article 5 flags, legal basis, confidence score, and clinical notes.
2. **Static rules engine** — a keyword-based validator loaded from curated regulatory JSON files. It cross-checks the agent's output against deterministic rules for prohibited practices (with a medical-purpose carveout for Article 5(1)(f)) and high-risk healthcare patterns.

The pipeline enforces a strict **never-downgrade invariant**: the rules engine may only escalate a classification (e.g. `LIMITED_RISK` to `HIGH_RISK`, or `HIGH_RISK` to `PROHIBITED`). It never lowers the risk level the agent assigned. This keeps the classifier conservative by design.

See [`docs/METHODOLOGY.md`](./docs/METHODOLOGY.md) for the full pipeline description.

---

## Example classifications

| System | Risk level | Legal basis |
|---|---|---|
| ICU 30-day readmission predictor used at discharge | `HIGH_RISK` + SaMD | Article 6, Annex III point 5; MDR cross-reference |
| NLP summariser of de-identified clinical notes for research | `LIMITED_RISK` | Article 50 transparency |
| Public-authority social score for healthcare benefit eligibility | `PROHIBITED` | Article 5(1)(c) |
| Consumer wearable dashboard showing step count and sleep trends | `MINIMAL_RISK` | Article 95 voluntary code of conduct |
| Oncology treatment recommendation system used by oncologists | `HIGH_RISK` + SaMD | Article 6, Annex III point 5; MDR/IVDR |

Full worked examples with compliance requirements and physician notes are in [`docs/EXAMPLES.md`](./docs/EXAMPLES.md).

---

## Tech stack

- **Python 3.11**
- **Streamlit 1.32.0** — UI layer (`app/`)
- **FastAPI** — classification API backend (`backend/`)
- **Anthropic SDK** — `claude-sonnet-4-5` for the classification agent
- **WeasyPrint** — PDF report generation
- **pytest** — unit and integration tests

---

## Installation & local run

```bash
# 1. Clone
git clone https://github.com/aramzakzuk/clinai-classifier.git
cd clinai-classifier

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# then edit .env and add your ANTHROPIC_API_KEY
```

Run the backend and the UI in two terminals:

```bash
# Terminal 1 — FastAPI backend
python -m backend.main
```

```bash
# Terminal 2 — Streamlit UI
streamlit run app/main.py
```

The backend listens on `http://localhost:8000` and the Streamlit UI on `http://localhost:8501`.

---

## Project structure

```text
EU AI ACT Classifier/
├── app/                          # Streamlit UI
│   ├── main.py
│   ├── components/
│   ├── pages/
│   └── utils/
├── backend/                      # FastAPI classification service
│   ├── main.py
│   ├── data/                     # Curated EU AI Act regulatory JSON
│   │   ├── eu_ai_act_article_5.json
│   │   ├── eu_ai_act_annex_iii.json
│   │   └── compliance_checklists.json
│   ├── models/                   # Pydantic request/response schemas
│   ├── routers/                  # FastAPI endpoints (classify, report, health)
│   ├── services/                 # Classification agent, rules engine, PDF generator
│   └── tests/                    # pytest suite
├── docs/
│   ├── METHODOLOGY.md
│   ├── LIMITATIONS.md
│   └── EXAMPLES.md
├── templates/                    # Jinja2 templates for PDF report
├── requirements.txt
├── REGULATORY_REFERENCE.md
└── README.md
```

---

## Testing

```bash
pytest backend/tests/
```

The test suite covers the rules engine (escalation logic, medical carveout, never-downgrade invariant), the classification endpoint, and the PDF generator.

---

## Regulatory basis

All classifications are grounded in the published text of [Regulation (EU) 2024/1689 — the EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj). A quick-reference mapping of the articles most relevant to healthcare AI is maintained in [`REGULATORY_REFERENCE.md`](./REGULATORY_REFERENCE.md).

---

## Limitations

ClinAI Classifier is a **decision-support tool, not legal advice**. It does not constitute a formal conformity assessment and it does not replace consultation with a qualified regulatory or legal professional, nor with a Notified Body. Large language model outputs can be inconsistent, and the classification is only as good as the system description provided. The classifier does not cover General Purpose AI (GPAI) obligations under Article 51+, and it does not evaluate MDR/IVDR conformity in depth. All outputs require human review by qualified regulatory and legal experts before any compliance action.

See [`docs/LIMITATIONS.md`](./docs/LIMITATIONS.md) for the full statement.

---

## Author

**Aram Zakzuk, MD** — Clinical AI Specialist | Health Informatics | HealthTech Consultant

CDSS · SaMD · EU AI Act · MDR

- LinkedIn: [linkedin.com/in/aramzakzuk](https://linkedin.com/in/aramzakzuk)
- Web: [alejandrozakzuk.com](https://alejandrozakzuk.com)

---

## Contributing

Contributions from the HealthTech community are welcome — especially from clinicians, regulatory professionals, and engineers working on Software as a Medical Device. Please open an issue to discuss significant changes before submitting a pull request. Bug reports, additional test cases drawn from real-world deployments, and refinements to the regulatory data files are particularly valued.

---

## License

MIT — see [`LICENSE`](./LICENSE).
