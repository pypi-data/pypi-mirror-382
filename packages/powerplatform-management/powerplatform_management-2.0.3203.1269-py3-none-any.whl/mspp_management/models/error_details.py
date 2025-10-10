from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class ErrorDetails(Parsable):
    # Error code from Dataverse
    error_code: Optional[int] = None
    # Error name
    error_name: Optional[str] = None
    # Error message
    message: Optional[str] = None
    # Source of the error
    source: Optional[str] = None
    # Status code for error
    status_code: Optional[int] = None
    # Error type
    type: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ErrorDetails:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ErrorDetails
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ErrorDetails()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "errorCode": lambda n : setattr(self, 'error_code', n.get_int_value()),
            "errorName": lambda n : setattr(self, 'error_name', n.get_str_value()),
            "message": lambda n : setattr(self, 'message', n.get_str_value()),
            "source": lambda n : setattr(self, 'source', n.get_str_value()),
            "statusCode": lambda n : setattr(self, 'status_code', n.get_int_value()),
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
        writer.write_int_value("errorCode", self.error_code)
        writer.write_str_value("errorName", self.error_name)
        writer.write_str_value("message", self.message)
        writer.write_str_value("source", self.source)
        writer.write_int_value("statusCode", self.status_code)
        writer.write_str_value("type", self.type)
    

