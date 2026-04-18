# Limitations

ClinAI Classifier is an open-source decision-support tool. It is not a regulator, not a Notified Body, and not a legal service. The limitations below are written plainly because compliance work is too consequential for hedged language.

---

## Not legal advice, not a conformity assessment

Nothing produced by this tool constitutes legal advice, regulatory approval, or a formal conformity assessment under [Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj), [MDR (EU) 2017/745](https://eur-lex.europa.eu/eli/reg/2017/745/oj), or [IVDR (EU) 2017/746](https://eur-lex.europa.eu/eli/reg/2017/746/oj). The classification, legal references, and compliance checklist are informational artefacts intended to support — not replace — engagement with qualified regulatory counsel, a certified quality management system, and a Notified Body where required.

---

## LLM outputs can be inconsistent

Stage 1 of the pipeline is a call to a large language model. Even with a strict system prompt, structured output schema, and a deterministic validator layered on top, LLMs can produce different answers to the same prompt across runs, and can mis-cite articles or miss subtle legal nuance. The rules engine partially mitigates this for prohibition and high-risk escalation, but it does not and cannot correct every kind of LLM error. Treat any single classification as a starting hypothesis, not a final answer.

---

## Only as good as the description provided

The classifier reads the description, intended purpose, data inputs, outputs, and deployment context supplied by the user. It cannot inspect source code, read training-data documentation, review a clinical validation study, or observe the system in production. A thin or misleading description will produce a thin or misleading classification. Systems with complex multi-purpose architectures — for example a platform with both patient-facing and clinician-facing modules — are particularly vulnerable to under-classification if described in aggregate.

---

## Does not cover General Purpose AI (GPAI)

The classifier does not evaluate General Purpose AI obligations under **Article 51 and following** of the AI Act. Providers of GPAI models have distinct obligations — technical documentation, information to downstream providers, copyright compliance, and for GPAI models with systemic risk, additional obligations around model evaluation and serious incident reporting. If you are building or fine-tuning a GPAI model, this tool will not surface those requirements.

---

## Does not evaluate MDR / IVDR depth

When the classifier sets the `samd_flag` and recommends Notified Body involvement, it is signalling the **need** for MDR/IVDR conformity assessment — it is not performing one. It does not evaluate your device's MDR risk class, clinical evaluation, technical documentation, or ISO 13485 QMS readiness. A positive SaMD signal is an instruction to engage your Notified Body and quality team, not a substitute for them.

---

## Requires human review by qualified experts

Every output from ClinAI Classifier requires review by:

- A regulatory affairs professional familiar with the AI Act and, where applicable, MDR/IVDR.
- Legal counsel experienced with EU technology and healthcare regulation.
- Clinical leadership responsible for the deployment context.
- Your organisation's data protection officer for GDPR implications.

The compliance checklist attached to each classification is a **starting list**, not an exhaustive regulatory dossier. The deadlines cited reflect the regulation's published timelines as of writing and should be confirmed against the current text of the published act and any delegated acts or guidance issued by the Commission or the AI Office.

---

## Not a replacement for a Notified Body

For high-risk AI systems that require conformity assessment through a Notified Body — which will be the case for most Software as a Medical Device that also qualifies as high-risk under the AI Act — the Notified Body is the authoritative assessor. ClinAI Classifier can help you prepare the conversation; it cannot substitute for it.
