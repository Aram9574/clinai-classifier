"""Formatting helpers for the Streamlit UI."""

from __future__ import annotations

_RISK_COLORS: dict[str, str] = {
    "PROHIBITED": "#DC2626",
    "HIGH_RISK": "#EA580C",
    "LIMITED_RISK": "#CA8A04",
    "MINIMAL_RISK": "#16A34A",
}

_PRIORITY_LABELS: dict[str, str] = {
    "MANDATORY": "[MANDATORY]",
    "RECOMMENDED": "[RECOMMENDED]",
    "CONDITIONAL": "[CONDITIONAL]",
}


def format_confidence(score: float) -> str:
    """Format a 0-1 confidence score as a percent string.

    Args:
        score: Confidence value in [0.0, 1.0].

    Returns:
        String like "87%".
    """
    clamped = max(0.0, min(1.0, float(score)))
    return f"{int(round(clamped * 100))}%"


def format_risk_badge_html(risk_level: str) -> str:
    """Render a colored HTML badge for a risk level.

    Args:
        risk_level: One of PROHIBITED, HIGH_RISK, LIMITED_RISK, MINIMAL_RISK.

    Returns:
        HTML span string with inline color styling.
    """
    color = _RISK_COLORS.get(risk_level, "#374151")
    label = risk_level.replace("_", " ")
    return (
        f'<span style="background-color:{color};color:#ffffff;'
        f"padding:4px 12px;border-radius:6px;font-weight:600;"
        f'font-size:0.9rem;">{label}</span>'
    )


def priority_emoji(priority: str) -> str:
    """Return a plain-text badge for a compliance priority.

    Args:
        priority: MANDATORY, RECOMMENDED, or CONDITIONAL.

    Returns:
        Bracketed label suitable for inline display.
    """
    return _PRIORITY_LABELS.get(priority, f"[{priority}]")
