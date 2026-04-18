"""Static rules engine for EU AI Act classification.

Acts as a safety net over the Claude classification agent: validates the
agent's output against keyword-based heuristics derived from the structured
regulatory JSON files. If the agent under-classifies, the rules engine
escalates the risk level — it NEVER downgrades (per bible critical rule #1).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from backend.models.responses import (
    ClassificationResult,
    ComplianceItem,
    LegalReference,
)

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

RISK_ORDER = {
    "MINIMAL_RISK": 0,
    "LIMITED_RISK": 1,
    "HIGH_RISK": 2,
    "PROHIBITED": 3,
}

EU_AI_ACT_URL = "https://eur-lex.europa.eu/eli/reg/2024/1689/oj"


class RulesEngine:
    """Keyword-driven validator that escalates classifications when needed."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self._annex_iii = self._load_json(data_dir / "eu_ai_act_annex_iii.json")
        self._article_5 = self._load_json(data_dir / "eu_ai_act_article_5.json")
        self._checklists = self._load_json(data_dir / "compliance_checklists.json")

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def detect_article_5_flags(self, description: str) -> list[str]:
        """Return IDs of Article 5 prohibitions triggered by the description."""
        text = description.lower()
        flags: list[str] = []
        for prohibition in self._article_5["prohibitions"]:
            for kw in prohibition["keywords"]:
                if kw.lower() in text:
                    flags.append(prohibition["id"])
                    break
        return flags

    def detect_high_risk_keywords(self, description: str) -> list[str]:
        """Return HIGH_RISK keywords found in the description."""
        text = description.lower()
        keywords = self._annex_iii["classification_keywords"]["HIGH_RISK"]
        return [kw for kw in keywords if kw.lower() in text]

    def _has_medical_carveout(self, description: str) -> bool:
        """Detect medical/safety-purpose context that exempts Art 5(1)(f)."""
        text = description.lower()
        carveout_markers = [
            "pain assessment", "delirium", "icu monitoring", "clinical",
            "diagnosis", "diagnostic", "medical device", "samd", "patient safety",
        ]
        return any(m in text for m in carveout_markers)

    def validate_and_enrich(
        self,
        agent_result: ClassificationResult,
        request_description: str,
        request_intended_purpose: str,
    ) -> ClassificationResult:
        """Cross-check agent output; escalate risk level if needed; enrich refs.

        Args:
            agent_result: Classification produced by the Claude agent.
            request_description: Original free-text system description.
            request_intended_purpose: Declared intended purpose.

        Returns:
            Possibly-escalated ClassificationResult with enriched legal refs
            and compliance checklist. Never downgrades.
        """
        combined_text = f"{request_description}\n{request_intended_purpose}"
        escalated = agent_result.model_copy(deep=True)

        art5_flags = self.detect_article_5_flags(combined_text)
        if art5_flags and not self._has_medical_carveout(combined_text):
            merged = sorted(set(escalated.article_5_flags) | set(art5_flags))
            escalated.article_5_flags = merged
            escalated = self._escalate_to(escalated, "PROHIBITED")
            logger.info("Rules engine: escalated to PROHIBITED on Art 5 flags %s", art5_flags)
            return self._attach_checklist_and_refs(escalated)

        hr_hits = self.detect_high_risk_keywords(combined_text)
        if hr_hits and RISK_ORDER[escalated.risk_level] < RISK_ORDER["HIGH_RISK"]:
            escalated = self._escalate_to(escalated, "HIGH_RISK")
            logger.info("Rules engine: escalated to HIGH_RISK on keywords %s", hr_hits)

        if hr_hits:
            samd_triggers = {"medical device", "samd", "diagnosis", "diagnostic",
                             "treatment recommendation", "mdr", "ivdr"}
            if any(t in hr_hits for t in samd_triggers):
                escalated.samd_flag = True
                escalated.requires_conformity_assessment = True
                escalated.requires_notified_body = True

        return self._attach_checklist_and_refs(escalated)

    def _escalate_to(
        self,
        result: ClassificationResult,
        target_level: str,
    ) -> ClassificationResult:
        """Raise risk_level only if target is strictly higher. Never lowers."""
        if RISK_ORDER[target_level] > RISK_ORDER[result.risk_level]:
            result.risk_level = target_level  # type: ignore[assignment]
        return result

    def _attach_checklist_and_refs(
        self, result: ClassificationResult
    ) -> ClassificationResult:
        """Populate compliance_requirements and legal_basis from static data."""
        checklist_raw = self._checklists["checklists"].get(result.risk_level, [])
        result.compliance_requirements = [ComplianceItem(**item) for item in checklist_raw]

        if not result.legal_basis:
            result.legal_basis = self._default_legal_refs_for(result.risk_level)

        return result

    def _default_legal_refs_for(self, risk_level: str) -> list[LegalReference]:
        """Minimum set of legal references per risk level."""
        if risk_level == "PROHIBITED":
            return [LegalReference(
                article="Article 5",
                title="Prohibited AI practices",
                excerpt="The following AI practices shall be prohibited…",
                url=EU_AI_ACT_URL,
            )]
        if risk_level == "HIGH_RISK":
            return [
                LegalReference(
                    article="Article 6",
                    title="Classification rules for high-risk AI systems",
                    excerpt="An AI system shall be considered high-risk where… "
                            "it is intended to be used as a safety component of a "
                            "product, or is itself a product, covered by the Union "
                            "harmonisation legislation listed in Annex I.",
                    url=EU_AI_ACT_URL,
                ),
                LegalReference(
                    article="Annex III",
                    title="High-risk AI systems referred to in Article 6(2)",
                    excerpt="AI systems in the areas listed in this Annex shall be "
                            "considered high-risk.",
                    url=EU_AI_ACT_URL,
                ),
            ]
        if risk_level == "LIMITED_RISK":
            return [LegalReference(
                article="Article 50",
                title="Transparency obligations for providers and deployers of certain AI systems",
                excerpt="Providers shall ensure that AI systems intended to interact "
                        "directly with natural persons are designed and developed in "
                        "such a way that the natural persons concerned are informed "
                        "that they are interacting with an AI system.",
                url=EU_AI_ACT_URL,
            )]
        return [LegalReference(
            article="Article 95",
            title="Codes of conduct for voluntary application of specific requirements",
            excerpt="The AI Office and the Member States shall encourage and facilitate "
                    "the drawing up of codes of conduct…",
            url=EU_AI_ACT_URL,
        )]
