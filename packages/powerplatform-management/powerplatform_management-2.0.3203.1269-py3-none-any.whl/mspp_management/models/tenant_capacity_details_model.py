from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .capacity_summary import CapacitySummary
    from .legacy_capacity_model import LegacyCapacityModel
    from .license_model import LicenseModel
    from .temporary_license_info import TemporaryLicenseInfo
    from .tenant_capacity_and_consumption_model import TenantCapacityAndConsumptionModel

@dataclass
class TenantCapacityDetailsModel(Parsable):
    # The capacitySummary property
    capacity_summary: Optional[CapacitySummary] = None
    # The legacyModelCapacity property
    legacy_model_capacity: Optional[LegacyCapacityModel] = None
    # The licenseModelType property
    license_model_type: Optional[LicenseModel] = None
    # The temporaryLicenseInfo property
    temporary_license_info: Optional[TemporaryLicenseInfo] = None
    # The tenantCapacities property
    tenant_capacities: Optional[list[TenantCapacityAndConsumptionModel]] = None
    # The tenantId property
    tenant_id: Optional[UUID] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TenantCapacityDetailsModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TenantCapacityDetailsModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TenantCapacityDetailsModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .capacity_summary import CapacitySummary
        from .legacy_capacity_model import LegacyCapacityModel
        from .license_model import LicenseModel
        from .temporary_license_info import TemporaryLicenseInfo
        from .tenant_capacity_and_consumption_model import TenantCapacityAndConsumptionModel

        from .capacity_summary import CapacitySummary
        from .legacy_capacity_model import LegacyCapacityModel
        from .license_model import LicenseModel
        from .temporary_license_info import TemporaryLicenseInfo
        from .tenant_capacity_and_consumption_model import TenantCapacityAndConsumptionModel

        fields: dict[str, Callable[[Any], None]] = {
            "capacitySummary": lambda n : setattr(self, 'capacity_summary', n.get_object_value(CapacitySummary)),
            "legacyModelCapacity": lambda n : setattr(self, 'legacy_model_capacity', n.get_object_value(LegacyCapacityModel)),
            "licenseModelType": lambda n : setattr(self, 'license_model_type', n.get_enum_value(LicenseModel)),
            "temporaryLicenseInfo": lambda n : setattr(self, 'temporary_license_info', n.get_object_value(TemporaryLicenseInfo)),
            "tenantCapacities": lambda n : setattr(self, 'tenant_capacities', n.get_collection_of_object_values(TenantCapacityAndConsumptionModel)),
            "tenantId": lambda n : setattr(self, 'tenant_id', n.get_uuid_value()),
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
        writer.write_object_value("capacitySummary", self.capacity_summary)
        writer.write_object_value("legacyModelCapacity", self.legacy_model_capacity)
        writer.write_enum_value("licenseModelType", self.license_model_type)
        writer.write_object_value("temporaryLicenseInfo", self.temporary_license_info)
        writer.write_collection_of_object_values("tenantCapacities", self.tenant_capacities)
        writer.write_uuid_value("tenantId", self.tenant_id)
    

