# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .file_param import FileParam

__all__ = [
    "RepoCreateParams",
    "Source",
    "SourceRepoCreateGitSource",
    "SourceRepoCreateFilesSource",
    "SourceRepoCreateRelaceSource",
]


class RepoCreateParams(TypedDict, total=False):
    auto_index: bool

    metadata: Optional[Dict[str, str]]

    source: Optional[Source]


class SourceRepoCreateGitSource(TypedDict, total=False):
    type: Required[Literal["git"]]

    url: Required[str]

    branch: Optional[str]

    hash: Optional[str]


class SourceRepoCreateFilesSource(TypedDict, total=False):
    files: Required[Iterable[FileParam]]

    type: Required[Literal["files"]]


class SourceRepoCreateRelaceSource(TypedDict, total=False):
    repo_id: Required[str]

    type: Required[Literal["relace"]]

    copy_metadata: bool

    copy_remote: bool


Source: TypeAlias = Union[SourceRepoCreateGitSource, SourceRepoCreateFilesSource, SourceRepoCreateRelaceSource]
