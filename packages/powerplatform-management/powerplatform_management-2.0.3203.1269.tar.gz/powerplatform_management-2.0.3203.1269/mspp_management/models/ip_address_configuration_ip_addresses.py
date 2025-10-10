from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .ip_address_type import IpAddressType

@dataclass
class IpAddressConfiguration_IpAddresses(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The IP address or CIDR range
    ip_address: Optional[str] = None
    # The type of the IP address
    ip_address_type: Optional[IpAddressType] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IpAddressConfiguration_IpAddresses:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IpAddressConfiguration_IpAddresses
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IpAddressConfiguration_IpAddresses()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .ip_address_type import IpAddressType

        from .ip_address_type import IpAddressType

        fields: dict[str, Callable[[Any], None]] = {
            "IpAddress": lambda n : setattr(self, 'ip_address', n.get_str_value()),
            "IpAddressType": lambda n : setattr(self, 'ip_address_type', n.get_enum_value(IpAddressType)),
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
        writer.write_str_value("IpAddress", self.ip_address)
        writer.write_enum_value("IpAddressType", self.ip_address_type)
        writer.write_additional_data_value(self.additional_data)
    

