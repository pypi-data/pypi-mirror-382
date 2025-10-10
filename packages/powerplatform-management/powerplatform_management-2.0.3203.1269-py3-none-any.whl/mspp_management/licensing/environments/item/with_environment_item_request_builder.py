from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .allocations.allocations_request_builder import AllocationsRequestBuilder
    from .billing_policy.billing_policy_request_builder import BillingPolicyRequestBuilder

class WithEnvironmentItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/environments/{environmentId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithEnvironmentItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/environments/{environmentId}", path_parameters)
    
    @property
    def allocations(self) -> AllocationsRequestBuilder:
        """
        The allocations property
        """
        from .allocations.allocations_request_builder import AllocationsRequestBuilder

        return AllocationsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def billing_policy(self) -> BillingPolicyRequestBuilder:
        """
        The billingPolicy property
        """
        from .billing_policy.billing_policy_request_builder import BillingPolicyRequestBuilder

        return BillingPolicyRequestBuilder(self.request_adapter, self.path_parameters)
    

