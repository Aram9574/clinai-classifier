"""Response models for the ClinAI Classifier API.

Pydantic v2 models for classification results, legal references,
compliance items, and the top-level API envelope.
"""

from typing import Literal

from pydantic import BaseModel, Field


class LegalReference(BaseModel):
    """A specific article citation with excerpt and source URL."""

    article: str
    title: str
    excerpt: str
    url: str


class ComplianceItem(BaseModel):
    """A single compliance requirement tied to an EU AI Act article."""

    id: str
    article: str
    requirement: str
    priority: Literal["MANDATORY", "RECOMMENDED", "CONDITIONAL"]
    deadline: str


class ClassificationResult(BaseModel):
    """Full classification output produced by the agent + rules engine."""

    risk_level: Literal["PROHIBITED", "HIGH_RISK", "LIMITED_RISK", "MINIMAL_RISK"]
    annex_iii_categories: list[str] = Field(default_factory=list)
    article_5_flags: list[str] = Field(default_factory=list)
    legal_basis: list[LegalReference] = Field(default_factory=list)
    compliance_requirements: list[ComplianceItem] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    clinical_notes: str
    samd_flag: bool
    requires_conformity_assessment: bool
    requires_notified_body: bool


class ClassificationResponse(BaseModel):
    """API envelope returned by POST /classify."""

    success: bool
    data: ClassificationResult | None = None
    error: str | None = None
    processing_time_ms: int
