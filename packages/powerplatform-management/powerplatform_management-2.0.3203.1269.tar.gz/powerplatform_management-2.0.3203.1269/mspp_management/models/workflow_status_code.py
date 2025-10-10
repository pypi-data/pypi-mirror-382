from enum import Enum

class WorkflowStatusCode(str, Enum):
    Default = "Default",
    Draft = "Draft",
    Published = "Published",
    CompanyDLPViolation = "CompanyDLPViolation",
    Quarantined = "Quarantined",

