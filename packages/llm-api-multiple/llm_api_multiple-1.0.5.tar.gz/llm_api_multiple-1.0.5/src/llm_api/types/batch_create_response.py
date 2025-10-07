# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["BatchCreateResponse", "RequestCounts"]


class RequestCounts(BaseModel):
    completed: Optional[int] = None

    failed: Optional[int] = None

    total: Optional[int] = None


class BatchCreateResponse(BaseModel):
    id: str
    """The batch ID."""

    completion_window: str
    """The time frame for the batch completion."""

    created_at: int
    """The creation timestamp in Unix format."""

    endpoint: str
    """The endpoint for the batch requests."""

    expires_at: int
    """The expiration timestamp in Unix format."""

    input_file_id: str
    """The ID of the input file."""

    cancelled_at: Optional[datetime] = None

    cancelling_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    error_file_id: Optional[str] = None

    errors: Optional[str] = None

    expired_at: Optional[datetime] = None

    failed_at: Optional[datetime] = None

    finalizing_at: Optional[datetime] = None

    in_progress_at: Optional[datetime] = None

    metadata: Optional[Dict[str, str]] = None

    object: Optional[str] = None
    """The object type, always 'batch'."""

    output_file_id: Optional[str] = None

    request_counts: Optional[RequestCounts] = None
    """A model to track the total, completed, and failed requests within a batch job."""

    status: Optional[str] = None
    """The status of the batch job."""
