from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .custom_rule_action import CustomRule_action
    from .custom_rule_enabled_state import CustomRule_enabledState
    from .custom_rule_match_conditions import CustomRule_matchConditions
    from .waf_rule_type import WafRuleType

@dataclass
class CustomRule(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Action to take when the rule matches
    action: Optional[CustomRule_action] = None
    # State of the rule
    enabled_state: Optional[CustomRule_enabledState] = None
    # The matchConditions property
    match_conditions: Optional[list[CustomRule_matchConditions]] = None
    # Name of the custom rule
    name: Optional[str] = None
    # Priority of the rule
    priority: Optional[int] = None
    # Duration in minutes for rate limiting
    rate_limit_duration_in_minutes: Optional[int] = None
    # Threshold for rate limiting
    rate_limit_threshold: Optional[int] = None
    # WAF rule type
    rule_type: Optional[WafRuleType] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CustomRule:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CustomRule
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CustomRule()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .custom_rule_action import CustomRule_action
        from .custom_rule_enabled_state import CustomRule_enabledState
        from .custom_rule_match_conditions import CustomRule_matchConditions
        from .waf_rule_type import WafRuleType

        from .custom_rule_action import CustomRule_action
        from .custom_rule_enabled_state import CustomRule_enabledState
        from .custom_rule_match_conditions import CustomRule_matchConditions
        from .waf_rule_type import WafRuleType

        fields: dict[str, Callable[[Any], None]] = {
            "action": lambda n : setattr(self, 'action', n.get_enum_value(CustomRule_action)),
            "enabledState": lambda n : setattr(self, 'enabled_state', n.get_enum_value(CustomRule_enabledState)),
            "matchConditions": lambda n : setattr(self, 'match_conditions', n.get_collection_of_object_values(CustomRule_matchConditions)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "priority": lambda n : setattr(self, 'priority', n.get_int_value()),
            "rateLimitDurationInMinutes": lambda n : setattr(self, 'rate_limit_duration_in_minutes', n.get_int_value()),
            "rateLimitThreshold": lambda n : setattr(self, 'rate_limit_threshold', n.get_int_value()),
            "ruleType": lambda n : setattr(self, 'rule_type', n.get_enum_value(WafRuleType)),
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
        writer.write_enum_value("action", self.action)
        writer.write_enum_value("enabledState", self.enabled_state)
        writer.write_collection_of_object_values("matchConditions", self.match_conditions)
        writer.write_str_value("name", self.name)
        writer.write_int_value("priority", self.priority)
        writer.write_int_value("rateLimitDurationInMinutes", self.rate_limit_duration_in_minutes)
        writer.write_int_value("rateLimitThreshold", self.rate_limit_threshold)
        writer.write_enum_value("ruleType", self.rule_type)
        writer.write_additional_data_value(self.additional_data)
    

