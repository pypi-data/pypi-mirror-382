from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class BotQuarantineStatus(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Indicates whether the bot is quarantined.
    is_bot_quarantined: Optional[bool] = None
    # The last update time in UTC.
    last_update_time_utc: Optional[datetime.datetime] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BotQuarantineStatus:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BotQuarantineStatus
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BotQuarantineStatus()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "isBotQuarantined": lambda n : setattr(self, 'is_bot_quarantined', n.get_bool_value()),
            "lastUpdateTimeUtc": lambda n : setattr(self, 'last_update_time_utc', n.get_datetime_value()),
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
        writer.write_bool_value("isBotQuarantined", self.is_bot_quarantined)
        writer.write_datetime_value("lastUpdateTimeUtc", self.last_update_time_utc)
        writer.write_additional_data_value(self.additional_data)
    

