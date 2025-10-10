from enum import Enum

class InstancePackageOperationStatus(str, Enum):
    NotStarted = "NotStarted",
    Running = "Running",
    Succeeded = "Succeeded",
    Failed = "Failed",
    Canceled = "Canceled",

