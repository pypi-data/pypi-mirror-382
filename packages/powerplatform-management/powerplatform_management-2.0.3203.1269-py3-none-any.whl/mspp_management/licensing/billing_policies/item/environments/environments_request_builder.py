from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from .....models.billing_policy_environment_response_model_v1_response_with_odata_continuation import BillingPolicyEnvironmentResponseModelV1ResponseWithOdataContinuation
    from .add.add_request_builder import AddRequestBuilder
    from .item.with_environment_item_request_builder import WithEnvironmentItemRequestBuilder
    from .remove.remove_request_builder import RemoveRequestBuilder

class EnvironmentsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/billingPolicies/{billingPolicyId}/environments
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EnvironmentsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/billingPolicies/{billingPolicyId}/environments?api-version={api%2Dversion}", path_parameters)
    
    def by_environment_id(self,environment_id: str) -> WithEnvironmentItemRequestBuilder:
        """
        Gets an item from the ApiSdk.licensing.billingPolicies.item.environments.item collection
        param environment_id: The environment ID.
        Returns: WithEnvironmentItemRequestBuilder
        """
        if environment_id is None:
            raise TypeError("environment_id cannot be null.")
        from .item.with_environment_item_request_builder import WithEnvironmentItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["environmentId"] = environment_id
        return WithEnvironmentItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[EnvironmentsRequestBuilderGetQueryParameters]] = None) -> Optional[BillingPolicyEnvironmentResponseModelV1ResponseWithOdataContinuation]:
        """
        Get the list of environments linked to the billing policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[BillingPolicyEnvironmentResponseModelV1ResponseWithOdataContinuation]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.billing_policy_environment_response_model_v1_response_with_odata_continuation import BillingPolicyEnvironmentResponseModelV1ResponseWithOdataContinuation

        return await self.request_adapter.send_async(request_info, BillingPolicyEnvironmentResponseModelV1ResponseWithOdataContinuation, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[EnvironmentsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get the list of environments linked to the billing policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> EnvironmentsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: EnvironmentsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return EnvironmentsRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def add(self) -> AddRequestBuilder:
        """
        The add property
        """
        from .add.add_request_builder import AddRequestBuilder

        return AddRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def remove(self) -> RemoveRequestBuilder:
        """
        The remove property
        """
        from .remove.remove_request_builder import RemoveRequestBuilder

        return RemoveRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class EnvironmentsRequestBuilderGetQueryParameters():
        """
        Get the list of environments linked to the billing policy.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "api_version":
                return "api%2Dversion"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

    
    @dataclass
    class EnvironmentsRequestBuilderGetRequestConfiguration(RequestConfiguration[EnvironmentsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

