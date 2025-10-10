from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .connection_reference_execution_restrictions import ConnectionReference_executionRestrictions

@dataclass
class ConnectionReference(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: dict[str, Any] = field(default_factory=dict)

    # API tier is standard or premium
    api_tier: Optional[str] = None
    # Flag indicates bypassed API consent
    bypass_consent: Optional[bool] = None
    # List of data sources for the connection
    data_sources: Optional[list[str]] = None
    # List of dependencies for the connection
    dependencies: Optional[list[str]] = None
    # List of dependant connectors for the connector
    dependents: Optional[list[str]] = None
    # The displayName property
    display_name: Optional[str] = None
    # Execution restrictions for the runtime policy
    execution_restrictions: Optional[ConnectionReference_executionRestrictions] = None
    # The iconUri property
    icon_uri: Optional[str] = None
    # The id property
    id: Optional[str] = None
    # Flag indicates custom connector
    is_custom_api_connection: Optional[bool] = None
    # Flag indicates on premise data gateway
    is_on_premise_connection: Optional[bool] = None
    # String indicating the name of the runtime policy
    runtime_policy_name: Optional[str] = None
    # String indicating the ID of the shared connection
    shared_connection_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ConnectionReference:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ConnectionReference
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ConnectionReference()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .connection_reference_execution_restrictions import ConnectionReference_executionRestrictions

        from .connection_reference_execution_restrictions import ConnectionReference_executionRestrictions

        fields: dict[str, Callable[[Any], None]] = {
            "apiTier": lambda n : setattr(self, 'api_tier', n.get_str_value()),
            "bypassConsent": lambda n : setattr(self, 'bypass_consent', n.get_bool_value()),
            "dataSources": lambda n : setattr(self, 'data_sources', n.get_collection_of_primitive_values(str)),
            "dependencies": lambda n : setattr(self, 'dependencies', n.get_collection_of_primitive_values(str)),
            "dependents": lambda n : setattr(self, 'dependents', n.get_collection_of_primitive_values(str)),
            "displayName": lambda n : setattr(self, 'display_name', n.get_str_value()),
            "executionRestrictions": lambda n : setattr(self, 'execution_restrictions', n.get_object_value(ConnectionReference_executionRestrictions)),
            "iconUri": lambda n : setattr(self, 'icon_uri', n.get_str_value()),
            "id": lambda n : setattr(self, 'id', n.get_str_value()),
            "isCustomApiConnection": lambda n : setattr(self, 'is_custom_api_connection', n.get_bool_value()),
            "isOnPremiseConnection": lambda n : setattr(self, 'is_on_premise_connection', n.get_bool_value()),
            "runtimePolicyName": lambda n : setattr(self, 'runtime_policy_name', n.get_str_value()),
            "sharedConnectionId": lambda n : setattr(self, 'shared_connection_id', n.get_str_value()),
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
        writer.write_str_value("apiTier", self.api_tier)
        writer.write_bool_value("bypassConsent", self.bypass_consent)
        writer.write_collection_of_primitive_values("dataSources", self.data_sources)
        writer.write_collection_of_primitive_values("dependencies", self.dependencies)
        writer.write_collection_of_primitive_values("dependents", self.dependents)
        writer.write_str_value("displayName", self.display_name)
        writer.write_object_value("executionRestrictions", self.execution_restrictions)
        writer.write_str_value("iconUri", self.icon_uri)
        writer.write_str_value("id", self.id)
        writer.write_bool_value("isCustomApiConnection", self.is_custom_api_connection)
        writer.write_bool_value("isOnPremiseConnection", self.is_on_premise_connection)
        writer.write_str_value("runtimePolicyName", self.runtime_policy_name)
        writer.write_str_value("sharedConnectionId", self.shared_connection_id)
        writer.write_additional_data_value(self.additional_data)
    

