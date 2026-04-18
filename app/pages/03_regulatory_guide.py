"""Interactive regulatory reference guide (Annex III + Article 5)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import streamlit as st

from app.utils.i18n import language_selector, t

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parents[2] / "backend" / "data"
_ANNEX_PATH = _DATA_DIR / "eu_ai_act_annex_iii.json"
_ART5_PATH = _DATA_DIR / "eu_ai_act_article_5.json"


def _load_json(path: Path) -> dict[str, Any]:
    """Load a JSON file from disk.

    Args:
        path: Path to a JSON file.

    Returns:
        Parsed dict, or empty dict on error.
    """
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        logger.exception("Failed to load %s: %s", path, exc)
        return {}


def _matches(query: str, *fields: str) -> bool:
    """Case-insensitive substring match helper.

    Args:
        query: User query string.
        fields: Arbitrary strings to search.

    Returns:
        True if the query is empty or found in any field.
    """
    if not query:
        return True
    q = query.lower()
    return any(q in (field or "").lower() for field in fields)


def _render_annex(annex: dict[str, Any], query: str) -> None:
    """Render Annex III categories filtered by query.

    Args:
        annex: Annex III JSON contents.
        query: Search query string.
    """
    st.subheader(t("regulatory.annex_header"))
    st.caption(annex.get("source", ""))
    categories = annex.get("categories", {})
    for key, entry in categories.items():
        title = entry.get("title", "")
        description = entry.get("description", "")
        sub = entry.get("subcategories", {}) or {}
        haystack = [title, description, *sub.values()]
        if not _matches(query, *haystack):
            continue
        with st.expander(f"{key}. {title}"):
            if description:
                st.write(description)
            for sub_key, sub_text in sub.items():
                st.markdown(f"**{sub_key}** — {sub_text}")


def _render_article5(art5: dict[str, Any], query: str) -> None:
    """Render Article 5 prohibitions filtered by query.

    Args:
        art5: Article 5 JSON contents.
        query: Search query string.
    """
    st.subheader(t("regulatory.article5_header"))
    st.caption(art5.get("source", ""))
    for entry in art5.get("prohibitions", []):
        title = entry.get("title", "")
        text = entry.get("text", "")
        keywords = ", ".join(entry.get("keywords", []))
        if not _matches(query, title, text, keywords):
            continue
        with st.expander(f"{entry.get('id', '')} — {title}"):
            st.write(text)
            if keywords:
                st.caption(f"Keywords: {keywords}")


language_selector()
st.title(t("regulatory.title"))
query = st.text_input(t("regulatory.search"), value="")

annex_data = _load_json(_ANNEX_PATH)
art5_data = _load_json(_ART5_PATH)

if not annex_data and not art5_data:
    st.error("Reference data could not be loaded.")
else:
    _render_article5(art5_data, query)
    st.divider()
    _render_annex(annex_data, query)
