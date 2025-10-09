from dataclasses import InitVar, dataclass, field


@dataclass
class Placeholder:
    name: InitVar[str]
    value: str
    placeholder: str = field(init=False)

    def __post_init__(self, name):
        self.placeholder = f"PLACEHOLDER_{name.replace(' ', '_').upper()}"
