# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["RepoListParams"]


class RepoListParams(TypedDict, total=False):
    created_after: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    created_before: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]

    filter_metadata: Optional[str]

    order_by: Literal["created_at", "updated_at"]

    order_descending: bool

    page_size: int

    page_start: int
