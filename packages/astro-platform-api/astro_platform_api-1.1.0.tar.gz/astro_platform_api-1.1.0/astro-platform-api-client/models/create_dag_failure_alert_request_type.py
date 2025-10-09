from enum import Enum


class CreateDagFailureAlertRequestType(str, Enum):
    DAG_DURATION = "DAG_DURATION"
    DAG_FAILURE = "DAG_FAILURE"
    DAG_SUCCESS = "DAG_SUCCESS"
    DAG_TIMELINESS = "DAG_TIMELINESS"
    TASK_DURATION = "TASK_DURATION"
    TASK_FAILURE = "TASK_FAILURE"

    def __str__(self) -> str:
        return str(self.value)
