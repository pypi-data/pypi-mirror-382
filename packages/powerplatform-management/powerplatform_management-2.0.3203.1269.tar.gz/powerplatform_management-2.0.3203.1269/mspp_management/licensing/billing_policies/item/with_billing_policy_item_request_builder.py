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
    from ....models.billing_policy_put_request_model import BillingPolicyPutRequestModel
    from ....models.billing_policy_response_model import BillingPolicyResponseModel
    from .environments.environments_request_builder import EnvironmentsRequestBuilder
    from .refresh_provisioning_status.refresh_provisioning_status_request_builder import RefreshProvisioningStatusRequestBuilder

class WithBillingPolicyItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/billingPolicies/{billingPolicyId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithBillingPolicyItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/billingPolicies/{billingPolicyId}?api-version={api%2Dversion}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[WithBillingPolicyItemRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Delete billing policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, None)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithBillingPolicyItemRequestBuilderGetQueryParameters]] = None) -> Optional[BillingPolicyResponseModel]:
        """
        Get the billing policy at tenant level by policy ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[BillingPolicyResponseModel]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.billing_policy_response_model import BillingPolicyResponseModel

        return await self.request_adapter.send_async(request_info, BillingPolicyResponseModel, None)
    
    async def put(self,body: BillingPolicyPutRequestModel, request_configuration: Optional[RequestConfiguration[WithBillingPolicyItemRequestBuilderPutQueryParameters]] = None) -> Optional[BillingPolicyResponseModel]:
        """
        Updates the billing policy at tenant level.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[BillingPolicyResponseModel]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.billing_policy_response_model import BillingPolicyResponseModel

        return await self.request_adapter.send_async(request_info, BillingPolicyResponseModel, None)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[WithBillingPolicyItemRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Delete billing policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithBillingPolicyItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get the billing policy at tenant level by policy ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: BillingPolicyPutRequestModel, request_configuration: Optional[RequestConfiguration[WithBillingPolicyItemRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Updates the billing policy at tenant level.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PUT, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> WithBillingPolicyItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithBillingPolicyItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithBillingPolicyItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def environments(self) -> EnvironmentsRequestBuilder:
        """
        The environments property
        """
        from .environments.environments_request_builder import EnvironmentsRequestBuilder

        return EnvironmentsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def refresh_provisioning_status(self) -> RefreshProvisioningStatusRequestBuilder:
        """
        The refreshProvisioningStatus property
        """
        from .refresh_provisioning_status.refresh_provisioning_status_request_builder import RefreshProvisioningStatusRequestBuilder

        return RefreshProvisioningStatusRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithBillingPolicyItemRequestBuilderDeleteQueryParameters():
        """
        Delete billing policy.
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
    class WithBillingPolicyItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[WithBillingPolicyItemRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithBillingPolicyItemRequestBuilderGetQueryParameters():
        """
        Get the billing policy at tenant level by policy ID.
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
    class WithBillingPolicyItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithBillingPolicyItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithBillingPolicyItemRequestBuilderPutQueryParameters():
        """
        Updates the billing policy at tenant level.
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
    class WithBillingPolicyItemRequestBuilderPutRequestConfiguration(RequestConfiguration[WithBillingPolicyItemRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

