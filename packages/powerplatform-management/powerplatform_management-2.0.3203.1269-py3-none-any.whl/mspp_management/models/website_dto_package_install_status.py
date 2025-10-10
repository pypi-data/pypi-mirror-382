from enum import Enum

class WebsiteDto_packageInstallStatus(str, Enum):
    None_ = "None",
    Installed = "Installed",
    Uninstalled = "Uninstalled",
    InstallRequested = "InstallRequested",
    UninstallRequested = "UninstallRequested",
    InstallFailed = "InstallFailed",
    UninstallFailed = "UninstallFailed",
    Installing = "Installing",
    Uninstalling = "Uninstalling",
    InstallScheduled = "InstallScheduled",
    InstallRetrying = "InstallRetrying",
    TemplateInstalled = "TemplateInstalled",

