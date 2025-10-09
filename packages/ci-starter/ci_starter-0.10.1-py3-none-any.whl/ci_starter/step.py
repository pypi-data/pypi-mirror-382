from collections.abc import Callable, Hashable, Mapping
from copy import deepcopy
from typing import Any, ClassVar, Self

from ruamel.yaml.comments import Comment, CommentedMap, comment_attrib
from ruamel.yaml.constructor import Constructor
from ruamel.yaml.nodes import MappingNode
from ruamel.yaml.representer import Representer
from ruamel.yaml.tokens import CommentToken
from semver import VersionInfo

from ci_starter.action import Action


class Step(Mapping, Hashable):
    yaml_tag: ClassVar[str] = "!step"
    version_comment_start = "# v"

    def __init__(self, **kwargs) -> None:
        comment = kwargs.pop("comment")
        setattr(self, comment_attrib, comment)

        # store original kwargs to preserve item order when dumping
        self._kwargs = kwargs

        action_text = kwargs.get("uses")
        version_string = self.comment_string.removeprefix(self.version_comment_start)
        version = VersionInfo.parse(version_string)
        self._uses = Action.from_text(action_text, version=version)

        for k, v in kwargs.items():
            if k != "uses":
                setattr(self, k, v)

    @property
    def comment_string(self) -> str:
        string = self.comment_token.value.strip()
        return string

    @comment_string.setter
    def comment_string(self, new_string: str) -> None:
        comment = self.get_comment_object()
        comment._items["uses"][2].value = f"{new_string}\n"

    def get_comment_object(self) -> Comment:
        comment = getattr(self, comment_attrib)
        return comment

    @property
    def comment_token(self) -> CommentToken:
        comment = self.get_comment_object()
        token: CommentToken = comment.items["uses"][2]
        return token

    @property
    def uses(self) -> Action:
        return self._uses

    @uses.setter
    def uses(self, action: Action) -> None:
        assert isinstance(action, Action), "uses must be set with an Action instance"

        current_action_text_length = len(action)
        previous_action_text_length = len(self.uses)
        shift_of_comment_start_column = current_action_text_length - previous_action_text_length

        self._uses = action
        self.comment_start_column += shift_of_comment_start_column
        self.comment_string = f"{self.version_comment_start}{action.version}"

    @property
    def comment_start_column(self) -> int:
        comment = self.get_comment_object()
        column: int = comment._items["uses"][2].column
        return column

    @comment_start_column.setter
    def comment_start_column(self, value) -> None:
        comment = self.get_comment_object()
        comment._items["uses"][2].column = value

    @property
    def dict(self) -> dict:
        result = deepcopy(self._kwargs)
        result["uses"] = self.uses.to_text()
        return result

    @property
    def items(self) -> Callable:
        return self.dict.items

    @classmethod
    def from_yaml(cls, constructor: Constructor, node: MappingNode) -> Self:
        comment = cls.get_action_comment(node)
        commented_map = CommentedMap()
        constructor.construct_mapping(node, maptyp=commented_map, deep=False)
        return cls(**commented_map, comment=comment)

    @classmethod
    def get_action_comment(cls, node: MappingNode) -> list[CommentToken | None]:
        f = filter(lambda tupl: tupl[0].value == "uses", node.value)
        _, scalar_node = next(f)
        comments: list[CommentToken | None] = scalar_node.comment
        comment = Comment()
        comment._items = {"uses": [None, None, *comments]}
        return comment

    @classmethod
    def to_yaml(cls, representer: Representer, node: Self) -> MappingNode:
        tag = cls.yaml_tag
        result = representer.represent_mapping(tag, node)
        return result

    def __repr__(self) -> str:
        attrs = ", ".join((f"{k}={v}" for k, v in self.dict.items()))
        result = f"{self.__class__.__name__}({attrs})"
        return result

    def __getitem__(self, key) -> Any:
        return self.dict[key]

    def __iter__(self) -> tuple[str, Any]:
        return self.dict.items

    def __len__(self) -> int:
        return len(self.dict)

    def __hash__(self) -> int:
        return hash(self.uses.to_text())
