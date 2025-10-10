from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .capacity_entitlement_type import CapacityEntitlementType
    from .capacity_type import CapacityType
    from .license_details_model import LicenseDetailsModel

@dataclass
class TenantCapacityEntitlementModel(Parsable):
    # The capacitySubType property
    capacity_sub_type: Optional[CapacityEntitlementType] = None
    # The capacityType property
    capacity_type: Optional[CapacityType] = None
    # The licenses property
    licenses: Optional[list[LicenseDetailsModel]] = None
    # The maxNextLifecycleDate property
    max_next_lifecycle_date: Optional[datetime.datetime] = None
    # The totalCapacity property
    total_capacity: Optional[float] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TenantCapacityEntitlementModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TenantCapacityEntitlementModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TenantCapacityEntitlementModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .capacity_entitlement_type import CapacityEntitlementType
        from .capacity_type import CapacityType
        from .license_details_model import LicenseDetailsModel

        from .capacity_entitlement_type import CapacityEntitlementType
        from .capacity_type import CapacityType
        from .license_details_model import LicenseDetailsModel

        fields: dict[str, Callable[[Any], None]] = {
            "capacitySubType": lambda n : setattr(self, 'capacity_sub_type', n.get_enum_value(CapacityEntitlementType)),
            "capacityType": lambda n : setattr(self, 'capacity_type', n.get_enum_value(CapacityType)),
            "licenses": lambda n : setattr(self, 'licenses', n.get_collection_of_object_values(LicenseDetailsModel)),
            "maxNextLifecycleDate": lambda n : setattr(self, 'max_next_lifecycle_date', n.get_datetime_value()),
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
        writer.write_enum_value("capacitySubType", self.capacity_sub_type)
        writer.write_enum_value("capacityType", self.capacity_type)
        writer.write_collection_of_object_values("licenses", self.licenses)
        writer.write_datetime_value("maxNextLifecycleDate", self.max_next_lifecycle_date)
        writer.write_float_value("totalCapacity", self.total_capacity)
    

