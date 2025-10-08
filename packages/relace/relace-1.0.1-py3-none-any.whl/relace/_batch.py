from typing import Dict, List, Union, Iterable, Optional, cast

from ._types import omit
from ._client import Relace
from .types.repo_info import RepoInfo
from .types.file_param import FileParam
from .types.repo_update_params import (
    SourceRepoUpdateDiff,
    SourceRepoUpdateFiles,
    SourceRepoUpdateDiffOperation,
)


class WriteOperation:
    def __init__(self, filename: str, content: str) -> None:
        self.type = "write"
        self.filename = filename
        self.content = content


class RenameOperation:
    def __init__(self, old_filename: str, new_filename: str) -> None:
        self.type = "rename"
        self.old_filename = old_filename
        self.new_filename = new_filename


class DeleteOperation:
    def __init__(self, filename: str) -> None:
        self.type = "delete"
        self.filename = filename


Operation = Union[WriteOperation, RenameOperation, DeleteOperation]


class BatchDiffUpdate:
    def __init__(self, client: Relace, repo_id: str) -> None:
        self.client = client
        self.repo_id = repo_id
        self.operations: List[Operation] = []

    def write(self, filename: str, content: str) -> "BatchDiffUpdate":
        self.operations.append(WriteOperation(filename, content))
        return self

    def rename(self, old_filename: str, new_filename: str) -> "BatchDiffUpdate":
        self.operations.append(RenameOperation(old_filename, new_filename))
        return self

    def delete(self, filename: str) -> "BatchDiffUpdate":
        self.operations.append(DeleteOperation(filename))
        return self

    def execute(self, metadata: Optional[Dict[str, str]] = None) -> RepoInfo:
        operations = [op.__dict__ for op in self.operations]
        source: SourceRepoUpdateDiff = {
            "type": "diff",
            "operations": cast(Iterable[SourceRepoUpdateDiffOperation], operations),
        }
        return self.client.repo.update(
            self.repo_id,
            source=source,
            metadata=metadata if metadata else omit,
        )


class BatchFilesUpdate:
    def __init__(self, client: Relace, repo_id: str) -> None:
        self.client = client
        self.repo_id = repo_id
        self.files: List[Dict[str, str]] = []
        self.metadata: Optional[Dict[str, str]] = None

    def add_file(self, filename: str, content: str) -> "BatchFilesUpdate":
        self.files.append({"filename": filename, "content": content})
        return self

    def add_files(self, files: List[Dict[str, str]]) -> "BatchFilesUpdate":
        self.files.extend(files)
        return self

    def execute(self, metadata: Optional[Dict[str, str]] = None) -> RepoInfo:
        source: SourceRepoUpdateFiles = {
            "type": "files",
            "files": cast(Iterable[FileParam], self.files),
        }
        return self.client.repo.update(
            self.repo_id,
            source=source,
            metadata=metadata if metadata else omit,
        )


class BatchFilesCreate:
    def __init__(self, client: Relace) -> None:
        self.client = client
        self.files: List[Dict[str, str]] = []
        self.metadata: Optional[Dict[str, str]] = None

    def add_file(self, filename: str, content: str) -> "BatchFilesCreate":
        self.files.append({"filename": filename, "content": content})
        return self

    def add_files(self, files: List[Dict[str, str]]) -> "BatchFilesCreate":
        self.files.extend(files)
        return self

    def set_metadata(self, metadata: Dict[str, str]) -> "BatchFilesCreate":
        self.metadata = metadata
        return self

    def execute(self) -> RepoInfo:
        source: SourceRepoUpdateFiles = {
            "type": "files",
            "files": cast(Iterable[FileParam], self.files),
        }
        return self.client.repo.create(
            source=source,
            metadata=self.metadata if self.metadata else omit,
        )


def attach_batch_update() -> None:
    def batch_diff_update(self: "Relace", repo_id: str) -> BatchDiffUpdate:
        return BatchDiffUpdate(self, repo_id)

    def batch_files_update(self: "Relace", repo_id: str) -> BatchFilesUpdate:
        return BatchFilesUpdate(self, repo_id)

    def batch_files_create(self: "Relace") -> BatchFilesCreate:
        return BatchFilesCreate(self)

    Relace.batch_diff_update = batch_diff_update  # type: ignore[attr-defined]
    Relace.batch_files_update = batch_files_update  # type: ignore[attr-defined]
    Relace.batch_files_create = batch_files_create  # type: ignore[attr-defined]
