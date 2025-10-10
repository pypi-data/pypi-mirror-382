from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class Alert(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Unique identifier of the alert
    alert_id: Optional[str] = None
    # Name of the alert
    alert_name: Optional[str] = None
    # Actions to address the alert
    call_to_action: Optional[list[str]] = None
    # Detailed description of the alert
    description: Optional[str] = None
    # Links to learn more about the alert
    learn_more_link: Optional[list[str]] = None
    # Steps to mitigate the issue
    mitigation: Optional[str] = None
    # Risk level associated with the alert
    risk: Optional[int] = None
    # Identifier of the rule that generated the alert
    rule_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Alert:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Alert
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Alert()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "AlertId": lambda n : setattr(self, 'alert_id', n.get_str_value()),
            "AlertName": lambda n : setattr(self, 'alert_name', n.get_str_value()),
            "CallToAction": lambda n : setattr(self, 'call_to_action', n.get_collection_of_primitive_values(str)),
            "Description": lambda n : setattr(self, 'description', n.get_str_value()),
            "LearnMoreLink": lambda n : setattr(self, 'learn_more_link', n.get_collection_of_primitive_values(str)),
            "Mitigation": lambda n : setattr(self, 'mitigation', n.get_str_value()),
            "Risk": lambda n : setattr(self, 'risk', n.get_int_value()),
            "RuleId": lambda n : setattr(self, 'rule_id', n.get_str_value()),
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
        writer.write_str_value("AlertId", self.alert_id)
        writer.write_str_value("AlertName", self.alert_name)
        writer.write_collection_of_primitive_values("CallToAction", self.call_to_action)
        writer.write_str_value("Description", self.description)
        writer.write_collection_of_primitive_values("LearnMoreLink", self.learn_more_link)
        writer.write_str_value("Mitigation", self.mitigation)
        writer.write_int_value("Risk", self.risk)
        writer.write_str_value("RuleId", self.rule_id)
        writer.write_additional_data_value(self.additional_data)
    

