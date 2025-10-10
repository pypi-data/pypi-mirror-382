from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .identity import Identity

@dataclass
class EnvironmentBackup(Parsable):
    # The backup expiry date time. Set when the backup is created based on environment's backup retention in days.
    backup_expiry_date_time: Optional[datetime.datetime] = None
    # The backup point date time. Set when the backup is created.
    backup_point_date_time: Optional[datetime.datetime] = None
    # The createdBy property
    created_by: Optional[Identity] = None
    # The identifier of the environment backup.If null, a new Guid will be generated when the backup is created.
    id: Optional[str] = None
    # The label for the manually created backup.
    label: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EnvironmentBackup:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EnvironmentBackup
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EnvironmentBackup()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .identity import Identity

        from .identity import Identity

        fields: dict[str, Callable[[Any], None]] = {
            "backupExpiryDateTime": lambda n : setattr(self, 'backup_expiry_date_time', n.get_datetime_value()),
            "backupPointDateTime": lambda n : setattr(self, 'backup_point_date_time', n.get_datetime_value()),
            "createdBy": lambda n : setattr(self, 'created_by', n.get_object_value(Identity)),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "label": lambda n : setattr(self, 'label', n.get_str_value()),
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
        writer.write_datetime_value("backupExpiryDateTime", self.backup_expiry_date_time)
        writer.write_datetime_value("backupPointDateTime", self.backup_point_date_time)
        writer.write_object_value("createdBy", self.created_by)
        writer.write_str_value("id", self.id)
        writer.write_str_value("label", self.label)
    

