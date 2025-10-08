# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["RepoRetrieveResponse", "Result"]


class Result(BaseModel):
    filename: str

    score: float

    content: Optional[str] = None


class RepoRetrieveResponse(BaseModel):
    hash: str

    pending_embeddings: int

    results: List[Result]
