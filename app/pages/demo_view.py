"""Demo page: gallery of curated examples with pre-computed classifications."""

from __future__ import annotations

import logging

import httpx
import streamlit as st

from app.components.checklist_view import render_checklist
from app.components.classification_card import render_classification_card
from app.components.pdf_download import render_pdf_download
from app.utils.api_client import get_demo_classification, get_demo_examples
from app.utils.i18n import get_language, t

logger = logging.getLogger(__name__)

_SELECTED_KEY = "demo_selected_id"
_RESPONSE_KEY = "demo_response"


def render() -> None:
    """Render the demo gallery + result view."""
    st.title(t("demo.title"))
    st.write(t("demo.intro"))

    try:
        examples = get_demo_examples()
    except httpx.HTTPError as exc:
        logger.exception("Failed to fetch demo examples")
        st.error(str(exc))
        return

    _render_gallery(examples)
    st.divider()
    _render_selected_result()


def _render_gallery(examples: list[dict]) -> None:
    """Render a card grid of demo examples."""
    lang = get_language()
    cols = st.columns(2)
    for idx, example in enumerate(examples):
        col = cols[idx % 2]
        label = example.get(f"label_{lang}") or example.get("label_en", example["id"])
        desc = example.get(f"description_{lang}") or example.get("description_en", "")
        with col.container(border=True):
            st.markdown(f"**{label}**")
            st.caption(desc)
            if st.button(
                t("demo.run_button"),
                key=f"demo_btn_{example['id']}",
                use_container_width=True,
            ):
                st.session_state[_SELECTED_KEY] = example["id"]
                try:
                    st.session_state[_RESPONSE_KEY] = get_demo_classification(example["id"])
                except httpx.HTTPError as exc:
                    logger.exception("Demo classification fetch failed")
                    st.session_state[_RESPONSE_KEY] = {
                        "success": False,
                        "error": str(exc),
                        "processing_time_ms": 0,
                    }


def _render_selected_result() -> None:
    """Render the pre-computed ClassificationResponse for the selected example."""
    response = st.session_state.get(_RESPONSE_KEY)
    if not response:
        return

    selected_id = st.session_state.get(_SELECTED_KEY, "")
    st.markdown(f"### {t('demo.selected_example')}: `{selected_id}`")

    if not response.get("success"):
        st.error(response.get("error") or t("classifier.error_title"))
        return

    data = response.get("data") or {}
    render_classification_card(data)
    st.divider()
    render_checklist(data.get("compliance_requirements", []))
    st.divider()
    render_pdf_download(response)
