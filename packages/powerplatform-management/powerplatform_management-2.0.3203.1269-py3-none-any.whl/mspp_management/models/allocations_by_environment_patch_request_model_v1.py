from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .currency_allocation_request_model_v1 import CurrencyAllocationRequestModelV1

@dataclass
class AllocationsByEnvironmentPatchRequestModelV1(Parsable):
    # Specify the request body with environment ID and currency details.
    currency_allocations: Optional[list[CurrencyAllocationRequestModelV1]] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> AllocationsByEnvironmentPatchRequestModelV1:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: AllocationsByEnvironmentPatchRequestModelV1
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return AllocationsByEnvironmentPatchRequestModelV1()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .currency_allocation_request_model_v1 import CurrencyAllocationRequestModelV1

        from .currency_allocation_request_model_v1 import CurrencyAllocationRequestModelV1

        fields: dict[str, Callable[[Any], None]] = {
            "currencyAllocations": lambda n : setattr(self, 'currency_allocations', n.get_collection_of_object_values(CurrencyAllocationRequestModelV1)),
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
    

