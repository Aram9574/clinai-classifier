# ClinAI Classifier — HF Spaces Deployment Guide

## Prerequisites

- Python 3.11+ with `huggingface_hub` installed: `pip install huggingface_hub`
- An active Anthropic API key
- A Hugging Face account with write access

Log in to the HF CLI before any Space operations:

```
huggingface-cli login
```

---

## 1. Create the Space

### Option A — Web UI

1. Go to https://huggingface.co/new-space
2. Set Space name to `clinai-classifier`
3. Select **Streamlit** as the SDK
4. Set visibility to Public or Private as preferred
5. Click **Create Space**

### Option B — CLI

```bash
python - <<'EOF'
from huggingface_hub import HfApi
api = HfApi()
api.create_repo(
    repo_id="clinai-classifier",
    repo_type="space",
    space_sdk="streamlit",
    private=False,
)
EOF
```

---

## 2. Set the Anthropic API Key as a Repository Secret

Do **not** use a Space variable — secrets are required so the value is not exposed in build logs.

1. Open your Space at `https://huggingface.co/spaces/<your-username>/clinai-classifier`
2. Go to **Settings → Repository secrets**
3. Add a secret named `ANTHROPIC_API_KEY` with your Anthropic key as the value

The key is injected as an environment variable at runtime and is never written to disk.

---

## 3. Push the Code

Add the Space as a git remote and push:

```bash
git remote add space https://huggingface.co/spaces/<your-username>/clinai-classifier
git push space main
```

If your local branch is not named `main`:

```bash
git push space HEAD:main
```

HF Spaces builds on every push to `main`. The build installs `packages.txt` (system packages) then `requirements.txt` (Python packages).

---

## 4. Check Build Logs

In the Space web UI, click the **Logs** tab. There are two log streams:

- **Build logs** — pip/apt install output; WeasyPrint font warnings appear here and are usually harmless.
- **Container logs** — Streamlit startup and FastAPI subprocess launch output. Look for:

  ```
  INFO     Launched backend: python -m uvicorn backend.main:app ...
  INFO     Application startup complete.
  ```

You can also stream logs via CLI:

```bash
huggingface-cli repo log spaces/<your-username>/clinai-classifier --follow
```

---

## 5. Architecture Note — Subprocess Model

`app/main.py` launches the FastAPI backend as a `subprocess.Popen` child process on port 8000. Streamlit runs on port 7860 (the public-facing HF port). Both processes live inside the same container. Streamlit calls `http://localhost:8000` internally — this never leaves the container and requires no additional networking configuration.

The Streamlit process is PID 1 (started by `CMD`). If FastAPI fails to start within 30 seconds, Streamlit surfaces an error and halts. Check container logs for the uvicorn traceback in that case.

---

## Troubleshooting

### WeasyPrint fails with "cannot load library 'gobject-2.0-0'"

The `packages.txt` at the project root lists the required apt packages. HF Spaces installs them automatically before the Python layer. If the build still fails, check that `packages.txt` is present and committed.

Verify the installed packages in build logs by searching for `libpango`.

### WeasyPrint font rendering issues (missing glyphs / garbled PDF)

HF Spaces runs Debian. The `fonts-liberation` package is included in `packages.txt` and provides Liberation Sans/Serif/Mono as fallback fonts. If your PDF template references a font not available on the system, WeasyPrint silently falls back. Add the font package to `packages.txt` and re-push.

Run `fc-list` in the Space terminal (if available) to confirm installed fonts.

### Port binding conflict — "address already in use :8000"

`app/main.py` checks `/health` before launching the backend. If port 8000 is already occupied (e.g., a stale uvicorn from a hot-reload), the `_backend_is_up()` check returns `True` and no second process is started. If it returns `False` but the port is still bound, the `Popen` will fail. Restart the Space from the Settings tab to get a clean container.

To use a different internal port, set the `FASTAPI_PORT` and `FASTAPI_BASE_URL` Space variables (not secrets — these are not sensitive):

```
FASTAPI_PORT=8001
FASTAPI_BASE_URL=http://localhost:8001
```

### Anthropic rate limits (HTTP 429)

The classifier calls `claude-sonnet-4-5` once per classification request. On the free Anthropic tier, sustained load will hit rate limits. The error surfaces as a 500 from the FastAPI `/classify` endpoint and Streamlit displays "Backend error".

Options:
- Upgrade to a paid Anthropic tier with higher RPM/TPM limits
- Add request-level retry logic in `backend/services/` with exponential back-off
- Cache identical requests in `st.session_state` to avoid re-classifying the same input

### HF Spaces hardware

The default hardware is CPU Basic (2 vCPU, 16 GB RAM). All inference is remote (Anthropic API), so no GPU is required. If the Space sleeps due to inactivity (free tier), the next cold-start takes 20–40 seconds while the subprocess backend restarts.

---

## Next Steps After First Successful Deploy

1. Confirm the `/health` endpoint returns `{"status": "healthy"}` by visiting `https://<your-username>-clinai-classifier.hf.space/health` — note this goes through Streamlit, not directly to FastAPI; use the Streamlit UI health indicator instead.
2. Run the three pre-built examples (ICU readmission, note summariser, social benefit scoring) to confirm all three risk tiers render correctly.
3. Test PDF download to confirm WeasyPrint renders without errors on the HF container fonts.
4. Pin the Space if you want it always awake (paid feature).
