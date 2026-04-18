"""Shared sidebar: language selector, mode selector, API key input."""

from __future__ import annotations

from typing import Literal

import streamlit as st

from app.utils.i18n import language_selector, t

Mode = Literal["demo", "byok"]

_MODE_KEY = "app_mode"
_API_KEY_STATE = "anthropic_api_key"


def render_sidebar() -> Mode:
    """Render the sidebar controls. Returns the active mode.

    The sidebar has three stacked sections:
      1. Language selector
      2. Mode selector (Demo / BYOK)
      3. API key input (only visible in BYOK mode)

    Returns:
        "demo" or "byok".
    """
    language_selector(location="sidebar")

    mode_labels = {
        "demo": t("app.mode_demo"),
        "byok": t("app.mode_byok"),
    }
    current = st.session_state.get(_MODE_KEY, "demo")
    choice_label = st.sidebar.radio(
        t("app.mode_label"),
        options=list(mode_labels.values()),
        index=0 if current == "demo" else 1,
        key="_mode_selector_radio",
    )
    mode: Mode = "demo" if choice_label == mode_labels["demo"] else "byok"
    st.session_state[_MODE_KEY] = mode

    if mode == "demo":
        st.sidebar.caption(t("app.mode_demo_help"))
    else:
        st.sidebar.caption(t("app.mode_byok_help"))
        api_key = st.sidebar.text_input(
            t("app.api_key_label"),
            value=st.session_state.get(_API_KEY_STATE, ""),
            type="password",
            placeholder=t("app.api_key_placeholder"),
            help=t("app.api_key_help"),
            key="_api_key_input",
        )
        st.session_state[_API_KEY_STATE] = api_key
        st.sidebar.caption(t("app.privacy_note"))

    return mode


def get_api_key() -> str:
    """Return the user-supplied API key (empty string if not set)."""
    return st.session_state.get(_API_KEY_STATE, "") or ""
