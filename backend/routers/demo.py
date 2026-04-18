"""Demo endpoints — serve pre-computed classifications for the curated examples.

These run without any Anthropic API key. They let the user explore the full
UX (result card, checklist, PDF) on canned inputs before deciding to plug in
their own key for custom classifications.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from backend.models.responses import ClassificationResponse, ClassificationResult

logger = logging.getLogger(__name__)

router = APIRouter(tags=["demo"])

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_EXAMPLES_PATH = _DATA_DIR / "demo_examples.json"
_CLASSIFICATIONS_PATH = _DATA_DIR / "demo_classifications.json"


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


@router.get("/demo/examples")
def list_examples() -> dict:
    """Return the list of curated demo examples (request payloads + labels)."""
    doc = _load_json(_EXAMPLES_PATH)
    return {"examples": doc["examples"]}


@router.get("/demo/classify/{example_id}", response_model=ClassificationResponse)
def demo_classify(example_id: str) -> ClassificationResponse:
    """Return the pre-computed classification for a demo example id."""
    store = _load_json(_CLASSIFICATIONS_PATH)
    if example_id not in store:
        raise HTTPException(status_code=404, detail=f"Unknown example id: {example_id}")
    result = ClassificationResult(**store[example_id])
    return ClassificationResponse(
        success=True,
        data=result,
        processing_time_ms=0,
    )
