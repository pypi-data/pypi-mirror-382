from enum import Enum


class Env(str, Enum):
    """Environment variable keys."""

    WHODAT_SERVICE_URL = "WHODAT_SERVICE_URL"
    WHODAT_SERVICE_AUTH_TOKEN = "WHODAT_SERVICE_AUTH_TOKEN"

    def __str__(self) -> str:
        """Use value for string representation."""
        return str(self.value)
