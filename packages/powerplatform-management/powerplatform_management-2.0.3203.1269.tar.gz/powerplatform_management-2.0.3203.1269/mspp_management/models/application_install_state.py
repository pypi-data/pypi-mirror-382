from enum import Enum

class ApplicationInstallState(str, Enum):
    All = "All",
    Installed = "Installed",
    NotInstalled = "NotInstalled",

