from arize.constants.config import ENV_API_KEY


class MissingAPIKeyError(Exception):
    def __init__(self, message: str = ""):
        self.message = message

    def __str__(self) -> str:
        return self.message or self._default_message()

    @staticmethod
    def _default_message() -> str:
        return f"Missing API key: Set '{ENV_API_KEY}' environment variable or pass api_key explicitly"
