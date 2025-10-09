from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class OwnerRepo:
    owner: str
    repo: str


@dataclass(eq=True, frozen=True)
class CommitVersion:
    commit: str
    version: str
