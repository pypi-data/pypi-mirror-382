from __future__ import annotations

from typing import Any

from ..models import ErrorResponse


class AICMError(Exception):
    """Base exception for SDK errors."""


class MissingConfiguration(AICMError):
    """Raised when required configuration is missing."""


class APIRequestError(AICMError):
    """Raised for non-successful HTTP responses."""

    def __init__(self, status_code: int, detail: Any) -> None:
        self.status_code = status_code
        self.error_response: ErrorResponse | None = None
        self.error: str | None = None
        self.message: str | None = None
        self.details: Any | None = None
        if isinstance(detail, dict):
            try:
                self.error_response = ErrorResponse.model_validate(detail)
                self.error = self.error_response.detail
                self.message = self.error_response.detail
                self.details = self.error_response.code
            except Exception:
                self.error = detail.get("detail")
                self.message = detail.get("detail")
        super().__init__(f"API request failed with status {status_code}: {detail}")


class UsageLimitExceeded(AICMError):
    """Raised when a usage limit has been exceeded and blocks API calls."""

    def __init__(self, triggered_limits: list) -> None:
        self.triggered_limits = triggered_limits
        limit_info = ", ".join(
            [f"limit {tl.limit_id} ({tl.threshold_type})" for tl in triggered_limits]
        )
        super().__init__(f"Usage limit exceeded: {limit_info}")


class NoCostsTrackedException(AICMError):
    """Raised when /track returns no cost events for immediate delivery."""

    def __init__(self) -> None:
        super().__init__("No cost events were recorded for the tracked payload")


class BatchSizeLimitExceeded(AICMError):
    """Raised when the batch size exceeds the maximum allowed limit."""

    def __init__(self, batch_size: int, max_batch_size: int) -> None:
        self.batch_size = batch_size
        self.max_batch_size = max_batch_size
        super().__init__(
            f"Batch size of {batch_size} exceeds maximum allowed limit of {max_batch_size}"
        )
