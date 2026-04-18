"""Classification endpoint (BYOK — bring your own Anthropic API key).

Each request carries its own API key in the body. The key is used for a
single outbound call to Claude and is never logged or persisted.
"""

from __future__ import annotations

import logging
import time

from fastapi import APIRouter

from backend.models.requests import ClassificationRequest
from backend.models.responses import ClassificationResponse
from backend.services.classification_agent import ClassificationAgent
from backend.services.rules_engine import RulesEngine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["classify"])

_rules_engine = RulesEngine()


@router.post("/classify", response_model=ClassificationResponse)
def classify(request: ClassificationRequest) -> ClassificationResponse:
    """Classify an AI system under the EU AI Act using a user-supplied key."""
    start = time.perf_counter()

    if not request.anthropic_api_key:
        return ClassificationResponse(
            success=False,
            error=(
                "Missing Anthropic API key. Paste your key in the sidebar, "
                "or switch to Demo mode to explore pre-computed examples."
            ),
            processing_time_ms=int((time.perf_counter() - start) * 1000),
        )

    try:
        agent = ClassificationAgent(api_key=request.anthropic_api_key)
        agent_result = agent.classify(request)
        final = _rules_engine.validate_and_enrich(
            agent_result,
            request_description=request.description,
            request_intended_purpose=request.intended_purpose,
        )
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return ClassificationResponse(
            success=True, data=final, processing_time_ms=elapsed_ms
        )
    except ValueError as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.warning("Classification parse error: %s", exc)
        return ClassificationResponse(
            success=False, error=str(exc), processing_time_ms=elapsed_ms
        )
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.exception("Classification failed")
        return ClassificationResponse(
            success=False,
            error=f"{type(exc).__name__}: {exc}",
            processing_time_ms=elapsed_ms,
        )
