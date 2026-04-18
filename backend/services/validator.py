"""Thin wrapper around Pydantic validation for consistent error messages."""

from __future__ import annotations

from pydantic import ValidationError

from backend.models.requests import ClassificationRequest


class InputValidationError(Exception):
    """Raised when a ClassificationRequest payload is invalid."""


def parse_classification_request(payload: dict) -> ClassificationRequest:
    """Parse and validate a raw dict into a ClassificationRequest.

    Args:
        payload: Raw dictionary from the HTTP request body.

    Returns:
        Validated ClassificationRequest.

    Raises:
        InputValidationError: on any Pydantic validation failure.
    """
    try:
        return ClassificationRequest(**payload)
    except ValidationError as exc:
        raise InputValidationError(str(exc)) from exc
