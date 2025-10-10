from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .billing_policy_conditions_api_model import BillingPolicyConditionsApiModel

@dataclass
class BillingPolicyConditionsApiFilterModel(Parsable):
    """
    The Power Platform connector filter.
    """
    # A flag indicating whether metered usage that involves premium connectors may be attributed.
    allow_other_premium_connectors: Optional[bool] = None
    # A list of connectors, at least one of which must be involved in the metered usage to be attributed.
    required_apis: Optional[list[BillingPolicyConditionsApiModel]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> BillingPolicyConditionsApiFilterModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: BillingPolicyConditionsApiFilterModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return BillingPolicyConditionsApiFilterModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .billing_policy_conditions_api_model import BillingPolicyConditionsApiModel

        from .billing_policy_conditions_api_model import BillingPolicyConditionsApiModel

        fields: dict[str, Callable[[Any], None]] = {
            "allowOtherPremiumConnectors": lambda n : setattr(self, 'allow_other_premium_connectors', n.get_bool_value()),
            "requiredApis": lambda n : setattr(self, 'required_apis', n.get_collection_of_object_values(BillingPolicyConditionsApiModel)),
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
        writer.write_bool_value("allowOtherPremiumConnectors", self.allow_other_premium_connectors)
        writer.write_collection_of_object_values("requiredApis", self.required_apis)
    

