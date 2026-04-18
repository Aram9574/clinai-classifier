"""Unit tests for the static rules engine."""

from __future__ import annotations

from backend.services.rules_engine import RulesEngine


def test_detects_article_5_social_scoring(make_agent_result) -> None:
    engine = RulesEngine()
    flags = engine.detect_article_5_flags(
        "Compute a social score for citizens based on lifestyle signals."
    )
    assert "art5_1_c" in flags


def test_detects_high_risk_keywords() -> None:
    engine = RulesEngine()
    hits = engine.detect_high_risk_keywords(
        "Clinical decision support for sepsis prediction in the ICU."
    )
    assert "clinical decision support" in hits
    assert "sepsis prediction" in hits


def test_never_downgrades_when_agent_says_high_risk(make_agent_result) -> None:
    engine = RulesEngine()
    agent = make_agent_result(risk_level="HIGH_RISK", samd=True)
    result = engine.validate_and_enrich(
        agent,
        request_description="Wearable dashboard for step counting.",
        request_intended_purpose="Consumer fitness tracking.",
    )
    assert result.risk_level == "HIGH_RISK"


def test_escalates_minimal_to_high_risk_on_diagnostic_keywords(make_agent_result) -> None:
    engine = RulesEngine()
    agent = make_agent_result(risk_level="MINIMAL_RISK", samd=False)
    result = engine.validate_and_enrich(
        agent,
        request_description=(
            "ML model for diagnosis of diabetic retinopathy from fundus images, "
            "intended as SaMD under MDR."
        ),
        request_intended_purpose="Diagnostic support in ophthalmology.",
    )
    assert result.risk_level == "HIGH_RISK"
    assert result.samd_flag is True
    assert result.requires_conformity_assessment is True


def test_escalates_to_prohibited_on_article_5(make_agent_result) -> None:
    engine = RulesEngine()
    agent = make_agent_result(risk_level="LIMITED_RISK", samd=False)
    result = engine.validate_and_enrich(
        agent,
        request_description="Social scoring system ranking citizens by behaviour.",
        request_intended_purpose="Allocate social benefits.",
    )
    assert result.risk_level == "PROHIBITED"


def test_attaches_checklist_matching_risk_level(make_agent_result) -> None:
    engine = RulesEngine()
    agent = make_agent_result(risk_level="HIGH_RISK", samd=True)
    result = engine.validate_and_enrich(
        agent,
        request_description="CDSS for ICU triage.",
        request_intended_purpose="Clinical decision support.",
    )
    assert len(result.compliance_requirements) > 0
    articles = {c.article for c in result.compliance_requirements}
    assert "Article 9" in articles
    assert "Article 14" in articles
