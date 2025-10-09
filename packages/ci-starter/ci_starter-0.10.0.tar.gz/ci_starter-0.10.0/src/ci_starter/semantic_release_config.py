from collections.abc import Iterable
from pathlib import Path
from tomllib import loads

from .bases import SemanticReleaseConfigurationBase
from .placeholder import Placeholder
from .utils import get_asset


class SemanticReleaseConfiguration(SemanticReleaseConfigurationBase):
    @staticmethod
    def get_configuration_toml_template() -> str:
        sr_config_asset: str = get_asset("toml/semantic-release.toml")
        return sr_config_asset

    @staticmethod
    def replace_placeholders(s: str, placeholders: Iterable[Placeholder]) -> str:
        for placeholder in placeholders:
            s = s.replace(placeholder.placeholder, placeholder.value)
        return s

    def __init__(
        self, repo_dir: Path, lockfile_artifact: str, repo_name: str, distribution_artifacts_dir: str
    ) -> None:
        self._repo_dir: Path = repo_dir

        toml_template: str = self.get_configuration_toml_template()
        placeholders: Iterable[Placeholder] = (
            Placeholder("lockfile artifact", lockfile_artifact),
            Placeholder("repo name", repo_name),
            Placeholder("distribution artifacts dir", distribution_artifacts_dir),
        )

        self.configuration_toml_str: str = self.replace_placeholders(toml_template, placeholders)

    @property
    def repo_dir(self) -> Path:
        return self._repo_dir

    @property
    def toml_dict(self) -> dict:
        return loads(self.configuration_toml_str)
