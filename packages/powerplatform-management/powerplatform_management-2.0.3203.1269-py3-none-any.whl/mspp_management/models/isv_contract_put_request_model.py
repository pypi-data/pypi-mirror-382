from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .billing_policy_conditions_model import BillingPolicyConditionsModel
    from .billing_policy_status import BillingPolicyStatus
    from .power_automate_policy_model import PowerAutomatePolicyModel

@dataclass
class IsvContractPutRequestModel(Parsable):
    # The ISV Contract API filter conditions.
    conditions: Optional[BillingPolicyConditionsModel] = None
    # The name property
    name: Optional[str] = None
    # The Power Platform requests policies.
    power_automate_policy: Optional[PowerAutomatePolicyModel] = None
    # The desired ISV contract status.
    status: Optional[BillingPolicyStatus] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IsvContractPutRequestModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IsvContractPutRequestModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IsvContractPutRequestModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .billing_policy_conditions_model import BillingPolicyConditionsModel
        from .billing_policy_status import BillingPolicyStatus
        from .power_automate_policy_model import PowerAutomatePolicyModel

        from .billing_policy_conditions_model import BillingPolicyConditionsModel
        from .billing_policy_status import BillingPolicyStatus
        from .power_automate_policy_model import PowerAutomatePolicyModel

        fields: dict[str, Callable[[Any], None]] = {
            "conditions": lambda n : setattr(self, 'conditions', n.get_object_value(BillingPolicyConditionsModel)),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "powerAutomatePolicy": lambda n : setattr(self, 'power_automate_policy', n.get_object_value(PowerAutomatePolicyModel)),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(BillingPolicyStatus)),
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
        writer.write_object_value("conditions", self.conditions)
        writer.write_str_value("name", self.name)
        writer.write_object_value("powerAutomatePolicy", self.power_automate_policy)
        writer.write_enum_value("status", self.status)
    

