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
    from .....models.create_backup_request import CreateBackupRequest
    from .....models.environment_backup import EnvironmentBackup
    from .....models.environment_backup_paged_collection import EnvironmentBackupPagedCollection
    from .....models.validation_response import ValidationResponse
    from .item.with_backup_item_request_builder import WithBackupItemRequestBuilder

class BackupsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /environmentmanagement/environments/{environment-id}/backups
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new BackupsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/environmentmanagement/environments/{environment%2Did}/backups?api-version={api%2Dversion}", path_parameters)
    
    def by_backup_id(self,backup_id: str) -> WithBackupItemRequestBuilder:
        """
        Gets an item from the ApiSdk.environmentmanagement.environments.item.backups.item collection
        param backup_id: The ID of the backup.
        Returns: WithBackupItemRequestBuilder
        """
        if backup_id is None:
            raise TypeError("backup_id cannot be null.")
        from .item.with_backup_item_request_builder import WithBackupItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["backupId"] = backup_id
        return WithBackupItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[BackupsRequestBuilderGetQueryParameters]] = None) -> Optional[EnvironmentBackupPagedCollection]:
        """
        Gets the backups for the specified environment.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[EnvironmentBackupPagedCollection]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from .....models.validation_response import ValidationResponse

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ValidationResponse,
            "404": ValidationResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.environment_backup_paged_collection import EnvironmentBackupPagedCollection

        return await self.request_adapter.send_async(request_info, EnvironmentBackupPagedCollection, error_mapping)
    
    async def post(self,body: CreateBackupRequest, request_configuration: Optional[RequestConfiguration[BackupsRequestBuilderPostQueryParameters]] = None) -> Optional[EnvironmentBackup]:
        """
        Creates a backup of the specified environment.
        param body: Request model for creating a backup.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[EnvironmentBackup]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        from .....models.validation_response import ValidationResponse

        error_mapping: dict[str, type[ParsableFactory]] = {
            "400": ValidationResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from .....models.environment_backup import EnvironmentBackup

        return await self.request_adapter.send_async(request_info, EnvironmentBackup, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[BackupsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Gets the backups for the specified environment.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json, text/plain;q=0.9")
        return request_info
    
    def to_post_request_information(self,body: CreateBackupRequest, request_configuration: Optional[RequestConfiguration[BackupsRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Creates a backup of the specified environment.
        param body: Request model for creating a backup.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json, text/plain;q=0.9")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> BackupsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: BackupsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return BackupsRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class BackupsRequestBuilderGetQueryParameters():
        """
        Gets the backups for the specified environment.
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
    class BackupsRequestBuilderGetRequestConfiguration(RequestConfiguration[BackupsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class BackupsRequestBuilderPostQueryParameters():
        """
        Creates a backup of the specified environment.
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
    class BackupsRequestBuilderPostRequestConfiguration(RequestConfiguration[BackupsRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

