from enum import Enum


class BasicSubjectProfileSubjectType(str, Enum):
    SERVICEKEY = "SERVICEKEY"
    USER = "USER"

    def __str__(self) -> str:
        return str(self.value)
