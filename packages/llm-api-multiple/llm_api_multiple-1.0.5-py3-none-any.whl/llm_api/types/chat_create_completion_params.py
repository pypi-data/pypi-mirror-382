# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Dict, List
from typing_extensions import TypedDict

__all__ = ["ChatCreateCompletionParams"]


class ChatCreateCompletionParams(TypedDict, total=False):
    messages: List[Dict[str, Any]]
    model: str
    max_tokens: int
    temperature: float
    top_p: float
    top_k: int
    stream: bool
