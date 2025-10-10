from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .error_info_field_errors import ErrorInfo_fieldErrors

@dataclass
class ErrorInfo(Parsable):
    """
    Represents error information for an operation.
    """
    # The error Code.
    code: Optional[str] = None
    # The detailed error.
    field_errors: Optional[ErrorInfo_fieldErrors] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ErrorInfo:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ErrorInfo
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ErrorInfo()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .error_info_field_errors import ErrorInfo_fieldErrors

        from .error_info_field_errors import ErrorInfo_fieldErrors

        fields: dict[str, Callable[[Any], None]] = {
            "code": lambda n : setattr(self, 'code', n.get_str_value()),
            "fieldErrors": lambda n : setattr(self, 'field_errors', n.get_object_value(ErrorInfo_fieldErrors)),
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
        writer.write_object_value("fieldErrors", self.field_errors)
    

