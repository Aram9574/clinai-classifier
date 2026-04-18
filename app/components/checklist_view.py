"""Compliance checklist rendering component."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.utils.formatting import priority_emoji
from app.utils.i18n import t

_PRIORITY_ORDER: dict[str, int] = {
    "MANDATORY": 0,
    "RECOMMENDED": 1,
    "CONDITIONAL": 2,
}


def render_checklist(compliance_requirements: list[dict[str, Any]]) -> None:
    """Render compliance requirements grouped and sorted by priority.

    Args:
        compliance_requirements: List of ComplianceItem dicts.
    """
    if not compliance_requirements:
        st.caption(t("checklist.empty"))
        return

    sorted_items = sorted(
        compliance_requirements,
        key=lambda item: _PRIORITY_ORDER.get(item.get("priority", "CONDITIONAL"), 99),
    )

    st.markdown(f"### {t('checklist.title')}")

    priority_label_keys = {
        "MANDATORY": "checklist.mandatory",
        "RECOMMENDED": "checklist.recommended",
        "CONDITIONAL": "checklist.conditional",
    }
    current_priority: str | None = None
    for item in sorted_items:
        priority = item.get("priority", "CONDITIONAL")
        if priority != current_priority:
            label = t(priority_label_keys.get(priority, "checklist.conditional"))
            st.markdown(f"#### {priority_emoji(priority)} {label}")
            current_priority = priority
        _render_item_row(item)


def _render_item_row(item: dict[str, Any]) -> None:
    """Render a single compliance requirement row.

    Args:
        item: ComplianceItem dict.
    """
    article = item.get("article", "")
    requirement = item.get("requirement", "")
    deadline = item.get("deadline", "")
    with st.container(border=True):
        st.markdown(f"**{article}** — {requirement}")
        if deadline:
            st.caption(f"{t('checklist.deadline')}: {deadline}")
