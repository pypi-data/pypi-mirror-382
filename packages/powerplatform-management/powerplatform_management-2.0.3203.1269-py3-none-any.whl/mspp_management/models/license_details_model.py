from __future__ import annotations
import datetime
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.serialization import Parsable, ParseNode, SerializationWriter
from typing import Any, Optional, TYPE_CHECKING, Union
from uuid import UUID

if TYPE_CHECKING:
    from .license_quantity import LicenseQuantity

@dataclass
class LicenseDetailsModel(Parsable):
    # The capabilityStatus property
    capability_status: Optional[str] = None
    # The displayName property
    display_name: Optional[str] = None
    # The entitlementCode property
    entitlement_code: Optional[str] = None
    # The isTemporaryLicense property
    is_temporary_license: Optional[bool] = None
    # The nextLifecycleDate property
    next_lifecycle_date: Optional[datetime.datetime] = None
    # The paid property
    paid: Optional[LicenseQuantity] = None
    # The servicePlanId property
    service_plan_id: Optional[UUID] = None
    # The skuId property
    sku_id: Optional[UUID] = None
    # The temporaryLicenseExpiryDate property
    temporary_license_expiry_date: Optional[datetime.datetime] = None
    # The totalCapacity property
    total_capacity: Optional[float] = None
    # The trial property
    trial: Optional[LicenseQuantity] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> LicenseDetailsModel:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: LicenseDetailsModel
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return LicenseDetailsModel()
    
    def get_field_deserializers(self,) -> dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: dict[str, Callable[[ParseNode], None]]
        """
        from .license_quantity import LicenseQuantity

        from .license_quantity import LicenseQuantity

        fields: dict[str, Callable[[Any], None]] = {
            "capabilityStatus": lambda n : setattr(self, 'capability_status', n.get_str_value()),
            "displayName": lambda n : setattr(self, 'display_name', n.get_str_value()),
            "entitlementCode": lambda n : setattr(self, 'entitlement_code', n.get_str_value()),
            "isTemporaryLicense": lambda n : setattr(self, 'is_temporary_license', n.get_bool_value()),
            "nextLifecycleDate": lambda n : setattr(self, 'next_lifecycle_date', n.get_datetime_value()),
            "paid": lambda n : setattr(self, 'paid', n.get_object_value(LicenseQuantity)),
            "servicePlanId": lambda n : setattr(self, 'service_plan_id', n.get_uuid_value()),
            "skuId": lambda n : setattr(self, 'sku_id', n.get_uuid_value()),
            "temporaryLicenseExpiryDate": lambda n : setattr(self, 'temporary_license_expiry_date', n.get_datetime_value()),
            "totalCapacity": lambda n : setattr(self, 'total_capacity', n.get_float_value()),
            "trial": lambda n : setattr(self, 'trial', n.get_object_value(LicenseQuantity)),
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
        writer.write_str_value("capabilityStatus", self.capability_status)
        writer.write_str_value("displayName", self.display_name)
        writer.write_str_value("entitlementCode", self.entitlement_code)
        writer.write_bool_value("isTemporaryLicense", self.is_temporary_license)
        writer.write_datetime_value("nextLifecycleDate", self.next_lifecycle_date)
        writer.write_object_value("paid", self.paid)
        writer.write_uuid_value("servicePlanId", self.service_plan_id)
        writer.write_uuid_value("skuId", self.sku_id)
        writer.write_datetime_value("temporaryLicenseExpiryDate", self.temporary_license_expiry_date)
        writer.write_float_value("totalCapacity", self.total_capacity)
        writer.write_object_value("trial", self.trial)
    

