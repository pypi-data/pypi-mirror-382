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
    from ...models.billing_policy_post_request_model import BillingPolicyPostRequestModel
    from ...models.billing_policy_response_model import BillingPolicyResponseModel
    from ...models.billing_policy_response_model_response_with_odata_continuation import BillingPolicyResponseModelResponseWithOdataContinuation
    from .item.with_billing_policy_item_request_builder import WithBillingPolicyItemRequestBuilder

class BillingPoliciesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/billingPolicies
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new BillingPoliciesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/billingPolicies?api-version={api%2Dversion}{&%24top*}", path_parameters)
    
    def by_billing_policy_id(self,billing_policy_id: str) -> WithBillingPolicyItemRequestBuilder:
        """
        Gets an item from the ApiSdk.licensing.billingPolicies.item collection
        param billing_policy_id: The billing policy ID.
        Returns: WithBillingPolicyItemRequestBuilder
        """
        if billing_policy_id is None:
            raise TypeError("billing_policy_id cannot be null.")
        from .item.with_billing_policy_item_request_builder import WithBillingPolicyItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["billingPolicyId"] = billing_policy_id
        return WithBillingPolicyItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[BillingPoliciesRequestBuilderGetQueryParameters]] = None) -> Optional[BillingPolicyResponseModelResponseWithOdataContinuation]:
        """
        Get the list of billing policies for the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[BillingPolicyResponseModelResponseWithOdataContinuation]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.billing_policy_response_model_response_with_odata_continuation import BillingPolicyResponseModelResponseWithOdataContinuation

        return await self.request_adapter.send_async(request_info, BillingPolicyResponseModelResponseWithOdataContinuation, None)
    
    async def post(self,body: BillingPolicyPostRequestModel, request_configuration: Optional[RequestConfiguration[BillingPoliciesRequestBuilderPostQueryParameters]] = None) -> Optional[BillingPolicyResponseModel]:
        """
        Creates the billing policy at tenant level.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[BillingPolicyResponseModel]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.billing_policy_response_model import BillingPolicyResponseModel

        return await self.request_adapter.send_async(request_info, BillingPolicyResponseModel, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[BillingPoliciesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get the list of billing policies for the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: BillingPolicyPostRequestModel, request_configuration: Optional[RequestConfiguration[BillingPoliciesRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Creates the billing policy at tenant level.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, '{+baseurl}/licensing/billingPolicies?api-version={api%2Dversion}', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> BillingPoliciesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: BillingPoliciesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return BillingPoliciesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class BillingPoliciesRequestBuilderGetQueryParameters():
        """
        Get the list of billing policies for the tenant.
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
            if original_name == "top":
                return "%24top"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # The ISV contract ID.
        top: Optional[str] = None

    
    @dataclass
    class BillingPoliciesRequestBuilderGetRequestConfiguration(RequestConfiguration[BillingPoliciesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class BillingPoliciesRequestBuilderPostQueryParameters():
        """
        Creates the billing policy at tenant level.
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
    class BillingPoliciesRequestBuilderPostRequestConfiguration(RequestConfiguration[BillingPoliciesRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

