from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .rule import Rule

@dataclass
class SiteSecurityResult(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # End time of the scan
    end_time: Optional[datetime.datetime] = None
    # Number of rules that failed
    failed_rule_count: Optional[int] = None
    # List of rules evaluated during the scan
    rules: Optional[list[Rule]] = None
    # Start time of the scan
    start_time: Optional[datetime.datetime] = None
    # Total number of alerts generated
    total_alert_count: Optional[int] = None
    # Total number of rules evaluated
    total_rule_count: Optional[int] = None
    # Name of the user who initiated the scan
    user_name: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> SiteSecurityResult:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: SiteSecurityResult
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return SiteSecurityResult()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .rule import Rule

        from .rule import Rule

        fields: dict[str, Callable[[Any], None]] = {
            "EndTime": lambda n : setattr(self, 'end_time', n.get_datetime_value()),
            "FailedRuleCount": lambda n : setattr(self, 'failed_rule_count', n.get_int_value()),
            "Rules": lambda n : setattr(self, 'rules', n.get_collection_of_object_values(Rule)),
            "StartTime": lambda n : setattr(self, 'start_time', n.get_datetime_value()),
            "TotalAlertCount": lambda n : setattr(self, 'total_alert_count', n.get_int_value()),
            "TotalRuleCount": lambda n : setattr(self, 'total_rule_count', n.get_int_value()),
            "UserName": lambda n : setattr(self, 'user_name', n.get_str_value()),
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
        writer.write_datetime_value("EndTime", self.end_time)
        writer.write_int_value("FailedRuleCount", self.failed_rule_count)
        writer.write_collection_of_object_values("Rules", self.rules)
        writer.write_datetime_value("StartTime", self.start_time)
        writer.write_int_value("TotalAlertCount", self.total_alert_count)
        writer.write_int_value("TotalRuleCount", self.total_rule_count)
        writer.write_str_value("UserName", self.user_name)
        writer.write_additional_data_value(self.additional_data)
    

