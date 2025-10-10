from enum import Enum

class WebApplicationFirewallStatus(str, Enum):
    None_ = "None",
    Creating = "Creating",
    Deleting = "Deleting",
    Created = "Created",
    CreationFailed = "CreationFailed",
    DeletionFailed = "DeletionFailed",

