from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .rule_assignment_resource_type import RuleAssignment_resourceType

@dataclass
class RuleAssignment(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The unique identifier of the policy.
    policy_id: Optional[str] = None
    # The unique identifier of the resource.
    resource_id: Optional[str] = None
    # The type of resource assigned to the rule.
    resource_type: Optional[RuleAssignment_resourceType] = None
    # The count of rule sets assigned.
    rule_set_count: Optional[int] = None
    # The unique identifier of the tenant.
    tenant_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> RuleAssignment:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: RuleAssignment
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return RuleAssignment()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .rule_assignment_resource_type import RuleAssignment_resourceType

        from .rule_assignment_resource_type import RuleAssignment_resourceType

        fields: dict[str, Callable[[Any], None]] = {
            "policyId": lambda n : setattr(self, 'policy_id', n.get_str_value()),
            "resourceId": lambda n : setattr(self, 'resource_id', n.get_str_value()),
            "resourceType": lambda n : setattr(self, 'resource_type', n.get_enum_value(RuleAssignment_resourceType)),
            "ruleSetCount": lambda n : setattr(self, 'rule_set_count', n.get_int_value()),
            "tenantId": lambda n : setattr(self, 'tenant_id', n.get_str_value()),
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
        writer.write_str_value("policyId", self.policy_id)
        writer.write_str_value("resourceId", self.resource_id)
        writer.write_enum_value("resourceType", self.resource_type)
        writer.write_int_value("ruleSetCount", self.rule_set_count)
        writer.write_str_value("tenantId", self.tenant_id)
        writer.write_additional_data_value(self.additional_data)
    

