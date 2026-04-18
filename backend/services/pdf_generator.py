"""Audit-report PDF generator using Jinja2 + WeasyPrint."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from backend.models.responses import ClassificationResult

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


class PDFGenerator:
    """Renders a ClassificationResult as a PDF audit report."""

    def __init__(self, templates_dir: Path = TEMPLATES_DIR) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )
        self._template = self._env.get_template("audit_report.html")

    def render_html(self, result: ClassificationResult) -> str:
        """Render the report HTML without converting to PDF (useful in tests)."""
        return self._template.render(
            data=result,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        )

    def render(self, result: ClassificationResult) -> bytes:
        """Render a PDF document as bytes.

        Args:
            result: Full ClassificationResult produced by the pipeline.

        Returns:
            PDF file contents.
        """
        from weasyprint import HTML  # imported lazily — heavy native dep

        html_str = self.render_html(result)
        return HTML(string=html_str).write_pdf()
