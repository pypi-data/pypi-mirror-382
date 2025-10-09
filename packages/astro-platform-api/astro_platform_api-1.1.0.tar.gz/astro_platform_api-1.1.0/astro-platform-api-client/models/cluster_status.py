from enum import Enum


class ClusterStatus(str, Enum):
    ACCESS_DENIED = "ACCESS_DENIED"
    CREATED = "CREATED"
    CREATE_FAILED = "CREATE_FAILED"
    CREATING = "CREATING"
    UPDATE_FAILED = "UPDATE_FAILED"
    UPDATING = "UPDATING"
    UPGRADE_PENDING = "UPGRADE_PENDING"

    def __str__(self) -> str:
        return str(self.value)
