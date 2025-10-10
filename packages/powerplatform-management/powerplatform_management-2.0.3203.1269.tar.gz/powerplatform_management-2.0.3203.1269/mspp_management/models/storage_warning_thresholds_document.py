from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .storage_warning_thresholds import StorageWarningThresholds

@dataclass
class StorageWarningThresholdsDocument(Parsable):
    # The isActive property
    is_active: Optional[bool] = None
    # The storageCategory property
    storage_category: Optional[str] = None
    # The storageEntity property
    storage_entity: Optional[str] = None
    # The thresholds property
    thresholds: Optional[list[StorageWarningThresholds]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> StorageWarningThresholdsDocument:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: StorageWarningThresholdsDocument
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return StorageWarningThresholdsDocument()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .storage_warning_thresholds import StorageWarningThresholds

        from .storage_warning_thresholds import StorageWarningThresholds

        fields: dict[str, Callable[[Any], None]] = {
            "isActive": lambda n : setattr(self, 'is_active', n.get_bool_value()),
            "storageCategory": lambda n : setattr(self, 'storage_category', n.get_str_value()),
            "storageEntity": lambda n : setattr(self, 'storage_entity', n.get_str_value()),
            "thresholds": lambda n : setattr(self, 'thresholds', n.get_collection_of_object_values(StorageWarningThresholds)),
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
        writer.write_bool_value("isActive", self.is_active)
        writer.write_str_value("storageCategory", self.storage_category)
        writer.write_str_value("storageEntity", self.storage_entity)
        writer.write_collection_of_object_values("thresholds", self.thresholds)
    

