"""FastAPI entrypoint for ClinAI Classifier backend."""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI

from backend.routers import classify, demo, health, report

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
)

app = FastAPI(
    title="ClinAI Classifier",
    description="EU AI Act classification engine for healthcare AI systems.",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(classify.router)
app.include_router(demo.router)
app.include_router(report.router)


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("FASTAPI_HOST", "0.0.0.0")
    port = int(os.environ.get("FASTAPI_PORT", "8000"))
    uvicorn.run("backend.main:app", host=host, port=port, reload=False)
