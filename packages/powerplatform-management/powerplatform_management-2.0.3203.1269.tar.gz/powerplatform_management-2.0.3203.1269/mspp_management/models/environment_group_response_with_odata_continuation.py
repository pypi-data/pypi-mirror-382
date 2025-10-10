from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .environment_group import EnvironmentGroup

@dataclass
class EnvironmentGroupResponseWithOdataContinuation(Parsable):
    # The OdataNextLink property
    odata_next_link: Optional[str] = None
    # The value property
    value: Optional[list[EnvironmentGroup]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EnvironmentGroupResponseWithOdataContinuation:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EnvironmentGroupResponseWithOdataContinuation
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EnvironmentGroupResponseWithOdataContinuation()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .environment_group import EnvironmentGroup

        from .environment_group import EnvironmentGroup

        fields: dict[str, Callable[[Any], None]] = {
            "@odata.nextLink": lambda n : setattr(self, 'odata_next_link', n.get_str_value()),
            "value": lambda n : setattr(self, 'value', n.get_collection_of_object_values(EnvironmentGroup)),
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
        writer.write_str_value("@odata.nextLink", self.odata_next_link)
        writer.write_collection_of_object_values("value", self.value)
    

