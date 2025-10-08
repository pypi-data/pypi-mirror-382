# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["RepoMetadata"]


class RepoMetadata(BaseModel):
    auto_index: bool

    created_at: datetime

    metadata: Optional[Dict[str, str]] = None

    repo_id: str

    updated_at: Optional[datetime] = None
