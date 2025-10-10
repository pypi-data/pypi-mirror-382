from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .copy_request_options import CopyRequestOptions
    from .copy_type import CopyType

@dataclass
class CopyRequest(Parsable):
    """
    Represents request to copy to a target environment from source environment.
    """
    # Optional inputs for copy request.
    copy_options: Optional[CopyRequestOptions] = None
    # Represents the type of copy operation.
    copy_type: Optional[CopyType] = None
    # Source environment ID to copy from.
    source_environment_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CopyRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CopyRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CopyRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .copy_request_options import CopyRequestOptions
        from .copy_type import CopyType

        from .copy_request_options import CopyRequestOptions
        from .copy_type import CopyType

        fields: dict[str, Callable[[Any], None]] = {
            "copyOptions": lambda n : setattr(self, 'copy_options', n.get_object_value(CopyRequestOptions)),
            "copyType": lambda n : setattr(self, 'copy_type', n.get_enum_value(CopyType)),
            "sourceEnvironmentId": lambda n : setattr(self, 'source_environment_id', n.get_str_value()),
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
        writer.write_object_value("copyOptions", self.copy_options)
        writer.write_enum_value("copyType", self.copy_type)
        writer.write_str_value("sourceEnvironmentId", self.source_environment_id)
    

