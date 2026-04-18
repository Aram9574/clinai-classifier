"""Renders a classification result card in Streamlit."""

from __future__ import annotations

import logging
from typing import Any

import streamlit as st

from app.utils.formatting import format_confidence, format_risk_badge_html
from app.utils.i18n import t

logger = logging.getLogger(__name__)


def render_classification_card(result: dict[str, Any]) -> None:
    """Render a full classification result as a Streamlit card.

    Args:
        result: ClassificationResult dict (the `data` field of the API envelope).
    """
    if not result:
        st.warning("No classification result to display.")
        return

    risk_level = result.get("risk_level", "UNKNOWN")
    confidence = float(result.get("confidence_score", 0.0))

    _render_header(risk_level, confidence)
    _render_flags(result)
    _render_categories(result)
    _render_legal_basis(result.get("legal_basis", []))
    _render_clinical_notes(result.get("clinical_notes", ""))


def _render_header(risk_level: str, confidence: float) -> None:
    """Render the top banner with risk badge and confidence.

    Args:
        risk_level: Risk level label.
        confidence: Confidence score in [0, 1].
    """
    st.markdown(f"### {t('classifier.result_header')}")
    badge = format_risk_badge_html(risk_level)
    st.markdown(
        f"{badge} &nbsp; **{t('card.confidence')}:** {format_confidence(confidence)}",
        unsafe_allow_html=True,
    )


def _render_flags(result: dict[str, Any]) -> None:
    """Render boolean regulatory flags as metrics.

    Args:
        result: Classification result dict.
    """
    yes_label = t("card.yes")
    no_label = t("card.no")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric(t("card.samd_flag"), yes_label if result.get("samd_flag") else no_label)
    col_b.metric(
        t("card.conformity_assessment"),
        yes_label if result.get("requires_conformity_assessment") else no_label,
    )
    col_c.metric(
        t("card.notified_body"),
        yes_label if result.get("requires_notified_body") else no_label,
    )


def _render_categories(result: dict[str, Any]) -> None:
    """Render Annex III and Article 5 tags.

    Args:
        result: Classification result dict.
    """
    annex = result.get("annex_iii_categories") or []
    art5 = result.get("article_5_flags") or []
    if annex:
        st.markdown(f"**{t('card.annex_iii')}:** " + ", ".join(annex))
    if art5:
        st.markdown(f"**{t('card.article_5')}:** " + ", ".join(art5))
    if not annex and not art5:
        st.caption(t("card.none"))


def _render_legal_basis(legal_basis: list[dict[str, Any]]) -> None:
    """Render legal basis entries in an expander.

    Args:
        legal_basis: List of LegalReference dicts.
    """
    if not legal_basis:
        return
    with st.expander(t("card.legal_basis"), expanded=False):
        for ref in legal_basis:
            article = ref.get("article", "")
            ref_title = ref.get("title", "")
            excerpt = ref.get("excerpt", "")
            url = ref.get("url", "")
            st.markdown(f"**{article} — {ref_title}**")
            st.write(excerpt)
            if url:
                st.markdown(f"[{t('regulatory.source')}]({url})")
            st.divider()


def _render_clinical_notes(notes: str) -> None:
    """Render clinician-facing narrative notes.

    Args:
        notes: Clinical notes string.
    """
    if not notes:
        return
    st.markdown(f"**{t('card.clinical_notes')}**")
    st.info(notes)
