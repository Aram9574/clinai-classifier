"""Claude-powered classification agent for EU AI Act.

Uses the Anthropic SDK with structured (JSON) output to produce a
preliminary ClassificationResult. The rules_engine validates and may
escalate the result afterward.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from anthropic import Anthropic

from backend.models.requests import ClassificationRequest
from backend.models.responses import ClassificationResult

logger = logging.getLogger(__name__)

MODEL_NAME = "claude-sonnet-4-5"
MAX_TOKENS = 2000

SYSTEM_PROMPT = """You are a regulatory expert specialized in the EU AI Act (Regulation 2024/1689) with deep clinical knowledge of AI systems in healthcare.

Your task is to classify an AI system based on its description and determine:
1. Whether it falls under prohibited practices (Article 5)
2. Whether it qualifies as high-risk under Annex III (specifically point 5 for health, and Article 6 for SaMD under MDR/IVDR)
3. The specific legal basis for the classification
4. Compliance requirements that apply

You must:
- Cite specific articles and annex points
- Be conservative: when in doubt, classify as higher risk
- Distinguish between AI systems that SUPPORT clinical decisions vs those that REPLACE them
- Consider the intended purpose, not just technical implementation
- Flag SaMD (Software as a Medical Device) implications separately
- Provide clinical_notes from the perspective of a physician who understands both clinical workflows and regulatory constraints

You must NOT:
- Provide legal advice or guarantee regulatory approval
- Classify systems you cannot reasonably assess from the description
- Underestimate risk to favor deployment speed

Output ONLY a valid JSON object matching this schema — no prose, no markdown fences:
{
  "risk_level": "PROHIBITED" | "HIGH_RISK" | "LIMITED_RISK" | "MINIMAL_RISK",
  "annex_iii_categories": [string],
  "article_5_flags": [string],
  "legal_basis": [{"article": str, "title": str, "excerpt": str, "url": str}],
  "compliance_requirements": [],
  "confidence_score": float between 0 and 1,
  "clinical_notes": str,
  "samd_flag": bool,
  "requires_conformity_assessment": bool,
  "requires_notified_body": bool
}

Leave compliance_requirements as an empty list — the rules engine will populate it."""


def _build_user_prompt(request: ClassificationRequest) -> str:
    return f"""Classify the following AI system under the EU AI Act.

System name: {request.system_name}

Description:
{request.description}

Intended purpose: {request.intended_purpose}

Data inputs: {", ".join(request.data_inputs) or "not specified"}
Outputs produced: {", ".join(request.outputs_produced) or "not specified"}
Deployment context: {request.deployment_context or "not specified"}
Affects clinical decisions: {request.affects_clinical_decision}

Return the JSON object only."""


class ClassificationAgent:
    """Wrapper around the Anthropic client for classification requests."""

    def __init__(
        self,
        client: Anthropic | None = None,
        api_key: str | None = None,
    ) -> None:
        """Build a classification agent.

        Args:
            client: Optional preconfigured Anthropic client (for tests).
            api_key: User-supplied Anthropic API key. If None, falls back to
                the ANTHROPIC_API_KEY env var — only used for local dev.
        """
        resolved_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._client = client or Anthropic(api_key=resolved_key)

    def classify(self, request: ClassificationRequest) -> ClassificationResult:
        """Run the agent and return a parsed ClassificationResult.

        Args:
            request: Validated ClassificationRequest.

        Returns:
            ClassificationResult parsed from the model's JSON output.

        Raises:
            ValueError: if the model returns invalid or unparseable JSON.
        """
        user_prompt = _build_user_prompt(request)
        message = self._client.messages.create(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw_text = "".join(
            block.text for block in message.content if getattr(block, "type", None) == "text"
        ).strip()

        payload = self._extract_json(raw_text)
        try:
            return ClassificationResult(**payload)
        except Exception as exc:
            logger.exception("Failed to parse classification result: %s", exc)
            raise ValueError(f"Invalid classification payload: {exc}") from exc

    @staticmethod
    def _extract_json(raw: str) -> dict[str, Any]:
        """Tolerate stray prose or markdown fences around the JSON body."""
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:]
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("Model output did not contain a JSON object")
        return json.loads(text[start : end + 1])
