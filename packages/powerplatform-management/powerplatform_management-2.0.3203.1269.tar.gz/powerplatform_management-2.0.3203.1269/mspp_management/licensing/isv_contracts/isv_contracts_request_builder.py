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
    from ...models.isv_contract_post_request_model import IsvContractPostRequestModel
    from ...models.isv_contract_response_model import IsvContractResponseModel
    from ...models.isv_contract_response_model_response_with_odata_continuation import IsvContractResponseModelResponseWithOdataContinuation
    from .item.with_isv_contract_item_request_builder import WithIsvContractItemRequestBuilder

class IsvContractsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/isvContracts
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new IsvContractsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/isvContracts?api-version={api%2Dversion}{&%24top*}", path_parameters)
    
    def by_isv_contract_id(self,isv_contract_id: str) -> WithIsvContractItemRequestBuilder:
        """
        Gets an item from the ApiSdk.licensing.isvContracts.item collection
        param isv_contract_id: The ISV contract ID.
        Returns: WithIsvContractItemRequestBuilder
        """
        if isv_contract_id is None:
            raise TypeError("isv_contract_id cannot be null.")
        from .item.with_isv_contract_item_request_builder import WithIsvContractItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["isvContractId"] = isv_contract_id
        return WithIsvContractItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[IsvContractsRequestBuilderGetQueryParameters]] = None) -> Optional[IsvContractResponseModelResponseWithOdataContinuation]:
        """
        Get the list of ISV contracts for the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[IsvContractResponseModelResponseWithOdataContinuation]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.isv_contract_response_model_response_with_odata_continuation import IsvContractResponseModelResponseWithOdataContinuation

        return await self.request_adapter.send_async(request_info, IsvContractResponseModelResponseWithOdataContinuation, None)
    
    async def post(self,body: IsvContractPostRequestModel, request_configuration: Optional[RequestConfiguration[IsvContractsRequestBuilderPostQueryParameters]] = None) -> Optional[IsvContractResponseModel]:
        """
        Create an ISV contract.
        param body: The ISV contract model for update operations.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[IsvContractResponseModel]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.isv_contract_response_model import IsvContractResponseModel

        return await self.request_adapter.send_async(request_info, IsvContractResponseModel, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[IsvContractsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get the list of ISV contracts for the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: IsvContractPostRequestModel, request_configuration: Optional[RequestConfiguration[IsvContractsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Create an ISV contract.
        param body: The ISV contract model for update operations.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, '{+baseurl}/licensing/isvContracts?api-version={api%2Dversion}', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> IsvContractsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: IsvContractsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return IsvContractsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class IsvContractsRequestBuilderGetQueryParameters():
        """
        Get the list of ISV contracts for the tenant.
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

        # Top limit of results.
        top: Optional[str] = None

    
    @dataclass
    class IsvContractsRequestBuilderGetRequestConfiguration(RequestConfiguration[IsvContractsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class IsvContractsRequestBuilderPostQueryParameters():
        """
        Create an ISV contract.
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
    class IsvContractsRequestBuilderPostRequestConfiguration(RequestConfiguration[IsvContractsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

