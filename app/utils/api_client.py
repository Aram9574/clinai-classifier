"""HTTP client for the ClinAI Classifier FastAPI backend."""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "http://localhost:8000"
_CLASSIFY_TIMEOUT = 60.0
_DEFAULT_TIMEOUT = 15.0


def _base_url() -> str:
    """Return the configured FastAPI base URL.

    Returns:
        Base URL string from FASTAPI_BASE_URL env var or default.
    """
    return os.environ.get("FASTAPI_BASE_URL", _DEFAULT_BASE_URL).rstrip("/")


def classify(payload: dict[str, Any]) -> dict[str, Any]:
    """Call POST /classify with the given request payload.

    Args:
        payload: ClassificationRequest fields as a dict.

    Returns:
        Parsed ClassificationResponse as a dict.
    """
    url = f"{_base_url()}/classify"
    logger.info("POST %s", url)
    response = httpx.post(url, json=payload, timeout=_CLASSIFY_TIMEOUT)
    response.raise_for_status()
    return response.json()


def get_report_pdf(classification_response: dict[str, Any]) -> bytes:
    """Call POST /report and return raw PDF bytes.

    Args:
        classification_response: A full ClassificationResponse dict.

    Returns:
        PDF file bytes.
    """
    url = f"{_base_url()}/report"
    logger.info("POST %s", url)
    response = httpx.post(url, json=classification_response, timeout=_DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.content


def get_demo_examples() -> list[dict[str, Any]]:
    """Fetch the curated demo examples.

    Returns:
        List of example payload dicts from GET /demo/examples.
    """
    url = f"{_base_url()}/demo/examples"
    logger.info("GET %s", url)
    response = httpx.get(url, timeout=_DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.json().get("examples", [])


def get_demo_classification(example_id: str) -> dict[str, Any]:
    """Fetch the pre-computed classification for a demo example.

    Args:
        example_id: The `id` field from /demo/examples.

    Returns:
        Parsed ClassificationResponse dict.
    """
    url = f"{_base_url()}/demo/classify/{example_id}"
    logger.info("GET %s", url)
    response = httpx.get(url, timeout=_DEFAULT_TIMEOUT)
    response.raise_for_status()
    return response.json()


def health() -> dict[str, Any]:
    """Call GET /health to check backend readiness.

    Returns:
        Health dict with status and version.
    """
    url = f"{_base_url()}/health"
    response = httpx.get(url, timeout=5.0)
    response.raise_for_status()
    return response.json()
