from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .....models.flow_action import FlowAction

@dataclass
class FlowActionsGetResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # URL to retrieve the next page of results, if any. Page size is 250.
    next_link: Optional[str] = None
    # The value property
    value: Optional[list[FlowAction]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> FlowActionsGetResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: FlowActionsGetResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return FlowActionsGetResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .....models.flow_action import FlowAction

        from .....models.flow_action import FlowAction

        fields: dict[str, Callable[[Any], None]] = {
            "nextLink": lambda n : setattr(self, 'next_link', n.get_str_value()),
            "value": lambda n : setattr(self, 'value', n.get_collection_of_object_values(FlowAction)),
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
        writer.write_str_value("nextLink", self.next_link)
        writer.write_collection_of_object_values("value", self.value)
        writer.write_additional_data_value(self.additional_data)
    

