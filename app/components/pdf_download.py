"""PDF download button component."""

from __future__ import annotations

import logging
from typing import Any

import httpx
import streamlit as st

from app.utils.api_client import get_report_pdf
from app.utils.i18n import t

logger = logging.getLogger(__name__)


def render_pdf_download(classification_response: dict[str, Any]) -> None:
    """Render a button that fetches and downloads the PDF audit report.

    Args:
        classification_response: Full ClassificationResponse envelope dict.
    """
    if not classification_response or not classification_response.get("success"):
        return

    session_key = "pdf_bytes_cache"
    generate_key = "pdf_generate_clicked"

    if st.button(t("pdf.generate"), key="generate_pdf_btn"):
        st.session_state[generate_key] = True

    if not st.session_state.get(generate_key):
        return

    if session_key not in st.session_state:
        try:
            with st.spinner(t("pdf.generating")):
                st.session_state[session_key] = get_report_pdf(classification_response)
        except httpx.HTTPError as exc:
            logger.exception("PDF generation failed")
            st.error(f"{t('pdf.error')}: {exc}")
            return

    pdf_bytes = st.session_state.get(session_key)
    if pdf_bytes:
        st.download_button(
            label=t("pdf.download"),
            data=pdf_bytes,
            file_name="clinai_audit_report.pdf",
            mime="application/pdf",
            key="download_pdf_btn",
        )
