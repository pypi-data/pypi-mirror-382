class MissingProjectNameError(Exception):
    def __init__(self, message: str = ""):
        self.message = message

    def __str__(self) -> str:
        return self.message or self._default_message()

    @staticmethod
    def _default_message() -> str:
        return "Missing Project Name: pass project_name explicitly"


class MissingModelNameError(Exception):
    def __init__(self, message: str = ""):
        self.message = message

    def __str__(self) -> str:
        return self.message or self._default_message()

    @staticmethod
    def _default_message() -> str:
        return "Missing Model Name: pass model name explicitly"
