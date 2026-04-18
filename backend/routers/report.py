"""PDF audit report endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.models.responses import ClassificationResponse
from backend.services.pdf_generator import PDFGenerator

router = APIRouter(tags=["report"])

_pdf_generator = PDFGenerator()


@router.post("/report")
def report(payload: ClassificationResponse) -> Response:
    """Generate a downloadable PDF audit report from a classification result."""
    if not payload.success or payload.data is None:
        raise HTTPException(
            status_code=400,
            detail="Cannot generate report: classification payload has no data.",
        )
    pdf_bytes = _pdf_generator.render(payload.data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="clinai_audit_report.pdf"'},
    )
