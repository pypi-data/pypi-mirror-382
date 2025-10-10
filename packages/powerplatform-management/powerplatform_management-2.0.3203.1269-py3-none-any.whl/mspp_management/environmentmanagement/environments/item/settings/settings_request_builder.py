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
    from .....models.create_environment_management_setting_response import CreateEnvironmentManagementSettingResponse
    from .....models.get_environment_management_setting_response import GetEnvironmentManagementSettingResponse
    from .....models.operation_response import OperationResponse
    from .settings_patch_request_body import SettingsPatchRequestBody
    from .settings_post_request_body import SettingsPostRequestBody

class SettingsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /environmentmanagement/environments/{environment-id}/settings
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new SettingsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/environmentmanagement/environments/{environment%2Did}/settings?api-version={api%2Dversion}{&%24select*,%24top*}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[SettingsRequestBuilderGetQueryParameters]] = None) -> Optional[GetEnvironmentManagementSettingResponse]:
        """
        Get environment management setting by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[GetEnvironmentManagementSettingResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models.create_environment_management_setting_response import CreateEnvironmentManagementSettingResponse
        from .....models.get_environment_management_setting_response import GetEnvironmentManagementSettingResponse
        from .....models.operation_response import OperationResponse

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": GetEnvironmentManagementSettingResponse,
            "404": GetEnvironmentManagementSettingResponse,
            "429": GetEnvironmentManagementSettingResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.get_environment_management_setting_response import GetEnvironmentManagementSettingResponse

        return await self.request_adapter.send_async(request_info, GetEnvironmentManagementSettingResponse, error_mapping)
    
    async def patch(self,body: SettingsPatchRequestBody, request_configuration: Optional[RequestConfiguration[SettingsRequestBuilderPatchQueryParameters]] = None) -> Optional[OperationResponse]:
        """
        Update fields on the environment management setting.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[OperationResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_patch_request_information(
            body, request_configuration
        )
        from .....models.create_environment_management_setting_response import CreateEnvironmentManagementSettingResponse
        from .....models.get_environment_management_setting_response import GetEnvironmentManagementSettingResponse
        from .....models.operation_response import OperationResponse

        error_mapping: dict[str, type[ParsableFactory]] = {
            "404": OperationResponse,
            "409": OperationResponse,
            "412": OperationResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.operation_response import OperationResponse

        return await self.request_adapter.send_async(request_info, OperationResponse, error_mapping)
    
    async def post(self,body: SettingsPostRequestBody, request_configuration: Optional[RequestConfiguration[SettingsRequestBuilderPostQueryParameters]] = None) -> Optional[CreateEnvironmentManagementSettingResponse]:
        """
        Create environment management settings.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[CreateEnvironmentManagementSettingResponse]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from .....models.create_environment_management_setting_response import CreateEnvironmentManagementSettingResponse
        from .....models.get_environment_management_setting_response import GetEnvironmentManagementSettingResponse
        from .....models.operation_response import OperationResponse

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": CreateEnvironmentManagementSettingResponse,
            "409": CreateEnvironmentManagementSettingResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.create_environment_management_setting_response import CreateEnvironmentManagementSettingResponse

        return await self.request_adapter.send_async(request_info, CreateEnvironmentManagementSettingResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[SettingsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Get environment management setting by ID.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json, application/json;odata.metadata=full, application/json;odata.metadata=full;odata.streaming=false, application/json;odata.metadata=full;odata.streaming=true, application/json;odata.metadata=minimal, application/json;odata.metadata=minimal;odata.streaming=false, application/json;odata.metadata=minimal;odata.streaming=true, application/json;odata.metadata=none, application/json;odata.metadata=none;odata.streaming=false, application/json;odata.metadata=none;odata.streaming=true, application/json;odata.streaming=false, application/json;odata.streaming=true, text/plain;q=0.9")
        return request_info
    
    def to_patch_request_information(self,body: SettingsPatchRequestBody, request_configuration: Optional[RequestConfiguration[SettingsRequestBuilderPatchQueryParameters]] = None) -> RequestInformation:
        """
        Update fields on the environment management setting.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PATCH, '{+baseurl}/environmentmanagement/environments/{environment%2Did}/settings?api-version={api%2Dversion}', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json, application/json;odata.metadata=full, application/json;odata.metadata=full;odata.streaming=false, application/json;odata.metadata=full;odata.streaming=true, application/json;odata.metadata=minimal, application/json;odata.metadata=minimal;odata.streaming=false, application/json;odata.metadata=minimal;odata.streaming=true, application/json;odata.metadata=none, application/json;odata.metadata=none;odata.streaming=false, application/json;odata.metadata=none;odata.streaming=true, application/json;odata.streaming=false, application/json;odata.streaming=true, text/plain;q=0.9")
        request_info.set_content_from_parsable(self.request_adapter, "application/json;odata.metadata=minimal;odata.streaming=true", body)
        return request_info
    
    def to_post_request_information(self,body: SettingsPostRequestBody, request_configuration: Optional[RequestConfiguration[SettingsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Create environment management settings.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, '{+baseurl}/environmentmanagement/environments/{environment%2Did}/settings?api-version={api%2Dversion}', self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json, application/json;odata.metadata=full, application/json;odata.metadata=full;odata.streaming=false, application/json;odata.metadata=full;odata.streaming=true, application/json;odata.metadata=minimal, application/json;odata.metadata=minimal;odata.streaming=false, application/json;odata.metadata=minimal;odata.streaming=true, application/json;odata.metadata=none, application/json;odata.metadata=none;odata.streaming=false, application/json;odata.metadata=none;odata.streaming=true, application/json;odata.streaming=false, application/json;odata.streaming=true, text/plain;q=0.9")
        request_info.set_content_from_parsable(self.request_adapter, "application/json;odata.metadata=minimal;odata.streaming=true", body)
        return request_info
    
    def with_url(self,raw_url: str) -> SettingsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: SettingsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return SettingsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class SettingsRequestBuilderGetQueryParameters():
        """
        Get environment management setting by ID.
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
            if original_name == "select":
                return "%24select"
            if original_name == "top":
                return "%24top"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # List of properties to select for this entity.
        select: Optional[str] = None

        # Number of records to retrieve. If not set, five humdred (500) records are returned.
        top: Optional[int] = None

    
    @dataclass
    class SettingsRequestBuilderGetRequestConfiguration(RequestConfiguration[SettingsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class SettingsRequestBuilderPatchQueryParameters():
        """
        Update fields on the environment management setting.
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
    class SettingsRequestBuilderPatchRequestConfiguration(RequestConfiguration[SettingsRequestBuilderPatchQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class SettingsRequestBuilderPostQueryParameters():
        """
        Create environment management settings.
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
    class SettingsRequestBuilderPostRequestConfiguration(RequestConfiguration[SettingsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

