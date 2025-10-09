class CiStarterError(Exception):
    code = -1


class RemoteNotFoundError(CiStarterError):
    code = 3

    def __str__(self):
        return "could not find any remote in the repository"


class ActionNotParsableError(CiStarterError):
    code = 4

    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return f"could not parse action '{self.value}'"
