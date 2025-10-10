from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .billing_instrument_model import BillingInstrumentModel
    from .billing_policy_conditions_model import BillingPolicyConditionsModel
    from .billing_policy_status import BillingPolicyStatus
    from .consumer_identity_model import ConsumerIdentityModel
    from .power_automate_policy_model import PowerAutomatePolicyModel
    from .principal import Principal

@dataclass
class IsvContractResponseModel(Parsable):
    # The ISV billing instrument information.
    billing_instrument: Optional[BillingInstrumentModel] = None
    # The ISV Contract API filter conditions.
    conditions: Optional[BillingPolicyConditionsModel] = None
    # The consumer identity for ISV contract.
    consumer: Optional[ConsumerIdentityModel] = None
    # The createdBy property
    created_by: Optional[Principal] = None
    # The createdOn property
    created_on: Optional[datetime.datetime] = None
    # The geo property
    geo: Optional[str] = None
    # The id property
    id: Optional[str] = None
    # The lastModifiedBy property
    last_modified_by: Optional[Principal] = None
    # The lastModifiedOn property
    last_modified_on: Optional[datetime.datetime] = None
    # The name property
    name: Optional[str] = None
    # The Power Platform requests policies.
    power_automate_policy: Optional[PowerAutomatePolicyModel] = None
    # The desired ISV contract status.
    status: Optional[BillingPolicyStatus] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> IsvContractResponseModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: IsvContractResponseModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return IsvContractResponseModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .billing_instrument_model import BillingInstrumentModel
        from .billing_policy_conditions_model import BillingPolicyConditionsModel
        from .billing_policy_status import BillingPolicyStatus
        from .consumer_identity_model import ConsumerIdentityModel
        from .power_automate_policy_model import PowerAutomatePolicyModel
        from .principal import Principal

        from .billing_instrument_model import BillingInstrumentModel
        from .billing_policy_conditions_model import BillingPolicyConditionsModel
        from .billing_policy_status import BillingPolicyStatus
        from .consumer_identity_model import ConsumerIdentityModel
        from .power_automate_policy_model import PowerAutomatePolicyModel
        from .principal import Principal

        fields: dict[str, Callable[[Any], None]] = {
            "billingInstrument": lambda n : setattr(self, 'billing_instrument', n.get_object_value(BillingInstrumentModel)),
            "conditions": lambda n : setattr(self, 'conditions', n.get_object_value(BillingPolicyConditionsModel)),
            "consumer": lambda n : setattr(self, 'consumer', n.get_object_value(ConsumerIdentityModel)),
            "createdBy": lambda n : setattr(self, 'created_by', n.get_object_value(Principal)),
            "createdOn": lambda n : setattr(self, 'created_on', n.get_datetime_value()),
            "geo": lambda n : setattr(self, 'geo', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "lastModifiedBy": lambda n : setattr(self, 'last_modified_by', n.get_object_value(Principal)),
            "lastModifiedOn": lambda n : setattr(self, 'last_modified_on', n.get_datetime_value()),
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
        writer.write_object_value("billingInstrument", self.billing_instrument)
        writer.write_object_value("conditions", self.conditions)
        writer.write_object_value("consumer", self.consumer)
        writer.write_object_value("createdBy", self.created_by)
        writer.write_datetime_value("createdOn", self.created_on)
        writer.write_str_value("geo", self.geo)
        writer.write_str_value("id", self.id)
        writer.write_object_value("lastModifiedBy", self.last_modified_by)
        writer.write_datetime_value("lastModifiedOn", self.last_modified_on)
        writer.write_str_value("name", self.name)
        writer.write_object_value("powerAutomatePolicy", self.power_automate_policy)
        writer.write_enum_value("status", self.status)
    

