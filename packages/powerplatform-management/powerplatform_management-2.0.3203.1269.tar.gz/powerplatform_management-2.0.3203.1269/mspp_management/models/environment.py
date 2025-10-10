from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

@dataclass
class Environment(Parsable):
    """
    Power platform Environment
    """
    # Dataverse organization Url of the environment.
    dataverse_organization_url: Optional[str] = None
    # Display name of the environment.
    display_name: Optional[str] = None
    # The environment ID.
    environment_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Environment:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Environment
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Environment()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        fields: dict[str, Callable[[Any], None]] = {
            "dataverseOrganizationUrl": lambda n : setattr(self, 'dataverse_organization_url', n.get_str_value()),
            "displayName": lambda n : setattr(self, 'display_name', n.get_str_value()),
            "environmentId": lambda n : setattr(self, 'environment_id', n.get_str_value()),
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
        writer.write_str_value("dataverseOrganizationUrl", self.dataverse_organization_url)
        writer.write_str_value("displayName", self.display_name)
        writer.write_str_value("environmentId", self.environment_id)
    

