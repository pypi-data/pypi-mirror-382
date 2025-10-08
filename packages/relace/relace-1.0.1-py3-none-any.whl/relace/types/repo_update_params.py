# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .file_param import FileParam

__all__ = [
    "RepoUpdateParams",
    "Source",
    "SourceRepoUpdateFiles",
    "SourceRepoUpdateDiff",
    "SourceRepoUpdateDiffOperation",
    "SourceRepoUpdateDiffOperationFileWriteOperation",
    "SourceRepoUpdateDiffOperationFileDeleteOperation",
    "SourceRepoUpdateDiffOperationFileRenameOperation",
    "SourceRepoUpdateGit",
]


class RepoUpdateParams(TypedDict, total=False):
    metadata: Optional[Dict[str, str]]

    source: Optional[Source]
    """Snapshot-style repository update.

    Treat the provided `files` list as the complete authoritative set of tracked
    text files. Any previously tracked file that is not present in the list will be
    deleted. Each listed file is created or overwritten.

    This mirrors the semantics of replacing the working tree with exactly the
    supplied set (excluding ignored/untracked items). Binary files are skipped
    downstream during embedding.

    Attributes: type: Discriminator literal `"files"`. files: List of files that
    should exist after the operation.
    """


class SourceRepoUpdateFiles(TypedDict, total=False):
    files: Required[Iterable[FileParam]]

    type: Required[Literal["files"]]


class SourceRepoUpdateDiffOperationFileWriteOperation(TypedDict, total=False):
    content: Required[str]

    filename: Required[str]

    type: Required[Literal["write"]]


class SourceRepoUpdateDiffOperationFileDeleteOperation(TypedDict, total=False):
    filename: Required[str]

    type: Required[Literal["delete"]]


class SourceRepoUpdateDiffOperationFileRenameOperation(TypedDict, total=False):
    new_filename: Required[str]

    old_filename: Required[str]

    type: Required[Literal["rename"]]


SourceRepoUpdateDiffOperation: TypeAlias = Union[
    SourceRepoUpdateDiffOperationFileWriteOperation,
    SourceRepoUpdateDiffOperationFileDeleteOperation,
    SourceRepoUpdateDiffOperationFileRenameOperation,
]


class SourceRepoUpdateDiff(TypedDict, total=False):
    operations: Required[Iterable[SourceRepoUpdateDiffOperation]]

    type: Required[Literal["diff"]]


class SourceRepoUpdateGit(TypedDict, total=False):
    type: Required[Literal["git"]]

    url: Required[str]

    branch: Optional[str]


Source: TypeAlias = Union[SourceRepoUpdateFiles, SourceRepoUpdateDiff, SourceRepoUpdateGit]
