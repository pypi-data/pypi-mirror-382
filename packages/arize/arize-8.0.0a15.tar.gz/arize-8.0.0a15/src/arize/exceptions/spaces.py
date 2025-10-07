class MissingSpaceIDError(Exception):
    def __init__(self, message: str = ""):
        self.message = message

    def __str__(self) -> str:
        return self.message or self._default_message()

    @staticmethod
    def _default_message() -> str:
        return "Missing Space ID: pass space_id explicitly"
