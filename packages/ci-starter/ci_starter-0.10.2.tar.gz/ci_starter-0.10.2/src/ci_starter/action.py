from os import getenv
from re import compile
from typing import Self

from requests import get
from semver.version import Version

from .errors import ActionNotParsableError


class Action:
    PATTERN = compile(r"(?P<owner>[\w_-]+)/(?P<repo>[\w_-]+)@(?P<commit>[\S]+)")
    TOKEN = getenv("CI_STARTER_GH_API_TOKEN")

    def __init__(self, owner: str, repo: str, commit: str, version: Version | None = None) -> None:
        self.owner: str = owner
        self.repo: str = repo
        self.commit: str = commit
        self.version: Version = version

    @property
    def name(self) -> str:
        return f"{self.owner}/{self.repo}"

    def to_text(self) -> str:
        return f"{self.name}@{self.commit}"

    @classmethod
    def from_text(cls, text: str, version: Version | None = None) -> Self:
        match = cls.PATTERN.search(text)
        if not match:
            raise ActionNotParsableError(text)

        action = cls(**match.groupdict(), version=version)

        return action

    def update(self) -> None:
        response = get(self.url, headers=self.header)
        if not response.ok:
            response.raise_for_status()

        data = response.json()
        current_release = data[0]

        current_version = current_release["name"].removeprefix("v")
        current_commit = current_release["commit"]["sha"]

        self.version = Version.parse(current_version)
        self.commit = current_commit

    def update_from_other(self, other: Self) -> None:
        if not self.name == other.name:
            raise ValueError(
                f"can update only from an {self.__class__.__name__} "
                f"of name '{self.name}', not '{other.name}'"
            )
        self.commit = other.commit
        self.version = other.version

    @property
    def url(self) -> str:
        return f"https://api.github.com/repos/{self.owner}/{self.repo}/tags"

    @property
    def header(self) -> dict[str, str]:
        result = {
            "User-Agent": __package__,
            "Accept": "application.vnd.github+json",
        }
        if self.TOKEN:
            result.update(Authorization=f"Bearer {self.TOKEN}")
        return result

    def __repr__(self) -> str:
        string = (
            f"{self.__class__.__name__}(owner={self.owner}, repo={self.repo}, "
            f"commit={self.commit}, version={self.version})"
        )
        return string

    def __len__(self) -> int:
        return len(self.to_text())
