# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Required, TypedDict

__all__ = ["BatchCreateParams"]


class BatchCreateParams(TypedDict, total=False):
    completion_window: Required[str]
    """The time frame for the batch completion, e.g., '24h'."""

    endpoint: Required[str]
    """The endpoint for the batch requests, e.g., '/v1/chat/completions'."""

    input_file_id: Required[str]
    """The ID of the file to be processed."""

    metadata: Optional[Dict[str, str]]
