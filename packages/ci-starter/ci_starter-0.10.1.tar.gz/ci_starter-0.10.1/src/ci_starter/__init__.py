from collections.abc import Mapping
from importlib.metadata import version as get_version
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from .constants import BASE_WORKFLOW_ASSET_PATH, HELPER_SCRIPT_ASSET_PATH
from .git_helpers import get_repo_name
from .presets import DISTRIBUTION_ARTIFACTS_DIR, LOCKFILE_ARTIFACT
from .semantic_release_config import SemanticReleaseConfiguration
from .utils import dump, from_yaml, get_actions, get_asset, update_step_data

if TYPE_CHECKING:
    from .action import Action

__version__ = get_version(__package__)

logger = getLogger(__name__)


def generate_semantic_release_config(project_repo_path: Path) -> None:
    repo_name = get_repo_name(project_repo_path)

    config = SemanticReleaseConfiguration(
        project_repo_path, LOCKFILE_ARTIFACT, repo_name, DISTRIBUTION_ARTIFACTS_DIR
    )
    config.write()


def generate_helper_script() -> str:
    script: str = get_asset(HELPER_SCRIPT_ASSET_PATH)
    return script


def generate_base_workflow(**kwargs: Mapping[str, str]) -> dict:
    workflow: str = get_asset(BASE_WORKFLOW_ASSET_PATH)
    yaml = from_yaml(workflow)

    env_dict = {k.upper(): v for k, v in kwargs.items()}
    yaml["env"].update(env_dict)

    return yaml


def generate_reusable_workflow(asset_path: Path) -> dict:
    workflow: str = get_asset(asset_path)
    yaml = from_yaml(workflow)
    return yaml


def update_actions(workflows_path: Path) -> None:
    actions: dict[str, Action] = {}

    for file in workflows_path.rglob("*.yml"):
        data = from_yaml(file)

        for action in get_actions(data):
            if action.name not in actions:
                action.update()
                actions[action.name] = action
            updated_action = actions[action.name]

            data = update_step_data(data, updated_action)

        dump(data, file)
