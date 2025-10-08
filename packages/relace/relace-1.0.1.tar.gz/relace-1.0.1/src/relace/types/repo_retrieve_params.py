# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["RepoRetrieveParams"]


class RepoRetrieveParams(TypedDict, total=False):
    query: Required[str]

    branch: Optional[str]

    hash: Optional[str]

    include_content: bool

    rerank: bool

    score_threshold: float

    token_limit: int
