from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .capacity_availability_status import CapacityAvailabilityStatus
    from .capacity_type import CapacityType
    from .capacity_units import CapacityUnits
    from .consumption_model import ConsumptionModel
    from .overflow_capacity_model import OverflowCapacityModel
    from .tenant_capacity_entitlement_model import TenantCapacityEntitlementModel

@dataclass
class TenantCapacityAndConsumptionModel(Parsable):
    # The capacityEntitlements property
    capacity_entitlements: Optional[list[TenantCapacityEntitlementModel]] = None
    # The capacityType property
    capacity_type: Optional[CapacityType] = None
    # The capacityUnits property
    capacity_units: Optional[CapacityUnits] = None
    # The consumption property
    consumption: Optional[ConsumptionModel] = None
    # The maxCapacity property
    max_capacity: Optional[float] = None
    # The overflowCapacity property
    overflow_capacity: Optional[list[OverflowCapacityModel]] = None
    # The status property
    status: Optional[CapacityAvailabilityStatus] = None
    # The totalCapacity property
    total_capacity: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TenantCapacityAndConsumptionModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TenantCapacityAndConsumptionModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TenantCapacityAndConsumptionModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .capacity_availability_status import CapacityAvailabilityStatus
        from .capacity_type import CapacityType
        from .capacity_units import CapacityUnits
        from .consumption_model import ConsumptionModel
        from .overflow_capacity_model import OverflowCapacityModel
        from .tenant_capacity_entitlement_model import TenantCapacityEntitlementModel

        from .capacity_availability_status import CapacityAvailabilityStatus
        from .capacity_type import CapacityType
        from .capacity_units import CapacityUnits
        from .consumption_model import ConsumptionModel
        from .overflow_capacity_model import OverflowCapacityModel
        from .tenant_capacity_entitlement_model import TenantCapacityEntitlementModel

        fields: dict[str, Callable[[Any], None]] = {
            "capacityEntitlements": lambda n : setattr(self, 'capacity_entitlements', n.get_collection_of_object_values(TenantCapacityEntitlementModel)),
            "capacityType": lambda n : setattr(self, 'capacity_type', n.get_enum_value(CapacityType)),
            "capacityUnits": lambda n : setattr(self, 'capacity_units', n.get_enum_value(CapacityUnits)),
            "consumption": lambda n : setattr(self, 'consumption', n.get_object_value(ConsumptionModel)),
            "maxCapacity": lambda n : setattr(self, 'max_capacity', n.get_float_value()),
            "overflowCapacity": lambda n : setattr(self, 'overflow_capacity', n.get_collection_of_object_values(OverflowCapacityModel)),
            "status": lambda n : setattr(self, 'status', n.get_enum_value(CapacityAvailabilityStatus)),
            "totalCapacity": lambda n : setattr(self, 'total_capacity', n.get_float_value()),
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
        writer.write_collection_of_object_values("capacityEntitlements", self.capacity_entitlements)
        writer.write_enum_value("capacityType", self.capacity_type)
        writer.write_enum_value("capacityUnits", self.capacity_units)
        writer.write_object_value("consumption", self.consumption)
        writer.write_float_value("maxCapacity", self.max_capacity)
        writer.write_collection_of_object_values("overflowCapacity", self.overflow_capacity)
        writer.write_enum_value("status", self.status)
        writer.write_float_value("totalCapacity", self.total_capacity)
    

