from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .custom_rule_match_conditions_operator import CustomRule_matchConditions_operator

@dataclass
class CustomRule_matchConditions(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # Values to match
    match_value: Optional[list[str]] = None
    # Variable to match
    match_variable: Optional[str] = None
    # Whether to negate the condition
    negate_condition: Optional[bool] = None
    # Operator for the match condition
    operator: Optional[CustomRule_matchConditions_operator] = None
    # Selector for the match variable
    selector: Optional[str] = None
    # Transformations to apply
    transforms: Optional[list[str]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CustomRule_matchConditions:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CustomRule_matchConditions
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CustomRule_matchConditions()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .custom_rule_match_conditions_operator import CustomRule_matchConditions_operator

        from .custom_rule_match_conditions_operator import CustomRule_matchConditions_operator

        fields: dict[str, Callable[[Any], None]] = {
            "matchValue": lambda n : setattr(self, 'match_value', n.get_collection_of_primitive_values(str)),
            "matchVariable": lambda n : setattr(self, 'match_variable', n.get_str_value()),
            "negateCondition": lambda n : setattr(self, 'negate_condition', n.get_bool_value()),
            "operator": lambda n : setattr(self, 'operator', n.get_enum_value(CustomRule_matchConditions_operator)),
            "selector": lambda n : setattr(self, 'selector', n.get_str_value()),
            "transforms": lambda n : setattr(self, 'transforms', n.get_collection_of_primitive_values(str)),
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
        writer.write_collection_of_primitive_values("matchValue", self.match_value)
        writer.write_str_value("matchVariable", self.match_variable)
        writer.write_bool_value("negateCondition", self.negate_condition)
        writer.write_enum_value("operator", self.operator)
        writer.write_str_value("selector", self.selector)
        writer.write_collection_of_primitive_values("transforms", self.transforms)
        writer.write_additional_data_value(self.additional_data)
    

