from enum import Enum


class EnvironmentObjectMetricsExportExporterType(str, Enum):
    PROMETHEUS = "PROMETHEUS"

    def __str__(self) -> str:
        return str(self.value)
