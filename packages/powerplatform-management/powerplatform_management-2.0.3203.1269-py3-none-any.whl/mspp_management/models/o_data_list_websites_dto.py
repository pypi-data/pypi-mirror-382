from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .website_dto import WebsiteDto

@dataclass
class ODataListWebsitesDto(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The OdataMetadata property
    odata_metadata: Optional[str] = None
    # The OdataNextLink property
    odata_next_link: Optional[str] = None
    # The value property
    value: Optional[list[WebsiteDto]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ODataListWebsitesDto:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ODataListWebsitesDto
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ODataListWebsitesDto()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .website_dto import WebsiteDto

        from .website_dto import WebsiteDto

        fields: dict[str, Callable[[Any], None]] = {
            "@odata.metadata": lambda n : setattr(self, 'odata_metadata', n.get_str_value()),
            "@odata.nextLink": lambda n : setattr(self, 'odata_next_link', n.get_str_value()),
            "value": lambda n : setattr(self, 'value', n.get_collection_of_object_values(WebsiteDto)),
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
        writer.write_str_value("@odata.metadata", self.odata_metadata)
        writer.write_str_value("@odata.nextLink", self.odata_next_link)
        writer.write_collection_of_object_values("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

