import logging
import subprocess
from typing import List, Union, Optional

from ._client import Relace

logger = logging.getLogger(__name__)


def ensure_git_available() -> None:
    try:
        subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as exc:
        raise RuntimeError("Git CLI is not installed or not found in PATH.") from exc


class GitHelper:
    def __init__(self, client: Relace, root_path: str) -> None:
        self.client = client
        self.root_path = root_path

    def clone(self, repo_id: str, depth: int = 1, branch: Optional[str] = None, quiet: bool = True, *args: str) -> None:
        if not self.root_path:
            raise ValueError("No repository path provided. Please specify in git() parameter")

        branch_arg = ["-b", branch] if branch else []
        quiet_arg = ["--quiet"] if quiet else []
        extra_args = list(args)

        api_token = self.client.api_key
        repo_url = f"https://token:{api_token}@api.relace.run/v1/repo/{repo_id}.git"

        ensure_git_available()
        cmd = ["git", "clone", "--depth", str(depth)] + branch_arg + quiet_arg + extra_args + [repo_url, self.root_path]

        subprocess.run(cmd, check=True)
        logger.info("Repository cloned successfully!")

    def stage(self, files: Union[str, List[str]] = ".") -> "GitHelper":
        if not self.root_path:
            raise ValueError("No repository path provided. Please specify in git() parameter")

        files_arg = files if isinstance(files, str) else " ".join(files)

        ensure_git_available()
        subprocess.run(["git", "-C", self.root_path, "add"] + files_arg.split(), check=True)

        return self

    def commit(self, message: str) -> "GitHelper":
        if not self.root_path:
            raise ValueError("No repository path provided. Please specify in git() parameter")

        if not message:
            raise ValueError("Please specify a commit message")

        ensure_git_available()
        subprocess.run(["git", "-C", self.root_path, "commit", "-m", message], check=True)

        return self

    def push(self) -> None:
        if not self.root_path:
            raise ValueError("No repository path provided. Please specify in git")

        ensure_git_available()
        subprocess.run(["git", "-C", self.root_path, "push"], check=True)


def attach_git_support() -> None:
    def git(self: "Relace", root_path: str) -> "GitHelper":
        return GitHelper(self, root_path)

    Relace.git = git  # type: ignore[attr-defined]
