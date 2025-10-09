from enum import Enum


class EnvironmentObjectObjectType(str, Enum):
    AIRFLOW_VARIABLE = "AIRFLOW_VARIABLE"
    CONNECTION = "CONNECTION"
    METRICS_EXPORT = "METRICS_EXPORT"

    def __str__(self) -> str:
        return str(self.value)
