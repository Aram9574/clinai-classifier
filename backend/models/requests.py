"""Request models for the ClinAI Classifier API.

Pydantic v2 models validating user input to the /classify endpoint.
"""

from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    """Input describing an AI system to be classified under the EU AI Act."""

    system_name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=50, max_length=3000)
    intended_purpose: str = Field(..., min_length=10, max_length=500)
    data_inputs: list[str] = Field(default_factory=list)
    outputs_produced: list[str] = Field(default_factory=list)
    deployment_context: str = Field(default="", max_length=500)
    affects_clinical_decision: bool = Field(default=False)
    anthropic_api_key: str | None = Field(
        default=None,
        description=(
            "User-supplied Anthropic API key. The server never logs or stores "
            "this value; it is only used for the single outbound call to "
            "Claude and then discarded."
        ),
    )
