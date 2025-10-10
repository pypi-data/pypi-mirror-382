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
    from ....models.environment_group import EnvironmentGroup
    from ....models.problem_details import ProblemDetails
    from .add_environment.add_environment_request_builder import AddEnvironmentRequestBuilder
    from .remove_environment.remove_environment_request_builder import RemoveEnvironmentRequestBuilder

class WithGroupItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /environmentmanagement/environmentGroups/{groupId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithGroupItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/environmentmanagement/environmentGroups/{groupId}?api-version={api%2Dversion}", path_parameters)
    
    async def delete(self,request_configuration: Optional[RequestConfiguration[WithGroupItemRequestBuilderDeleteQueryParameters]] = None) -> None:
        """
        Delete the environment group.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: None
        """
        request_info = self.to_delete_request_information(
            request_configuration
        )
        from ....models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        return await self.request_adapter.send_no_response_content_async(request_info, error_mapping)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithGroupItemRequestBuilderGetQueryParameters]] = None) -> Optional[EnvironmentGroup]:
        """
        Get the environment group.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[EnvironmentGroup]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.environment_group import EnvironmentGroup

        return await self.request_adapter.send_async(request_info, EnvironmentGroup, error_mapping)
    
    async def put(self,body: EnvironmentGroup, request_configuration: Optional[RequestConfiguration[WithGroupItemRequestBuilderPutQueryParameters]] = None) -> Optional[EnvironmentGroup]:
        """
        Update the environment group.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[EnvironmentGroup]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        from ....models.problem_details import ProblemDetails

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ProblemDetails,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.environment_group import EnvironmentGroup

        return await self.request_adapter.send_async(request_info, EnvironmentGroup, error_mapping)
    
    def to_delete_request_information(self,request_configuration: Optional[RequestConfiguration[WithGroupItemRequestBuilderDeleteQueryParameters]] = None) -> RequestInformation:
        """
        Delete the environment group.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.DELETE, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithGroupItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get the environment group.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: EnvironmentGroup, request_configuration: Optional[RequestConfiguration[WithGroupItemRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Update the environment group.
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
    
    def with_url(self,raw_url: str) -> WithGroupItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithGroupItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithGroupItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def add_environment(self) -> AddEnvironmentRequestBuilder:
        """
        The addEnvironment property
        """
        from .add_environment.add_environment_request_builder import AddEnvironmentRequestBuilder

        return AddEnvironmentRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def remove_environment(self) -> RemoveEnvironmentRequestBuilder:
        """
        The removeEnvironment property
        """
        from .remove_environment.remove_environment_request_builder import RemoveEnvironmentRequestBuilder

        return RemoveEnvironmentRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithGroupItemRequestBuilderDeleteQueryParameters():
        """
        Delete the environment group.
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
    class WithGroupItemRequestBuilderDeleteRequestConfiguration(RequestConfiguration[WithGroupItemRequestBuilderDeleteQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithGroupItemRequestBuilderGetQueryParameters():
        """
        Get the environment group.
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
    class WithGroupItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithGroupItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithGroupItemRequestBuilderPutQueryParameters():
        """
        Update the environment group.
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
    class WithGroupItemRequestBuilderPutRequestConfiguration(RequestConfiguration[WithGroupItemRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

