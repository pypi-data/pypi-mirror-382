from pathlib import Path

from git import Remote, Repo

from .errors import RemoteNotFoundError


def get_remote(repo: Repo) -> Remote:
    try:
        remote = next(iter(repo.remotes))
        return remote
    except StopIteration as exception:
        raise RemoteNotFoundError from exception


def get_repo_name(project_path: Path) -> str:
    repo = Repo(project_path)
    remote = get_remote(repo)
    url = remote.url
    last_part = url.split("/")[-1]
    repo_name = last_part.removesuffix(".git")
    return repo_name
