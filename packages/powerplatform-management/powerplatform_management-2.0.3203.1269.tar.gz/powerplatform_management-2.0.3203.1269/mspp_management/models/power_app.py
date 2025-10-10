from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .power_app_properties import PowerApp_properties
    from .power_app_tags import PowerApp_tags

@dataclass
class PowerApp(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # PowerApp ID field.
    id: Optional[str] = None
    # PowerApp name field.
    name: Optional[str] = None
    # PowerApp properties object.
    properties: Optional[PowerApp_properties] = None
    # tags
    tags: Optional[PowerApp_tags] = None
    # PowerApp type field.
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PowerApp:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PowerApp
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PowerApp()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .power_app_properties import PowerApp_properties
        from .power_app_tags import PowerApp_tags

        from .power_app_properties import PowerApp_properties
        from .power_app_tags import PowerApp_tags

        fields: dict[str, Callable[[Any], None]] = {
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "properties": lambda n : setattr(self, 'properties', n.get_object_value(PowerApp_properties)),
            "tags": lambda n : setattr(self, 'tags', n.get_object_value(PowerApp_tags)),
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
        writer.write_object_value("tags", self.tags)
        writer.write_str_value("type", self.type)
        writer.write_additional_data_value(self.additional_data)
    

