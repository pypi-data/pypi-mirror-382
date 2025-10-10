from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .allowed_ip_addresses_configuration_allowed_ip_addresses import AllowedIpAddressesConfiguration_AllowedIpAddresses

@dataclass
class AllowedIpAddressesConfiguration(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The AllowedIpAddresses property
    allowed_ip_addresses: Optional[list[AllowedIpAddressesConfiguration_AllowedIpAddresses]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AllowedIpAddressesConfiguration:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AllowedIpAddressesConfiguration
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AllowedIpAddressesConfiguration()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .allowed_ip_addresses_configuration_allowed_ip_addresses import AllowedIpAddressesConfiguration_AllowedIpAddresses

        from .allowed_ip_addresses_configuration_allowed_ip_addresses import AllowedIpAddressesConfiguration_AllowedIpAddresses

        fields: dict[str, Callable[[Any], None]] = {
            "AllowedIpAddresses": lambda n : setattr(self, 'allowed_ip_addresses', n.get_collection_of_object_values(AllowedIpAddressesConfiguration_AllowedIpAddresses)),
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
        writer.write_collection_of_object_values("AllowedIpAddresses", self.allowed_ip_addresses)
        writer.write_additional_data_value(self.additional_data)
    

