from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .get_connector_by_id_response_properties import GetConnectorByIdResponse_properties

@dataclass
class GetConnectorByIdResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The id property
    id: Optional[str] = None
    # The name property
    name: Optional[str] = None
    # The properties property
    properties: Optional[GetConnectorByIdResponse_properties] = None
    # The type property
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetConnectorByIdResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetConnectorByIdResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GetConnectorByIdResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .get_connector_by_id_response_properties import GetConnectorByIdResponse_properties

        from .get_connector_by_id_response_properties import GetConnectorByIdResponse_properties

        fields: dict[str, Callable[[Any], None]] = {
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "properties": lambda n : setattr(self, 'properties', n.get_object_value(GetConnectorByIdResponse_properties)),
            "type": lambda n : setattr(self, 'type', n.get_str_value()),
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
        writer.write_str_value("id", self.id)
        writer.write_str_value("name", self.name)
        writer.write_object_value("properties", self.properties)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

