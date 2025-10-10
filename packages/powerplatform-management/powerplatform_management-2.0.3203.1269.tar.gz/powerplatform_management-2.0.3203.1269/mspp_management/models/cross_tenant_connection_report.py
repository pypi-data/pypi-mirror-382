from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .cross_tenant_connection import CrossTenantConnection
    from .cross_tenant_connection_report_status import CrossTenantConnectionReport_status

@dataclass
class CrossTenantConnectionReport(Parsable):
    # The page of cross-tenant connections occurring within the report date window.
    connections: Optional[list[CrossTenantConnection]] = None
    # The end of the report date window.
    end_date: Optional[datetime.datetime] = None
    # The URI of the next page of the report containing additional cross-tenant connections.
    odata_next_link: Optional[str] = None
    # The report ID.
    report_id: Optional[UUID] = None
    # The date when the cross-tenant connection report was requested.
    request_date: Optional[datetime.datetime] = None
    # The start of the report date window.
    start_date: Optional[datetime.datetime] = None
    # The status property
    status: Optional[CrossTenantConnectionReport_status] = None
    # The Azure AD tenant ID for which the report was generated.
    tenant_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CrossTenantConnectionReport:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CrossTenantConnectionReport
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CrossTenantConnectionReport()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .cross_tenant_connection import CrossTenantConnection
        from .cross_tenant_connection_report_status import CrossTenantConnectionReport_status

        from .cross_tenant_connection import CrossTenantConnection
        from .cross_tenant_connection_report_status import CrossTenantConnectionReport_status

        fields: dict[str, Callable[[Any], None]] = {
            "connections": lambda n : setattr(self, 'connections', n.get_collection_of_object_values(CrossTenantConnection)),
            "endDate": lambda n : setattr(self, 'end_date', n.get_datetime_value()),
            "@odata.nextLink": lambda n : setattr(self, 'odata_next_link', n.get_str_value()),
            "reportId": lambda n : setattr(self, 'report_id', n.get_uuid_value()),
            "requestDate": lambda n : setattr(self, 'request_date', n.get_datetime_value()),
            "startDate": lambda n : setattr(self, 'start_date', n.get_datetime_value()),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(CrossTenantConnectionReport_status)),
            "tenantId": lambda n : setattr(self, 'tenant_id', n.get_uuid_value()),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        writer.write_collection_of_object_values("connections", self.connections)
        writer.write_datetime_value("endDate", self.end_date)
        writer.write_str_value("@odata.nextLink", self.odata_next_link)
        writer.write_uuid_value("reportId", self.report_id)
        writer.write_datetime_value("requestDate", self.request_date)
        writer.write_datetime_value("startDate", self.start_date)
        writer.write_enum_value("status", self.status)
        writer.write_uuid_value("tenantId", self.tenant_id)
    

