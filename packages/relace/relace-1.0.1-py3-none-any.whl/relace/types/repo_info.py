# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["RepoInfo"]


class RepoInfo(BaseModel):
    repo_head: str

    repo_id: str

    changed_files: Optional[List[str]] = None
