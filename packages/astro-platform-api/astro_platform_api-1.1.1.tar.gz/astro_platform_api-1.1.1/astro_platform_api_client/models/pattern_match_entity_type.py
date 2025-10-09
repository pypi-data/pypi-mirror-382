from enum import Enum


class PatternMatchEntityType(str, Enum):
    DAG_ID_TASK_ID = "DAG_ID TASK_ID"

    def __str__(self) -> str:
        return str(self.value)
