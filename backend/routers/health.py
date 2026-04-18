"""Health check router."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])

VERSION = "1.0.0"


@router.get("/health")
def health() -> dict[str, str]:
    """Return service health and version."""
    return {"status": "healthy", "version": VERSION}
