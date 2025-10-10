from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class CopyRequestOptions(Parsable):
    """
    Optional inputs for copy request.
    """
    # Environment name to override on target environment.
    environment_name_to_override: Optional[str] = None
    # Boolean flag to execute advanced copy for Finance and Operation data.
    execute_advanced_copy_for_finance_and_operations: Optional[bool] = None
    # Security group ID to override on target environment.
    security_group_id_to_override: Optional[str] = None
    # Boolean flag to skip audit data for copy.
    skip_audit_data: Optional[bool] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CopyRequestOptions:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CopyRequestOptions
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CopyRequestOptions()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "environmentNameToOverride": lambda n : setattr(self, 'environment_name_to_override', n.get_str_value()),
            "executeAdvancedCopyForFinanceAndOperations": lambda n : setattr(self, 'execute_advanced_copy_for_finance_and_operations', n.get_bool_value()),
            "securityGroupIdToOverride": lambda n : setattr(self, 'security_group_id_to_override', n.get_str_value()),
            "skipAuditData": lambda n : setattr(self, 'skip_audit_data', n.get_bool_value()),
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
        writer.write_str_value("environmentNameToOverride", self.environment_name_to_override)
        writer.write_bool_value("executeAdvancedCopyForFinanceAndOperations", self.execute_advanced_copy_for_finance_and_operations)
        writer.write_str_value("securityGroupIdToOverride", self.security_group_id_to_override)
        writer.write_bool_value("skipAuditData", self.skip_audit_data)
    

