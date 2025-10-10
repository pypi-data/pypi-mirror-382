from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .currency_allocation_response_model_v1 import CurrencyAllocationResponseModelV1

@dataclass
class AllocationsByEnvironmentResponseModelV1(Parsable):
    """
    The response body includes environment ID and allocated currencies.
    """
    # The collection of currencies with allocation count.
    currency_allocations: Optional[list[CurrencyAllocationResponseModelV1]] = None
    # The environment ID for which the currency has been allocated.
    environment_id: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AllocationsByEnvironmentResponseModelV1:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AllocationsByEnvironmentResponseModelV1
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AllocationsByEnvironmentResponseModelV1()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .currency_allocation_response_model_v1 import CurrencyAllocationResponseModelV1

        from .currency_allocation_response_model_v1 import CurrencyAllocationResponseModelV1

        fields: dict[str, Callable[[Any], None]] = {
            "currencyAllocations": lambda n : setattr(self, 'currency_allocations', n.get_collection_of_object_values(CurrencyAllocationResponseModelV1)),
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
        writer.write_collection_of_object_values("currencyAllocations", self.currency_allocations)
        writer.write_str_value("environmentId", self.environment_id)
    

