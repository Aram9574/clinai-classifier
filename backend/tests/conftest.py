"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Make project root importable when pytest is run from anywhere
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.models.responses import ClassificationResult  # noqa: E402
from backend.services.classification_agent import ClassificationAgent  # noqa: E402


def _build_agent_result(
    risk_level: str = "HIGH_RISK",
    annex_iii: list[str] | None = None,
    art5_flags: list[str] | None = None,
    samd: bool = True,
    confidence: float = 0.85,
    notes: str = "Physician note: system supports clinical decisions.",
) -> ClassificationResult:
    return ClassificationResult(
        risk_level=risk_level,  # type: ignore[arg-type]
        annex_iii_categories=annex_iii or [],
        article_5_flags=art5_flags or [],
        legal_basis=[],
        compliance_requirements=[],
        confidence_score=confidence,
        clinical_notes=notes,
        samd_flag=samd,
        requires_conformity_assessment=samd,
        requires_notified_body=samd,
    )


@pytest.fixture
def make_agent_result():
    """Factory fixture for ClassificationResult stubs."""
    return _build_agent_result


@pytest.fixture
def stub_agent(monkeypatch, make_agent_result):
    """Replace ClassificationAgent.classify with a MagicMock returning a stub."""
    result = make_agent_result()
    mock = MagicMock(return_value=result)
    monkeypatch.setattr(ClassificationAgent, "classify", lambda self, request: mock(request))
    return mock
