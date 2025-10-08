# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List

from .file import File
from .._models import BaseModel

__all__ = ["RepoCloneResponse"]


class RepoCloneResponse(BaseModel):
    files: List[File]
