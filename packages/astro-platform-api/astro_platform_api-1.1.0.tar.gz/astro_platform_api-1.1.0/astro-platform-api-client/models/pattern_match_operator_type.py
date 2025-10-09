from enum import Enum


class PatternMatchOperatorType(str, Enum):
    IS_IS_NOT_INCLUDES_EXCLUDES = "IS IS_NOT INCLUDES EXCLUDES"

    def __str__(self) -> str:
        return str(self.value)
