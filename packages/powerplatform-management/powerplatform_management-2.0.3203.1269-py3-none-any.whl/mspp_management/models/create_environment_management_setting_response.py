from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.api_error import APIError
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .error_response import ErrorResponse

@dataclass
class CreateEnvironmentManagementSettingResponse(APIError, Parsable):
    """
    Represents the response object for APIs in this service.
    """
    # The errors property
    errors: Optional[ErrorResponse] = None
    # Gets or sets the next link if there are more records to be returned
    next_link: Optional[str] = None
    # Gets or sets the ID of the entity being created in the response
    object_result: Optional[str] = None
    # Gets or sets the error message.
    response_message: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CreateEnvironmentManagementSettingResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CreateEnvironmentManagementSettingResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CreateEnvironmentManagementSettingResponse()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .error_response import ErrorResponse

        from .error_response import ErrorResponse

        fields: dict[str, Callable[[Any], None]] = {
            "errors": lambda n : setattr(self, 'errors', n.get_object_value(ErrorResponse)),
            "nextLink": lambda n : setattr(self, 'next_link', n.get_str_value()),
            "objectResult": lambda n : setattr(self, 'object_result', n.get_str_value()),
            "responseMessage": lambda n : setattr(self, 'response_message', n.get_str_value()),
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
        writer.write_object_value("errors", self.errors)
        writer.write_str_value("nextLink", self.next_link)
        writer.write_str_value("objectResult", self.object_result)
        writer.write_str_value("responseMessage", self.response_message)
    
    @property
    def primary_message(self) -> Optional[str]:
        """
        The primary error message.
        """
        return super().message

