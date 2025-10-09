from enum import Enum


class PatternMatchRequestOperatorType(str, Enum):
    EXCLUDES = "EXCLUDES"
    INCLUDES = "INCLUDES"
    IS = "IS"
    IS_NOT = "IS_NOT"

    def __str__(self) -> str:
        return str(self.value)
