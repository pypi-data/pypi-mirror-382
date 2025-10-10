from enum import Enum

class WebsiteDto_status(str, Enum):
    OperationComplete = "OperationComplete",
    OperationInProgress = "OperationInProgress",
    OperationNotStarted = "OperationNotStarted",
    OperationFailed = "OperationFailed",

