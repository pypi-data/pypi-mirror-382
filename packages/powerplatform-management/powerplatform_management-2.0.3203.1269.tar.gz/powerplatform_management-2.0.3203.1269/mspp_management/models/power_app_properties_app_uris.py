from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .power_app_properties_app_uris_document_uri import PowerApp_properties_appUris_documentUri

@dataclass
class PowerApp_properties_appUris(AdditionalDataHolder, Parsable):
    """
    PowerApp appUri object.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # PowerApp appUri document URI object.
    document_uri: Optional[PowerApp_properties_appUris_documentUri] = None
    # PowerApp appUri image URI array.
    image_uris: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PowerApp_properties_appUris:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PowerApp_properties_appUris
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PowerApp_properties_appUris()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .power_app_properties_app_uris_document_uri import PowerApp_properties_appUris_documentUri

        from .power_app_properties_app_uris_document_uri import PowerApp_properties_appUris_documentUri

        fields: dict[str, Callable[[Any], None]] = {
            "documentUri": lambda n : setattr(self, 'document_uri', n.get_object_value(PowerApp_properties_appUris_documentUri)),
            "imageUris": lambda n : setattr(self, 'image_uris', n.get_collection_of_primitive_values(str)),
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
        writer.write_object_value("documentUri", self.document_uri)
        writer.write_collection_of_primitive_values("imageUris", self.image_uris)
        writer.write_additional_data_value(self.additional_data)
    

