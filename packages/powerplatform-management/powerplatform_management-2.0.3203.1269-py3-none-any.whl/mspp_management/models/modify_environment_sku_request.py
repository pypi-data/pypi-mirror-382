from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .environment_sku import EnvironmentSku

@dataclass
class ModifyEnvironmentSkuRequest(Parsable):
    """
    Represents request to change the sku of an environment.
    """
    # The environment SKU.
    environment_sku: Optional[EnvironmentSku] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ModifyEnvironmentSkuRequest:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ModifyEnvironmentSkuRequest
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ModifyEnvironmentSkuRequest()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .environment_sku import EnvironmentSku

        from .environment_sku import EnvironmentSku

        fields: dict[str, Callable[[Any], None]] = {
            "environmentSku": lambda n : setattr(self, 'environment_sku', n.get_enum_value(EnvironmentSku)),
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
        writer.write_enum_value("environmentSku", self.environment_sku)
    

