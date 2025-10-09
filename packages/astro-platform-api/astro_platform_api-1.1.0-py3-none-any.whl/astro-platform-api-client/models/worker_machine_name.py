from enum import Enum


class WorkerMachineName(str, Enum):
    A10 = "A10"
    A120 = "A120"
    A160 = "A160"
    A20 = "A20"
    A40 = "A40"
    A5 = "A5"
    A60 = "A60"

    def __str__(self) -> str:
        return str(self.value)
