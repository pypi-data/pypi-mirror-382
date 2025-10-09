from abc import ABC, abstractmethod
from pathlib import Path


class AbstractManagedFile(ABC):
    @classmethod
    @property
    @abstractmethod
    def name(cls) -> str: ...

    @property
    @abstractmethod
    def path(self) -> Path: ...

    @property
    @abstractmethod
    def repo_dir(self) -> Path: ...

    @property
    @abstractmethod
    def base_dir(self) -> Path: ...

    @property
    @abstractmethod
    def content(self): ...

    @abstractmethod
    def write(self): ...
