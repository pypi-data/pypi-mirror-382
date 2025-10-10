from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.api_error import APIError
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .error_detail import ErrorDetail

@dataclass
class ErrorResponse(APIError, Parsable):
    # The code property
    code: Optional[str] = None
    # The details property
    details: Optional[list[ErrorDetail]] = None
    # The message property
    message: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ErrorResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ErrorResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ErrorResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .error_detail import ErrorDetail

        from .error_detail import ErrorDetail

        fields: dict[str, Callable[[Any], None]] = {
            "code": lambda n : setattr(self, 'code', n.get_str_value()),
            "details": lambda n : setattr(self, 'details', n.get_collection_of_object_values(ErrorDetail)),
            "message": lambda n : setattr(self, 'message', n.get_str_value()),
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
    
    @property
    def primary_message(self) -> Optional[str]:
        """
        The primary error message.
        """
        return super().message

