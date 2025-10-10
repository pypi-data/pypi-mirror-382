from enum import Enum

class WorkflowStateCode(str, Enum):
    Draft = "Draft",
    Published = "Published",
    Suspended = "Suspended",

