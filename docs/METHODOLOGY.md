# Classification Methodology

This document describes how ClinAI Classifier assigns an EU AI Act risk level to a described healthcare AI system, and the design decisions that keep the classifier conservative and auditable.

---

## Two-stage pipeline

ClinAI Classifier uses a **two-stage pipeline** rather than a single LLM call. The stages are deliberately separated so that the deterministic stage can correct the probabilistic one.

### Stage 1 — Claude classification agent

The first stage is an LLM call to [Anthropic's Claude](https://www.anthropic.com/) using the `claude-sonnet-4-5` model. The agent receives:

- A **regulatory-expert system prompt** instructing it to act as an EU AI Act expert with clinical knowledge, to cite articles and annex points, to be conservative when in doubt, and to distinguish clinical decision support from clinical decision replacement.
- A **structured user prompt** built from the `ClassificationRequest` (system name, description, intended purpose, data inputs, outputs, deployment context, clinical-decision impact flag).
- A **strict output schema** — the model is instructed to return a single JSON object with fields for `risk_level`, `annex_iii_categories`, `article_5_flags`, `legal_basis`, `confidence_score`, `clinical_notes`, `samd_flag`, `requires_conformity_assessment`, and `requires_notified_body`.

The agent populates everything except `compliance_requirements`, which is intentionally left empty for the rules engine to fill from a curated static checklist. This separation prevents the model from hallucinating compliance items.

### Stage 2 — Static rules engine validator

The second stage is the `RulesEngine` in `backend/services/rules_engine.py`. It loads three curated JSON files:

- `eu_ai_act_article_5.json` — the eight prohibited practices with keyword triggers and healthcare carveouts.
- `eu_ai_act_annex_iii.json` — high-risk categories and healthcare-relevant keyword lists.
- `compliance_checklists.json` — the compliance items mapped to each risk level, with article citations, priorities, and deadlines.

The rules engine runs **keyword-based detection** on the original free-text description and intended purpose, then cross-checks the agent's output against its own findings.

---

## The "never downgrade" invariant

The rules engine's core design rule is simple: **it may escalate risk level but never lower it.**

Risk levels are ordered:

```text
MINIMAL_RISK (0) < LIMITED_RISK (1) < HIGH_RISK (2) < PROHIBITED (3)
```

The `_escalate_to` method only raises the risk level when the target is strictly higher than the agent's assigned level. This means:

- If the agent says `LIMITED_RISK` but the rules engine finds high-risk keywords (e.g. "diagnosis", "CDSS", "sepsis prediction"), the result is escalated to `HIGH_RISK`.
- If the agent says `HIGH_RISK` but Article 5 keywords are triggered without a medical carveout, the result is escalated to `PROHIBITED`.
- If the agent says `HIGH_RISK` and the rules engine finds no high-risk keywords, the result remains `HIGH_RISK` — the engine never downgrades based on its own absence of findings.

This keeps the classifier conservative by construction. A false positive (flagging something as higher-risk than it truly is) triggers human review; a false negative (silently downgrading a high-risk system) would let an unsafe system slip through without review. The asymmetric cost justifies the asymmetric rule.

---

## How Article 5 detection works

Article 5 detection runs a keyword match from `eu_ai_act_article_5.json` against the combined description and intended purpose. Example trigger keywords include "social scoring", "predictive policing", "emotion recognition workplace", "facial recognition scraping", and "biometric categorisation".

A match triggers escalation to `PROHIBITED` **unless** a medical carveout is detected. The carveout reflects Article 5(1)(f), which explicitly exempts emotion-recognition systems placed on the market for medical or safety reasons. The `_has_medical_carveout` method checks the text for markers such as `pain assessment`, `delirium`, `ICU monitoring`, `clinical`, `diagnosis`, `diagnostic`, `medical device`, `SaMD`, and `patient safety`.

When the carveout applies, the system is not prohibited — but it will typically still qualify as high-risk SaMD under MDR/IVDR and Article 6, so the pipeline falls through to the high-risk keyword check.

---

## How the SaMD flag is set

The `samd_flag` is set to `True` by the rules engine when high-risk keywords are found **and** one of the SaMD-specific triggers appears: `medical device`, `samd`, `diagnosis`, `diagnostic`, `treatment recommendation`, `mdr`, or `ivdr`. Setting the flag also sets `requires_conformity_assessment` and `requires_notified_body` to `True`, reflecting the typical obligations for Software as a Medical Device under combined MDR/IVDR and AI Act conformity assessment.

The agent itself is also instructed to set `samd_flag` in Stage 1, so the two stages reinforce each other. Because the rules engine only turns the flag on and never off, a Stage 1 flag on an unambiguous SaMD case will not be cleared by Stage 2.

---

## How confidence scoring is interpreted

The `confidence_score` is a float between 0 and 1 returned by the Claude agent in Stage 1. It reflects the model's self-assessed confidence given the description provided, not a calibrated probability. It is displayed to the user as a transparency signal — a low confidence score is a prompt to enrich the system description and re-run the classification, or to escalate to manual expert review. It is not used by the rules engine to change classification.

---

## Why `claude-sonnet-4-5`

`claude-sonnet-4-5` is used in Stage 1 because it offers the strongest combination of three properties for this task:

- **Instruction-following at length** — the system prompt is detailed and requires strict JSON-only output. Sonnet-4-5 reliably returns well-formed JSON without markdown fences or prose leakage, which keeps the parser simple.
- **Regulatory and clinical reasoning** — the task requires simultaneous handling of legal text (articles, annexes, carveouts) and clinical context (SaMD, CDSS, triage, workflow). Sonnet-4-5 handles this multi-domain reasoning more consistently than smaller models in our testing.
- **Latency and cost** — Sonnet-class models keep end-to-end classification under 10 seconds at a cost compatible with open-source deployment on Hugging Face Spaces, where Opus-class pricing would be prohibitive.

The model identifier is centralised in `backend/services/classification_agent.py` as `MODEL_NAME` so it can be updated in one place.
