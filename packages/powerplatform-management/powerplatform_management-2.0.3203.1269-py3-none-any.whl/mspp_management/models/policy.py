from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .rule_set import RuleSet

@dataclass
class Policy(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # The unique identifier of the policy assignment.
    id: Optional[str] = None
    # The date and time when the policy was last modified.
    last_modified: Optional[datetime.datetime] = None
    # The name of the policy.
    name: Optional[str] = None
    # The number of rule sets associated with this policy.
    rule_set_count: Optional[int] = None
    # The ruleSets property
    rule_sets: Optional[list[RuleSet]] = None
    # The unique identifier of the tenant.
    tenant_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Policy:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Policy
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Policy()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .rule_set import RuleSet

        from .rule_set import RuleSet

        fields: dict[str, Callable[[Any], None]] = {
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "lastModified": lambda n : setattr(self, 'last_modified', n.get_datetime_value()),
            "name": lambda n : setattr(self, 'name', n.get_str_value()),
            "ruleSetCount": lambda n : setattr(self, 'rule_set_count', n.get_int_value()),
            "ruleSets": lambda n : setattr(self, 'rule_sets', n.get_collection_of_object_values(RuleSet)),
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
        writer.write_str_value("id", self.id)
        writer.write_datetime_value("lastModified", self.last_modified)
        writer.write_str_value("name", self.name)
        writer.write_int_value("ruleSetCount", self.rule_set_count)
        writer.write_collection_of_object_values("ruleSets", self.rule_sets)
        writer.write_str_value("tenantId", self.tenant_id)
        writer.write_additional_data_value(self.additional_data)
    

