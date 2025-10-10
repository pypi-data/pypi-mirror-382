from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .billing_policies.billing_policies_request_builder import BillingPoliciesRequestBuilder
    from .environments.environments_request_builder import EnvironmentsRequestBuilder
    from .isv_contracts.isv_contracts_request_builder import IsvContractsRequestBuilder
    from .storage_warning.storage_warning_request_builder import StorageWarningRequestBuilder
    from .temporary_currency_entitlement.temporary_currency_entitlement_request_builder import TemporaryCurrencyEntitlementRequestBuilder
    from .tenant_capacity.tenant_capacity_request_builder import TenantCapacityRequestBuilder

class LicensingRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new LicensingRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing", path_parameters)
    
    @property
    def billing_policies(self) -> BillingPoliciesRequestBuilder:
        """
        The billingPolicies property
        """
        from .billing_policies.billing_policies_request_builder import BillingPoliciesRequestBuilder

        return BillingPoliciesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def environments(self) -> EnvironmentsRequestBuilder:
        """
        The environments property
        """
        from .environments.environments_request_builder import EnvironmentsRequestBuilder

        return EnvironmentsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def isv_contracts(self) -> IsvContractsRequestBuilder:
        """
        The isvContracts property
        """
        from .isv_contracts.isv_contracts_request_builder import IsvContractsRequestBuilder

        return IsvContractsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def storage_warning(self) -> StorageWarningRequestBuilder:
        """
        The storageWarning property
        """
        from .storage_warning.storage_warning_request_builder import StorageWarningRequestBuilder

        return StorageWarningRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def temporary_currency_entitlement(self) -> TemporaryCurrencyEntitlementRequestBuilder:
        """
        The TemporaryCurrencyEntitlement property
        """
        from .temporary_currency_entitlement.temporary_currency_entitlement_request_builder import TemporaryCurrencyEntitlementRequestBuilder

        return TemporaryCurrencyEntitlementRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def tenant_capacity(self) -> TenantCapacityRequestBuilder:
        """
        The tenantCapacity property
        """
        from .tenant_capacity.tenant_capacity_request_builder import TenantCapacityRequestBuilder

        return TenantCapacityRequestBuilder(self.request_adapter, self.path_parameters)
    

