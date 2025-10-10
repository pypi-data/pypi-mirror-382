from enum import Enum

class CrossTenantConnection_connectionType(str, Enum):
    Inbound = "Inbound",
    Outbound = "Outbound",

