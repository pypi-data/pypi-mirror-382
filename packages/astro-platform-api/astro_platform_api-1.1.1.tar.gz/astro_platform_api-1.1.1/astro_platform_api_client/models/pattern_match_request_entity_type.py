from enum import Enum


class PatternMatchRequestEntityType(str, Enum):
    DAG_ID = "DAG_ID"
    TASK_ID = "TASK_ID"

    def __str__(self) -> str:
        return str(self.value)
