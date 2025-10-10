from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class PowerApp_properties_userAppMetadata(AdditionalDataHolder, Parsable):
    """
    PowerApp property user app metadata object.
    """
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # PowerApp property user app metadata favorite.
    favorite: Optional[str] = None
    # PowerApp property user app metadata include in apps list.
    include_in_apps_list: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> PowerApp_properties_userAppMetadata:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: PowerApp_properties_userAppMetadata
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return PowerApp_properties_userAppMetadata()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "favorite": lambda n : setattr(self, 'favorite', n.get_str_value()),
            "includeInAppsList": lambda n : setattr(self, 'include_in_apps_list', n.get_bool_value()),
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
        writer.write_str_value("favorite", self.favorite)
        writer.write_bool_value("includeInAppsList", self.include_in_apps_list)
        writer.write_additional_data_value(self.additional_data)
    

