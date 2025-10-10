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
    from ....models.isv_contract_put_request_model import IsvContractPutRequestModel
    from ....models.isv_contract_response_model import IsvContractResponseModel

class WithIsvContractItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/isvContracts/{isvContractId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithIsvContractItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/isvContracts/{isvContractId}?api-version={api%2Dversion}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[WithIsvContractItemRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Delete an ISV contract.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, None)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithIsvContractItemRequestBuilderGetQueryParameters]] = None) -> Optional[IsvContractResponseModel]:
        """
        Get an ISV contract by its identifier (ID).
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[IsvContractResponseModel]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.isv_contract_response_model import IsvContractResponseModel

        return await self.request_adapter.send_async(request_info, IsvContractResponseModel, None)
    
    async def put(self,body: IsvContractPutRequestModel, request_configuration: Optional[RequestConfiguration[WithIsvContractItemRequestBuilderPutQueryParameters]] = None) -> Optional[IsvContractResponseModel]:
        """
        Update an ISV contract.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[IsvContractResponseModel]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.isv_contract_response_model import IsvContractResponseModel

        return await self.request_adapter.send_async(request_info, IsvContractResponseModel, None)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[WithIsvContractItemRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Delete an ISV contract.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithIsvContractItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get an ISV contract by its identifier (ID).
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: IsvContractPutRequestModel, request_configuration: Optional[RequestConfiguration[WithIsvContractItemRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Update an ISV contract.
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
    
    def with_url(self,raw_url: str) -> WithIsvContractItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithIsvContractItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithIsvContractItemRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class WithIsvContractItemRequestBuilderDeleteQueryParameters():
        """
        Delete an ISV contract.
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
    class WithIsvContractItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[WithIsvContractItemRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithIsvContractItemRequestBuilderGetQueryParameters():
        """
        Get an ISV contract by its identifier (ID).
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
    class WithIsvContractItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithIsvContractItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithIsvContractItemRequestBuilderPutQueryParameters():
        """
        Update an ISV contract.
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
    class WithIsvContractItemRequestBuilderPutRequestConfiguration(RequestConfiguration[WithIsvContractItemRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

