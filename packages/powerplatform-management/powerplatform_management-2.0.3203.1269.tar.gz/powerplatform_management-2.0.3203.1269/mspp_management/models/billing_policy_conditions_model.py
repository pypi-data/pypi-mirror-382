from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .billing_policy_conditions_api_filter_model import BillingPolicyConditionsApiFilterModel

@dataclass
class BillingPolicyConditionsModel(Parsable):
    """
    The ISV Contract API filter conditions.
    """
    # The Power Platform connector filter.
    api_filter: Optional[BillingPolicyConditionsApiFilterModel] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BillingPolicyConditionsModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BillingPolicyConditionsModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BillingPolicyConditionsModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .billing_policy_conditions_api_filter_model import BillingPolicyConditionsApiFilterModel

        from .billing_policy_conditions_api_filter_model import BillingPolicyConditionsApiFilterModel

        fields: dict[str, Callable[[Any], None]] = {
            "apiFilter": lambda n : setattr(self, 'api_filter', n.get_object_value(BillingPolicyConditionsApiFilterModel)),
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
        writer.write_object_value("apiFilter", self.api_filter)
    

