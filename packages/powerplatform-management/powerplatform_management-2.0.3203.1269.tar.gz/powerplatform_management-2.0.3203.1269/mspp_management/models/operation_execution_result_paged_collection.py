from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .operation_execution_result import OperationExecutionResult

@dataclass
class OperationExecutionResultPagedCollection(Parsable):
    # The collection property
    collection: Optional[list[OperationExecutionResult]] = None
    # The continuationToken property
    continuation_token: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> OperationExecutionResultPagedCollection:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: OperationExecutionResultPagedCollection
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return OperationExecutionResultPagedCollection()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .operation_execution_result import OperationExecutionResult

        from .operation_execution_result import OperationExecutionResult

        fields: dict[str, Callable[[Any], None]] = {
            "collection": lambda n : setattr(self, 'collection', n.get_collection_of_object_values(OperationExecutionResult)),
            "continuationToken": lambda n : setattr(self, 'continuation_token', n.get_str_value()),
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
        writer.write_collection_of_object_values("collection", self.collection)
        writer.write_str_value("continuationToken", self.continuation_token)
    

