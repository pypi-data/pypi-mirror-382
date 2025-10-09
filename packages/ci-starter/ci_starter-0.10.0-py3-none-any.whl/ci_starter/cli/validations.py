from logging import getLogger
from pathlib import Path

from click import BadParameter, Context, Parameter, echo

logger = getLogger(__name__)


def report(msg: str) -> None:
    echo(msg)
    logger.debug(msg)


def validate_workflow_file_name(_ctx: Context, _param: Parameter, path: Path) -> Path:
    if path.suffix != ".yml":
        report("Correcting workflow file suffix to .yml")
        path = path.with_suffix(".yml")
    return path


def validate_test_group(_ctx: Context, _param: Parameter, s: str) -> str:
    try:
        assert s.isidentifier()
        assert not s.startswith("_")
        return s
    except AssertionError as err:
        raise BadParameter("must be an identifier and not start with '_'") from err
