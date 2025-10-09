from enum import Enum


class CreateEnvironmentObjectMetricsExportRequestExporterType(str, Enum):
    PROMETHEUS = "PROMETHEUS"

    def __str__(self) -> str:
        return str(self.value)
