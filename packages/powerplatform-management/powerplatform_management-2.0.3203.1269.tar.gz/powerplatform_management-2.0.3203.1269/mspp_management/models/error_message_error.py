from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .error_message_error_details import ErrorMessage_error_details

@dataclass
class ErrorMessage_error(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Error code
    code: Optional[str] = None
    # The details property
    details: Optional[list[ErrorMessage_error_details]] = None
    # Error message
    message: Optional[str] = None
    # Target parameter
    target: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ErrorMessage_error:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ErrorMessage_error
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ErrorMessage_error()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .error_message_error_details import ErrorMessage_error_details

        from .error_message_error_details import ErrorMessage_error_details

        fields: dict[str, Callable[[Any], None]] = {
            "code": lambda n : setattr(self, 'code', n.get_str_value()),
            "details": lambda n : setattr(self, 'details', n.get_collection_of_object_values(ErrorMessage_error_details)),
            "message": lambda n : setattr(self, 'message', n.get_str_value()),
            "target": lambda n : setattr(self, 'target', n.get_str_value()),
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
        writer.write_str_value("code", self.code)
        writer.write_collection_of_object_values("details", self.details)
        writer.write_str_value("message", self.message)
        writer.write_str_value("target", self.target)
        writer.write_additional_data_value(self.additional_data)
    

