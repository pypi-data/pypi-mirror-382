from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .get_connector_by_id_response_properties_metadata_version import GetConnectorByIdResponse_properties_metadata_version

@dataclass
class GetConnectorByIdResponse_properties_metadata(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The allowSharing property
    allow_sharing: Optional[bool] = None
    # The brandColor property
    brand_color: Optional[str] = None
    # The source property
    source: Optional[str] = None
    # The useNewApimVersion property
    use_new_apim_version: Optional[str] = None
    # The version property
    version: Optional[GetConnectorByIdResponse_properties_metadata_version] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> GetConnectorByIdResponse_properties_metadata:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: GetConnectorByIdResponse_properties_metadata
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return GetConnectorByIdResponse_properties_metadata()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .get_connector_by_id_response_properties_metadata_version import GetConnectorByIdResponse_properties_metadata_version

        from .get_connector_by_id_response_properties_metadata_version import GetConnectorByIdResponse_properties_metadata_version

        fields: dict[str, Callable[[Any], None]] = {
            "allowSharing": lambda n : setattr(self, 'allow_sharing', n.get_bool_value()),
            "brandColor": lambda n : setattr(self, 'brand_color', n.get_str_value()),
            "source": lambda n : setattr(self, 'source', n.get_str_value()),
            "useNewApimVersion": lambda n : setattr(self, 'use_new_apim_version', n.get_str_value()),
            "version": lambda n : setattr(self, 'version', n.get_object_value(GetConnectorByIdResponse_properties_metadata_version)),
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
        writer.write_bool_value("allowSharing", self.allow_sharing)
        writer.write_str_value("brandColor", self.brand_color)
        writer.write_str_value("source", self.source)
        writer.write_str_value("useNewApimVersion", self.use_new_apim_version)
        writer.write_object_value("version", self.version)
        writer.write_additional_data_value(self.additional_data)
    

