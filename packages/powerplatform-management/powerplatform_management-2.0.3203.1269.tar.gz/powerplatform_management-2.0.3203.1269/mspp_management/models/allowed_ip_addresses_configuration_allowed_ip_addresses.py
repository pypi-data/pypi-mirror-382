from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .ip_address_type import IpAddressType

@dataclass
class AllowedIpAddressesConfiguration_AllowedIpAddresses(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The creation timestamp of the IP address entry
    created_on: Optional[datetime.datetime] = None
    # The IP address or CIDR range
    ip_address: Optional[str] = None
    # The type of the IP address
    ip_type: Optional[IpAddressType] = None
    # The LastModifiedOn property
    last_modified_on: Optional[str] = None
    # The unique identifier of the tenant
    tenant_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AllowedIpAddressesConfiguration_AllowedIpAddresses:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AllowedIpAddressesConfiguration_AllowedIpAddresses
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AllowedIpAddressesConfiguration_AllowedIpAddresses()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .ip_address_type import IpAddressType

        from .ip_address_type import IpAddressType

        fields: dict[str, Callable[[Any], None]] = {
            "CreatedOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "IpAddress": lambda n : setattr(self, 'ip_address', n.get_str_value()),
            "IpType": lambda n : setattr(self, 'ip_type', n.get_enum_value(IpAddressType)),
            "LastModifiedOn": lambda n : setattr(self, 'last_modified_on', n.get_str_value()),
            "TenantId": lambda n : setattr(self, 'tenant_id', n.get_uuid_value()),
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
        writer.write_datetime_value("CreatedOn", self.created_on)
        writer.write_str_value("IpAddress", self.ip_address)
        writer.write_enum_value("IpType", self.ip_type)
        writer.write_str_value("LastModifiedOn", self.last_modified_on)
        writer.write_uuid_value("TenantId", self.tenant_id)
        writer.write_additional_data_value(self.additional_data)
    

