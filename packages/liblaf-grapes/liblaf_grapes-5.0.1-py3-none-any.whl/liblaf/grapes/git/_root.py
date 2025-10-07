from pathlib import Path

import git
import git.exc

from liblaf.grapes.typing import PathLike


def root(
    path: PathLike | None = None, *, search_parent_directories: bool = True
) -> Path:
    repo = git.Repo(path=path, search_parent_directories=search_parent_directories)
    return Path(repo.working_dir)


def root_or_cwd(
    path: PathLike | None = None, *, search_parent_directories: bool = True
) -> Path:
    try:
        return root(path=path, search_parent_directories=search_parent_directories)
    except git.exc.InvalidGitRepositoryError:
        return Path()
