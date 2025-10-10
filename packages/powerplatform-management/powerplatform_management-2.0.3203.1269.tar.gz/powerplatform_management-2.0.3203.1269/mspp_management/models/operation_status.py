from enum import Enum

class OperationStatus(str, Enum):
    Queued = "Queued",
    InProgress = "InProgress",
    Succeeded = "Succeeded",
    ValidationFailed = "ValidationFailed",
    Failed = "Failed",
    NoOperation = "NoOperation",
    ValidationPassed = "ValidationPassed",

