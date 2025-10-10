from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class StorageWarningThresholds(Parsable):
    # The storageCategory property
    storage_category: Optional[str] = None
    # The storageEntity property
    storage_entity: Optional[str] = None
    # The thresholdInMB property
    threshold_in_m_b: Optional[int] = None
    # The warningMessageConstKey property
    warning_message_const_key: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> StorageWarningThresholds:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: StorageWarningThresholds
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return StorageWarningThresholds()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "storageCategory": lambda n : setattr(self, 'storage_category', n.get_str_value()),
            "storageEntity": lambda n : setattr(self, 'storage_entity', n.get_str_value()),
            "thresholdInMB": lambda n : setattr(self, 'threshold_in_m_b', n.get_int_value()),
            "warningMessageConstKey": lambda n : setattr(self, 'warning_message_const_key', n.get_str_value()),
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
        writer.write_str_value("storageCategory", self.storage_category)
        writer.write_str_value("storageEntity", self.storage_entity)
        writer.write_int_value("thresholdInMB", self.threshold_in_m_b)
        writer.write_str_value("warningMessageConstKey", self.warning_message_const_key)
    

