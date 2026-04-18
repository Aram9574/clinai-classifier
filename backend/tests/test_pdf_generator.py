"""Tests for the PDF report generator (HTML rendering stage)."""

from __future__ import annotations

from backend.services.pdf_generator import PDFGenerator
from backend.services.rules_engine import RulesEngine


def test_pdf_report_html_contains_classification(make_agent_result) -> None:
    engine = RulesEngine()
    agent = make_agent_result(risk_level="HIGH_RISK", samd=True)
    enriched = engine.validate_and_enrich(
        agent,
        request_description="CDSS for sepsis prediction in the ICU.",
        request_intended_purpose="Clinical decision support.",
    )
    html = PDFGenerator().render_html(enriched)
    assert "HIGH_RISK" in html
    assert "Article 9" in html
    assert "ClinAI Classifier" in html
    assert "disclaimer" in html.lower()


def test_pdf_report_generated_successfully(make_agent_result) -> None:
    """Full PDF rendering — skipped if WeasyPrint native deps unavailable."""
    import pytest

    engine = RulesEngine()
    agent = make_agent_result(risk_level="LIMITED_RISK", samd=False)
    enriched = engine.validate_and_enrich(
        agent,
        request_description="Patient-facing chatbot for appointment information.",
        request_intended_purpose="Patient-facing information.",
    )
    try:
        pdf_bytes = PDFGenerator().render(enriched)
    except (OSError, ModuleNotFoundError, ImportError) as exc:
        pytest.skip(f"WeasyPrint unavailable: {exc}")
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000
