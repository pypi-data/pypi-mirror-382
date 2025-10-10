from enum import Enum

class PortalScanIssues_result(str, Enum):
    Pass_ = "Pass",
    Warning = "Warning",
    Error = "Error",

