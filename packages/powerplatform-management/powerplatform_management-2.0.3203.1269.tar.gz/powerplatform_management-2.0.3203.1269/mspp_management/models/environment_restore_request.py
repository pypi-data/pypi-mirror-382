from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class EnvironmentRestoreRequest(Parsable):
    """
    Request model for restoring an environment to a previous backup.
    """
    # Date and time of when the restore point is. Date and Time should with timezone offset per RFC 3339 (e.g., 2025-04-30T12:34:56+02:00).
    restore_point_date_time: Optional[datetime.datetime] = None
    # A value indicating whether to skip audit data during the restore process.
    skip_audit_data: Optional[bool] = None
    # The ID of the source environment from which the backup will be restored from.
    source_environment_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EnvironmentRestoreRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EnvironmentRestoreRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EnvironmentRestoreRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "restorePointDateTime": lambda n : setattr(self, 'restore_point_date_time', n.get_datetime_value()),
            "skipAuditData": lambda n : setattr(self, 'skip_audit_data', n.get_bool_value()),
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
        writer.write_datetime_value("restorePointDateTime", self.restore_point_date_time)
        writer.write_bool_value("skipAuditData", self.skip_audit_data)
        writer.write_str_value("sourceEnvironmentId", self.source_environment_id)
    

