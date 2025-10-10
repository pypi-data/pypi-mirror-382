from enum import Enum

class PortalScanIssues_category(str, Enum):
    ProvisioningIssues = "Provisioning issues",
    ConfigurationIssues = "Configuration Issues",
    PortalStartupIssue = "Portal Startup Issue",
    Performance = "Performance",
    Security = "Security",

