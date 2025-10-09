from pathlib import Path

from tomli_w import dumps

from .contracts import AbstractManagedFile
from .presets import ENCODING, SEMANTIC_RELEASE_CONFIG_FILE, WORKFLOWS_DIR


class ManagedFileBase(AbstractManagedFile):
    @property
    def path(self) -> Path:
        return self.base_dir / self.name

    def write(self) -> None:
        with self.path.open("wb") as file:
            file.write(self.content)


class SemanticReleaseConfigurationBase(ManagedFileBase):
    @classmethod
    @property
    def name(cls) -> str:
        return SEMANTIC_RELEASE_CONFIG_FILE

    @property
    def base_dir(self) -> Path:
        return self.repo_dir

    @property
    def content(self) -> bytes:
        result = dumps(self.toml_dict, multiline_strings=True).encode(ENCODING)
        return result

    @property
    def toml_dict(self) -> dict:
        raise NotImplementedError()

    @property
    def repo_dir(self) -> Path:
        raise NotImplementedError()


class WorkflowFileBase(ManagedFileBase):
    @property
    def repo_dir(self):
        raise NotImplementedError()

    @property
    def base_dir(self):
        return self.repo_dir / WORKFLOWS_DIR
