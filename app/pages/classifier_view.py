"""Shared rendering logic for the classifier page."""

from __future__ import annotations

import logging
from typing import Any

import httpx
import streamlit as st

from app.components.checklist_view import render_checklist
from app.components.classification_card import render_classification_card
from app.components.pdf_download import render_pdf_download
from app.utils.api_client import classify, get_demo_examples
from app.utils.i18n import t
from app.utils.sidebar import get_api_key

logger = logging.getLogger(__name__)

_DATA_INPUT_OPTIONS: list[str] = [
    "EHR",
    "Imaging",
    "Vital signs",
    "Lab results",
    "Claims data",
    "De-identified notes",
    "Biometric data",
    "Genomic data",
    "Wearable sensor data",
]

_RESULT_KEY = "classification_response"
_EXAMPLE_KEY = "selected_example"


def render() -> None:
    """Render the full classifier page."""
    _render_header()
    _render_example_selector()
    payload = _render_form()
    if payload is not None:
        _run_classification(payload)
    _render_result()


def _render_header() -> None:
    """Render the title and author line."""
    st.title(f"{t('app.title')} — {t('app.subtitle')}")
    st.caption(t("app.author_byline"))
    st.markdown(f"### {t('classifier.title')}")
    st.write(t("classifier.intro"))
    st.divider()


def _render_example_selector() -> None:
    """Render the example loader dropdown."""
    try:
        examples = get_demo_examples()
    except httpx.HTTPError as exc:
        logger.warning("Failed to fetch examples: %s", exc)
        examples = []

    if not examples:
        return

    from app.utils.i18n import get_language
    lang = get_language()
    def _label(ex: dict) -> str:
        return ex.get(f"label_{lang}") or ex.get("label_en") or ex.get("label", "")
    labels = [t("classifier.example_placeholder")] + [_label(ex) for ex in examples]
    choice = st.selectbox(t("classifier.load_example"), labels, key="example_selector")
    if choice and choice != labels[0]:
        idx = labels.index(choice) - 1
        st.session_state[_EXAMPLE_KEY] = examples[idx]


def _render_form() -> dict[str, Any] | None:
    """Render the input form.

    Returns:
        The request payload dict if user clicks Classify, else None.
    """
    example = st.session_state.get(_EXAMPLE_KEY, {})

    with st.form("classify_form"):
        system_name = st.text_input(
            t("classifier.system_name"),
            value=example.get("system_name", ""),
            max_chars=200,
        )
        description = st.text_area(
            t("classifier.description"),
            value=example.get("description", ""),
            height=160,
            max_chars=3000,
            help=t("classifier.description_help"),
        )
        intended_purpose = st.text_input(
            t("classifier.intended_purpose"),
            value=example.get("intended_purpose", ""),
            max_chars=500,
        )
        data_inputs = st.multiselect(
            t("classifier.data_inputs"),
            options=_DATA_INPUT_OPTIONS,
            default=[
                opt
                for opt in _DATA_INPUT_OPTIONS
                if opt.lower() in [d.lower() for d in example.get("data_inputs", [])]
            ],
            help=t("classifier.data_inputs_help"),
        )
        outputs_raw = st.text_input(
            t("classifier.outputs_produced"),
            value=", ".join(example.get("outputs_produced", [])),
        )
        deployment_context = st.text_input(
            t("classifier.deployment_context"),
            value=example.get("deployment_context", ""),
            max_chars=500,
        )
        affects_clinical_decision = st.checkbox(
            t("classifier.affects_clinical_decision"),
            value=bool(example.get("affects_clinical_decision", False)),
        )
        submitted = st.form_submit_button(t("classifier.submit"))

    if not submitted:
        return None
    if len(description) < 50:
        st.error(t("classifier.description_help"))
        return None

    api_key = get_api_key().strip()
    if not api_key:
        st.warning(t("app.api_key_missing"))
        return None

    outputs_list = [part.strip() for part in outputs_raw.split(",") if part.strip()]
    return {
        "system_name": system_name,
        "description": description,
        "intended_purpose": intended_purpose,
        "data_inputs": data_inputs,
        "outputs_produced": outputs_list,
        "deployment_context": deployment_context,
        "affects_clinical_decision": affects_clinical_decision,
        "anthropic_api_key": api_key,
    }


def _run_classification(payload: dict[str, Any]) -> None:
    """Call the backend classify endpoint and store the response.

    Args:
        payload: Validated ClassificationRequest dict.
    """
    # Reset cached PDF when a new classification runs.
    for cache_key in ("pdf_bytes_cache", "pdf_generate_clicked"):
        st.session_state.pop(cache_key, None)

    with st.spinner(t("classifier.submitting")):
        try:
            response = classify(payload)
        except httpx.HTTPError as exc:
            logger.exception("Classify API call failed")
            st.error(f"{t('classifier.error_title')}: {exc}")
            return
    st.session_state[_RESULT_KEY] = response


def _render_result() -> None:
    """Render the last classification response stored in session state."""
    response = st.session_state.get(_RESULT_KEY)
    if not response:
        st.info(t("classifier.empty_prompt"))
        return

    if not response.get("success"):
        st.error(response.get("error") or t("classifier.error_title"))
        return

    data = response.get("data") or {}
    render_classification_card(data)
    st.divider()
    render_checklist(data.get("compliance_requirements", []))
    st.divider()
    render_pdf_download(response)
    elapsed = response.get("processing_time_ms")
    if elapsed is not None:
        st.caption(f"Processed in {elapsed} ms")
