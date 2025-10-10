from enum import Enum

class CrossTenantConnectionReport_status(str, Enum):
    Received = "Received",
    InProgress = "InProgress",
    Completed = "Completed",
    Failed = "Failed",

