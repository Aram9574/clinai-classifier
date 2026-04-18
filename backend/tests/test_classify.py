"""End-to-end-ish tests for the /classify endpoint via FastAPI TestClient.

Tests stub the Claude agent — no real API calls are made.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.main import app
from backend.models.responses import ClassificationResult
from backend.routers import classify as classify_router


def _patch_agent(monkeypatch, result: ClassificationResult) -> None:
    class _FakeAgent:
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            pass

        def classify(self, request):  # noqa: D401, ANN001
            return result

    monkeypatch.setattr(classify_router, "ClassificationAgent", _FakeAgent)


def _base_payload(**overrides):
    payload = {
        "system_name": "TestSystem",
        "description": "A" * 80,
        "intended_purpose": "Support clinical workflow",
        "data_inputs": ["EHR"],
        "outputs_produced": ["score"],
        "deployment_context": "hospital",
        "affects_clinical_decision": True,
        "anthropic_api_key": "sk-ant-test-dummy",
    }
    payload.update(overrides)
    return payload


def test_health_endpoint_returns_200() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_classification_request_validation() -> None:
    with TestClient(app) as client:
        response = client.post("/classify", json={"system_name": "x"})
    assert response.status_code == 422


def test_cdss_classified_as_high_risk(monkeypatch, make_agent_result) -> None:
    agent_output = make_agent_result(risk_level="HIGH_RISK", samd=True)
    _patch_agent(monkeypatch, agent_output)
    payload = _base_payload(
        description=(
            "Clinical decision support system for ICU triage using ML to predict "
            "patient deterioration and support physician decisions at the bedside."
        ),
    )
    with TestClient(app) as client:
        response = client.post("/classify", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["risk_level"] == "HIGH_RISK"
    assert data["samd_flag"] is True
    assert any("Article 9" in c["article"] or "Article" in c["article"]
               for c in data["compliance_requirements"])


def test_administrative_tool_classified_as_limited_risk(
    monkeypatch, make_agent_result
) -> None:
    agent_output = make_agent_result(
        risk_level="LIMITED_RISK", samd=False,
        notes="Administrative scheduling assistant, no clinical decision impact.",
    )
    _patch_agent(monkeypatch, agent_output)
    payload = _base_payload(
        description=(
            "Appointment scheduling chatbot for a clinic. Provides information about "
            "opening hours and books slots. Does not process clinical content or give "
            "any medical advice to patients or staff whatsoever."
        ),
        intended_purpose="Appointment scheduling assistant",
        affects_clinical_decision=False,
    )
    with TestClient(app) as client:
        response = client.post("/classify", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["risk_level"] == "LIMITED_RISK"


def test_prohibited_social_scoring_flagged(monkeypatch, make_agent_result) -> None:
    agent_output = make_agent_result(
        risk_level="PROHIBITED", samd=False,
        art5_flags=["art5_1_c"],
        notes="Social scoring is prohibited under Article 5(1)(c).",
    )
    _patch_agent(monkeypatch, agent_output)
    payload = _base_payload(
        description=(
            "AI system used by a public authority to compute a social scoring metric "
            "from citizens' healthcare utilisation and lifestyle behaviour in order to "
            "grant or deny access to social benefits."
        ),
        intended_purpose="Social scoring for benefit eligibility",
    )
    with TestClient(app) as client:
        response = client.post("/classify", json=payload)
    data = response.json()["data"]
    assert data["risk_level"] == "PROHIBITED"
    assert "art5_1_c" in data["article_5_flags"]


def test_samd_flag_set_for_diagnostic_ai(monkeypatch, make_agent_result) -> None:
    agent_output = make_agent_result(risk_level="HIGH_RISK", samd=True)
    _patch_agent(monkeypatch, agent_output)
    payload = _base_payload(
        description=(
            "AI diagnostic model for chest X-ray interpretation, intended as a medical "
            "device (SaMD) under MDR, providing diagnostic suggestions to radiologists."
        ),
        intended_purpose="Diagnostic support for chest imaging",
    )
    with TestClient(app) as client:
        response = client.post("/classify", json=payload)
    data = response.json()["data"]
    assert data["samd_flag"] is True
    assert data["requires_conformity_assessment"] is True
    assert data["requires_notified_body"] is True


def test_rules_engine_escalates_when_claude_underclassifies(
    monkeypatch, make_agent_result
) -> None:
    # Agent says MINIMAL, but description contains HIGH_RISK keywords
    agent_output = make_agent_result(
        risk_level="MINIMAL_RISK", samd=False, confidence=0.3,
        notes="Agent was uncertain.",
    )
    _patch_agent(monkeypatch, agent_output)
    payload = _base_payload(
        description=(
            "An AI treatment recommendation system that suggests chemotherapy "
            "protocols for oncology patients based on tumour biomarker panels."
        ),
        intended_purpose="Treatment recommendation for oncology",
    )
    with TestClient(app) as client:
        response = client.post("/classify", json=payload)
    data = response.json()["data"]
    assert data["risk_level"] == "HIGH_RISK"
    assert data["samd_flag"] is True


def test_demo_examples_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/demo/examples")
    assert response.status_code == 200
    assert len(response.json()["examples"]) >= 3


def test_demo_classify_endpoint_returns_precomputed() -> None:
    with TestClient(app) as client:
        examples = client.get("/demo/examples").json()["examples"]
        first_id = examples[0]["id"]
        response = client.get(f"/demo/classify/{first_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["risk_level"] in {
        "PROHIBITED", "HIGH_RISK", "LIMITED_RISK", "MINIMAL_RISK",
    }


def test_classify_requires_api_key() -> None:
    payload = {
        "system_name": "X",
        "description": "A" * 80,
        "intended_purpose": "test purpose",
        "data_inputs": [],
        "outputs_produced": [],
        "deployment_context": "",
        "affects_clinical_decision": False,
    }
    with TestClient(app) as client:
        response = client.post("/classify", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert "API key" in body["error"]
