# Worked Examples

Five end-to-end classification examples drawn from the test suite. Each shows the input you would provide to ClinAI Classifier, the expected classification, the legal basis, the key compliance requirements the rules engine attaches, and physician-oriented notes.

---

## 1. ICU 30-day readmission predictor — `HIGH_RISK` (SaMD)

**Input**

- System name: `ReadmitAI`
- Description: Machine learning model that predicts 30-day ICU readmission risk from EHR data, used at discharge to support triage and follow-up decisions by the attending physician.
- Intended purpose: Support clinical discharge and triage decisions.

**Expected classification**

- `risk_level`: `HIGH_RISK`
- `samd_flag`: `true`
- `requires_conformity_assessment`: `true`
- `requires_notified_body`: `true`

**Legal basis**

- Article 6(1) — safety component of a product covered by MDR/IVDR.
- Annex III point 5 — access to essential services (healthcare relevance).
- Articles 9–15 — risk management, data governance, technical documentation, logging, transparency, human oversight, accuracy.

**Key compliance requirements**

- Article 9 risk management system across the lifecycle.
- Article 10 data governance with explicit bias examination for health equity.
- Article 14 human oversight — the attending physician must be able to interpret, override, and refuse the readmission score.
- Article 43 conformity assessment through a Notified Body, combined with MDR assessment.
- Article 72 post-market monitoring and Article 73 serious-incident reporting.

**Physician notes**

A readmission score sits directly in a clinical decision pathway. Even when framed as "decision support", the output is likely to anchor discharge conversations. Automation bias is the primary clinical risk. The model's performance must be validated across the actual patient demographics of the deploying ICU, not just the training cohort, and the discharging clinician must have a clear, documented ability to dissent.

---

## 2. Clinical note summariser for research — `LIMITED_RISK`

**Input**

- System name: `NoteBrief`
- Description: NLP system that extracts structured data and summarises clinical notes for downstream research use on de-identified records. Does not provide any diagnostic or treatment suggestions.
- Intended purpose: Research-facing summarisation of de-identified clinical notes.

**Expected classification**

- `risk_level`: `LIMITED_RISK`
- `samd_flag`: `false`

**Legal basis**

- Article 50 — transparency obligations for AI systems generating or manipulating content.

**Key compliance requirements**

- Article 50(1) transparency — users of the research platform must be informed that summaries are AI-generated.
- Article 50(2) synthetic content marking — machine-readable marking of generated summaries where applicable.
- Recital 27 — maintain internal documentation of the classification rationale.
- GDPR — even on de-identified data, confirm that re-identification risk is adequately mitigated.

**Physician notes**

Research-only, de-identified, non-clinical-decision tooling sits cleanly in the limited-risk band. The main failure mode is **scope creep**: if the summarisation output ever starts informing clinical care or is integrated into a clinician's workflow, the classification must be re-run — the system would then almost certainly become high-risk.

---

## 3. Public-authority healthcare social score — `PROHIBITED`

**Input**

- System name: `HealthBenefitScore`
- Description: AI system used by a public authority to build a social score for citizens based on healthcare utilisation and lifestyle behaviour, used to grant or deny access to general social services.
- Intended purpose: Social scoring for benefit eligibility.

**Expected classification**

- `risk_level`: `PROHIBITED`

**Legal basis**

- Article 5(1)(c) — social scoring by classification of natural persons based on social behaviour, leading to detrimental or unfavourable treatment.

**Key compliance requirements**

- Cease development and deployment immediately — the prohibition has applied since 2 February 2025.
- Conduct a formal legal review to confirm the prohibition finding and document the discontinuation with dated records.

**Physician notes**

The medical carveout does **not** apply here. The system scores citizens based on behavioural and health signals to decide benefit eligibility, which is the paradigm example of Article 5(1)(c). Any overlap with Annex III 5(a) (public-authority eligibility evaluation for healthcare services) is secondary — the prohibition takes precedence. A hospital or insurer contemplating a variant of this design should stop and engage legal counsel before any further work.

---

## 4. Consumer wearable dashboard — `MINIMAL_RISK`

**Input**

- System name: `WellnessView`
- Description: A consumer mobile app that aggregates step count, heart rate, and sleep metrics from a commercial wearable and displays trends to the user. No diagnostic interpretation, no clinical advice, no clinician-facing outputs.
- Intended purpose: Consumer wellness visualisation.

**Expected classification**

- `risk_level`: `MINIMAL_RISK`
- `samd_flag`: `false`

**Legal basis**

- Article 95 — voluntary codes of conduct for minimal-risk AI.

**Key compliance requirements**

- Article 95 voluntary adherence to codes of conduct on transparency, human oversight, and bias mitigation.
- GDPR compliance for any processing of personal health data.
- Article 6 monitoring — if substantial modification introduces diagnostic interpretation, reassess classification.

**Physician notes**

Wellness dashboards without diagnostic claims sit at minimal risk. The clinical risk lever is medical-claim creep: once the app starts suggesting "your sleep pattern indicates apnea — see a doctor" or integrating with a clinician portal, it crosses into limited or high-risk territory. Vendors frequently misjudge this boundary in marketing copy; legal review of the intended-purpose statement matters.

---

## 5. Oncology treatment recommendation system — `HIGH_RISK` (SaMD)

**Input**

- System name: `OncoAdvisor`
- Description: Clinical decision support system that ingests tumour pathology, genomic profile, and patient history to generate ranked treatment recommendations. Used by oncologists during multidisciplinary tumour board meetings.
- Intended purpose: Generate evidence-based oncology treatment recommendations to support the tumour board.

**Expected classification**

- `risk_level`: `HIGH_RISK`
- `samd_flag`: `true`
- `requires_conformity_assessment`: `true`
- `requires_notified_body`: `true`

**Legal basis**

- Article 6(1) — safety component of a product regulated under MDR/IVDR.
- Annex III point 5 — access to essential healthcare services.
- Articles 9–15, 17, 43, 48, 49, 72, 73.

**Key compliance requirements**

- Full high-risk compliance stack — risk management (Art. 9), data governance with oncology-cohort bias examination (Art. 10), technical documentation (Art. 11), logging (Art. 12), transparency to oncologists (Art. 13), robust human oversight in the tumour board workflow (Art. 14), validated accuracy (Art. 15).
- ISO 13485-integrated QMS (Art. 17).
- Combined AI Act and MDR conformity assessment with a Notified Body (Art. 43).
- CE marking (Art. 48) and EU database registration (Art. 49).
- Post-market monitoring (Art. 72) and serious incident reporting (Art. 73).

**Physician notes**

Treatment recommendation systems in oncology are a textbook high-risk SaMD case. The tumour board framing provides natural human oversight but does not lower the risk classification — the recommendation itself is the safety-relevant output. Particular attention should be paid to representativeness of the training cohort (rare cancers, paediatric cases, under-represented populations) and to the traceability of each recommendation back to the evidence base the system cites. Clinicians must be able to reject a recommendation without workflow penalty.
