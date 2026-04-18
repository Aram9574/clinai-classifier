"""Streamlit entrypoint for the ClinAI Classifier app.

Launches the FastAPI backend as a subprocess (single-process deploy mode
required by Hugging Face Spaces), waits for health, then renders the
classifier page.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import time

import httpx
import streamlit as st

from app.utils.api_client import health
from app.utils.i18n import t
from app.utils.sidebar import render_sidebar

logger = logging.getLogger(__name__)

_BACKEND_HOST = os.environ.get("FASTAPI_HOST", "0.0.0.0")
_BACKEND_PORT = os.environ.get("FASTAPI_PORT", "8000")
_HEALTH_POLL_SECONDS = 0.5
_HEALTH_MAX_WAIT = 90.0


def _backend_is_up() -> bool:
    """Return True if the FastAPI /health endpoint responds healthy."""
    try:
        response = health()
        return response.get("status") == "healthy"
    except (httpx.HTTPError, OSError):
        return False


def _launch_backend() -> subprocess.Popen | None:
    """Start uvicorn as a child process if the backend isn't already running.

    Returns:
        Popen handle if a process was started, else None.
    """
    if _backend_is_up():
        logger.info("Backend already running; skipping launch.")
        return None

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        _BACKEND_HOST,
        "--port",
        _BACKEND_PORT,
        "--log-level",
        "info",
    ]
    logger.info("Launching backend: %s", " ".join(cmd))
    env = os.environ.copy()
    # Ensure the subprocess can import the top-level `backend` package
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.Popen(
        cmd,
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def _wait_for_backend(proc: subprocess.Popen | None) -> bool:
    """Poll /health until ready or timeout.

    Args:
        proc: The uvicorn subprocess (or None if we didn't launch one).

    Returns:
        True if backend became healthy within the timeout.
    """
    deadline = time.time() + _HEALTH_MAX_WAIT
    while time.time() < deadline:
        if _backend_is_up():
            return True
        if proc is not None and proc.poll() is not None:
            logger.error("Backend process exited with code %s", proc.returncode)
            return False
        time.sleep(_HEALTH_POLL_SECONDS)
    return False


def _ensure_backend() -> None:
    """Guarantee a running FastAPI instance for this Streamlit session."""
    if st.session_state.get("backend_ready"):
        return
    proc = _launch_backend()
    st.session_state["backend_process"] = proc
    if not _wait_for_backend(proc):
        st.error(
            f"Backend failed to start within {int(_HEALTH_MAX_WAIT)}s. "
            "Check server logs."
        )
        st.stop()
    st.session_state["backend_ready"] = True


def _render_shell() -> None:
    """Render the Streamlit page shell (page config + sidebar nav hint)."""
    st.set_page_config(
        page_title="ClinAI Classifier",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def main() -> None:
    """Entry point called by `streamlit run app/main.py`."""
    _render_shell()
    mode = render_sidebar()
    _ensure_backend()

    if mode == "demo":
        from app.pages import demo_view

        demo_view.render()
    else:
        from app.pages import classifier_view

        classifier_view.render()


if __name__ == "__main__":
    main()
