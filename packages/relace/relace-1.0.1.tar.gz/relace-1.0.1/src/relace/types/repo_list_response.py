# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .repo_metadata import RepoMetadata

__all__ = ["RepoListResponse"]


class RepoListResponse(BaseModel):
    items: List[RepoMetadata]

    total_items: int

    next_page: Optional[int] = None
